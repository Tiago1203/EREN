<<<<<<< HEAD
/**
 * Notifications Module - PHASE 6 EPIC 6
 * 
 * Placeholder for Notifications module.
 * Full implementation pending PHASE 7.
 * 
 * Contains:
 * - Notification Center
 * - Alert Management
 * - Real-time Notifications
 */
export default function NotificationsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Notificaciones</h1>
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)] p-8">
        <p className="text-muted">
          Módulo de notificaciones. Implementación completa en PHASE 7.
        </p>
=======
'use client';

import { useNotifications } from '../hooks/useNotifications';
import { NotificationItem } from '../components/NotificationItem';

/**
 * NotificationsPage - Página completa de notificaciones
 */
export default function NotificationsPage() {
  const { notifications, unreadCount, markAllAsRead, loading } = useNotifications();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Notificaciones</h1>
          {unreadCount > 0 && (
            <p className="text-sm text-muted">{unreadCount} sin leer</p>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="px-4 py-2 text-sm bg-[var(--primary)] text-white rounded-lg hover:opacity-90"
          >
            Marcar todas leídas
          </button>
        )}
      </div>

      {/* Notifications List */}
      <div className="bg-[var(--card)] rounded-lg border border-[var(--border)]">
        {loading ? (
          <div className="p-4 space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="p-4 rounded-lg bg-[var(--background)] animate-pulse">
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-3" />
                <div className="h-4 bg-gray-100 rounded w-full" />
              </div>
            ))}
          </div>
        ) : notifications.length === 0 ? (
          <div className="p-12 text-center">
            <svg className="w-16 h-16 mx-auto text-muted mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <p className="text-lg text-muted">No hay notificaciones</p>
            <p className="text-sm text-muted mt-1">Las notificaciones aparecerán aquí cuando las recibas</p>
          </div>
        ) : (
          <div className="divide-y divide-[var(--border)]">
            {notifications.map((notification) => (
              <NotificationItem key={notification.id} notification={notification} />
            ))}
          </div>
        )}
>>>>>>> origin/main
      </div>
    </div>
  );
}
