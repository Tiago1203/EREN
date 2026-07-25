"use client";

/**
 * PHASE 7 - EPIC 5: Audit Log Viewer
 * Integración: EPIC 1 (audit logs)
 */

import React, { useEffect, useState } from "react";
import { auditService, AuditLogEntry, AuditFilters } from "../../services/audit.service";
import { Search, Download, ChevronDown, FileText, Eye } from "lucide-react";

export function AuditViewer() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<AuditFilters>({});
  const [selectedEntry, setSelectedEntry] = useState<AuditLogEntry | null>(null);
  const [page, setPage] = useState(0);
  const limit = 25;

  const loadLogs = async (f: AuditFilters, offset: number) => {
    setLoading(true);
    try {
      const result = await auditService.queryLogs(f, limit, offset);
      setEntries(result.entries);
      setCount(result.count);
    } catch {
      // En demo, datos vacíos es ok
      setEntries([]);
      setCount(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs(filters, page * limit);
  }, [filters, page]);

  const actionColors: Record<string, string> = {
    create: "bg-green-100 text-green-700",
    read: "bg-blue-100 text-blue-700",
    update: "bg-yellow-100 text-yellow-700",
    delete: "bg-red-100 text-red-700",
    login: "bg-purple-100 text-purple-700",
    logout: "bg-gray-100 text-gray-700",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Audit Log Viewer</h2>
          <p className="text-sm text-gray-500">{count} entries total</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => auditService.exportLogs(filters, "csv")}
            className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button
            onClick={() => auditService.exportLogs(filters, "json")}
            className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            <FileText className="w-4 h-4" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search..."
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          onChange={(e) => setFilters({ ...filters, action: e.target.value || undefined })}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Actions</option>
          <option value="create">Create</option>
          <option value="read">Read</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
          <option value="login">Login</option>
        </select>
        <select
          onChange={(e) => setFilters({ ...filters, category: e.target.value || undefined })}
          className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Categories</option>
          <option value="equipment">Equipment</option>
          <option value="maintenance">Maintenance</option>
          <option value="establishment">Establishment</option>
          <option value="user">User</option>
          <option value="security">Security</option>
          <option value="clinical">Clinical</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400">Loading...</td>
              </tr>
            ) : entries.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400">No audit entries found</td>
              </tr>
            ) : (
              entries.map((entry) => (
                <tr key={entry.entry_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {new Date(entry.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-xs font-medium text-gray-900">{entry.user_email}</p>
                      <p className="text-xs text-gray-400">{entry.user_id}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${actionColors[entry.action] || "bg-gray-100 text-gray-700"}`}>
                      {entry.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-700">
                    <span className="font-medium">{entry.resource_type}</span>
                    <span className="text-gray-400 ml-1">#{entry.resource_id}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-400">{entry.ip_address}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => setSelectedEntry(entry)}
                      className="p-1.5 text-gray-400 hover:text-blue-600 rounded transition"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
          <span className="text-xs text-gray-500">
            Showing {page * limit + 1}–{Math.min((page + 1) * limit, count)} of {count}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 text-xs border border-gray-200 rounded disabled:opacity-50 hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * limit >= count}
              className="px-3 py-1 text-xs border border-gray-200 rounded disabled:opacity-50 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedEntry && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Audit Entry Detail</h3>
            <dl className="space-y-3 text-sm">
              {[
                ["Entry ID", selectedEntry.entry_id],
                ["Timestamp", new Date(selectedEntry.timestamp).toLocaleString()],
                ["User", `${selectedEntry.user_email} (${selectedEntry.user_id})`],
                ["Action", selectedEntry.action],
                ["Category", selectedEntry.category],
                ["Resource", `${selectedEntry.resource_type} #${selectedEntry.resource_id}`],
                ["IP Address", selectedEntry.ip_address],
                ["Session ID", selectedEntry.session_id],
              ].map(([label, value]) => (
                <div key={label} className="flex">
                  <dt className="w-32 text-gray-500 flex-shrink-0">{label}:</dt>
                  <dd className="text-gray-900 break-all">{value}</dd>
                </div>
              ))}
              {Object.keys(selectedEntry.details).length > 0 && (
                <div>
                  <dt className="text-gray-500 mb-1">Details:</dt>
                  <dd>
                    <pre className="bg-gray-50 rounded p-2 text-xs overflow-x-auto">
                      {JSON.stringify(selectedEntry.details, null, 2)}
                    </pre>
                  </dd>
                </div>
              )}
            </dl>
            <button
              onClick={() => setSelectedEntry(null)}
              className="mt-4 w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
