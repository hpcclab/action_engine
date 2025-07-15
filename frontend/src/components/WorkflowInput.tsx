// WorkflowInput

import React, { useContext, useState } from "react";
import { WorkflowContext } from "./WorkflowContext";

export default function WorkflowInput() {
  const { invokeUrl, setStatusResult, setInvokeUrl } = useContext(WorkflowContext);
  const [manualInput, setManualInput] = useState('{\n  "key": "value"\n}');
  const [loading, setLoading] = useState(false);

  const handleManualExecution = async () => {
    if (!invokeUrl) {
      alert("No invoke URL available. Please generate a workflow first.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(invokeUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: manualInput,
      });

      // First check if the HTTP response itself indicates failure
      if (!response.ok) {
        const errorData = await response.json();
        setStatusResult({
          status: "FAILED",
          error: errorData.output?.error || "Request failed with status: " + response.status,
          ...errorData
        });
        setLoading(false);
        return;
      }

      const result = await response.json();

      // Check for errors in the result or output
      if (result.status === "FAILED" || result.error || result.output?.error) {
        setStatusResult({
          status: "FAILED",
          error: result.error || result.output?.error || "Execution failed",
          ...result,
        });
      } else {
        setStatusResult({
          status: result.status || "SUCCEEDED",
          ...result,
        });
      }
    } catch (err) {
  setStatusResult({ 
    status: "FAILED", 
    error: err instanceof Error ? err.message : "Manual execution failed." 
  });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-md shadow-md border space-y-4">
      <h2 className="text-lg font-semibold">🛠️ Manual Execution</h2>

      <div>
        <label className="text-sm font-medium text-gray-700">Invoke URL:</label>
        <input
          type="text"
          value={invokeUrl}
          onChange={(e) => setInvokeUrl(e.target.value)} 
          className="w-full mt-1 p-2 text-sm border border-gray-300 rounded bg-gray-100 text-gray-500"
        />
      </div>

      <div>
        <label className="text-sm font-medium text-gray-700">Input JSON:</label>
        <textarea
          rows={5}
          value={manualInput}
          onChange={(e) => setManualInput(e.target.value)}
          className="w-full mt-1 p-3 text-sm border border-gray-300 rounded font-mono"
        />
      </div>

      <button
        onClick={handleManualExecution}
        disabled={loading}
        className={`w-full py-2 px-4 font-semibold rounded text-white ${
          loading ? "bg-gray-400 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700"
        }`}
      >
        {loading ? "⏳ Executing..." : "⚙️ Execute Manually"}
      </button>
    </div>
  );
}