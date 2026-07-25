/**
 * Activity Service
 */

import type { Activity, ActivityType, User } from '../types/workspace.types';

export class ActivityService {
  async getActivities(): Promise<Activity[]> {
    return this.getMockActivities();
  }

  private getMockActivities(): Activity[] {
    const users: User[] = [
      { id: 'user-1', name: 'Carlos García', email: 'carlos@hospital.com', role: 'Ingeniero' },
      { id: 'user-2', name: 'María López', email: 'maria@hospital.com', role: 'Técnico' },
      { id: 'user-3', name: 'Juan Pérez', email: 'juan@hospital.com', role: 'Coordinador' },
    ];

    return [
      {
        id: 'act-1',
        type: 'completed',
        title: 'Tarea completada',
        description: 'Carlos García completó "Instalar repuesto en monitor #MON-008"',
        user: users[0],
        timestamp: new Date(Date.now() - 15 * 60 * 1000),
        entityType: 'task',
        entityId: 'task-old-1',
      },
      {
        id: 'act-2',
        type: 'created',
        title: 'Incidente reportado',
        description: 'María López reportó incidente en área de UCI',
        user: users[1],
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
        entityType: 'incident',
        entityId: 'INC-024',
      },
      {
        id: 'act-3',
        type: 'updated',
        title: 'Orden de trabajo actualizada',
        description: 'Juan Pérez actualizó orden WO-042',
        user: users[2],
        timestamp: new Date(Date.now() - 45 * 60 * 1000),
        entityType: 'work_order',
        entityId: 'WO-042',
      },
      {
        id: 'act-4',
        type: 'assigned',
        title: 'Tarea asignada',
        description: 'Carlos García fue asignado a "Revisar bomba #BI-004"',
        user: users[2],
        timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
        entityType: 'task',
        entityId: 'task-1',
      },
      {
        id: 'act-5',
        type: 'commented',
        title: 'Nuevo comentario',
        description: 'María López comentó en incidente #INC-023',
        user: users[1],
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        entityType: 'incident',
        entityId: 'INC-023',
      },
      {
        id: 'act-6',
        type: 'updated',
        title: 'Artículo actualizado',
        description: 'Juan Pérez actualizó "Protocolo de mantenimiento - Bombas"',
        user: users[2],
        timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000),
        entityType: 'article',
        entityId: 'art-1',
      },
      {
        id: 'act-7',
        type: 'completed',
        title: 'Mantenimiento completado',
        description: 'María López completó mantenimiento preventivo en área de Rayos X',
        user: users[1],
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
        entityType: 'work_order',
        entityId: 'WO-040',
      },
      {
        id: 'act-8',
        type: 'created',
        title: 'Equipo registrado',
        description: 'Carlos García registró nuevo equipo "Ventilador #VENT-015"',
        user: users[0],
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
        entityType: 'device',
        entityId: 'VENT-015',
      },
    ];
  }
}

export const activityService = new ActivityService();
