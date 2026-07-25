'use client';

import type { Alert } from '../types/operations.types';

interface AlertListProps {
  alerts: Alert[];
  onAcknowledge?: (id: string) => void;
  onDismiss?: (id: string) => void;
}

export function AlertList({ alerts, onAcknowledge, onDismiss }: AlertListProps) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-8 text-muted">
        No hay alertas activas
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onAcknowledge={onAcknowledge}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
}

interface AlertCardProps {
  alert: Alert;
  onAcknowledge?: (id: string) => void;
  onDismiss?: (id: string) => void;
}

function AlertCard({ alert, onAcknowledge, onDismiss }: AlertCardProps) {
  const severityColors = {
    low: 'border-l-blue-500',
    medium: 'border-l-yellow-500',
    high: 'border-l-orange-500',
    critical: 'border-l-red-500',
  };

  const typeIcons = {
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️',
    success: '✅',
  };

  return (
    <div
      className={`
        card p-4 border-l-4 ${severityColors[alert.severity]}
        ${alert.acknowledged ? 'opacity-60' : ''}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <span className="text-xl">{typeIcons[alert.type]}</span>
          <div>
            <h4 className="font-medium">{alert.title}</h4>
            <p className="text-sm text-muted mt-1">{alert.message}</p>
            {alert.deviceName && (
              <p className="text-xs text-muted mt-1">
                Dispositivo: {alert.deviceName}
              </p>
            )}
            <p className="text-xs text-muted mt-1">
              {new Date(alert.createdAt).toLocaleString()}
            </p>
          </div>
        </div>
        
        {!alert.acknowledged && (
          <div className="flex gap-2">
            <button
              onClick={() => onAcknowledge?.(alert.id)}
              className="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Aceptar
            </button>
            <button
              onClick={() => onDismiss?.(alert.id)}
              className="px-3 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Dismiss
            </button>
          </div>
        )}
        
        {alert.acknowledged && (
          <span className="badge badge-success">Confirmada</span>
        )}
      </div>
    </div>
  );
}

export default AlertList;
