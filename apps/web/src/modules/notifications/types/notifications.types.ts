/**
 * Tipos para el módulo Notifications
 */

export type NotificationType = 'info' | 'success' | 'warning' | 'error';
export type NotificationSource = 'system' | 'operations' | 'ai' | 'analytics';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  createdAt: Date;
  actionUrl?: string;
  actionLabel?: string;
  source: NotificationSource;
  metadata?: Record<string, unknown>;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  inApp: boolean;
  sources: Record<NotificationSource, boolean>;
  quietHours?: QuietHours;
}

export interface QuietHours {
  enabled: boolean;
  start: string;
  end: string;
}

export interface NotificationFilters {
  types?: NotificationType[];
  sources?: NotificationSource[];
  read?: boolean;
  dateFrom?: Date;
  dateTo?: Date;
}

export interface NotificationsState {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
}
