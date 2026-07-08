# RAG Knowledge System

## Overview

This implementation adds a comprehensive RAG (Retrieval-Augmented Generation) knowledge training system inspired by Chatbase's legacy RAG learning chatbots.

## Key Features

### ✨ Core Capabilities
- **Knowledge Source Management**: Add text, files, URLs, and Q&A pairs
- **Auto-Training System**: Automatic processing and embedding generation
- **Vector Similarity Search**: Semantic retrieval using cosine similarity
- **Context Augmentation**: Inject relevant knowledge into LLM prompts
- **Real-time Status Tracking**: Monitor training jobs and processing status

### 🎨 User Interface
- **Knowledge Base Page**: Full-featured management interface
- **Training Dashboard**: Visual progress tracking with stats
- **RAG Toggle**: Enable/disable RAG in Playground
- **Dark Mode**: Purple/indigo theme consistent with design
- **Navigation Integration**: Seamless access from agent pages

### 🔧 Technical Implementation
- **Text Chunking**: Smart overlapping windows (1000 chars, 200 overlap)
- **Embeddings**: OpenAI-compatible API (text-embedding-3-small)
- **Vector Storage**: JSON format in MySQL database
- **Retrieval**: Top-K search with similarity thresholds
- **Context Building**: Relevance-scored knowledge injection

## Quick Start

### 1. Add Knowledge Sources

Navigate to an agent's Knowledge Base page and add sources:

```typescript
// Via UI or API
POST /api/knowledge.create
{
  agentId: 1,
  sourceType: "text",
  title: "Product Documentation",
  content: "Your knowledge content here..."
}
```

### 2. Train Your Agent

Process knowledge sources individually or in batch:

```typescript
// Process single source
POST /api/knowledge.process
{ sourceId: 1 }

// Or batch train all pending sources
POST /api/knowledge.train
{ agentId: 1 }
```

### 3. Test with RAG

Use the Playground with RAG enabled:

```typescript
POST /api/chat.sendMessage
{
  agentId: 1,
  message: "What is our return policy?",
  useRAG: true
}
```

## Architecture

### Database Schema

```sql
-- Knowledge Sources
CREATE TABLE knowledgeSources (
  id INT PRIMARY KEY,
  agentId INT,
  sourceType ENUM('text', 'file', 'url', 'qa'),
  title VARCHAR(255),
  content TEXT,
  status ENUM('pending', 'processing', 'trained', 'error'),
  chunksCount INT
);

-- Vector Embeddings
CREATE TABLE knowledgeEmbeddings (
  id INT PRIMARY KEY,
  sourceId INT,
  agentId INT,
  chunkText TEXT,
  chunkIndex INT,
  embedding JSON  -- 1536-dimensional vector
);

-- Training Jobs
CREATE TABLE trainingJobs (
  id INT PRIMARY KEY,
  agentId INT,
  status ENUM('queued', 'processing', 'completed', 'failed'),
  sourcesProcessed INT,
  sourcesTotal INT
);
```

### RAG Pipeline

```
1. Ingestion → 2. Chunking → 3. Embedding → 4. Storage
                                              ↓
5. Query → 6. Embed Query → 7. Find Similar → 8. Build Context → 9. LLM
```

### Retrieval Flow

```typescript
// 1. Generate query embedding
const queryEmbedding = await generateEmbedding(userMessage);

// 2. Find relevant chunks
const relevantChunks = findRelevantChunks(
  queryEmbedding,
  agentEmbeddings,
  topK: 5,
  minSimilarity: 0.7
);

// 3. Build augmented context
const ragContext = buildRAGContext(relevantChunks, maxLength: 3000);

// 4. Inject into system prompt
const systemPrompt = ragContext + originalSystemPrompt;
```

## API Reference

### Knowledge Endpoints

