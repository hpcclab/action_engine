import React from 'react';

interface WorkflowExportProps {
  workflowName: string;
}

const WorkflowExport: React.FC<WorkflowExportProps> = ({ workflowName }) => {
  const handleExport = async () => {
    try {
      const response = await fetch(`http://localhost:8000/workflows/${workflowName}/export`);
      if (!response.ok) {
        throw new Error('Failed to export workflow');
      }
      
      const data = await response.json();
      
      // Create and download JSON file
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${workflowName}_export_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export workflow');
    }
  };

  return (
    <button
      onClick={handleExport}
      className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <span>Export Workflow</span>
    </button>
  );
};

export default WorkflowExport; 