"use client";

/**
 * PHASE 7 - EPIC 5: Monitoring Dashboard UI
 * Integración: EPIC 4 (observability)
 */

import React from "react";
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Cpu,
  Database,
  HardDrive,
  Network,
  Zap,
} from "lucide-react";

interface ServiceMetric {
  name: string;
  status: "healthy" | "degraded" | "unhealthy";
  metrics: Record<string, string | number>;
}

const services: ServiceMetric[] = [
  {
    name: "API Server",
    status: "healthy",
    metrics: {
      "Requests/s": "1,234",
      "P95 Latency": "145ms",
      "Error Rate": "0.1%",
      Uptime: "99.97%",
    },
  },
  {
    name: "Database",
    status: "healthy",
    metrics: {
      "Connections": "25/100",
      "Queries/s": "450",
      "P95 Latency": "12ms",
      "Cache Hit": "94%",
    },
  },
  {
    name: "Redis Cache",
    status: "healthy",
    metrics: {
      "Memory": "512MB / 2GB",
      "Connections": "50",
      "Hit Rate": "95%",
      Ops: "10,000/s",
    },
  },
  {
    name: "AI/LLM Service",
    status: "healthy",
    metrics: {
      "Requests/min": "120",
      "Avg Latency": "800ms",
      "Error Rate": "0.5%",
      "Queue Depth": "12",
    },
  },
  {
    name: "Vector DB (Qdrant)",
    status: "healthy",
    metrics: {
      Collections: "10",
      Vectors: "1.2M",
      "P95 Latency": "25ms",
      "Disk Usage": "45GB",
    },
  },
];

const alerts = [
  { severity: "high", message: "CPU usage above 85% on api-server-2", time: "5 min ago" },
  { severity: "medium", message: "Slow query detected (>2s) on maintenance_table", time: "12 min ago" },
  { severity: "low", message: "Cache hit rate dropped below 90%", time: "30 min ago" },
];

export function MonitoringDashboard() {
  const statusIcon = (status: ServiceMetric["status"]) => {
    if (status === "healthy") return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === "degraded") return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    return <AlertCircle className="w-5 h-5 text-red-500" />;
  };

  const severityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      high: "bg-red-100 text-red-700",
      medium: "bg-yellow-100 text-yellow-700",
      low: "bg-blue-100 text-blue-700",
    };
    return (
      <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${colors[severity]}`}>
        {severity}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Monitoring Dashboard</h2>
        <p className="text-sm text-gray-500">System health and alerts</p>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: <Cpu className="w-5 h-5" />, label: "CPU Usage", value: "45%", color: "text-blue-600" },
          { icon: <HardDrive className="w-5 h-5" />, label: "Memory", value: "62%", color: "text-purple-600" },
          { icon: <Network className="w-5 h-5" />, label: "Network I/O", value: "120MB/s", color: "text-green-600" },
          { icon: <Database className="w-5 h-5" />, label: "Storage", value: "55%", color: "text-orange-600" },
        ].map((m) => (
          <div key={m.label} className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
            <div className={`flex items-center gap-2 ${m.color}`}>
              {m.icon}
              <span className="text-sm font-medium">{m.label}</span>
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900">{m.value}</p>
          </div>
        ))}
      </div>

      {/* Services */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Service Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((svc) => (
            <div
              key={svc.name}
              className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {statusIcon(svc.status)}
                  <span className="text-sm font-medium text-gray-900">{svc.name}</span>
                </div>
                <span className="text-xs text-gray-400 capitalize">{svc.status}</span>
              </div>
              <div className="space-y-1.5">
                {Object.entries(svc.metrics).map(([k, v]) => (
                  <div key={k} className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">{k}</span>
                    <span className="text-xs font-medium text-gray-700">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Alerts Panel */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Recent Alerts</h3>
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-100">
          {alerts.map((alert, i) => (
            <div key={i} className="flex items-start gap-3 p-4">
              <AlertCircle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                alert.severity === "high" ? "text-red-500" :
                alert.severity === "medium" ? "text-yellow-500" : "text-blue-500"
              }`} />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  {severityBadge(alert.severity)}
                  <span className="text-sm text-gray-700">{alert.message}</span>
                </div>
                <span className="text-xs text-gray-400">{alert.time}</span>
              </div>
            </div>
          ))}
          {alerts.length === 0 && (
            <div className="p-4 text-center text-sm text-gray-400">
              No active alerts
            </div>
          )}
        </div>
      </div>

      {/* SLO Status */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-3">SLO Status</h3>
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {[
            { name: "API Availability", target: "99.9%", current: "99.97%", status: "healthy" },
            { name: "API Latency P95", target: "<500ms", current: "145ms", status: "healthy" },
            { name: "Error Rate", target: "<0.1%", current: "0.1%", status: "healthy" },
            { name: "Database Availability", target: "99.9%", current: "99.99%", status: "healthy" },
          ].map((slo) => (
            <div key={slo.name} className="flex items-center justify-between px-4 py-3 border-b border-gray-100 last:border-0">
              <div>
                <p className="text-sm font-medium text-gray-900">{slo.name}</p>
                <p className="text-xs text-gray-400">Target: {slo.target}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-green-600">{slo.current}</p>
                <div className="flex items-center gap-1 justify-end">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-600">{slo.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
