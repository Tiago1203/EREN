/**
 * Notification Service
 */

import type { Notification, NotificationType, NotificationSource } from '../types/notifications.types';

export class NotificationService {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/notifications') {
    this.baseUrl = baseUrl;
  }

  async getNotifications(): Promise<Notification[]> {
    return this.getMockNotifications();
  }

  async markAsRead(id: string): Promise<void> {
    console.log('Mark as read:', id);
  }

  async markAllAsRead(): Promise<void> {
    console.log('Mark all as read');
  }

  async deleteNotification(id: string): Promise<void> {
    console.log('Delete notification:', id);
  }

  async getUnreadCount(): Promise<number> {
    const notifications = this.getMockNotifications();
    return notifications.filter((n) => !n.read).length;
  }

  private getMockNotifications(): Notification[] {
    return [
      {
        id: 'notif-1',
        type: 'warning',
        title: 'Incidente Crítico',
        message: 'Se ha reportado un incidente crítico en el área de UCI',
        read: false,
        createdAt: new Date(Date.now() - 10 * 60 * 1000),
        actionUrl: '/operations/incidents/INC-001',
        actionLabel: 'Ver incidente',
        source: 'operations',
      },
      {
        id: 'notif-2',
        type: 'info',
        title: 'Mantenimiento Programado',
        message: 'Bomba de infusión #BI-004 programada para mantenimiento preventivo',
        read: false,
        createdAt: new Date(Date.now() - 30 * 60 * 1000),
        actionUrl: '/operations/work-orders/WO-042',
        actionLabel: 'Ver orden',
        source: 'operations',
      },
      {
        id: 'notif-3',
        type: 'success',
        title: 'AI Recommends',
        message: 'El agente biomédico recomienda calibración del monitor #MON-012',
        read: true,
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
        source: 'ai',
      },
      {
        id: 'notif-4',
        type: 'info',
        title: 'Reporte Generado',
        message: 'Reporte mensual de mantenimiento listo para descarga',
        read: true,
        createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
        actionUrl: '/analytics/reports/REP-023',
        actionLabel: 'Ver reporte',
        source: 'analytics',
      },
      {
        id: 'notif-5',
        type: 'warning',
        title: 'Vencimiento de Certificado',
        message: 'Certificado de calibración del equipo #EQ-087 vence en 7 días',
        read: false,
        createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
        actionUrl: '/operations/devices/EQ-087',
        actionLabel: 'Ver equipo',
        source: 'system',
      },
    ];
  }
}

export const notificationService = new NotificationService();
