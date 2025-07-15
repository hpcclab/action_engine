import { FaRocket, FaHistory, FaCogs, FaInfoCircle } from "react-icons/fa";
import WorkflowHistory from "./WorkflowHistory";
import SidebarRecentWorkflows from "./SidebarRecentWorkflows";
import React, { useState } from "react";
import { Link, NavLink } from "react-router-dom";

export default function Sidebar() {
  const [activeTab, setActiveTab] = useState<'settings' | 'about'>();

  return (
    <aside className="w-64 min-h-screen bg-gray-900 text-white flex flex-col justify-between py-6 px-1">
      <div>
        <div className="text-2xl font-bold mb-10 flex items-center gap-2">
          <FaRocket className="text-green-400" />
          <span>Action Engine</span>
        </div>
        <nav className="space-y-4 mb-6">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-2 text-sm w-full text-left ${isActive ? 'text-green-400 font-bold' : 'hover:text-green-400'}`
            }
          >
            <FaRocket /> Dashboard
          </NavLink>
          <NavLink
            to="/history"
            className={({ isActive }) =>
              `flex items-center gap-2 text-sm w-full text-left ${isActive ? 'text-green-400 font-bold' : 'hover:text-green-400'}`
            }
          >
            <FaHistory /> History
          </NavLink>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-2 text-sm w-full text-left ${activeTab === 'settings' ? 'text-green-400 font-bold' : 'hover:text-green-400'}`}
          >
            <FaCogs /> Settings
          </button>
          <button
            onClick={() => setActiveTab('about')}
            className={`flex items-center gap-2 text-sm w-full text-left ${activeTab === 'about' ? 'text-green-400 font-bold' : 'hover:text-green-400'}`}
          >
            <FaInfoCircle /> About Action Engine
          </button>
        </nav>
        <div className="mt-4">
          {/* Only show recent workflows in the sidebar dashboard area */}
          <SidebarRecentWorkflows />
        </div>
      </div>
      <div className="mt-auto">
        <img
          src="/images/hpcc_logo.png"
          alt="HPCC Lab"
          className="w-full object-contain"
        />
      </div>
    </aside>
  );
}
