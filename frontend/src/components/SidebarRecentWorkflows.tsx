import React, { useEffect, useState } from "react";
import { FaRedo } from "react-icons/fa";

interface WorkflowRecord {
  workflow_name: string;
  user_query: string;
  timestamp: string;
}

export default function SidebarRecentWorkflows() {
  const [recent, setRecent] = useState<WorkflowRecord[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/workflows")
      .then((res) => res.json())
      .then((data) => setRecent(data.slice(-5).reverse()))
      .catch(() => {});
  }, []);

  const handleReinvoke = async (workflowName: string) => {
    await fetch(`http://localhost:8000/invoke-workflow/${workflowName}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    // Optionally show a toast/notification
  };

  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-400 mb-2">Recent Workflows</h3>
      <div className="flex flex-col gap-2 max-h-64 overflow-y-auto">
        {recent.length === 0 ? (
          <span className="text-xs text-gray-500">No recent workflows</span>
        ) : (
          recent.map((wf) => (
            <div key={wf.workflow_name} className="flex items-center justify-between bg-gray-800 rounded px-2 py-1">
              <span className="truncate text-xs" title={wf.user_query}>
                {wf.user_query.length > 30 ? wf.user_query.slice(0, 30) + "…" : wf.user_query}
              </span>
              <button
                className="ml-2 text-green-400 hover:text-green-200"
                title="Re-run"
                onClick={() => handleReinvoke(wf.workflow_name)}
              >
                <FaRedo size={12} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
} 