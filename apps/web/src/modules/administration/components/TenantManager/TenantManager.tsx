"use client";

import React, { useEffect } from "react";
import { useAdminStore } from "../../stores/admin.store";
import { Building2, Users, Activity } from "lucide-react";

export function TenantManager() {
  const { tenants, tenantsLoading, tenantsCount, fetchTenants } = useAdminStore();

  useEffect(() => { fetchTenants(); }, [fetchTenants]);

  const tierColors: Record<string, string> = {
    starter: "bg-gray-100 text-gray-700",
    professional: "bg-blue-100 text-blue-700",
    enterprise: "bg-purple-100 text-purple-700",
    trial: "bg-yellow-100 text-yellow-700",
  };

  const statusColors: Record<string, string> = {
    active: "bg-green-100 text-green-700",
    suspended: "bg-red-100 text-red-700",
    pending: "bg-yellow-100 text-yellow-700",
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">Tenant Management</h2>
        <p className="text-sm text-gray-500">{tenantsCount} tenants</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg"><Building2 className="w-5 h-5 text-blue-600" /></div>
          <div><p className="text-2xl font-bold text-gray-900">{tenantsCount}</p><p className="text-xs text-gray-500">Total Tenants</p></div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm flex items-center gap-3">
          <div className="p-2 bg-green-100 rounded-lg"><Users className="w-5 h-5 text-green-600" /></div>
          <div><p className="text-2xl font-bold text-gray-900">{tenants.filter(t => t.status === "active").length}</p><p className="text-xs text-gray-500">Active</p></div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg"><Activity className="w-5 h-5 text-purple-600" /></div>
          <div><p className="text-2xl font-bold text-gray-900">{tenants.filter(t => t.subscription_tier === "enterprise").length}</p><p className="text-xs text-gray-500">Enterprise</p></div>
        </div>
      </div>
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tenant</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tier</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {tenantsLoading ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : tenants.length === 0 ? (
              <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-400">No tenants found</td></tr>
            ) : (
              tenants.map((tenant) => (
                <tr key={tenant.tenant_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Building2 className="w-4 h-4 text-gray-400" />
                      <span className="text-sm font-medium text-gray-900">{tenant.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={}>
                      {tenant.subscription_tier}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={}>
                      {tenant.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50">Manage</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
