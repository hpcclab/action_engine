import React, { useContext, useEffect } from "react";
import { WorkflowContext } from "./WorkflowContext";
import WorkflowSteps from "./WorkflowSteps";
import WorkflowExport from "./WorkflowExport";
import OutputDisplay from "./OutputDisplay";
import WorkflowJsonEditor from "./WorkflowJsonEditor";

interface WorkflowStep {
  id: string;
  name: string;
  displayName?: string;
}

interface WorkflowDefinitionStep {
  id: string;
  name?: string;
  Resource?: string;
}

// Helper function to check if a URL points to a media type
const isImageUrl = (url: any): url is string => typeof url === 'string' && /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url);
const isVideoUrl = (url: any): url is string => typeof url === 'string' && /\.(mp4|webm|mov)$/i.test(url);
const isAudioUrl = (url: any): url is string => typeof url === 'string' && /\.(mp3|wav|ogg)$/i.test(url);

export default function ExecutionResult() {
  const {
    executionArn,
    statusResult,
    invokeUrl,
    workflowSteps,
    setWorkflowSteps,
    isRestructuring,
    setIsRestructuring,
    setExecutionArn,
    setInvokeUrl,
    setStatusResult
  } = useContext(WorkflowContext);

  const [reorderStatus, setReorderStatus] = React.useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  
  const [originalStepOrder, setOriginalStepOrder] = React.useState<string[]>([]);
  const [batchMode, setBatchMode] = React.useState(true);
  const [pendingOrder, setPendingOrder] = React.useState<string[] | null>(null);
  const [dependencyErrors, setDependencyErrors] = React.useState<string[]>([]);
  const [activeTab, setActiveTab] = React.useState<'visual' | 'json'>('json');
  const [jsonEditorMessage, setJsonEditorMessage] = React.useState<{type: 'success' | 'error', message: string} | null>(null);

  const status = statusResult?.status;
  const start = statusResult?.startDate;
  const stop = statusResult?.stopDate;
  const outputMessage = statusResult?.output?.message;

  useEffect(() => {
    // Extract workflow steps from the execution ARN
    if (executionArn) {
      console.log("Execution ARN available:", executionArn);
      // Get the workflow name from the ARN
      const workflowName = extractWorkflowName(executionArn);
      console.log("Extracted workflow name:", workflowName);
      if (workflowName) {
        // Fetch the workflow definition from the backend
        console.log("Fetching workflow definition...");
        fetch(`http://localhost:8000/workflows/${workflowName}`)
          .then(res => {
            console.log("Response status:", res.status);
            return res.json();
          })
          .then(data => {
            console.log("Workflow definition data:", data);
            if (data.steps && Array.isArray(data.steps)) {
              // Map the step IDs to more readable names
              const mappedSteps = data.steps.map((step: WorkflowDefinitionStep): WorkflowStep => {
                const functionName = step.Resource?.split(":").pop() || "";
                // Convert function name to display name (e.g., getusermood -> Get User Mood)
                const displayName = functionName
                  ? functionName
                      .replace(/([A-Z])/g, " $1") // Add space before capitals
                      .replace(/^./, str => str.toUpperCase()) // Capitalize first letter
                      .trim()
                  : step.name || step.id;
                
                return {
                  id: step.id,
                  name: step.name || step.id,
                  displayName
                };
              });
              console.log("Mapped steps:", mappedSteps);
              setWorkflowSteps(mappedSteps);
              // Save the original order
              setOriginalStepOrder(mappedSteps.map((step: WorkflowStep) => step.id));
            } else {
              console.error("Invalid steps data received:", data);
            }
          })
          .catch(error => console.error("Error fetching workflow definition:", error));
      }
    }
  }, [executionArn, setWorkflowSteps]);

  // Add console log for workflowSteps changes
  useEffect(() => {
    console.log("Current workflow steps:", workflowSteps);
  }, [workflowSteps]);

  // Add console log for isRestructuring changes
  useEffect(() => {
    console.log("isRestructuring:", isRestructuring);
  }, [isRestructuring]);

  // Add console log for pendingOrder changes
  useEffect(() => {
    console.log("pendingOrder changed to:", pendingOrder);
  }, [pendingOrder]);

  const extractWorkflowName = (arn: string) => {
    console.log("Extracting workflow name from ARN:", arn);
    
    // Example ARN: arn:aws:states:us-east-2:559198857332:execution:workflow__It_will_be_perfect_if_you_play_music_th:cf93ef37-f239-40c8-8853-d11282fd5b62
    // We need to extract: workflow__It_will_be_perfect_if_you_play_music_th
    
    const parts = arn.split(":");
    if (parts.length >= 7 && parts[5] === "execution") {
      // This is an execution ARN, extract the state machine name
      const stateMachineName = parts[6];
      console.log("Extracted state machine name:", stateMachineName);
      return stateMachineName;
    } else if (parts.length >= 6 && parts[5] === "stateMachine") {
      // This is a state machine ARN
      const stateMachineName = parts[6];
      console.log("Extracted state machine name:", stateMachineName);
      return stateMachineName;
    }
    
    // Fallback: try to extract from the end
    const lastPart = arn.split(":").pop()?.split("/").pop();
    console.log("Fallback extraction:", lastPart);
    return lastPart;
  };

  // Simple frontend dependency checker
  const checkDependencies = (newOrder: string[]): string[] => {
    const errors: string[] = [];
    
    // Based on common workflow patterns, check basic dependencies
    // This is a simplified check - the backend will do the full validation
    const stepPositions = new Map<string, number>();
    newOrder.forEach((stepId, index) => {
      stepPositions.set(stepId, index);
    });
    
    // Find steps by their function names
    const stepsByFunction = new Map<string, WorkflowStep>();
    workflowSteps.forEach(step => {
      const funcName = step.displayName?.toLowerCase().replace(/\s+/g, '') || '';
      stepsByFunction.set(funcName, step);
    });
    
    // Check common dependency patterns
    const playMusic = stepsByFunction.get('playmusic');
    const recommendSong = stepsByFunction.get('recommendsong');
    const getUserMood = stepsByFunction.get('getusermood');
    const username2id = stepsByFunction.get('username2id');
    
    if (playMusic && recommendSong) {
      const playPos = stepPositions.get(playMusic.id) ?? -1;
      const recPos = stepPositions.get(recommendSong.id) ?? -1;
      if (playPos < recPos) {
        errors.push("'Play Music' needs a song recommendation from 'Recommend Song'");
      }
    }
    
    if (recommendSong && getUserMood) {
      const recPos = stepPositions.get(recommendSong.id) ?? -1;
      const moodPos = stepPositions.get(getUserMood.id) ?? -1;
      if (recPos < moodPos) {
        errors.push("'Recommend Song' needs the user's mood from 'Get User Mood'");
      }
    }
    
    if (getUserMood && username2id) {
      const moodPos = stepPositions.get(getUserMood.id) ?? -1;
      const idPos = stepPositions.get(username2id.id) ?? -1;
      if (moodPos < idPos) {
        errors.push("'Get User Mood' needs the user ID from 'Username to ID'");
      }
    }
    
    return errors;
  };

  const handleReorder = async (newOrder: string[]) => {
    console.log("handleReorder called with:", newOrder);
    console.log("batchMode:", batchMode);
    
    // Check dependencies immediately
    const depErrors = checkDependencies(newOrder);
    setDependencyErrors(depErrors);
    
    if (batchMode) {
      // In batch mode, just save the order without calling the API
      console.log("Setting pendingOrder to:", newOrder);
      setPendingOrder(newOrder);
      
      if (depErrors.length > 0) {
        setReorderStatus({
          type: 'error',
          message: 'Warning: This order violates dependencies!'
        });
      } else {
        setReorderStatus({
          type: 'success',
          message: 'Changes pending - click "Save Changes" to apply'
        });
      }
      
      setTimeout(() => {
        setReorderStatus({ type: null, message: '' });
      }, 3000);
      return;
    }
    
    try {
      console.log("Reordering workflow with new order:", newOrder);
      const workflowName = extractWorkflowName(executionArn);
      if (!workflowName) {
        throw new Error("Could not extract workflow name from ARN");
      }

      const response = await fetch("http://localhost:8000/restructure-workflow", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          workflow_name: workflowName,
          new_order: newOrder,  // This should already be the state IDs (t1, t2, etc.)
          create_new: false  // Update existing restructured workflow instead of creating new
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Restructure error:", errorText);
        throw new Error(`Failed to restructure workflow: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log("Restructure result:", result);
      
      // Show success feedback
      setReorderStatus({
        type: 'success',
        message: 'Workflow order updated successfully!'
      });
      
      // Clear the message after 3 seconds
      setTimeout(() => {
        setReorderStatus({ type: null, message: '' });
      }, 3000);
      
      // Don't close the restructuring mode - let the user continue reordering
      // The mode will be closed when they click "Generate New Workflow" or "Cancel Restructuring"
    } catch (error) {
      console.error("Error restructuring workflow:", error);
      setReorderStatus({
        type: 'error',
        message: error instanceof Error ? error.message : "Unknown error"
      });
      
      // Clear error after 5 seconds
      setTimeout(() => {
        setReorderStatus({ type: null, message: '' });
      }, 5000);
    }
  };

  const handleSaveBatch = async () => {
    if (pendingOrder) {
      // Don't turn off batch mode - keep it always enabled
      // Just temporarily set it to false for this one call
      const originalBatchMode = batchMode;
      setBatchMode(false);
      await handleReorder(pendingOrder); // Apply the pending order
      setBatchMode(originalBatchMode); // Restore batch mode
      setPendingOrder(null); // Clear pending order
    }
  };

  const handleResetOrder = async () => {
    if (originalStepOrder.length > 0) {
      await handleReorder(originalStepOrder);
      setReorderStatus({
        type: 'success',
        message: 'Reset to original order'
      });
      setTimeout(() => {
        setReorderStatus({ type: null, message: '' });
      }, 3000);
    }
  };

  const handleGenerateAfterRestructure = async () => {
    try {
      const workflowName = extractWorkflowName(executionArn);
      if (!workflowName) {
        throw new Error("Could not extract workflow name from ARN");
      }

      // First restructure the workflow
      const restructureResponse = await fetch("http://localhost:8000/restructure-workflow", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          workflow_name: workflowName,
          new_order: workflowSteps.map(step => step.id),
          create_new: false  // Update existing restructured workflow instead of creating new
        }),
      });

      const restructureResult = await restructureResponse.json();
      
      if (!restructureResult.execution_arn) {
        throw new Error("Failed to get execution ARN from restructured workflow");
      }

      // Update the UI state
      setIsRestructuring(false);
      setExecutionArn(restructureResult.execution_arn);
      setInvokeUrl(restructureResult.invoke_api_endpoint);

      // Poll for execution status
      let statusJson = { status: "RUNNING" };
      for (let i = 0; i < 10; i++) {
        const statusRes = await fetch(
          `http://localhost:8000/execution-status?executionArn=${encodeURIComponent(restructureResult.execution_arn)}`
        );
        statusJson = await statusRes.json();
        if (statusJson.status !== "RUNNING") break;
        await new Promise(r => setTimeout(r, 3000));
      }

      // Update status result
      setStatusResult(statusJson);

      if (statusJson.status === "SUCCEEDED") {
        alert("Workflow executed successfully!");
      } else if (statusJson.status === "FAILED") {
        alert("Workflow execution failed. Please check the execution details.");
      }
    } catch (error) {
      console.error("Error generating workflow:", error);
      alert("Failed to generate workflow: " + (error instanceof Error ? error.message : "Unknown error"));
    }
  };

  const handleJsonEditorSave = (success: boolean, message: string) => {
    setJsonEditorMessage({ type: success ? 'success' : 'error', message });
    
    // Clear message after 5 seconds
    setTimeout(() => {
      setJsonEditorMessage(null);
    }, 5000);
    
    // If successful, you might want to refresh the workflow data
    if (success) {
      // Optionally reload workflow steps or trigger a refresh
      console.log('JSON editor save successful:', message);
    }
  };

  /**
   * Renders a visual preview for media types if available.
   * Returns null if no specific media type is found.
   */
  const renderMediaPreview = (output: any) => {
    if (typeof output !== 'object' || output === null) return null;

    // Case 1: Image URL
    const imageUrl = output.public_url || output.image_url || output.imageUrl;
    if (isImageUrl(imageUrl)) {
      return (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Processed Image Preview</h4>
          <a href={imageUrl} target="_blank" rel="noopener noreferrer">
            <img 
              src={imageUrl} 
              alt="Workflow Processed Image" 
              className="max-w-full h-auto rounded border border-gray-200 shadow-sm" 
            />
          </a>
        </div>
      );
    }
    
    // Add other media checks here (video, audio) in the same pattern if needed

    return null; // No specific media found to preview
  };

  return (
    <div className="bg-white p-6 rounded-md shadow-md border h-fit space-y-4">
      <h2 className="text-xl font-semibold mb-2">Execution Result</h2>

      {/* Debug info */}
      <div className="text-xs text-gray-500">
        <p>Steps loaded: {workflowSteps.length}</p>
        <p>Restructuring mode: {isRestructuring ? "Yes" : "No"}</p>
      </div>

      {/* Workflow Steps Visualization */}
      {workflowSteps.length > 0 && (
        <div className="border-b pb-4">
          {/* Tab Navigation */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex space-x-1">
              <button
                onClick={() => setActiveTab('json')}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'json'
                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                📝 JSON Editor
              </button>
              <button
                onClick={() => setActiveTab('visual')}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'visual'
                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                📊 Visual Editor
              </button>
            </div>
            
            {activeTab === 'visual' && (
              <div className="space-x-2">
                {isRestructuring && (
                  <>
                    <button
                      onClick={handleResetOrder}
                      className="px-3 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors text-sm"
                    >
                      ↺ Reset Order
                    </button>
                  </>
                )}
                <button
                  onClick={() => {
                    if (isRestructuring) {
                      // Exiting restructuring mode
                      if (pendingOrder) {
                        if (window.confirm('You have unsaved changes. Are you sure you want to cancel?')) {
                          setIsRestructuring(false);
                          setPendingOrder(null);
                        }
                      } else {
                        setIsRestructuring(false);
                      }
                    } else {
                      // Entering restructuring mode
                      setIsRestructuring(true);
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                >
                  {isRestructuring ? "Cancel Restructuring" : "✨ Restructure Workflow"}
                </button>
              </div>
            )}
          </div>
          
          {/* JSON Editor Message */}
          {jsonEditorMessage && (
            <div className={`mb-4 p-3 rounded-md ${
              jsonEditorMessage.type === 'success' 
                ? 'bg-green-50 border border-green-200 text-green-800' 
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              {jsonEditorMessage.type === 'success' ? '✅' : '❌'} {jsonEditorMessage.message}
            </div>
          )}
          
          {/* Tab Content */}
          {activeTab === 'visual' ? (
            isRestructuring ? (
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                {/* Save Changes button */}
                {pendingOrder && (
                  <div className="mb-4 flex justify-end">
                    <button
                      onClick={handleSaveBatch}
                      disabled={dependencyErrors.length > 0}
                      className={`px-4 py-2 rounded text-sm font-semibold ${
                        dependencyErrors.length > 0
                          ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                          : 'bg-green-600 text-white hover:bg-green-700 animate-pulse'
                      }`}
                    >
                      💾 Save Changes ({pendingOrder.length} steps)
                    </button>
                  </div>
                )}
                
                {/* Unsaved changes warning */}
                {pendingOrder && (
                  <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <p className="text-sm text-yellow-800">
                      ⚠️ You have unsaved changes. Click "Save Changes" to apply them.
                    </p>
                  </div>
                )}
                
                {/* Dependency errors */}
                {dependencyErrors.length > 0 && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
                    <p className="text-sm font-semibold text-red-800 mb-2">
                      ❌ Dependency Violations Detected:
                    </p>
                    <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                      {dependencyErrors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                    <p className="text-xs text-red-600 mt-2 italic">
                      Fix these issues before saving, or the workflow will fail.
                    </p>
                  </div>
                )}
                
                {/* Status feedback */}
                {reorderStatus.type && (
                  <div className={`mb-4 p-3 rounded ${
                    reorderStatus.type === 'success' 
                      ? 'bg-green-100 text-green-800 border border-green-200' 
                      : 'bg-red-100 text-red-800 border border-red-200'
                  }`}>
                    {reorderStatus.type === 'success' ? '✅' : '❌'} {reorderStatus.message}
                  </div>
                )}
                
                <WorkflowSteps 
                  steps={workflowSteps} 
                  onReorder={handleReorder}
                  onGenerate={handleGenerateAfterRestructure}
                />
              </div>
            ) : (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Current Workflow Structure</h3>
                <div className="flex items-center space-x-2 flex-wrap">
                  {workflowSteps.map((step, index) => (
                    <React.Fragment key={step.id}>
                      <span className="px-3 py-1 bg-gray-100 rounded text-sm">
                        {step.displayName || step.name}
                      </span>
                      {index < workflowSteps.length - 1 && (
                        <span className="text-gray-400">→</span>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )
          ) : (
            /* JSON Editor Tab */
            <div className="w-full">
              {executionArn && (
                <WorkflowJsonEditor 
                  workflowName={extractWorkflowName(executionArn) || ''}
                  onSave={handleJsonEditorSave}
                />
              )}
            </div>
          )}
        </div>
      )}

      {/* API Endpoint Display - Simplified */}
      {invokeUrl && (
        <div className="border-t pt-4 mb-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-blue-800 mb-3">🚀 Generated API Endpoint</h3>
            
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={invokeUrl}
                readOnly
                className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded text-sm font-mono"
              />
              <button
                onClick={() => navigator.clipboard.writeText(invokeUrl)}
                className="px-3 py-2 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
                title="Copy API URL"
              >
                📋 Copy
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Execution Summary */}
      {status && (
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div
                className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  status === "SUCCEEDED"
                    ? "bg-green-100 text-green-800"
                    : status === "FAILED"
                    ? "bg-red-100 text-red-800"
                    : "bg-yellow-100 text-yellow-800"
                }`}
              >
                {status}
              </div>
              
              {status === "SUCCEEDED" && (
                <span className="text-green-600 font-medium">✅ Workflow executed successfully!</span>
              )}
            </div>
          </div>

          {/* Execution Details - Restored */}
          {start && stop && (
            <div className="mb-3 p-3 bg-gray-50 rounded border">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Start Time:</span>
                  <div className="text-gray-600 font-mono text-xs">
                    {new Date(start).toLocaleString()}
                  </div>
                </div>
                <div>
                  <span className="font-medium text-gray-700">End Time:</span>
                  <div className="text-gray-600 font-mono text-xs">
                    {new Date(stop).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          )}

          {outputMessage && (
            <div className="text-sm text-gray-800 bg-gray-50 p-3 rounded border border-gray-200">
              <strong>Output:</strong> {outputMessage}
            </div>
          )}
        </div>
      )}

      {/* Visual Preview Section */}
      {statusResult && statusResult.output && renderMediaPreview(statusResult.output)}

      {/* Original Output Display (Restored) */}
      {statusResult && statusResult.output && (
        <OutputDisplay 
          output={{
            success: status === "SUCCEEDED",
            message: outputMessage,
            text_output: typeof statusResult.output === "string" ? statusResult.output : JSON.stringify(statusResult.output, null, 2),
            files: statusResult.output.generated_files || statusResult.output.files || [],
            execution_time: statusResult.execution_time,
            metadata: {
              execution_arn: executionArn,
              status: status,
              start_time: start,
              end_time: stop,
              ...statusResult.output.metadata
            }
          }}
        />
      )}

      {/* Error Display - handles cases where statusResult exists but statusResult.output might not */}
      {statusResult && !statusResult.output && (
        <div className="border-t pt-4">
          <p className="text-sm font-medium text-red-700">Error:</p>
          <pre className="bg-red-50 p-4 rounded text-xs overflow-auto text-red-800 border border-red-200 max-h-32 break-all whitespace-pre-wrap">
            {statusResult.error ? (typeof statusResult.error === "string" ? statusResult.error : JSON.stringify(statusResult.error, null, 2)) : JSON.stringify(statusResult, null, 2)}
          </pre>
        </div>
      )}

      {/* Download Links and Export - Only show if execution succeeded */}
      {status === "SUCCEEDED" && (
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between">
            <div className="flex space-x-4">
              <a
                href="http://localhost:8000/output_file/argo_workflow.yaml"
                download
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
              >
                <span>📥</span>
                <span>Download YAML</span>
              </a>
              <a
                href="http://localhost:8000/output_file/step_function_workflow.json"
                download
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
              >
                <span>📄</span>
                <span>Download JSON</span>
              </a>
            </div>
            
            {executionArn && (
              <WorkflowExport 
                workflowName={extractWorkflowName(executionArn) || ''} 
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
