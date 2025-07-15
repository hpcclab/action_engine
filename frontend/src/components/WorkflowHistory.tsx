import React, { useEffect, useState } from "react";

interface WorkflowRecord {
  workflow_name: string;
  invoke_api_endpoint: string;
  user_query: string;
  timestamp: string;
}

export default function WorkflowHistory() {
  const [history, setHistory] = useState<WorkflowRecord[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/workflows")
      .then((res) => res.json())
      .then((data) => setHistory(data.reverse()))
      .catch((err) => console.error("Failed to fetch history", err));
  }, []);

  const handleReinvoke = async (workflowName: string) => {
    const res = await fetch(`http://localhost:8000/invoke-workflow/${workflowName}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const json = await res.json();
    alert("Re-executed: " + json.executionArn);
  };

  const handleDelete = async (workflowName: string) => {
    if (!window.confirm(`Are you sure you want to delete '${workflowName}'?`)) return;
    try {
      const res = await fetch(`http://localhost:8000/workflows/${workflowName}`, {
        method: "DELETE"
      });
      const result = await res.json();
      alert(result.message);
      setHistory((prev) => prev.filter((wf) => wf.workflow_name !== workflowName));
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  return (
    <div className="bg-white p-6 rounded-md shadow-md border">
      <h2 className="text-xl font-semibold mb-4">📝 Workflow History</h2>

      {history.length === 0 ? (
        <p className="text-gray-500">No workflow history found.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2">
          {history.map((wf) => (
            <div
              key={wf.workflow_name}
              className="p-4 bg-gray-50 border rounded-lg shadow hover:shadow-md transition"
            >
              <p className="text-sm text-gray-700 mb-1">
                <strong className="text-blue-600">Query:</strong> {wf.user_query}
              </p>
              <p className="text-xs text-gray-500 mb-2">
                Created: {new Date(wf.timestamp).toLocaleString()}
              </p>
              <div className="flex gap-4">
                <button
                  onClick={() => handleReinvoke(wf.workflow_name)}
                  className="text-sm text-blue-600 hover:underline"
                >
                  🔁 Re-run
                </button>
                <button
                  onClick={() => handleDelete(wf.workflow_name)}
                  className="text-sm text-red-600 hover:underline"
                >
                  🗑 Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
