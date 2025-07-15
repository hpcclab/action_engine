import './index.css';
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { WorkflowProvider } from "./components/WorkflowContext";


const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(
  <React.StrictMode>
    <WorkflowProvider>
      <App />
    </WorkflowProvider>
  </React.StrictMode>
);
