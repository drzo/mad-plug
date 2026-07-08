-- Create file uploads table for tracking uploaded files
CREATE TABLE IF NOT EXISTS `fileUploads` (
  `id` int AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `agentId` int NOT NULL,
  `userId` int NOT NULL,
  `sourceId` int,
  `filename` varchar(255) NOT NULL,
  `originalFilename` varchar(255) NOT NULL,
  `fileType` enum('pdf','docx','doc','txt','md') NOT NULL,
  `mimeType` varchar(100) NOT NULL,
  `fileSize` int NOT NULL,
  `s3Key` varchar(500),
  `localPath` varchar(500),
  `status` enum('uploading','processing','completed','error') NOT NULL DEFAULT 'uploading',
  `errorMessage` text,
  `extractedText` text,
  `metadata` json,
  `uploadedAt` timestamp NOT NULL DEFAULT (now()),
  `processedAt` timestamp
);
--> statement-breakpoint

-- Add indexes for performance
CREATE INDEX idx_file_uploads_agent ON `fileUploads`(`agentId`);
--> statement-breakpoint
CREATE INDEX idx_file_uploads_user ON `fileUploads`(`userId`);
--> statement-breakpoint
CREATE INDEX idx_file_uploads_source ON `fileUploads`(`sourceId`);
--> statement-breakpoint
CREATE INDEX idx_file_uploads_status ON `fileUploads`(`status`);
