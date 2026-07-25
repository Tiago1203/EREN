"use client";

/**
 * PHASE 7 - EPIC 5: Role Manager Component
 */

import React, { useEffect, useState } from "react";
import { useAdminStore } from "../../stores/admin.store";
import { Plus, Shield, ChevronRight } from "lucide-react";

export function RoleManager() {
  const { roles, rolesLoading, fetchRoles, createRole } = useAdminStore();
  const [showCreate, setShowCreate] = useState(false);
  const [expandedRole, setExpandedRole] = useState<string | null>(null);

  useEffect(() => {
    fetchRoles();
  }, [fetchRoles]);

  const roleTypeLabels: Record<string, string> = {
    system_admin: "System Admin",
    tenant_admin: "Tenant Admin",
    department_head: "Department Head",
    technician: "Technician",
    clinical_staff: "Clinical Staff",
    viewer: "Viewer",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Role Manager</h2>
          <p className="text-sm text-gray-500">
            Manage roles and permissions
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium transition"
        >
          <Plus className="w-4 h-4" />
          Create Role
        </button>
      </div>

      {/* Role List */}
      <div className="space-y-3">
        {rolesLoading ? (
          <div className="text-center py-8 text-gray-400">Loading roles...</div>
        ) : roles.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            No roles found. Create your first role.
          </div>
        ) : (
          roles.map((role) => (
            <div
              key={role.role_id}
              className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
            >
              <button
                onClick={() =>
                  setExpandedRole(expandedRole === role.role_id ? null : role.role_id)
                }
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    role.is_system ? "bg-purple-100" : "bg-blue-100"
                  }`}>
                    <Shield className={`w-5 h-5 ${
                      role.is_system ? "text-purple-600" : "text-blue-600"
                    }`} />
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">{role.name}</p>
                    <p className="text-xs text-gray-500">
                      {roleTypeLabels[role.role_type] || role.role_type}
                      {role.tenant_id && " · Tenant Role"}
                      {role.is_system && " · System Role"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-400">
                    {role.permissions.length} permissions
                  </span>
                  <ChevronRight
                    className={`w-4 h-4 text-gray-400 transition-transform ${
                      expandedRole === role.role_id ? "rotate-90" : ""
                    }`}
                  />
                </div>
              </button>

              {expandedRole === role.role_id && (
                <div className="border-t border-gray-100 p-4 bg-gray-50">
                  {role.description && (
                    <p className="text-sm text-gray-600 mb-3">{role.description}</p>
                  )}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {role.permissions.map((perm) => (
                      <div
                        key={perm.permission_id}
                        className="bg-white rounded border border-gray-200 px-3 py-2"
                      >
                        <p className="text-xs font-medium text-gray-700">{perm.name}</p>
                        <p className="text-xs text-gray-400">
                          {perm.resource}:{perm.action} · {perm.scope}
                        </p>
                      </div>
                    ))}
                    {role.permissions.length === 0 && (
                      <p className="text-xs text-gray-400 col-span-full">
                        No permissions assigned
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Create Role Modal */}
      {showCreate && (
        <CreateRoleModal
          onClose={() => setShowCreate(false)}
          onCreate={createRole}
        />
      )}
    </div>
  );
}

function CreateRoleModal({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (payload: Parameters<typeof useAdminStore.getState>["createRole"]>[0]) => Promise<void>;
}) {
  const [form, setForm] = useState({
    name: "",
    role_type: "viewer",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onCreate(form);
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Create Role</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role Name</label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role Type</label>
            <select
              value={form.role_type}
              onChange={(e) => setForm({ ...form, role_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="system_admin">System Admin</option>
              <option value="tenant_admin">Tenant Admin</option>
              <option value="department_head">Department Head</option>
              <option value="technician">Technician</option>
              <option value="clinical_staff">Clinical Staff</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? "Creating..." : "Create Role"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
