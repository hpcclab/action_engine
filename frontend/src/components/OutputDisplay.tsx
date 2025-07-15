import React, { useState } from 'react';
import { FaDownload, FaEye, FaImage, FaVideo, FaFileAudio, FaFileAlt, FaExternalLinkAlt } from 'react-icons/fa';

interface OutputFile {
  filename: string;
  url: string;
  content_type: string;
  size?: number;
  description?: string;
}

interface ProcessedOutput {
  success: boolean;
  message?: string;
  files?: OutputFile[];
  text_output?: string;
  execution_time?: number;
  metadata?: Record<string, any>;
}

interface OutputDisplayProps {
  output: ProcessedOutput;
  title?: string;
}

const OutputDisplay: React.FC<OutputDisplayProps> = ({ output, title = "Workflow Output" }) => {
  const [previewFile, setPreviewFile] = useState<OutputFile | null>(null);

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

  const handlePreview = (file: OutputFile) => {
    if (file.content_type.startsWith('image/')) {
      setPreviewFile(file);
    } else {
      window.open(file.url, '_blank');
    }
  };

  const handleDownload = (file: OutputFile) => {
    const link = document.createElement('a');
    link.href = file.url;
    link.download = file.filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!output.success) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-800 mb-2">{title}</h3>
        <div className="flex items-center space-x-2 text-red-700">
          <span className="text-xl">❌</span>
          <span>Workflow execution failed</span>
        </div>
        {output.message && (
          <p className="mt-2 text-sm text-red-600">{output.message}</p>
        )}
      </div>
    );
  }

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-green-800">{title}</h3>
        <div className="flex items-center space-x-2 text-green-700">
          <span className="text-xl">✅</span>
          <span className="text-sm">Completed</span>
          {output.execution_time && (
            <span className="text-xs text-gray-500">
              ({output.execution_time}s)
            </span>
          )}
        </div>
      </div>

      {output.message && (
        <div className="mb-4 p-3 bg-white rounded border">
          <p className="text-sm text-gray-700">{output.message}</p>
        </div>
      )}

      {output.text_output && (
        <div className="mb-4 p-3 bg-white rounded border">
          <h4 className="font-medium text-gray-800 mb-2">Text Output:</h4>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
            {output.text_output}
          </pre>
        </div>
      )}

      {output.files && output.files.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-800">Generated Files:</h4>
          <div className="grid gap-3">
            {output.files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-white rounded-lg border hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  {getFileIcon(file.content_type)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.filename}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span>{file.content_type}</span>
                      {file.size && (
                        <>
                          <span>•</span>
                          <span>{formatFileSize(file.size)}</span>
                        </>
                      )}
                    </div>
                    {file.description && (
                      <p className="text-xs text-gray-600 mt-1">{file.description}</p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePreview(file)}
                    className="p-2 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded"
                    title="Preview/View file"
                  >
                    {file.content_type.startsWith('image/') ? <FaEye /> : <FaExternalLinkAlt />}
                  </button>
                  <button
                    onClick={() => handleDownload(file)}
                    className="p-2 text-green-500 hover:text-green-700 hover:bg-green-50 rounded"
                    title="Download file"
                  >
                    <FaDownload />
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
              ✕
            </button>
            <img
              src={previewFile.url}
              alt={previewFile.filename}
              className="max-w-full max-h-full object-contain"
            />
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 text-white p-2 rounded">
              <p className="text-sm">{previewFile.filename}</p>
              {previewFile.description && (
                <p className="text-xs opacity-75">{previewFile.description}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OutputDisplay; 