"use client";

import React, { useEffect, useState } from "react";
import { useAdminStore } from "../../stores/admin.store";
import { Settings, Lock, Bell, Globe } from "lucide-react";

const categoryIcons: Record<string, React.ReactNode> = {
  general: <Settings className="w-4 h-4" />,
  security: <Lock className="w-4 h-4" />,
  notifications: <Bell className="w-4 h-4" />,
  integrations: <Globe className="w-4 h-4" />,
};

export function SettingsManager() {
  const { settings, settingsLoading, fetchSettings, updateSetting } = useAdminStore();
  const [editing, setEditing] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => { fetchSettings(); }, [fetchSettings]);

  const grouped = settings.reduce((acc, s) => {
    acc[s.category] = acc[s.category] || [];
    acc[s.category].push(s);
    return acc;
  }, {} as Record<string, typeof settings>);

  const handleSave = async (key: string) => {
    await updateSetting(key, editValue);
    setEditing(null);
  };

  const startEdit = (setting: typeof settings[0]) => {
    setEditing(setting.key);
    setEditValue(setting.value);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-gray-900">System Settings</h2>
        <p className="text-sm text-gray-500">{settings.length} settings</p>
      </div>
      {settingsLoading ? (
        <div className="text-center py-8 text-gray-400">Loading...</div>
      ) : (
        Object.entries(grouped).map(([category, categorySettings]) => (
          <div key={category}>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              {categoryIcons[category] || <Settings className="w-4 h-4" />}
              {category.charAt(0).toUpperCase() + category.slice(1)} Settings
            </h3>
            <div className="space-y-2">
              {categorySettings.map((setting) => (
                <div key={setting.setting_id} className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{setting.key}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{setting.description}</p>
                    </div>
                    {editing === setting.key ? (
                      <div className="flex items-center gap-2 ml-4">
                        <input
                          type={setting.is_encrypted ? "password" : "text"}
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="px-3 py-1 border border-gray-200 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button onClick={() => handleSave(setting.key)} className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">Save</button>
                        <button onClick={() => setEditing(null)} className="px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50">Cancel</button>
                      </div>
                    ) : (
                      <button
                        onClick={() => startEdit(setting)}
                        disabled={setting.is_readonly}
                        className="ml-4 px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50"
                      >
                        Edit
                      </button>
                    )}
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    <span className="font-mono bg-gray-50 px-2 py-0.5 rounded">
                      {setting.is_encrypted ? "••••••••" : setting.value}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
