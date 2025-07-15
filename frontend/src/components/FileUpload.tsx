import React, { useState, useRef, useCallback } from 'react';
import { FaCloudUploadAlt, FaImage, FaVideo, FaFileAudio, FaFileAlt, FaTimes, FaEye } from 'react-icons/fa';

interface UploadedFile {
  original_filename: string;
  s3_key: string;
  s3_url: string;
  public_url: string;
  content_type: string;
  file_size: number;
  presigned_url: string;
  success?: boolean;
  error?: string;
}

interface FileUploadProps {
  onFilesUploaded: (files: UploadedFile[]) => void;
  maxFiles?: number;
  acceptedTypes?: string[];
}

const FileUpload: React.FC<FileUploadProps> = ({ 
  onFilesUploaded, 
  maxFiles = 10,
  acceptedTypes = ['image/*', 'video/*', 'audio/*', 'text/*', '.pdf', '.doc', '.docx']
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [previewFile, setPreviewFile] = useState<UploadedFile | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getFileIcon = (contentType: string) => {
    if (contentType.startsWith('image/')) return <FaImage className="text-blue-500" />;
    if (contentType.startsWith('video/')) return <FaVideo className="text-purple-500" />;
    if (contentType.startsWith('audio/')) return <FaFileAudio className="text-green-500" />;
    return <FaFileAlt className="text-gray-500" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files);
      if (uploadedFiles.length + files.length <= maxFiles) {
        uploadFiles(files);
      } else {
        alert(`Maximum ${maxFiles} files allowed`);
      }
    }
  }, [uploadedFiles.length, maxFiles]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      if (uploadedFiles.length + files.length <= maxFiles) {
        uploadFiles(files);
      } else {
        alert(`Maximum ${maxFiles} files allowed`);
      }
    }
  };

  const uploadFiles = async (files: File[]) => {
    setIsUploading(true);
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/upload-files', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (result.uploaded_files) {
        const successfulUploads = result.uploaded_files.filter((file: UploadedFile) => file.success !== false);
        const newFiles = [...uploadedFiles, ...successfulUploads];
        setUploadedFiles(newFiles);
        onFilesUploaded(newFiles);

        // Show errors for failed uploads
        const failedUploads = result.uploaded_files.filter((file: UploadedFile) => file.success === false);
        if (failedUploads.length > 0) {
          alert(`Some files failed to upload: ${failedUploads.map((f: UploadedFile) => f.error).join(', ')}`);
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload files. Please try again.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
    onFilesUploaded(newFiles);
  };

  const clearAllFiles = () => {
    setUploadedFiles([]);
    onFilesUploaded([]);
  };

  const openPreview = (file: UploadedFile) => {
    if (file.content_type.startsWith('image/')) {
      setPreviewFile(file);
    } else {
      // For non-image files, open in new tab
      window.open(file.presigned_url, '_blank');
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <FaCloudUploadAlt className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          {isUploading ? 'Uploading...' : 'Drop files here or click to upload'}
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Supports images, videos, audio files, and documents (max {maxFiles} files)
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
          disabled={isUploading}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading || uploadedFiles.length >= maxFiles}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg transition-colors"
        >
          {isUploading ? 'Uploading...' : 'Select Files'}
        </button>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Uploaded Files ({uploadedFiles.length})</h3>
            <button
              onClick={clearAllFiles}
              className="text-red-500 hover:text-red-700 text-sm"
            >
              Clear All
            </button>
          </div>
          
          <div className="grid gap-3 max-h-60 overflow-y-auto">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  {getFileIcon(file.content_type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.original_filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.file_size)} • {file.content_type}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => openPreview(file)}
                    className="p-1 text-blue-500 hover:text-blue-700"
                    title="Preview/View file"
                  >
                    <FaEye />
                  </button>
                  <button
                    onClick={() => removeFile(index)}
                    className="p-1 text-red-500 hover:text-red-700"
                    title="Remove file"
                  >
                    <FaTimes />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Image Preview Modal */}
      {previewFile && previewFile.content_type.startsWith('image/') && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-4xl max-h-full">
            <button
              onClick={() => setPreviewFile(null)}
              className="absolute top-4 right-4 text-white text-xl hover:text-gray-300 z-10"
            >
              <FaTimes />
            </button>
            <img
              src={previewFile.presigned_url}
              alt={previewFile.original_filename}
              className="max-w-full max-h-full object-contain"
            />
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white p-2 rounded">
              <p className="text-sm">{previewFile.original_filename}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 