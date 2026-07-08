# API Documentation
## AI Chatbot Management Platform - API Reference

**Version**: 2.0.0  
**Last Updated**: January 30, 2026  
**Base URL**: `/api`  
**Protocol**: tRPC (Type-safe RPC)

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Agents API](#agents-api)
3. [Knowledge API](#knowledge-api)
4. [Chat API](#chat-api)
5. [Chat Logs API](#chat-logs-api)
6. [Analytics API](#analytics-api)
7. [Settings API](#settings-api)
8. [Storage API](#storage-api)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

All API requests require authentication via session cookies or API keys.

### Authentication Methods

#### Session-Based (Web)
```typescript
// Login
POST /api/auth.login
{
  email: string;
  password: string;
}

// Logout
POST /api/auth.logout

// Get current user
GET /api/auth.me
```

#### API Key (Programmatic)
```typescript
Headers:
  Authorization: Bearer YOUR_API_KEY
```

---

## 🤖 Agents API

Manage AI agents and their configurations.

### List Agents
```typescript
GET /api/agent.list

Response: {
  id: number;
  name: string;
  systemPrompt: string;
  model: string;
  temperature: number;
  maxTokens: number;
  status: "active" | "training" | "needs_retraining";
  conversationStarters: string[];
  constraints: {
    maxLength: number;
    visibility: string;
    rateLimit: number;
  };
  createdAt: Date;
  updatedAt: Date;
}[]
```

### Get Agent
```typescript
GET /api/agent.get
Input: { id: number }

Response: {
  id: number;
  name: string;
  systemPrompt: string;
  model: string;
  temperature: number;
  maxTokens: number;
  status: string;
  conversationStarters: string[];
  constraints: object;
  createdAt: Date;
  updatedAt: Date;
  // Statistics
  totalMessages: number;
  totalSessions: number;
  averageSignalScore: number;
}
```

### Create Agent
```typescript
POST /api/agent.create
Input: {
  name: string;
  systemPrompt?: string;
  model?: string; // default: "gpt-4"
  temperature?: number; // default: 0.7
  maxTokens?: number; // default: 2000
  conversationStarters?: string[];
  constraints?: {
    maxLength?: number;
    visibility?: string;
    rateLimit?: number;
  };
}

Response: {
  id: number;
  name: string;
  // ... other agent fields
}
```

### Update Agent
```typescript
POST /api/agent.update
Input: {
  id: number;
  name?: string;
  systemPrompt?: string;
  model?: string;
  temperature?: number;
  maxTokens?: number;
  conversationStarters?: string[];
  constraints?: object;
  status?: string;
}

Response: {
  id: number;
  // ... updated agent fields
}
```

### Delete Agent
```typescript
POST /api/agent.delete
Input: { id: number }

Response: { success: boolean }
```

### Clone Agent
```typescript
POST /api/agent.clone
Input: {
  id: number;
  newName?: string; // default: "Copy of {original name}"
}

Response: {
  id: number;
  // ... cloned agent fields
}
```

---

## 🧠 Knowledge API

Manage RAG knowledge sources and training.

### List Knowledge Sources
```typescript
GET /api/knowledge.list
Input: { agentId: number }

Response: {
  id: number;
  agentId: number;
  sourceType: "text" | "file" | "url" | "qa";
  title: string;
  content?: string;
  sourceUrl?: string;
  status: "pending" | "processing" | "trained" | "error";
  characterCount: number;
  chunksCount: number;
  errorMessage?: string;
  createdAt: Date;
  processedAt?: Date;
}[]
```

### Get Knowledge Source
```typescript
GET /api/knowledge.get
Input: { id: number }

Response: {
  id: number;
  agentId: number;
  sourceType: string;
  title: string;
  content: string;
  sourceUrl?: string;
  status: string;
  characterCount: number;
  chunksCount: number;
  errorMessage?: string;
  metadata: object;
  createdAt: Date;
  processedAt?: Date;
  // Related embeddings
  embeddings: {
    id: number;
    chunkText: string;
    chunkIndex: number;
  }[];
}
```

### Create Knowledge Source
```typescript
POST /api/knowledge.create
Input: {
  agentId: number;
  sourceType: "text" | "file" | "url" | "qa";
  title: string;
  content?: string; // Required for text and qa types
  sourceUrl?: string; // Required for url type
  question?: string; // For qa type
  answer?: string; // For qa type
  metadata?: object;
}

Response: {
  id: number;
  agentId: number;
  sourceType: string;
  title: string;
  status: "pending";
  createdAt: Date;
}
```

### Process Knowledge Source
```typescript
POST /api/knowledge.process
Input: { sourceId: number }

Response: {
  id: number;
  status: "trained";
  chunksCount: number;
  processedAt: Date;
}

// Processing Steps:
// 1. Chunk text into overlapping segments
// 2. Generate embeddings for each chunk
// 3. Store vectors in database
// 4. Update source status
```

### Delete Knowledge Source
```typescript
POST /api/knowledge.delete
Input: { id: number }

Response: { success: boolean }
```

### Batch Train Agent
```typescript
POST /api/knowledge.train
Input: { agentId: number }

Response: {
  jobId: number;
  status: "queued" | "processing";
  sourcesTotal: number;
  sourcesProcessed: number;
  startedAt: Date;
}

// Processes all pending sources for the agent
// Returns immediately with job ID
// Check progress with getTrainingJobs
```

### Get Training Jobs
```typescript
GET /api/knowledge.getTrainingJobs
Input: {
  agentId: number;
  limit?: number; // default: 10
}

Response: {
  id: number;
  agentId: number;
  status: "queued" | "processing" | "completed" | "failed";
  jobType: "initial" | "retrain" | "incremental";
  sourcesTotal: number;
  sourcesProcessed: number;
  errorMessage?: string;
  startedAt: Date;
  completedAt?: Date;
}[]
```

---

## 💬 Chat API

Send messages and interact with agents.

### Send Message
```typescript
POST /api/chat.sendMessage
Input: {
  agentId: number;
  sessionId?: number; // Optional, creates new session if not provided
  message: string;
  useRAG?: boolean; // default: true
  temperature?: number; // Override agent temperature
  maxTokens?: number; // Override agent max tokens
}

Response: {
  messageId: number;
  sessionId: number;
  role: "assistant";
  content: string;
  signalScore: number;
  aiRequestsCount: number;
  ragContext?: {
    chunks: {
      text: string;
      similarity: number;
      sourceId: number;
      sourceTitle: string;
    }[];
    totalChunks: number;
  };
  metadata: {
    model: string;
    tokensUsed: number;
    responseTime: number;
  };
  createdAt: Date;
}

// With RAG enabled:
// 1. Generate query embedding
// 2. Retrieve relevant knowledge chunks (Top-K)
// 3. Build augmented context
// 4. Send to LLM with context
// 5. Return enhanced response
```

### Create Session
```typescript
POST /api/chat.createSession
Input: {
  agentId: number;
  metadata?: object;
}

Response: {
  sessionId: number;
  agentId: number;
  createdAt: Date;
}
```

### Get Session Messages
```typescript
GET /api/chat.getMessages
Input: {
  sessionId: number;
  limit?: number; // default: 50
  offset?: number; // default: 0
}

Response: {
  id: number;
  sessionId: number;
  role: "user" | "assistant";
  content: string;
  signalScore?: number;
  aiRequestsCount?: number;
  metadata: object;
  createdAt: Date;
}[]
```

### Clear Session
```typescript
POST /api/chat.clearSession
Input: { sessionId: number }

Response: { success: boolean }
```

---

## 📝 Chat Logs API

View and manage conversation history.

### List Sessions
```typescript
GET /api/logs.listSessions
Input: {
  agentId?: number; // Optional filter
  startDate?: string; // ISO date
  endDate?: string; // ISO date
  search?: string; // Search in messages
  limit?: number; // default: 20
  offset?: number; // default: 0
}

Response: {
  id: number;
  agentId: number;
  agentName: string;
  userId?: number;
  messageCount: number;
  lastMessage: string;
  lastMessageAt: Date;
  averageSignalScore: number;
  createdAt: Date;
}[]
```

### Get Session Details
```typescript
GET /api/logs.getSession
Input: { sessionId: number }

Response: {
  id: number;
  agentId: number;
  agentName: string;
  userId?: number;
  messageCount: number;
  averageSignalScore: number;
  createdAt: Date;
  messages: {
    id: number;
    role: string;
    content: string;
    signalScore?: number;
    aiRequestsCount?: number;
    createdAt: Date;
  }[];
}
```

### Export Sessions
```typescript
POST /api/logs.export
Input: {
  agentId?: number;
  sessionIds?: number[]; // Specific sessions
  startDate?: string;
  endDate?: string;
  format: "csv" | "pdf" | "json";
}

Response: {
  url: string; // S3 presigned URL
  expiresAt: Date;
  filename: string;
  fileSize: number;
}
```

### Delete Session
```typescript
POST /api/logs.deleteSession
Input: { sessionId: number }

Response: { success: boolean }
```

---

## 📊 Analytics API

Get insights and metrics.

### Get Agent Analytics
```typescript
GET /api/analytics.getAgentStats
Input: {
  agentId: number;
  startDate?: string; // default: 30 days ago
  endDate?: string; // default: now
}

Response: {
  totalMessages: number;
  totalSessions: number;
  userMessages: number;
  botMessages: number;
  averageSignalScore: number;
  averageResponseTime: number;
  peakUsageHour: number;
  messagesByDay: {
    date: string;
    count: number;
  }[];
  topicDistribution: {
    topic: string;
    count: number;
    percentage: number;
  }[];
  signalScoreDistribution: {
    range: string;
    count: number;
  }[];
}
```

### Get Dashboard Metrics
```typescript
GET /api/analytics.getDashboard

Response: {
  totalAgents: number;
  activeAgents: number;
  totalMessages: number;
  totalSessions: number;
  averageSignalScore: number;
  recentActivity: {
    agentId: number;
    agentName: string;
    messageCount: number;
    lastActivity: Date;
  }[];
  alerts: {
    id: number;
    type: string;
    message: string;
    severity: "low" | "medium" | "high";
    createdAt: Date;
  }[];
}
```

### Get Topic Analysis
```typescript
GET /api/analytics.getTopics
Input: {
  agentId?: number;
  startDate?: string;
  endDate?: string;
  limit?: number; // default: 10
}

Response: {
  topic: string;
  count: number;
  percentage: number;
  trend: "up" | "down" | "stable";
  examples: string[];
}[]
```

### Get Emoji Usage
```typescript
GET /api/analytics.getEmojiStats
Input: {
  agentId?: number;
  startDate?: string;
  endDate?: string;
}

Response: {
  emoji: string;
  count: number;
  sentiment: "positive" | "negative" | "neutral";
}[]
```

---

## ⚙️ Settings API

Manage account and configuration.

### Get Settings
```typescript
GET /api/settings.get

Response: {
  user: {
    id: number;
    email: string;
    name: string;
    createdAt: Date;
  };
  credits: {
    balance: number;
    used: number;
    resetDate: Date;
  };
  apiKeys: {
    id: number;
    name: string;
    key: string; // Masked: sk-***...***xyz
    lastUsed?: Date;
    createdAt: Date;
  }[];
  integrations: {
    database?: {
      type: string;
      connected: boolean;
    };
    storage?: {
      type: string;
      connected: boolean;
    };
  };
}
```

### Update Settings
```typescript
POST /api/settings.update
Input: {
  name?: string;
  email?: string;
  preferences?: {
    theme?: string;
    notifications?: boolean;
    emailAlerts?: boolean;
  };
}

Response: { success: boolean }
```

### Create API Key
```typescript
POST /api/settings.createApiKey
Input: {
  name: string;
  permissions?: string[];
}

Response: {
  id: number;
  name: string;
  key: string; // Full key, shown only once
  createdAt: Date;
}
```

### Revoke API Key
```typescript
POST /api/settings.revokeApiKey
Input: { id: number }

Response: { success: boolean }
```

---

## 📦 Storage API

Manage file uploads and storage.

### Upload File
```typescript
POST /api/storage.uploadFile
Input: FormData {
  file: File;
  agentId?: number;
  type: "avatar" | "document" | "export";
}

Response: {
  fileId: number;
  filename: string;
  url: string;
  size: number;
  type: string;
  createdAt: Date;
}
```

### Get Upload URL
```typescript
POST /api/storage.getUploadUrl
Input: {
  filename: string;
  contentType: string;
  size: number;
}

Response: {
  uploadUrl: string; // Presigned S3 URL
  fileId: number;
  expiresIn: number; // seconds
}
```

### Delete File
```typescript
POST /api/storage.deleteFile
Input: { fileId: number }

Response: { success: boolean }
```

---

## ❌ Error Handling

All API endpoints return errors in a consistent format.

### Error Response Structure
```typescript
{
  error: {
    code: string;
    message: string;
    details?: object;
  }
}
```

### Common Error Codes

#### Authentication Errors
- `UNAUTHORIZED` - Not authenticated
- `FORBIDDEN` - Insufficient permissions
- `INVALID_TOKEN` - Invalid or expired token

#### Validation Errors
- `VALIDATION_ERROR` - Input validation failed
- `INVALID_INPUT` - Invalid input format
- `REQUIRED_FIELD` - Required field missing

#### Resource Errors
- `NOT_FOUND` - Resource not found
- `ALREADY_EXISTS` - Resource already exists
- `CONFLICT` - Resource conflict

#### Rate Limiting
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `QUOTA_EXCEEDED` - Usage quota exceeded

#### Server Errors
- `INTERNAL_ERROR` - Internal server error
- `SERVICE_UNAVAILABLE` - Service temporarily unavailable
- `TIMEOUT` - Request timeout

### Example Error Response
```typescript
{
  error: {
    code: "VALIDATION_ERROR",
    message: "Invalid agent ID",
    details: {
      field: "agentId",
      value: -1,
      constraint: "Must be a positive integer"
    }
  }
}
```

---

## 🚦 Rate Limiting

API requests are rate-limited to ensure fair usage.

### Rate Limits

#### Free Tier
- **API Requests**: 100 per minute
- **Messages**: 1,000 per day
- **Embeddings**: 10,000 per day
- **File Uploads**: 10 per hour

#### Pro Tier
- **API Requests**: 500 per minute
- **Messages**: 10,000 per day
- **Embeddings**: 100,000 per day
- **File Uploads**: 100 per hour

#### Enterprise Tier
- **Custom limits** based on agreement

### Rate Limit Headers
```typescript
Headers:
  X-RateLimit-Limit: 100        // Max requests per window
  X-RateLimit-Remaining: 95     // Requests remaining
  X-RateLimit-Reset: 1738247400 // Unix timestamp when limit resets
```

### Rate Limit Exceeded Response
```typescript
Status: 429 Too Many Requests
{
  error: {
    code: "RATE_LIMIT_EXCEEDED",
    message: "Rate limit exceeded. Please try again later.",
    details: {
      limit: 100,
      remaining: 0,
      resetAt: "2026-01-30T09:30:00Z"
    }
  }
}
```

---

## 🔧 Request/Response Examples

### Example: Create Agent and Add Knowledge

```typescript
// 1. Create an agent
const agent = await api.agent.create({
  name: "Customer Support Bot",
  systemPrompt: "You are a helpful customer support assistant.",
  model: "gpt-4",
  temperature: 0.7,
  conversationStarters: [
    "How can I help you today?",
    "What can I assist you with?",
    "Tell me about your issue"
  ]
});
// Response: { id: 1, name: "Customer Support Bot", ... }

// 2. Add knowledge source
const knowledge = await api.knowledge.create({
  agentId: agent.id,
  sourceType: "text",
  title: "Product FAQ",
  content: "Q: What is your return policy?\nA: We offer 30-day returns..."
});
// Response: { id: 1, status: "pending", ... }

// 3. Process knowledge
const processed = await api.knowledge.process({
  sourceId: knowledge.id
});
// Response: { id: 1, status: "trained", chunksCount: 5, ... }

// 4. Send a test message
const response = await api.chat.sendMessage({
  agentId: agent.id,
  message: "What is your return policy?",
  useRAG: true
});
// Response: {
//   content: "We offer a 30-day return policy...",
//   ragContext: { chunks: [...], totalChunks: 5 },
//   ...
// }
```

### Example: Export Chat Logs

```typescript
// Export last month's chat logs
const exportResult = await api.logs.export({
  agentId: 1,
  startDate: "2026-01-01",
  endDate: "2026-01-31",
  format: "csv"
});

// Response: {
//   url: "https://s3.amazonaws.com/bucket/exports/logs-123.csv",
//   expiresAt: "2026-01-30T10:00:00Z",
//   filename: "chat-logs-2026-01.csv",
//   fileSize: 1048576
// }

// Download the file
const response = await fetch(exportResult.url);
const blob = await response.blob();
// ... handle download
```

### Example: Get Analytics

```typescript
// Get agent analytics for last 30 days
const analytics = await api.analytics.getAgentStats({
  agentId: 1,
  startDate: "2026-01-01",
  endDate: "2026-01-30"
});

// Response: {
//   totalMessages: 1234,
//   totalSessions: 567,
//   averageSignalScore: 0.85,
//   messagesByDay: [
//     { date: "2026-01-01", count: 42 },
//     { date: "2026-01-02", count: 38 },
//     ...
//   ],
//   topicDistribution: [
//     { topic: "returns", count: 123, percentage: 15.5 },
//     { topic: "shipping", count: 98, percentage: 12.3 },
//     ...
//   ]
// }
```

---

## 📚 SDK Examples

### JavaScript/TypeScript

```typescript
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import type { AppRouter } from './server/routers';

const client = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: 'http://localhost:3000/api',
      headers() {
        return {
          authorization: `Bearer ${API_KEY}`,
        };
      },
    }),
  ],
});

// Use the client
const agents = await client.agent.list.query();
const response = await client.chat.sendMessage.mutate({
  agentId: 1,
  message: "Hello!"
});
```

### Python (using requests)

```python
import requests

API_URL = "http://localhost:3000/api"
API_KEY = "your_api_key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create agent
response = requests.post(
    f"{API_URL}/agent.create",
    json={
        "name": "My Agent",
        "systemPrompt": "You are helpful"
    },
    headers=headers
)
agent = response.json()

# Send message
response = requests.post(
    f"{API_URL}/chat.sendMessage",
    json={
        "agentId": agent["id"],
        "message": "Hello!",
        "useRAG": True
    },
    headers=headers
)
message = response.json()
print(message["content"])
```

---

## 🔒 Security Best Practices

### API Key Management
1. **Never commit API keys** to version control
2. **Rotate keys regularly** (every 90 days recommended)
3. **Use environment variables** for key storage
4. **Set appropriate permissions** for each key
5. **Monitor key usage** for anomalies

### Request Security
1. **Use HTTPS** for all API requests
2. **Validate all inputs** on client side
3. **Handle errors gracefully** without exposing details
4. **Implement retry logic** with exponential backoff
5. **Set timeouts** for all requests

### Data Protection
1. **Don't log sensitive data** (passwords, API keys)
2. **Sanitize user inputs** before display
3. **Use parameterized queries** (handled by ORM)
4. **Encrypt sensitive data** at rest
5. **Implement CORS** properly

---

## 📞 Support

### Getting Help
- **Documentation**: https://github.com/o9nn/cbase
- **GitHub Issues**: https://github.com/o9nn/cbase/issues
- **GitHub Discussions**: https://github.com/o9nn/cbase/discussions

### Reporting Issues
When reporting API issues, include:
1. Request method and endpoint
2. Request payload (sanitized)
3. Response status and body
4. Timestamp of the request
5. Your API key ID (not the key itself)

---

## 📝 Changelog

### Version 2.0.0 (2026-01-30)
- ✅ Added RAG knowledge system endpoints
- ✅ Enhanced chat API with RAG support
- ✅ Added training job tracking
- ✅ Improved error handling
- ✅ Added comprehensive analytics

### Version 1.0.0 (2026-01-15)
- ✅ Initial API release
- ✅ Agent management
- ✅ Chat functionality
- ✅ Basic analytics
- ✅ Settings management

---

*API Documentation v2.0.0 - Last Updated: January 30, 2026*
