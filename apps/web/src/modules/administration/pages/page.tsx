/**
 * PHASE 7 - EPIC 5: Admin Panel
 * Complete administrative panel with:
 * - Admin Dashboard
 * - User Management
 * - Role Manager
 * - Settings Manager
 * - Audit Viewer
 * - Tenant Manager
 * - Monitoring Dashboard
 *
 * Dependencies: EPIC 1 (audit), EPIC 2 (multi-tenant), EPIC 3 (HA), EPIC 4 (observability)
 */

"use client";

import React, { useState } from "react";
import { useAdminStore } from "../stores/admin.store";
import {
  AdminDashboard,
  UserManagement,
  RoleManager,
  SettingsManager,
  AuditViewer,
  TenantManager,
  MonitoringDashboard,
} from "../components";
import {
  LayoutDashboard,
  Users,
  Shield,
  Settings,
  FileText,
  Building2,
  Activity,
  X,
} from "lucide-react";

type TabId = "overview" | "users" | "roles" | "settings" | "audit" | "tenants" | "monitoring";

interface Tab {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

const tabs: Tab[] = [
  { id: "overview", label: "Dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
  { id: "users", label: "Users", icon: <Users className="w-4 h-4" /> },
  { id: "roles", label: "Roles", icon: <Shield className="w-4 h-4" /> },
  { id: "settings", label: "Settings", icon: <Settings className="w-4 h-4" /> },
  { id: "audit", label: "Audit Logs", icon: <FileText className="w-4 h-4" /> },
  { id: "tenants", label: "Tenants", icon: <Building2 className="w-4 h-4" /> },
  { id: "monitoring", label: "Monitoring", icon: <Activity className="w-4 h-4" /> },
];

export default function AdministrationPage() {
  const { activeTab, setActiveTab } = useAdminStore();

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <aside className="w-56 border-r border-gray-200 bg-white flex-shrink-0">
        <div className="p-4 border-b border-gray-100">
          <h2 className="text-sm font-semibold text-gray-900">Administration</h2>
          <p className="text-xs text-gray-500 mt-0.5">EREN Platform</p>
        </div>
        <nav className="p-2 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition ${
                activeTab === tab.id
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Content */}
      <main className="flex-1 p-6 bg-gray-50 overflow-y-auto">
        {activeTab === "overview" && <AdminDashboard />}
        {activeTab === "users" && <UserManagement />}
        {activeTab === "roles" && <RoleManager />}
        {activeTab === "settings" && <SettingsManager />}
        {activeTab === "audit" && <AuditViewer />}
        {activeTab === "tenants" && <TenantManager />}
        {activeTab === "monitoring" && <MonitoringDashboard />}
      </main>
    </div>
  );
}
