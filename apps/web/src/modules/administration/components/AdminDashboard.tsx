"use client";

/**
 * PHASE 7 - EPIC 5: Admin Dashboard Component
 * Dashboard principal del panel administrativo
 */

import React, { useEffect } from "react";
import { useAdminStore } from "../../stores/admin.store";
import {
  Users,
  Shield,
  Settings,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
}

function MetricCard({ title, value, subtitle, icon, trend, trendValue }: MetricCardProps) {
  const trendColors = {
    up: "text-green-600",
    down: "text-red-600",
    neutral: "text-gray-500",
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
          {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
          {trend && trendValue && (
            <p className={`mt-2 text-sm ${trendColors[trend]}`}>
              {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {trendValue}
            </p>
          )}
        </div>
        <div className="p-3 bg-gray-50 rounded-lg">{icon}</div>
      </div>
    </div>
  );
}

export function AdminDashboard() {
  const { overview, loadingOverview, fetchOverview, error } = useAdminStore();

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  if (loadingOverview) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-700">
          <AlertTriangle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const data = overview || {
    total_users: 0,
    active_users: 0,
    total_roles: 0,
    total_settings: 0,
    total_admin_operations: 0,
    recent_operations: [],
  };

  const activeRate = data.total_users > 0
    ? Math.round((data.active_users / data.total_users) * 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          System overview and administration tools
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Users"
          value={data.total_users}
          subtitle={`${data.active_users} active`}
          icon={<Users className="w-6 h-6 text-blue-600" />}
          trend="up"
          trendValue={`${activeRate}% active`}
        />
        <MetricCard
          title="Roles"
          value={data.total_roles}
          subtitle="System and tenant roles"
          icon={<Shield className="w-6 h-6 text-purple-600" />}
        />
        <MetricCard
          title="Settings"
          value={data.total_settings}
          subtitle="Configurable parameters"
          icon={<Settings className="w-6 h-6 text-orange-600" />}
        />
        <MetricCard
          title="Admin Operations"
          value={data.total_admin_operations}
          subtitle="All time operations"
          icon={<Activity className="w-6 h-6 text-green-600" />}
        />
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h3 className="text-sm font-medium text-gray-500 mb-4">User Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-700">Active</span>
              </div>
              <span className="text-sm font-medium">{data.active_users}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-red-500" />
                <span className="text-sm text-gray-700">Inactive</span>
              </div>
              <span className="text-sm font-medium">
                {data.total_users - data.active_users}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h3 className="text-sm font-medium text-gray-500 mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Database</span>
              <span className="flex items-center gap-1 text-sm text-green-600">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                Healthy
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Cache</span>
              <span className="flex items-center gap-1 text-sm text-green-600">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                Healthy
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">AI Services</span>
              <span className="flex items-center gap-1 text-sm text-green-600">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                Healthy
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h3 className="text-sm font-medium text-gray-500 mb-4">Recent Activity</h3>
          <div className="space-y-2">
            {data.recent_operations.slice(0, 4).map((op) => (
              <div key={op.operation_id} className="flex items-center justify-between text-sm">
                <span className="text-gray-700 truncate max-w-[180px]">
                  {op.operation_type.replace("_", " ")}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  op.status === "success"
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }`}>
                  {op.status}
                </span>
              </div>
            ))}
            {data.recent_operations.length === 0 && (
              <p className="text-sm text-gray-400">No recent operations</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h3 className="text-sm font-medium text-gray-500 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700 transition">
            + Create User
          </button>
          <button className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700 transition">
            + Create Role
          </button>
          <button className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700 transition">
            View Audit Logs
          </button>
          <button className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700 transition">
            Export Data
          </button>
        </div>
      </div>
    </div>
  );
}
