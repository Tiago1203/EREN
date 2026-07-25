/**
 * Servicio de Operations
 * Consume datos del Business Domain (PHASE 1)
 */

import type {
  WorkOrder,
  Incident,
  Alert,
  DeviceStatus,
  OperationsStats,
  WorkOrderFilters,
  IncidentFilters,
  AlertFilters,
  TimelineFilters,
  TimelineEvent,
} from '../types/operations.types';

export class OperationsService {
  /**
   * Obtiene todas las órdenes de trabajo
   */
  async getWorkOrders(filters?: WorkOrderFilters): Promise<WorkOrder[]> {
    // TODO: Integrar con PHASE 1 - WorkOrder Context
    // Por ahora retornar datos de ejemplo
    return this.getMockWorkOrders();
  }

  /**
   * Obtiene estadísticas de operaciones
   */
  async getStats(): Promise<OperationsStats> {
    const workOrders = await this.getWorkOrders();
    const incidents = await this.getIncidents();
    const alerts = await this.getAlerts();
    const deviceStatuses = await this.getDeviceStatuses();

    return {
      totalWorkOrders: workOrders.length,
      pendingWorkOrders: workOrders.filter(w => w.status === 'pending').length,
      inProgressWorkOrders: workOrders.filter(w => w.status === 'in_progress').length,
      completedWorkOrders: workOrders.filter(w => w.status === 'completed').length,
      totalIncidents: incidents.length,
      openIncidents: incidents.filter(i => i.status === 'open').length,
      criticalIncidents: incidents.filter(i => i.severity === 'critical').length,
      totalAlerts: alerts.length,
      criticalAlerts: alerts.filter(a => a.severity === 'critical').length,
      devicesOnline: deviceStatuses.filter(d => d.status === 'online').length,
      devicesOffline: deviceStatuses.filter(d => d.status === 'offline').length,
      devicesWarning: deviceStatuses.filter(d => d.status === 'warning').length,
    };
  }

  /**
   * Obtiene todos los incidentes
   */
  async getIncidents(filters?: IncidentFilters): Promise<Incident[]> {
    // TODO: Integrar con PHASE 1 - Incident Context
    return this.getMockIncidents();
  }

  /**
   * Obtiene todas las alertas
   */
  async getAlerts(filters?: AlertFilters): Promise<Alert[]> {
    // TODO: Integrar con PHASE 1 - Alert system
    return this.getMockAlerts();
  }

  /**
   * Obtiene estado de dispositivos
   */
  async getDeviceStatuses(): Promise<DeviceStatus[]> {
    // TODO: Integrar con PHASE 1 - Device Context
    return this.getMockDeviceStatuses();
  }

