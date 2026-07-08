import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";
import { uploadSingle, uploadMultiple } from "../uploadHandler";
import * as db from "../db";
import * as fileProcessor from "../fileProcessor";
import * as rag from "../rag";
import fs from "fs";
import path from "path";

const UPLOAD_ROOT = process.env.UPLOAD_ROOT || path.resolve(process.cwd(), "uploads");

function safeUnlinkUpload(filePath: string | undefined) {
  if (!filePath) return;

  try {
    const root = fs.realpathSync(path.resolve(UPLOAD_ROOT));
    const resolvedPath = path.resolve(root, filePath);
    const absoluteFilePath = fs.realpathSync(resolvedPath);

    if (absoluteFilePath !== root && !absoluteFilePath.startsWith(root + path.sep)) {
      // Do not delete files outside the upload root
      return;
    }

    fs.unlinkSync(absoluteFilePath);
  } catch {
    // Swallow errors to avoid crashing on cleanup
  }
}

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

/**
 * Process uploaded file asynchronously
 */
async function processFileAsync(
  fileId: number, 
  filePath: string, 
  fileType: string, 
  agentId: number, 
  userId: number,
  customTitle?: string
) {
  try {
    // Extract text from file
    const processed = await fileProcessor.processFile(filePath, fileType);
    
    // Update file upload with extracted text
    await db.updateFileUpload(fileId, {
      extractedText: processed.text,
      metadata: processed.metadata,
      processedAt: new Date(),
    });
    
    // Create knowledge source from extracted text
    const source = await db.createKnowledgeSource({
      agentId,
      userId,
      sourceType: "file",
      title: customTitle || `File Upload (${fileType.toUpperCase()})`,
      content: processed.text,
      metadata: {
        fileId,
        ...processed.metadata,
      },
      status: "pending",
      charactersCount: processed.text.length,
    });
    
    // Link file upload to knowledge source
    await db.updateFileUpload(fileId, {
      sourceId: source.id,
      status: "completed",
    });
    
    // Process document for RAG (chunk and embed)
    const ragProcessed = await rag.processDocumentForRAG(processed.text);
    
    // Save embeddings
    for (const chunk of ragProcessed) {
      await db.createKnowledgeEmbedding({
        sourceId: source.id,
        agentId,
        chunkText: chunk.text,
        chunkIndex: chunk.index,
        embedding: chunk.embedding,
        metadata: chunk.metadata,
      });
    }
    
    // Update source status
    await db.updateKnowledgeSource(source.id, userId, {
      status: "trained",
      chunksCount: ragProcessed.length,
    });
    
    // Update agent's last trained timestamp
    await db.updateAgent(agentId, userId, {
      lastTrainedAt: new Date(),
    });
    
    console.log(`✓ File processed successfully: ${fileId}`);
  } catch (error) {
    console.error(`✗ File processing failed: ${fileId}`, error);
    await db.updateFileUpload(fileId, {
      status: "error",
      errorMessage: error instanceof Error ? error.message : "Unknown error",
    });
    
    // Clean up file on error
    try {
      safeUnlinkUpload(filePath);
    } catch (cleanupError) {
      console.error(`Failed to cleanup file ${fileId}:`, cleanupError);
    }
  }
}

async function startServer() {
  const app = express();
  const server = createServer(app);
  // Configure body parser with larger size limit for file uploads
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  
  // File upload endpoint
  app.post("/api/upload", async (req, res) => {
    uploadSingle(req, res, async (err) => {
      if (err) {
        return res.status(400).json({ 
          success: false, 
          error: err.message 
        });
      }
      
      if (!req.file) {
        return res.status(400).json({ 
          success: false, 
          error: "No file uploaded" 
        });
      }
      
      try {
        // Get user from session (assuming context has user info)
        const context = await createContext({ req, res, info: {} as any });
        if (!context.user) {
          // Clean up uploaded file
          safeUnlinkUpload(req.file.path);
          return res.status(401).json({ 
            success: false, 
            error: "Unauthorized" 
          });
        }
        
        const agentId = parseInt(req.body.agentId || "0");
        if (!agentId) {
          safeUnlinkUpload(req.file.path);
          return res.status(400).json({ 
            success: false, 
            error: "Agent ID is required" 
          });
        }
        
        // Verify agent ownership
        const agent = await db.getAgentById(agentId, context.user.id);
        if (!agent) {
          safeUnlinkUpload(req.file.path);
          return res.status(403).json({ 
            success: false, 
            error: "Agent not found or access denied" 
          });
        }
        
        // Create file upload record
        const fileType = fileProcessor.mimeTypeToFileType(req.file.mimetype);
        const fileUpload = await db.createFileUpload({
          agentId,
          userId: context.user.id,
          filename: req.file.filename,
          originalFilename: req.file.originalname,
          fileType: fileType as any,
          mimeType: req.file.mimetype,
          fileSize: req.file.size,
          localPath: req.file.path,
          status: "processing",
        });
        
        // Get custom title from request
        const customTitle = req.body.title?.trim() || undefined;
        
        // Process file in background
        processFileAsync(fileUpload.id, req.file.path, fileType, agentId, context.user.id, customTitle)
          .catch((error) => {
            console.error(`Background file processing error for file ${fileUpload.id}:`, error);
          });
        
        res.json({ 
          success: true, 
          fileId: fileUpload.id,
          filename: req.file.originalname,
          fileSize: req.file.size 
        });
      } catch (error) {
        // Clean up uploaded file on error
        if (req.file) {
          safeUnlinkUpload(req.file.path);
        }
        res.status(500).json({ 
          success: false, 
          error: error instanceof Error ? error.message : "Unknown error" 
        });
      }
    });
  });
  
  // OAuth callback under /api/oauth/callback
  registerOAuthRoutes(app);
  // tRPC API
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
