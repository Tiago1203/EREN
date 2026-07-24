'use client';

import type { AuditLog } from '../types/admin.types';

interface AuditLogViewerProps {
  logs: AuditLog[];
  loading?: boolean;
}

export function AuditLogViewer({ logs, loading }: AuditLogViewerProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="card p-4 animate-pulse">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gray-200 rounded-full" />
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                <div className="h-3 bg-gray-100 rounded w-1/2" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="text-center py-12 text-muted">
        No hay registros de auditoría
      </div>
    );
  }

  const actionConfig: Record<string, { icon: string; color: string }> = {
    create: { icon: '➕', color: 'text-green-600' },
    update: { icon: '✏️', color: 'text-blue-600' },
    delete: { icon: '🗑️', color: 'text-red-600' },
    login: { icon: '🔓', color: 'text-purple-600' },
    logout: { icon: '🔒', color: 'text-gray-600' },
    export: { icon: '📥', color: 'text-orange-600' },
    sync: { icon: '🔄', color: 'text-cyan-600' },
  };

  return (
    <div className="space-y-3">
      {logs.map((log) => {
        const config = actionConfig[log.action] || { icon: '📋', color: 'text-gray-600' };
        
        return (
          <div key={log.id} className="card p-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-[var(--background)] flex items-center justify-center flex-shrink-0">
                <span>{config.icon}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <div>
                    <span className="font-medium">{log.userName}</span>
                    <span className="text-muted ml-2">{log.description}</span>
                  </div>
                  <span className="text-xs text-muted whitespace-nowrap">
                    {formatTimestamp(log.timestamp)}
                  </span>
                </div>
                <div className="flex items-center gap-4 mt-1 text-xs text-muted">
                  <span className="capitalize">{log.action}</span>
                  <span>{log.resource}</span>
                  {log.resourceId && <span className="font-mono">{log.resourceId}</span>}
                  {log.ipAddress && <span>{log.ipAddress}</span>}
                </div>
                {log.changes && log.changes.length > 0 && (
                  <div className="mt-2 p-2 bg-[var(--background)] rounded text-xs">
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(log.changes, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - new Date(date).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Ahora';
  if (minutes < 60) return `Hace ${minutes} min`;
  if (hours < 24) return `Hace ${hours} h`;
  if (days < 7) return `Hace ${days} d`;
  
  return new Date(date).toLocaleDateString('es-ES', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default AuditLogViewer;
