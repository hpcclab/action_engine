import React from 'react';

interface WorkflowStep {
  id: string;
  name: string;
  displayName?: string;
}

interface WorkflowPreviewProps {
  steps: WorkflowStep[];
  title?: string;
}

const WorkflowPreview: React.FC<WorkflowPreviewProps> = ({ steps, title = "Execution Preview" }) => {
  return (
    <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
      <h4 className="text-sm font-semibold text-blue-900 mb-3">{title}</h4>
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full text-sm font-semibold">
              {index + 1}
            </div>
            <div className="ml-3 flex-1">
              <div className="text-sm font-medium text-gray-900">
                {step.displayName || step.name}
              </div>
              <div className="text-xs text-gray-500">
                Step ID: {step.id}
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className="ml-3">
                <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="mt-3 text-xs text-blue-700 italic">
        This preview shows how your workflow will execute after restructuring.
      </div>
    </div>
  );
};

export default WorkflowPreview; 