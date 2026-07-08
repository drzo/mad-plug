/**
 * RAG Service - Handles document ingestion, chunking, embeddings, and retrieval
 * Inspired by Chatbase legacy RAG knowledge training system
 */

import { ENV } from "./_core/env";

export interface ChunkResult {
  text: string;
  index: number;
  metadata?: Record<string, unknown>;
}

export interface EmbeddingResult {
  embedding: number[];
  text: string;
}

/**
 * Chunk text into smaller pieces for embedding
 * Uses a sliding window approach with overlap for context preservation
 */
export function chunkText(
  text: string,
  chunkSize: number = 1000,
  chunkOverlap: number = 200
): ChunkResult[] {
  const chunks: ChunkResult[] = [];
  
  // Clean and normalize text
  const cleanedText = text
    .replace(/\s+/g, ' ')
    .replace(/\n+/g, '\n')
    .trim();
  
  if (cleanedText.length === 0) {
    return chunks;
  }
  
  let startIndex = 0;
  let chunkIndex = 0;
  
  while (startIndex < cleanedText.length) {
    // Calculate end index for this chunk
    let endIndex = startIndex + chunkSize;
    
    // If this is not the last chunk, try to break at sentence boundary
    if (endIndex < cleanedText.length) {
      // Look for sentence endings within the last 200 chars of the chunk
      const searchStart = Math.max(endIndex - 200, startIndex);
      const segment = cleanedText.slice(searchStart, endIndex + 100);
      const sentenceEnd = segment.search(/[.!?]\s/);
      
      if (sentenceEnd !== -1) {
        endIndex = searchStart + sentenceEnd + 1;
      }
    } else {
      endIndex = cleanedText.length;
    }
    
    const chunkText = cleanedText.slice(startIndex, endIndex).trim();
    
    if (chunkText.length > 0) {
      chunks.push({
        text: chunkText,
        index: chunkIndex,
        metadata: {
          startChar: startIndex,
          endChar: endIndex,
          length: chunkText.length,
        },
      });
      chunkIndex++;
    }
    
    // Move to next chunk with overlap
    startIndex = endIndex - chunkOverlap;
    if (startIndex >= cleanedText.length) break;
  }
  
  return chunks;
}

/**
 * Generate embeddings for text using OpenAI-compatible embedding API
 */
export async function generateEmbedding(text: string): Promise<number[]> {
  if (!ENV.forgeApiKey) {
    throw new Error("FORGE_API_KEY is required for embeddings");
  }
  
  const apiUrl = ENV.forgeApiUrl && ENV.forgeApiUrl.trim().length > 0
    ? `${ENV.forgeApiUrl.replace(/\/$/, "")}/v1/embeddings`
    : "https://forge.manus.im/v1/embeddings";
  
  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${ENV.forgeApiKey}`,
    },
    body: JSON.stringify({
      model: "text-embedding-3-small",
      input: text,
    }),
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Embedding generation failed: ${response.status} - ${errorText}`);
  }
  
  const data = await response.json();
  return data.data[0].embedding;
}

/**
 * Generate embeddings for multiple text chunks
 */
export async function generateEmbeddings(texts: string[]): Promise<EmbeddingResult[]> {
  const results: EmbeddingResult[] = [];
  
  // Process in batches to avoid rate limits
  const batchSize = 10;
  for (let i = 0; i < texts.length; i += batchSize) {
    const batch = texts.slice(i, i + batchSize);
    const batchPromises = batch.map(async (text) => {
      const embedding = await generateEmbedding(text);
      return { embedding, text };
    });
    
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
    
    // Small delay between batches
    if (i + batchSize < texts.length) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }
  
  return results;
}

/**
 * Calculate cosine similarity between two vectors
 */
export function cosineSimilarity(vecA: number[], vecB: number[]): number {
  if (vecA.length !== vecB.length) {
    throw new Error("Vectors must have the same length");
  }
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }
  
  normA = Math.sqrt(normA);
  normB = Math.sqrt(normB);
  
  if (normA === 0 || normB === 0) {
    return 0;
  }
  
  return dotProduct / (normA * normB);
}

/**
 * Find most relevant chunks for a query using vector similarity
 */
export function findRelevantChunks(
  queryEmbedding: number[],
  embeddings: Array<{ id: number; embedding: number[]; text: string; metadata?: Record<string, unknown> }>,
  topK: number = 5,
  minSimilarity: number = 0.7
): Array<{ id: number; text: string; similarity: number; metadata?: Record<string, unknown> }> {
  const similarities = embeddings.map((item) => ({
    id: item.id,
    text: item.text,
    similarity: cosineSimilarity(queryEmbedding, item.embedding),
    metadata: item.metadata,
  }));
  
  // Filter by minimum similarity and sort by descending similarity
  const relevant = similarities
    .filter((item) => item.similarity >= minSimilarity)
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, topK);
  
  return relevant;
}

/**
 * Process a document for RAG: chunk and embed
 */
export async function processDocumentForRAG(
  text: string,
  chunkSize: number = 1000,
  chunkOverlap: number = 200
): Promise<Array<{ text: string; embedding: number[]; index: number; metadata?: Record<string, unknown> }>> {
  // Chunk the text
  const chunks = chunkText(text, chunkSize, chunkOverlap);
  
  if (chunks.length === 0) {
    return [];
  }
  
  // Generate embeddings for all chunks
  const texts = chunks.map(c => c.text);
  const embeddingResults = await generateEmbeddings(texts);
  
  // Combine chunks with embeddings
  return chunks.map((chunk, idx) => ({
    text: chunk.text,
    embedding: embeddingResults[idx].embedding,
    index: chunk.index,
    metadata: chunk.metadata,
  }));
}

/**
 * Build augmented context for LLM from retrieved chunks
 */
export function buildRAGContext(
  relevantChunks: Array<{ text: string; similarity: number }>,
  maxContextLength: number = 3000
): string {
  if (relevantChunks.length === 0) {
    return "";
  }
  
  let context = "Based on the following relevant information:\n\n";
  let currentLength = context.length;
  
  for (let i = 0; i < relevantChunks.length; i++) {
    const chunk = relevantChunks[i];
    const chunkHeader = `[Source ${i + 1}, relevance: ${(chunk.similarity * 100).toFixed(1)}%]\n`;
    const chunkText = `${chunk.text}\n\n`;
    const chunkContent = chunkHeader + chunkText;
    
    if (currentLength + chunkContent.length > maxContextLength) {
      break;
    }
    
    context += chunkContent;
    currentLength += chunkContent.length;
  }
  
  context += "Please answer the user's question based on the above information. If the information is not sufficient to answer the question, please say so.\n\n";
  
  return context;
}
