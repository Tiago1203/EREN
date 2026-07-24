/**
 * Tipos para el módulo Operations
 */

// ============== WORK ORDERS ==============

export type WorkOrderType = 'preventive' | 'corrective' | 'predictive' | 'inspection';
export type WorkOrderStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
export type Priority = 'low' | 'medium' | 'high' | 'critical';

export interface WorkOrder {
  id: string;
  title: string;
  description: string;
  status: WorkOrderStatus;
  priority: Priority;
  type: WorkOrderType;
  assignedTo?: string;
  assignedToName?: string;
  deviceId?: string;
  deviceName?: string;
  establishmentId?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  dueDate?: string;
  completedAt?: string;
  notes?: string;
}

export interface WorkOrderFilters {
  status?: WorkOrderStatus;
  priority?: Priority;
  type?: WorkOrderType;
  assignedTo?: string;
  deviceId?: string;
  establishmentId?: string;
  search?: string;
}

// ============== INCIDENTS ==============

export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentStatus = 'open' | 'investigating' | 'resolved' | 'closed';
export type IncidentType = 'equipment_failure' | 'safety' | 'compliance' | 'operational' | 'other';

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: IncidentStatus;
  type: IncidentType;
  location?: string;
  deviceId?: string;
  deviceName?: string;
  reportedBy: string;
  reportedByName?: string;
  assignedTo?: string;
  assignedToName?: string;
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
  closedAt?: string;
  impact?: string;
  resolution?: string;
}

export interface IncidentFilters {
  severity?: Severity;
  status?: IncidentStatus;
  type?: IncidentType;
  search?: string;
}

// ============== ALERTS ==============

export type AlertType = 'warning' | 'error' | 'info' | 'success';
export type AlertSource = 'system' | 'device' | 'user' | 'schedule';

export interface Alert {
  id: string;
  title: string;
  message: string;
  type: AlertType;
  severity: Severity;
  source: AlertSource;
  acknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  deviceId?: string;
  deviceName?: string;
  createdAt: string;
  expiresAt?: string;
}

export interface AlertFilters {
  type?: AlertType;
  severity?: Severity;
  acknowledged?: boolean;
  source?: AlertSource;
  search?: string;
}

// ============== DEVICE STATUS ==============

export type DeviceStatusType = 'online' | 'offline' | 'warning' | 'maintenance' | 'unknown';

export interface DeviceStatus {
  id: string;
  name: string;
  serialNumber?: string;
  status: DeviceStatusType;
  lastSeen: string;
  location?: string;
  establishmentId?: string;
  criticality?: 'low' | 'medium' | 'high';
}

// ============== TIMELINE ==============

export type TimelineEventType = 'work_order' | 'incident' | 'alert' | 'maintenance';

export interface TimelineEvent {
  id: string;
  type: TimelineEventType;
  title: string;
  description?: string;
  timestamp: string;
  user?: string;
  userName?: string;
  entityId?: string;
}

export interface TimelineFilters {
  types?: TimelineEventType[];
  startDate?: string;
  endDate?: string;
  userId?: string;
}

// ============== STATS ==============

export interface OperationsStats {
  totalWorkOrders: number;
  pendingWorkOrders: number;
  inProgressWorkOrders: number;
  completedWorkOrders: number;
  totalIncidents: number;
  openIncidents: number;
  criticalIncidents: number;
  totalAlerts: number;
  criticalAlerts: number;
  devicesOnline: number;
  devicesOffline: number;
  devicesWarning: number;
}

// ============== STATE ==============

export interface OperationsFilters {
  workOrders: WorkOrderFilters;
  incidents: IncidentFilters;
  alerts: AlertFilters;
  timeline: TimelineFilters;
}

export interface OperationsPageState {
  activeTab: 'overview' | 'workorders' | 'incidents' | 'alerts' | 'timeline';
}
