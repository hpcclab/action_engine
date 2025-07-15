import React, { createContext, useState } from "react";

interface WorkflowStep {
  id: string;
  name: string;
  displayName?: string;
}

type WorkflowContextType = {
  invokeUrl: string;
  setInvokeUrl: (val: string) => void;
  executionArn: string;
  setExecutionArn: (val: string) => void;
  statusResult: any;
  setStatusResult: (val: any) => void;
  workflowSteps: WorkflowStep[];
  setWorkflowSteps: (steps: WorkflowStep[]) => void;
  isRestructuring: boolean;
  setIsRestructuring: (val: boolean) => void;
};

export const WorkflowContext = createContext<WorkflowContextType>({
  invokeUrl: "",
  setInvokeUrl: () => {},
  executionArn: "",
  setExecutionArn: () => {},
  statusResult: null,
  setStatusResult: () => {},
  workflowSteps: [],
  setWorkflowSteps: () => {},
  isRestructuring: false,
  setIsRestructuring: () => {},
});

export const WorkflowProvider = ({ children }: { children: React.ReactNode }) => {
  const [invokeUrl, setInvokeUrl] = useState("");
  const [executionArn, setExecutionArn] = useState("");
  const [statusResult, setStatusResult] = useState(null);
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([]);
  const [isRestructuring, setIsRestructuring] = useState(false);

  return (
    <WorkflowContext.Provider
      value={{
        invokeUrl,
        setInvokeUrl,
        executionArn,
        setExecutionArn,
        statusResult,
        setStatusResult,
        workflowSteps,
        setWorkflowSteps,
        isRestructuring,
        setIsRestructuring,
      }}
    >
      {children}
    </WorkflowContext.Provider>
  );
};
