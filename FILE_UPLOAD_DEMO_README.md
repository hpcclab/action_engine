# Multi-Input File Upload System for Automatic Workflow Generation

## 🚀 Overview

This system enables the AutomaticWorkflowGeneration platform to accept and process multiple input types including **images, videos, voice recordings, and text files**. Files are uploaded to AWS S3 and workflows can retrieve and process them automatically.

## ✨ Features

### **Frontend Capabilities**
- 📤 **Drag-and-drop file upload** with visual feedback
- 🖼️ **Multi-file support** (images, videos, audio, documents)
- 👁️ **File preview** with modal display for images
- 📊 **File management** (view, remove, clear all)
- 🔄 **Progress indicators** and error handling
- 📱 **Responsive design** with Tailwind CSS

### **Backend Capabilities**
- ☁️ **AWS S3 integration** with automatic bucket creation
- 🔒 **Secure file handling** with presigned URLs
- 🏷️ **Metadata tracking** (filename, size, type, timestamp)
- 🔗 **Workflow integration** with file-aware endpoints
- 📡 **RESTful API** for file operations

### **Workflow Processing**
- 🧠 **AI-enhanced** workflow generation using file context
- 🔄 **Automatic execution** with file parameters
- 📝 **Enhanced output display** with file preview and download
- 📊 **Result visualization** with proper file type handling

## 🛠️ Installation & Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 3. AWS Configuration
Ensure your AWS credentials are configured:
```bash
aws configure
# OR set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-2
```

### 4. Start Services
```bash
# Terminal 1: Backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

## 📋 API Endpoints

### **File Upload**
```http
POST /upload-files
Content-Type: multipart/form-data

# Upload multiple files
curl -X POST "http://localhost:8000/upload-files" \
  -F "files=@image1.jpg" \
  -F "files=@document.pdf"
```

### **Workflow with Files**
```http
POST /generate-and-run-workflow-with-files
Content-Type: application/json

{
  "user_query": "Process the uploaded image and enhance its quality",
  "file_urls": ["s3://automatic-workflow-files/abc123.jpg"]
}
```

### **File Information**
```http
GET /file-info/{s3_key}
# Returns file metadata and presigned URL
```

### **File Deletion**
```http
DELETE /files/{s3_key}
# Removes file from S3
```

## 🖼️ Image Processing Demo

### **Run the Demo**
```bash
python demo_image_workflow.py
```

### **Available Demo Workflows**

1. **Image Enhancement**
   - Enhance quality, apply filters, resize to 1024x768
   
2. **Style Transfer**
   - Apply artistic effects (watercolor, oil painting, etc.)
   
3. **Object Detection**
   - Detect and label objects with bounding boxes
   
4. **Background Removal**
   - Remove background, add transparency
   
5. **Analysis Report**
   - Generate detailed image analysis report

### **Demo Features**
- 🎨 **Sample image generation** with PIL
- 📤 **Automatic upload** to S3
- 🔄 **Real-time monitoring** of workflow execution
- 📊 **Results display** with file links and metadata

## 💻 Usage Examples

### **Frontend Integration**
```tsx
import FileUpload from './components/FileUpload';

function MyComponent() {
  const handleFilesUploaded = (files) => {
    console.log('Uploaded files:', files);
    // files array contains S3 URLs and metadata
  };

  return (
    <FileUpload 
      onFilesUploaded={handleFilesUploaded}
      maxFiles={5}
      acceptedTypes={['image/*', 'video/*', 'audio/*']}
    />
  );
}
```

### **Backend Processing**
```python
from utils.s3_handler import S3FileHandler

s3_handler = S3FileHandler()

# Upload file
result = s3_handler.upload_file(
    file_content=file_bytes,
    filename="example.jpg",
    content_type="image/jpeg"
)

# Get presigned URL for secure access
url = s3_handler.get_presigned_url(result["s3_key"])
```

## 🎯 Supported File Types

| Category | Extensions | Max Size | Processing |
|----------|------------|----------|------------|
| **Images** | `.jpg`, `.png`, `.gif`, `.bmp`, `.webp` | 50MB | ✅ Preview, Enhancement, Analysis |
| **Videos** | `.mp4`, `.avi`, `.mov`, `.mkv` | 500MB | ✅ Transcoding, Analysis |
| **Audio** | `.mp3`, `.wav`, `.flac`, `.aac` | 100MB | ✅ Transcription, Analysis |
| **Documents** | `.pdf`, `.doc`, `.docx`, `.txt` | 25MB | ✅ Text extraction, Processing |

## 🔧 Configuration

### **S3 Settings**
```python
# In utils/s3_handler.py
S3FileHandler(
    bucket_name="automatic-workflow-files",  # Change bucket name
    region="us-east-2"                       # Change AWS region
)
```

### **Frontend Settings**
```tsx
// In FileUpload component
<FileUpload 
  maxFiles={10}                              // Max files per upload
  acceptedTypes={['image/*', 'video/*']}     // Allowed file types
/>
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │    AWS S3       │
│                 │    │                 │    │                 │
│ • FileUpload    │───▶│ • /upload-files │───▶│ • File Storage  │
│ • QueryForm     │    │ • /workflows    │    │ • Presigned URLs│
│ • OutputDisplay │    │ • S3Handler     │    │ • Metadata      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        ▼                        │
         │              ┌─────────────────┐                │
         │              │ AWS Step Functions │              │
         │              │                 │                │
         └──────────────│ • Workflow Exec │◀───────────────┘
                        │ • File Processing│
                        │ • Result Output │
                        └─────────────────┘
```

## 🚨 Error Handling

### **Common Issues**

1. **AWS Credentials**
   ```bash
   # Error: Unable to locate credentials
   aws configure  # Set up credentials
   ```

2. **CORS Issues**
   ```javascript
   // Backend already configured for localhost:3000, 3001
   // Add your domain to CORS origins in main.py
   ```

3. **File Size Limits**
   ```python
   # Increase limits in FastAPI if needed
   app.add_middleware(
       MaxSizeMiddleware,
       max_size=100_000_000  # 100MB
   )
   ```

4. **S3 Bucket Permissions**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": ["s3:*"],
         "Resource": ["arn:aws:s3:::automatic-workflow-files/*"]
       }
     ]
   }
   ```

## 🔮 Future Enhancements

- [ ] **Batch processing** for multiple files
- [ ] **Real-time collaboration** on uploaded files
- [ ] **Advanced file preview** (PDF, video thumbnails)
- [ ] **Cloud storage options** (Google Drive, Dropbox)
- [ ] **File versioning** and history
- [ ] **Automated cleanup** of old files
- [ ] **CDN integration** for faster access
- [ ] **File compression** and optimization

## 📚 Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [FastAPI File Upload Guide](https://fastapi.tiangolo.com/tutorial/request-files/)
- [React File Upload Best Practices](https://react.dev/learn/sharing-state-between-components)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🎉 Quick Start Example

```bash
# 1. Start the system
uvicorn main:app --reload &
cd frontend && npm start &

# 2. Open browser to http://localhost:3000

# 3. Try the demo
python demo_image_workflow.py

# 4. Upload an image and create a workflow like:
# "Enhance this image quality and resize it to 800x600"
```

**Result**: Your workflow will automatically process the uploaded image and provide downloadable results! 🎨✨ 