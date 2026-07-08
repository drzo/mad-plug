-- Create knowledge sources table for RAG training data
CREATE TABLE IF NOT EXISTS `knowledgeSources` (
  `id` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `agentId` int NOT NULL,
  `userId` int NOT NULL,
  `sourceType` enum('text','file','url','qa') NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text,
  `sourceUrl` text,
  `metadata` json,
  `status` enum('pending','processing','trained','error') NOT NULL DEFAULT 'pending',
  `errorMessage` text,
  `charactersCount` int DEFAULT 0,
  `chunksCount` int DEFAULT 0,
  `createdAt` timestamp NOT NULL DEFAULT (now()),
  `updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP
);
--> statement-breakpoint

-- Create knowledge embeddings table for vector storage
CREATE TABLE IF NOT EXISTS `knowledgeEmbeddings` (
  `id` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `sourceId` int NOT NULL,
  `agentId` int NOT NULL,
  `chunkText` text NOT NULL,
  `chunkIndex` int NOT NULL,
  `embedding` json,
  `metadata` json,
  `createdAt` timestamp NOT NULL DEFAULT (now())
);
--> statement-breakpoint

-- Create training jobs table for auto-training tracking
CREATE TABLE IF NOT EXISTS `trainingJobs` (
  `id` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `agentId` int NOT NULL,
  `userId` int NOT NULL,
  `jobType` enum('initial','retrain','incremental') NOT NULL,
  `status` enum('queued','processing','completed','failed') NOT NULL DEFAULT 'queued',
  `sourcesProcessed` int DEFAULT 0,
  `sourcesTotal` int DEFAULT 0,
  `errorMessage` text,
  `startedAt` timestamp,
  `completedAt` timestamp,
  `createdAt` timestamp NOT NULL DEFAULT (now())
);
--> statement-breakpoint

-- Add indexes for performance
CREATE INDEX idx_knowledge_sources_agent ON `knowledgeSources`(`agentId`);
--> statement-breakpoint
CREATE INDEX idx_knowledge_sources_user ON `knowledgeSources`(`userId`);
--> statement-breakpoint
CREATE INDEX idx_knowledge_sources_status ON `knowledgeSources`(`status`);
--> statement-breakpoint
CREATE INDEX idx_knowledge_embeddings_source ON `knowledgeEmbeddings`(`sourceId`);
--> statement-breakpoint
CREATE INDEX idx_knowledge_embeddings_agent ON `knowledgeEmbeddings`(`agentId`);
--> statement-breakpoint
CREATE INDEX idx_training_jobs_agent ON `trainingJobs`(`agentId`);
--> statement-breakpoint
CREATE INDEX idx_training_jobs_status ON `trainingJobs`(`status`);
