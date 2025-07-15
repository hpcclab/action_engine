import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';

interface WorkflowJsonEditorProps {
  workflowName: string;
  onSave?: (success: boolean, message: string) => void;
}



export default function WorkflowJsonEditor({ workflowName, onSave }: WorkflowJsonEditorProps) {
  const [jsonContent, setJsonContent] = useState<string>('');
  const [originalContent, setOriginalContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setSaving] = useState(false);
  const [validationError, setValidationError] = useState<string>('');
  const [hasChanges, setHasChanges] = useState(false);
  const [activeTab, setActiveTab] = useState<'full' | 'states' | 'metadata'>('full');
  const [editorHeight, setEditorHeight] = useState<number>(600); // Default height in pixels

  // Load workflow JSON on component mount
  useEffect(() => {
    loadWorkflowJson();
  }, [workflowName]);

  // Check for changes
  useEffect(() => {
    setHasChanges(jsonContent !== originalContent && jsonContent !== '');
  }, [jsonContent, originalContent]);

  const loadWorkflowJson = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`http://localhost:8000/workflows/${workflowName}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load workflow: ${response.status}`);
      }
      
      const data = await response.json();
      const formattedJson = JSON.stringify(data.definition, null, 2);
      
      setJsonContent(formattedJson);
      setOriginalContent(formattedJson);
      setValidationError('');
    } catch (error) {
      console.error('Error loading workflow JSON:', error);
      setValidationError(error instanceof Error ? error.message : 'Failed to load workflow');
    } finally {
      setIsLoading(false);
    }
  };

  const validateJson = (content: string): { isValid: boolean; error?: string; parsed?: any } => {
    try {
      if (!content.trim()) {
        return { isValid: false, error: 'JSON content cannot be empty' };
      }

      const parsed = JSON.parse(content);
      
      // Validate Step Functions structure
      if (!parsed.StartAt) {
        return { isValid: false, error: 'Missing required field: StartAt' };
      }
      
      if (!parsed.States || typeof parsed.States !== 'object') {
        return { isValid: false, error: 'Missing or invalid States object' };
      }
      
      if (!parsed.States[parsed.StartAt]) {
        return { isValid: false, error: `StartAt references non-existent state: ${parsed.StartAt}` };
      }
      
      // Validate state references
      for (const [stateName, state] of Object.entries(parsed.States)) {
        const stateObj = state as any;
        if (stateObj.Next && !parsed.States[stateObj.Next]) {
          return { isValid: false, error: `State "${stateName}" references non-existent Next state: ${stateObj.Next}` };
        }
      }
      
      return { isValid: true, parsed };
    } catch (error) {
      return { 
        isValid: false, 
        error: error instanceof Error ? error.message : 'Invalid JSON syntax' 
      };
    }
  };

  const handleValidate = () => {
    const validation = validateJson(jsonContent);
    if (validation.isValid) {
      setValidationError('');
      onSave?.(true, 'JSON is valid!');
    } else {
      setValidationError(validation.error || 'Validation failed');
    }
  };

  const handleSave = async () => {
    const validation = validateJson(jsonContent);
    
    if (!validation.isValid) {
      setValidationError(validation.error || 'Invalid JSON');
      return;
    }
    
    try {
      setSaving(true);
      setValidationError('');
      
      const response = await fetch(`http://localhost:8000/workflows/${workflowName}/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          definition: validation.parsed
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
      
      const result = await response.json();
      setOriginalContent(jsonContent); // Mark as saved
      onSave?.(true, result.message || 'Workflow updated successfully!');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save workflow';
      setValidationError(errorMessage);
      onSave?.(false, errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all changes?')) {
      setJsonContent(originalContent);
      setValidationError('');
    }
  };

  const getTabContent = () => {
    if (!jsonContent) return '';
    
    try {
      const parsed = JSON.parse(jsonContent);
      
      switch (activeTab) {
        case 'states':
          return JSON.stringify(parsed.States || {}, null, 2);
        case 'metadata':
          const { States, ...metadata } = parsed;
          return JSON.stringify(metadata, null, 2);
        default:
          return jsonContent;
      }
    } catch {
      return jsonContent;
    }
  };

  const updateFromTab = (content: string) => {
    if (activeTab === 'full') {
      setJsonContent(content);
      return;
    }
    
    try {
      const currentParsed = JSON.parse(jsonContent);
      const newContent = JSON.parse(content);
      
      if (activeTab === 'states') {
        currentParsed.States = newContent;
      } else if (activeTab === 'metadata') {
        // Update metadata while preserving States
        const { States } = currentParsed;
        Object.assign(currentParsed, newContent, { States });
      }
      
      setJsonContent(JSON.stringify(currentParsed, null, 2));
    } catch (error) {
      // If parsing fails, just update the raw content
      setJsonContent(content);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading workflow JSON...</div>
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Workflow JSON Editor</h3>
        <div className="flex space-x-2 items-center">
          {/* Size Controls */}
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <span>Size:</span>
            <button
              onClick={() => setEditorHeight(400)}
              className={`px-2 py-1 rounded ${editorHeight === 400 ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}
            >
              Small
            </button>
            <button
              onClick={() => setEditorHeight(600)}
              className={`px-2 py-1 rounded ${editorHeight === 600 ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}
            >
              Medium
            </button>
            <button
              onClick={() => setEditorHeight(800)}
              className={`px-2 py-1 rounded ${editorHeight === 800 ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}
            >
              Large
            </button>
            <button
              onClick={() => setEditorHeight(Math.max(600, window.innerHeight - 200))}
              className={`px-2 py-1 rounded ${editorHeight > 800 ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}
            >
              Full
            </button>
          </div>
          
          <div className="border-l border-gray-300 h-6"></div>
          
          <button
            onClick={handleValidate}
            className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
          >
            Validate
          </button>
          <button
            onClick={handleReset}
            disabled={!hasChanges}
            className="px-3 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Reset
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
            className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? 'Saving...' : 'Save & Regenerate'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-4">
        {[
          { key: 'full', label: 'Full JSON' },
          { key: 'states', label: 'States Only' },
          { key: 'metadata', label: 'Metadata' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === tab.key
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Status indicators */}
      <div className="flex space-x-4 mb-4 text-sm">
        {hasChanges && (
          <span className="text-orange-600 font-medium">
            ● Unsaved changes
          </span>
        )}
        {!hasChanges && jsonContent && (
          <span className="text-green-600">
            ✓ Saved
          </span>
        )}
      </div>

      {/* Error display */}
      {validationError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="text-red-800 text-sm">
            <strong>Validation Error:</strong> {validationError}
          </div>
        </div>
      )}

      {/* Editor */}
      <div className="border border-gray-300 rounded-md overflow-hidden" style={{ height: `${editorHeight}px` }}>
        <Editor
          height={`${editorHeight}px`}
          defaultLanguage="json"
          value={getTabContent()}
          onChange={(value: string | undefined) => updateFromTab(value || '')}
          options={{
            minimap: { enabled: editorHeight > 600 }, // Enable minimap for larger views
            scrollBeyondLastLine: false,
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            readOnly: false,
            cursorStyle: 'line',
            automaticLayout: true,
            wordWrap: 'on',
            formatOnPaste: true,
            formatOnType: true,
            folding: true, // Enable code folding
            renderWhitespace: 'selection',
            showFoldingControls: 'always',
          }}
          theme="vs-dark"
        />
      </div>

      {/* Footer info */}
      <div className="mt-4 text-xs text-gray-500 space-y-1">
        <p>• Use the tabs above to edit specific sections of the workflow</p>
        <p>• Click "Validate" to check for errors before saving</p>
        <p>• "Save & Regenerate" will update the workflow and create a new execution</p>
      </div>
    </div>
  );
} 