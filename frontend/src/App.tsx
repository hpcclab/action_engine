import Sidebar from "./components/Sidebar";
import QueryForm from "./components/QueryForm";
import ExecutionResult from "./components/ExecutionResult";
import WorkflowHistory from "./components/WorkflowHistory";
import RecentQueries from "./components/RecentQueries";
import WorkflowInput from "./components/WorkflowInput";
import { WorkflowProvider } from "./components/WorkflowContext";
import { BrowserRouter, Routes, Route } from "react-router-dom";

function DashboardPage() {
  return (
    <main className="flex-1 px-8 py-10 space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">
        Action Engine Dashboard
      </h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <QueryForm />
          <WorkflowInput />
        </div>
        <ExecutionResult />
      </div>
      <div className="space-y-6">
        <RecentQueries />
      </div>
    </main>
  );
}

export default function App() {
  return (
    <WorkflowProvider>
      <BrowserRouter>
        <div className="flex min-h-screen bg-gray-50">
          <Sidebar />
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/history" element={<WorkflowHistory />} />
          </Routes>
        </div>
      </BrowserRouter>
    </WorkflowProvider>
  );
}
