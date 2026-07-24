'use client';

import type { SystemSetting } from '../types/admin.types';

interface SettingsPanelProps {
  settings: SystemSetting[];
  onSettingChange?: (key: string, value: unknown) => void;
}

export function SettingsPanel({ settings, onSettingChange }: SettingsPanelProps) {
  const categories = ['general', 'security', 'notifications', 'integrations', 'appearance'];
  const categoryLabels: Record<string, string> = {
    general: 'General',
    security: 'Seguridad',
    notifications: 'Notificaciones',
    integrations: 'Integraciones',
    appearance: 'Apariencia',
  };

  const settingsByCategory = categories.reduce((acc, cat) => {
    acc[cat] = settings.filter((s) => s.category === cat);
    return acc;
  }, {} as Record<string, SystemSetting[]>);

  return (
    <div className="space-y-6">
      {categories.map((category) => {
        const categorySettings = settingsByCategory[category];
        if (categorySettings.length === 0) return null;

        return (
          <div key={category}>
            <h3 className="text-lg font-semibold mb-3">{categoryLabels[category]}</h3>
            <div className="card divide-y divide-[var(--border)]">
              {categorySettings.map((setting) => (
                <SettingRow
                  key={setting.id}
                  setting={setting}
                  onChange={(value) => onSettingChange?.(setting.key, value)}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface SettingRowProps {
  setting: SystemSetting;
  onChange: (value: unknown) => void;
}

function SettingRow({ setting, onChange }: SettingRowProps) {
  const renderInput = () => {
    switch (setting.type) {
      case 'boolean':
        return (
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={Boolean(setting.value)}
              onChange={(e) => onChange(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        );

      case 'string':
        return (
          <input
            type="text"
            value={String(setting.value || '')}
            onChange={(e) => onChange(e.target.value)}
            className="px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--background)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
          />
        );

      case 'number':
        return (
          <input
            type="number"
            value={Number(setting.value || 0)}
            onChange={(e) => onChange(Number(e.target.value))}
            className="px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--background)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)] w-24"
          />
        );

      case 'select':
        return (
          <select
            value={String(setting.value || '')}
            onChange={(e) => onChange(e.target.value)}
            className="px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--background)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
          >
            {setting.options?.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        );

      default:
        return <span className="text-muted">{String(setting.value)}</span>;
    }
  };

  return (
    <div className="p-4 flex items-center justify-between">
      <div>
        <label className="font-medium">{setting.label}</label>
        {setting.description && (
          <p className="text-sm text-muted mt-1">{setting.description}</p>
        )}
      </div>
      <div>{renderInput()}</div>
    </div>
  );
}

export default SettingsPanel;
