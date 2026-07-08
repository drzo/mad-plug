# Phase 8: File Upload & Processing Implementation

## Overview

This phase implements comprehensive file upload and processing capabilities for the CBase platform, allowing users to upload documents (PDF, DOCX, TXT, MD) for RAG knowledge training.

## Features Implemented

### 1. File Processing Service (`server/fileProcessor.ts`)
- **PDF Text Extraction**: Extracts text from PDF files using `pdf-parse`
- **DOCX Processing**: Extracts text from Word documents using `mammoth`
- **Plain Text Support**: Handles TXT and MD files
- **Metadata Extraction**: Captures page count, word count, author, and title
- **Validation**: File size (max 10MB) and file type validation

### 2. File Upload Handler (`server/uploadHandler.ts`)
- **Multer Configuration**: Handles multipart/form-data file uploads
- **Local Storage**: Saves files to `/uploads` directory
- **File Filtering**: Only allows supported file types
- **Size Limits**: Enforces 10MB maximum file size
- **Unique Filenames**: Generates unique IDs to prevent conflicts

### 3. Database Schema
- **fileUploads Table**: Tracks uploaded files with metadata
  - File information (name, type, size, mime type)
  - Processing status (uploading, processing, completed, error)
  - Links to knowledge sources after processing
  - Error tracking
  - Timestamps

### 4. API Endpoints
- **POST /api/upload**: Upload file via multipart form data
- **GET /api/trpc/knowledge.listFiles**: List files for an agent
- **GET /api/trpc/knowledge.getFile**: Get specific file details
- **DELETE /api/trpc/knowledge.deleteFile**: Delete file and associated data

### 5. Automatic Processing Pipeline
1. File uploaded via API
2. File metadata stored in database
3. Background processing starts:
   - Text extraction from file
   - Create knowledge source
   - Chunk text for RAG
   - Generate embeddings
   - Update agent training status
4. Status updates reflected in UI

### 6. User Interface
- **File Upload Dialog**: Drag-and-drop or click to upload
- **File Type Selection**: Select "File" in source type dropdown
- **Upload Progress**: Shows uploading/processing status
- **File List Tab**: Dedicated tab showing all uploaded files
- **File Management**: View file details and delete files
- **Status Badges**: Visual indicators for processing status

## Usage

### Uploading a File

1. Navigate to Knowledge Base page for an agent
2. Click "Add Knowledge Source"
3. Select "File" as the source type
4. Enter a descriptive title
5. Click or drag-and-drop to upload a file
6. Supported formats: PDF, DOCX, DOC, TXT, MD
7. Maximum size: 10MB
8. Click "Add Source" to upload

### Viewing Uploaded Files

1. Navigate to Knowledge Base page
2. Click on the "Uploaded Files" tab
3. View list of all uploaded files with:
   - File name and type
   - File size
   - Upload date
   - Processing status
   - Error messages (if any)

### Deleting Files

1. Go to Uploaded Files tab
2. Click trash icon next to file
3. Confirm deletion
4. File and associated knowledge source are removed

## Technical Details

### File Processing Flow

```
User uploads file
       ↓
POST /api/upload
       ↓
Create fileUpload record (status: uploading)
       ↓
Save file to disk
       ↓
Update status to processing
       ↓
Extract text from file
       ↓
Create knowledgeSource
       ↓
Chunk and embed text
       ↓
Update status to completed
```

### Error Handling

- **Invalid File Type**: Rejected at upload
- **File Too Large**: Rejected at upload
- **Processing Errors**: Logged in database with error message
- **User Feedback**: Toast notifications for all operations

### Security Considerations

- File type validation on server-side
- Size limits enforced
- User authentication required
- Files stored outside web root
- Secure file deletion

## Configuration

### Environment Variables
No new environment variables required. Uses existing:
- `DATABASE_URL`: For database access
- `FORGE_API_KEY`: For embeddings generation

### File Storage
- Local storage in `/uploads` directory
- Added to `.gitignore` to prevent commits
- Can be migrated to S3 in future (handler already supports it)

## Dependencies Added

```json
{
  "pdf-parse": "^2.4.5",
  "mammoth": "^1.11.0",
  "multer": "^2.0.2",
  "@types/multer": "^2.0.0",
  "@types/pdf-parse": "^1.1.5"
}
```

## Migration

Database migration file: `drizzle/0004_file_uploads.sql`

Run migrations:
```bash
pnpm run db:push
```

## Testing Checklist

- [ ] Upload PDF file
- [ ] Upload DOCX file
- [ ] Upload TXT file
- [ ] Test file size validation (>10MB)
- [ ] Test invalid file type
- [ ] Test file processing and text extraction
- [ ] Test knowledge source creation
- [ ] Test file deletion
- [ ] Test concurrent uploads
- [ ] Test error handling

## Future Enhancements

1. **S3 Storage Integration**: Move files to S3 for production
2. **Image OCR**: Extract text from images in PDFs
3. **Advanced PDF Processing**: Handle tables and complex layouts
4. **Batch Upload**: Upload multiple files at once
5. **File Preview**: Preview file content before processing
6. **Download Original**: Allow downloading original files
7. **Re-process**: Ability to re-process files with different settings

## Known Limitations

1. PDF password-protected files not supported
2. Complex PDF layouts may not extract perfectly
3. Large files (near 10MB) may take time to process
4. Binary formats (images, videos) not supported

## Support

For issues or questions:
- Check server logs for processing errors
- Verify file format and size
- Ensure database migrations are applied
- Check file system permissions for `/uploads` directory