  /**
   * Obtiene timeline de eventos
   */
  async getTimeline(filters?: TimelineFilters): Promise<TimelineEvent[]> {
    const workOrders = await this.getWorkOrders();
    const incidents = await this.getIncidents();
    const alerts = await this.getAlerts();

    const events: TimelineEvent[] = [
      ...workOrders.map(wo => ({
        id: wo.id,
        type: 'work_order' as const,
        title: wo.title,
        description: wo.description,
        timestamp: wo.createdAt,
        user: wo.assignedTo,
        userName: wo.assignedToName,
        entityId: wo.id,
      })),
      ...incidents.map(inc => ({
        id: inc.id,
        type: 'incident' as const,
        title: inc.title,
        description: inc.description,
        timestamp: inc.createdAt,
        user: inc.reportedBy,
        userName: inc.reportedByName,
        entityId: inc.id,
      })),
      ...alerts.map(alert => ({
        id: alert.id,
        type: 'alert' as const,
        title: alert.title,
        description: alert.message,
        timestamp: alert.createdAt,
        entityId: alert.id,
      })),
    ];

    return events.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  // ============== MOCK DATA ==============

  private getMockWorkOrders(): WorkOrder[] {
    return [
      {
        id: 'wo-1',
        title: 'Mantenimiento preventivo - Bomba de infusión',
        description: 'Revisión y calibración según cronograma',
        status: 'pending',
        priority: 'medium',
        type: 'preventive',
        deviceId: 'dev-1',
        deviceName: 'Bomba de Infusión Sigma',
        createdBy: 'user-1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 'wo-2',
        title: 'Reparación - Monitor de signos vitales',
        description: 'Reemplazo de sensor SpO2 defectuoso',
        status: 'in_progress',
        priority: 'high',
        type: 'corrective',
        assignedTo: 'tech-1',
        assignedToName: 'Juan Pérez',
        deviceId: 'dev-2',
        deviceName: 'Monitor VS 100',
        createdBy: 'user-2',
        createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'wo-3',
        title: 'Inspección anual - Respirador',
        description: 'Inspección completa según normativa',
        status: 'completed',
        priority: 'low',
        type: 'inspection',
        assignedTo: 'tech-2',
        assignedToName: 'María García',
        deviceId: 'dev-3',
        deviceName: 'Respirador Puritan Bennett',
        createdBy: 'user-1',
        createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        completedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ];
  }

  private getMockIncidents(): Incident[] {
    return [
      {
        id: 'inc-1',
        title: 'Fallo en monitor de paciente',
        description: 'El monitor muestra lecturas incorrectas de frecuencia cardíaca',
        severity: 'high',
        status: 'investigating',
        type: 'equipment_failure',
        location: 'UCI - Cama 5',
        deviceId: 'dev-2',
        deviceName: 'Monitor VS 100',
        reportedBy: 'user-3',
        reportedByName: 'Enfermera López',
        createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'inc-2',
        title: 'Alarma de temperatura en refrigerador de vacunas',
        description: 'Temperatura fuera de rango acceptable',
        severity: 'critical',
        status: 'open',
        type: 'equipment_failure',
        location: 'Almacén de Farmacia',
        deviceId: 'dev-4',
        deviceName: 'Refrigerador Pharma',
        reportedBy: 'user-4',
        reportedByName: 'Farmacéutico Rodríguez',
        createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];
  }

  private getMockAlerts(): Alert[] {
    return [
      {
        id: 'alert-1',
        title: 'Mantenimiento próximo',
        message: 'El equipo EQ-001 tiene mantenimiento programado en 5 días',
        type: 'warning',
        severity: 'medium',
        source: 'schedule',
        acknowledged: false,
        deviceId: 'dev-1',
        deviceName: 'Bomba de Infusión',
        createdAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: 'alert-2',
        title: 'Temperatura elevada',
        message: 'Sensor TMP-05 reporta 28°C (máximo: 25°C)',
        type: 'error',
        severity: 'high',
        source: 'device',
        acknowledged: false,
        deviceId: 'dev-4',
        deviceName: 'Sensor TMP-05',
        createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      },
      {
        id: 'alert-3',
        title: 'Equipo desconectado',
        message: 'Monitor de signos vitales desconectado de red',
        type: 'info',
        severity: 'low',
        source: 'device',
        acknowledged: true,
        acknowledgedBy: 'tech-1',
        deviceId: 'dev-2',
        deviceName: 'Monitor VS 100',
        createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
    ];
  }

  private getMockDeviceStatuses(): DeviceStatus[] {
    return [
      { id: 'dev-1', name: 'Bomba de Infusión', status: 'online', lastSeen: new Date().toISOString(), location: 'UCI' },
      { id: 'dev-2', name: 'Monitor VS 100', status: 'warning', lastSeen: new Date().toISOString(), location: 'UCI' },
      { id: 'dev-3', name: 'Respirador PB', status: 'online', lastSeen: new Date().toISOString(), location: 'UCI' },
      { id: 'dev-4', name: 'Refrigerador Pharma', status: 'warning', lastSeen: new Date().toISOString(), location: 'Farmacia' },
      { id: 'dev-5', name: 'Desfibrilador', status: 'online', lastSeen: new Date().toISOString(), location: 'Emergencias' },
      { id: 'dev-6', name: 'ECG Portátil', status: 'offline', lastSeen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), location: 'Cardiología' },
    ];
  }
}

export const operationsService = new OperationsService();