```typescript
// List knowledge sources
knowledge.list({ agentId: number })

// Get specific source
knowledge.get({ id: number })

// Create new source
knowledge.create({
  agentId: number,
  sourceType: "text" | "file" | "url" | "qa",
  title: string,
  content?: string,
  sourceUrl?: string
})

// Process source (chunk & embed)
knowledge.process({ sourceId: number })

// Delete source
knowledge.delete({ id: number })

// Batch train agent
knowledge.train({ agentId: number })

// Get training jobs
knowledge.getTrainingJobs({ agentId: number })
```

### Enhanced Chat

```typescript
// Send message with RAG
chat.sendMessage({
  agentId: number,
  message: string,
  useRAG?: boolean,  // default: true
  sessionId?: number
})
```

## Configuration

### Environment Variables

```bash
# Required for embeddings
FORGE_API_KEY=your_api_key_here
FORGE_API_URL=https://api.your-provider.com  # optional

# Database
DATABASE_URL=mysql://user:pass@host:3306/db
```

### Customization Options

```typescript
// Chunking parameters (in server/rag.ts)
const CHUNK_SIZE = 1000;        // characters per chunk
const CHUNK_OVERLAP = 200;      // overlap between chunks

// Retrieval parameters (in server/routers.ts)
const TOP_K = 5;                // number of chunks to retrieve
const MIN_SIMILARITY = 0.7;     // minimum relevance threshold
const MAX_CONTEXT_LENGTH = 3000; // max characters in context
```

## Use Cases

### Customer Support Bot
Train with FAQ, policies, and documentation to provide accurate answers.

### Technical Documentation Assistant
Index code documentation, API references, and guides for developer queries.

### Domain Expert Chatbot
Load industry-specific knowledge to create specialized AI assistants.

### Educational Tutor
Train with course materials, textbooks, and learning resources.

## Performance Considerations

### Optimization Tips
- **Batch Processing**: Process multiple sources together
- **Chunk Size**: Larger chunks = fewer DB rows but less granular
- **Indexing**: Add indexes on frequently queried fields
- **Caching**: Cache embeddings for repeated queries (future enhancement)

### Scaling
- Current implementation suitable for agents with up to 10,000 chunks
- For larger deployments, consider:
  - Dedicated vector database (Pinecone, Weaviate)
  - Async processing with job queue
  - Embedding caching layer

## Troubleshooting

### Common Issues

**Problem**: Sources stuck in "pending"
**Solution**: Click "Process" or "Train Agent" to trigger processing

**Problem**: Low retrieval relevance
**Solution**: Add more specific knowledge, lower similarity threshold

**Problem**: Embedding generation fails
**Solution**: Verify FORGE_API_KEY is set and API is accessible

**Problem**: Out of memory during processing
**Solution**: Process sources individually instead of batch training

## Roadmap

### Completed ✅
- ✅ Database schema and migrations
- ✅ RAG service implementation
- ✅ API endpoints
- ✅ Knowledge Base UI
- ✅ Playground integration
- ✅ Training status tracking

### Planned 🚧
- 🚧 File upload support (PDF, DOCX, TXT)
- 🚧 URL scraping and web crawling
- 🚧 Scheduled auto-retraining
- 🚧 Knowledge source versioning
- 🚧 Embedding caching
- 🚧 Advanced chunking strategies
- 🚧 Multi-language support
- 🚧 Custom embedding models

## Contributing

To extend the RAG system:

1. **Add new source types**: Update `sourceType` enum in schema
2. **Customize chunking**: Modify `chunkText()` in `server/rag.ts`
3. **Change embedding model**: Update `generateEmbedding()` API call
4. **Adjust retrieval**: Modify `findRelevantChunks()` parameters

## Documentation

- **Full Guide**: See [RAG_DOCUMENTATION.md](./RAG_DOCUMENTATION.md)
- **Examples**: See [examples/rag-examples.ts](./examples/rag-examples.ts)
- **Schema**: See [drizzle/0003_rag_knowledge_system.sql](./drizzle/0003_rag_knowledge_system.sql)

## License

MIT License - See LICENSE file for details
