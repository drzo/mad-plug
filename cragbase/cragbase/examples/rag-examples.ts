/**
 * RAG System Test Examples
 * 
 * These examples demonstrate the RAG system functionality.
 * Run these tests after setting up a test agent with knowledge sources.
 */

import { chunkText, cosineSimilarity, findRelevantChunks, buildRAGContext } from '../server/rag';

// Example 1: Text Chunking
console.log("=== Example 1: Text Chunking ===\n");

const sampleText = `Artificial Intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Machine learning is a subset of AI that provides systems the ability to automatically learn and improve from experience.`;

const chunks = chunkText(sampleText, 100, 20);
console.log(`Created ${chunks.length} chunks from text of ${sampleText.length} characters`);
console.log("\nFirst chunk:", chunks[0]);

// Example 2: Cosine Similarity
console.log("\n=== Example 2: Cosine Similarity ===\n");

const vec1 = [1, 0, 0, 1, 0];
const vec2 = [1, 0, 0, 0, 1];
console.log("Similarity:", cosineSimilarity(vec1, vec2).toFixed(3));

// Example 3: Finding Relevant Chunks
console.log("\n=== Example 3: Finding Relevant Chunks ===\n");

const mockEmbeddings = [
  { id: 1, embedding: [0.9, 0.1, 0.2], text: "Machine learning is a subset of AI", metadata: {} },
  { id: 2, embedding: [0.1, 0.9, 0.1], text: "Deep learning uses neural networks", metadata: {} },
];

const queryEmbedding = [0.85, 0.15, 0.25];
const relevant = findRelevantChunks(queryEmbedding, mockEmbeddings, 2, 0.6);
console.log("Top relevant chunks:", relevant.length);

export { };
