// QuesryForm.tsx

import React, { useState, useContext } from "react";
import { WorkflowContext } from "./WorkflowContext";
import FileUpload from "./FileUpload";

// Type definition for uploaded files
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

// Type definition for the status object received from the backend
type ExecutionStatus = {
  status: string;
  [key: string]: any;
};

export default function QueryForm() {
  // Local state for the user query and loading flag
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [showFileUpload, setShowFileUpload] = useState(false);

  // Access global workflow-related setters from context
  const { setInvokeUrl, setExecutionArn, setStatusResult } = useContext(WorkflowContext);

  // Handler for file uploads
  const handleFilesUploaded = (files: UploadedFile[]) => {
    setUploadedFiles(files);
  };

  // Handler for generating and running the workflow
  const handleGenerate = async () => {
    setLoading(true);
    setStatusResult(null); // Reset any previous result

    try {
      let data;
      
      if (uploadedFiles.length > 0) {
        // Use the file-aware endpoint
        const fileUrls = uploadedFiles.map(file => file.s3_url);
        const res = await fetch("http://localhost:8000/generate-and-run-workflow-with-files", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            user_query: query,
            file_urls: fileUrls
          })
        });
        data = await res.json();
      } else {
        // Use the regular endpoint
        const res = await fetch("http://localhost:8000/generate-and-run-workflow", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_query: query })
        });
        data = await res.json();
      }

      if (data.execution_arn) {
        // If workflow started successfully, update context
        setExecutionArn(data.execution_arn);
        setInvokeUrl(data.invoke_api_endpoint);

        // Poll the execution status (max 10 times, every 3 sec)
        let statusJson: ExecutionStatus = { status: "UNKNOWN" };
        for (let i = 0; i < 10; i++) {
          const statusRes = await fetch(
            `http://localhost:8000/execution-status?executionArn=${encodeURIComponent(data.execution_arn)}`
          );
          statusJson = await statusRes.json();
          if (statusJson.status !== "RUNNING") break;
          await new Promise((r) => setTimeout(r, 3000)); // wait 3 sec
        }

        // If succeeded but contains an error inside the output, treat as FAILED
        if (statusJson.status === "SUCCEEDED" && statusJson.output?.error) {
          setStatusResult({
              ...statusJson,
              status: "FAILED",
              error: statusJson.output.error,
          });
        } else {
          setStatusResult(statusJson); // Normal success or failure
        }
      } else if (data.error) {
        // If the workflow failed to start
        setStatusResult({ status: "FAILED", error: data.error });
      } else {
        // Unknown backend response
        setStatusResult({ status: "FAILED", error: "Workflow registration failed." });
      }
    } catch (err) {
      console.error("Failed to generate workflow", err);
      alert("Failed to generate workflow");
    } finally {
      setLoading(false); // Reset loading indicator
    }
  };

  return (
    <div className="bg-white p-6 rounded-md shadow-md border space-y-4">
      {/* Text input for the user's workflow description */}
      <textarea
        placeholder="Describe your workflow in natural language..."
        rows={4}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full p-4 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
      ></textarea>

      {/* File Upload Toggle */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => setShowFileUpload(!showFileUpload)}
          className="text-blue-600 hover:text-blue-800 font-medium flex items-center space-x-2"
        >
          <span>{showFileUpload ? '📁 Hide' : '📎 Add'} File Inputs</span>
          {uploadedFiles.length > 0 && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''}
            </span>
          )}
        </button>
      </div>

      {/* File Upload Area */}
      {showFileUpload && (
        <div className="border-t pt-4">
          <FileUpload onFilesUploaded={handleFilesUploaded} maxFiles={5} />
        </div>
      )}

      {/* Button to trigger workflow generation */}
      <button
        onClick={handleGenerate}
        disabled={loading || !query}
        className={`w-full py-3 px-4 font-semibold rounded-lg transition text-white shadow-md
          ${loading ? "bg-blue-300 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"}`}
      >
        {loading ? "⏳ Generating..." : 
         uploadedFiles.length > 0 ? 
         `🚀 Generate & Run Workflow (${uploadedFiles.length} files)` : 
         "🚀 Generate & Run Workflow"}
      </button>
    </div>
  );
}
