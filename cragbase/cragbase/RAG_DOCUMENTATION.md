# RAG Knowledge System Documentation

## Overview

The RAG (Retrieval-Augmented Generation) Knowledge System enables agents to be trained with custom knowledge sources and use that knowledge to provide more accurate, contextual responses.

## Features

### 1. Knowledge Sources
- **Text**: Direct text content pasted into the system
- **File**: Document uploads (planned for future enhancement)
- **URL**: Web pages to scrape and learn from (planned for future enhancement)
- **Q&A**: Question-answer pairs for specific knowledge

### 2. Training Pipeline
1. **Ingestion**: Add knowledge sources to your agent
2. **Chunking**: Text is split into overlapping chunks (1000 chars, 200 overlap)
3. **Embedding**: Each chunk is converted to a vector embedding
4. **Storage**: Embeddings are stored for fast retrieval
5. **Status Tracking**: Monitor processing status in real-time

### 3. Retrieval Process
1. User sends a message to the agent
2. Message is converted to an embedding
3. Top 5 most relevant knowledge chunks are retrieved using cosine similarity
4. Relevant chunks are injected into the system prompt with relevance scores
5. LLM generates response using both the knowledge and conversation context

## Usage Guide

### Adding Knowledge Sources

1. Navigate to your agent's Knowledge Base page
2. Click "Add Source"
3. Select source type (text, file, URL, Q&A)
4. Enter a descriptive title
5. Provide the content
6. Click "Add Source"

The source will be marked as "pending" and ready for processing.

### Training Your Agent

**Manual Processing:**
1. Click "Process" on individual pending sources
2. Wait for processing to complete
3. Source status will update to "trained"

**Batch Training:**
1. Add multiple knowledge sources
2. Click "Train Agent" to process all pending sources
3. Monitor training progress in the stats cards

### Using RAG in Playground

1. Go to agent's Playground
2. Click "Settings" 
3. Enable "RAG Knowledge Retrieval" toggle
4. Send messages to test RAG-enhanced responses
5. Responses will include context from trained knowledge

## Technical Details

### Text Chunking
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Boundary Detection**: Attempts to break at sentence boundaries
- **Metadata**: Each chunk includes position, length, and index

### Embeddings
- **Model**: text-embedding-3-small (via OpenAI-compatible API)
- **Dimension**: 1536 (standard for this model)
- **Storage**: JSON format in MySQL
- **Batch Processing**: 10 chunks at a time to manage rate limits

### Retrieval
- **Algorithm**: Cosine similarity
- **Top-K**: 5 most relevant chunks
- **Minimum Similarity**: 0.7 threshold
- **Context Length**: Max 3000 characters
- **Ranking**: Chunks sorted by relevance score

### Database Schema

**knowledgeSources**
- Stores source metadata and raw content
- Tracks processing status
- Records character and chunk counts

**knowledgeEmbeddings**
- Stores vector embeddings
- Links to source and agent
- Includes chunk text and metadata

**trainingJobs**
- Tracks training operations
- Records progress and status
- Logs errors for debugging

## API Endpoints

### Knowledge Management
- `knowledge.list` - List all sources for an agent
- `knowledge.get` - Get a specific source
- `knowledge.create` - Add a new source
- `knowledge.process` - Process a pending source
- `knowledge.delete` - Remove a source

### Training
- `knowledge.train` - Trigger batch training
- `knowledge.getTrainingJobs` - View training history

### Chat Integration
- `chat.sendMessage` - Send message with optional RAG (useRAG parameter)

## Best Practices

### Content Guidelines
- **Be Specific**: Add focused, relevant content
- **Good Structure**: Use clear paragraphs and sections
- **Avoid Duplication**: Don't add the same information multiple times
- **Regular Updates**: Retrain when adding significant new content

### Performance Tips
- **Chunk Size**: Default 1000 chars works well for most content
- **Source Organization**: Group related content in single sources
- **Training Frequency**: Train after adding 5-10 sources, not after each one
- **Cleanup**: Remove outdated sources to maintain quality

### Monitoring
- Check training job status regularly
- Review signal scores to measure response quality
- Monitor chunk counts for source processing
- Use playground to test RAG effectiveness

## Troubleshooting

### Source stays in "pending" status
- Click "Process" manually to trigger processing
- Check that content is not empty
- Verify API key is configured

### Low relevance scores
- Add more specific knowledge sources
- Ensure content is relevant to queries
- Adjust minimum similarity threshold if needed

### Processing errors
- Check error message in source details
- Verify content is valid text
- Ensure embeddings API is accessible

## Future Enhancements

Planned features:
- File upload support (PDF, DOCX, TXT)
- URL scraping and crawling
- Automatic retraining schedules
- Knowledge source versioning
- Multi-language support
- Custom embedding models
- Advanced chunking strategies

## Support

For issues or questions:
1. Check the error messages in source details
2. Review training job logs
3. Test with simple text sources first
4. Verify API connectivity in settings
