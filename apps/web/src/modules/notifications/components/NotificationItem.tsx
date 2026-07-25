'use client';

import Link from 'next/link';
import type { Notification } from '../types/notifications.types';
import { useNotifications } from '../hooks/useNotifications';

interface NotificationItemProps {
  notification: Notification;
}

export function NotificationItem({ notification }: NotificationItemProps) {
  const { markAsRead } = useNotifications();

  const typeConfig = {
    info: { bg: 'bg-blue-50', border: 'border-l-blue-500', icon: 'ℹ️' },
    success: { bg: 'bg-green-50', border: 'border-l-green-500', icon: '✅' },
    warning: { bg: 'bg-yellow-50', border: 'border-l-yellow-500', icon: '⚠️' },
    error: { bg: 'bg-red-50', border: 'border-l-red-500', icon: '❌' },
  };

  const config = typeConfig[notification.type];

  const handleClick = () => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
  };

  const timeAgo = getTimeAgo(notification.createdAt);

  return (
    <div
      className={`p-4 border-l-4 ${config.border} hover:bg-[var(--background)] transition-colors ${
        !notification.read ? config.bg : ''
      }`}
      onClick={handleClick}
    >
      <div className="flex items-start gap-3">
        <span className="text-lg">{config.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-medium text-sm">{notification.title}</h3>
            {!notification.read && (
              <span className="w-2 h-2 bg-[var(--primary)] rounded-full flex-shrink-0" />
            )}
          </div>
          <p className="text-sm text-muted mt-1 line-clamp-2">
            {notification.message}
          </p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-muted">{timeAgo}</span>
            {notification.actionUrl && notification.actionLabel && (
              <Link
                href={notification.actionUrl}
                className="text-xs text-[var(--primary)] hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                {notification.actionLabel}
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function getTimeAgo(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - new Date(date).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Ahora';
  if (minutes < 60) return `Hace ${minutes} min`;
  if (hours < 24) return `Hace ${hours} h`;
  return `Hace ${days} d`;
}

export default NotificationItem;
