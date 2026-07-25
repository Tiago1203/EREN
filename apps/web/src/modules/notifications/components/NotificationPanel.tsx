'use client';

import { useNotifications } from '../hooks/useNotifications';
import { NotificationItem } from './NotificationItem';

interface NotificationPanelProps {
  open: boolean;
  onClose: () => void;
}

export function NotificationPanel({ open, onClose }: NotificationPanelProps) {
  const { notifications, unreadCount, markAllAsRead, loading } = useNotifications();

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Panel */}
      <div className="relative w-full max-w-md bg-[var(--card)] border-l border-[var(--border)] shadow-xl">
        {/* Header */}
        <div className="p-4 border-b border-[var(--border)] flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Notificaciones</h2>
            {unreadCount > 0 && (
              <p className="text-sm text-muted">{unreadCount} sin leer</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-sm text-[var(--primary)] hover:underline"
              >
                Marcar todas leídas
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-[var(--background)] rounded-lg"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Notifications */}
        <div className="overflow-y-auto max-h-[calc(100vh-4rem)]">
          {loading ? (
            <div className="p-4 space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-3 rounded-lg bg-[var(--background)] animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="h-3 bg-gray-100 rounded w-full" />
                </div>
              ))}
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center">
              <svg className="w-12 h-12 mx-auto text-muted mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p className="text-muted">No hay notificaciones</p>
            </div>
          ) : (
            <div className="divide-y divide-[var(--border)]">
              {notifications.map((notification) => (
                <NotificationItem key={notification.id} notification={notification} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default NotificationPanel;
