# EPIC 2: Operations Center

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Centralizar todas las operaciones clínicas y de ingeniería biomédica.**

EPIC 2 es responsable de:
- Gestionar work orders (órdenes de trabajo)
- Gestionar incidentes
- Gestionar alertas de equipos médicos
- Monitorear estado de dispositivos
- Visualizar operaciones en timeline

---

## Dependencias

```
FASE 5 (Cognitive Multi-Agent System)
        │
        ▼
   PHASE 6 (Hospital Platform)
        │
        ▼
   EPIC 0 (Platform Foundation)
        │
        ├── EPIC 1 (Dashboard & Navigation)
        │
        ▼
   EPIC 2 (Operations Center)
        │
        ├── EPIC 3 (AI Center & Chat)
        └── EPIC 4 (Knowledge Center)
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 2: Operations Center                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    OPERATIONS MODULE                               │   │
│  │  ├── components/ ──────────────────── WorkOrderList, AlertCard   │   │
│  │  ├── pages/ ──────────────────────── page.tsx (Operations)       │   │
│  │  ├── hooks/ ─────────────────────── useOperations                │   │
│  │  ├── services/ ──────────────────── OperationsService           │   │
│  │  ├── api/ ──────────────────────── operations.queries           │   │
│  │  ├── stores/ ───────────────────── operations.store              │   │
│  │  ├── types/ ─────────────────────── operations.types             │   │
│  │  └── utils/ ─────────────────────── operations.utils            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SUB-MODULES                                      │   │
│  │  ├── Work Orders ─────────────────── Gestión de órdenes            │   │
│  │  ├── Incidents ──────────────────── Gestión de incidentes       │   │
│  │  ├── Alerts ─────────────────────── Gestión de alertas          │   │
│  │  └── Timeline ───────────────────── Vista de timeline           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/modules/
├── operations/                         # Módulo Operations
│   ├── components/
│   │   ├── OperationsDashboard.tsx
│   │   ├── WorkOrderList.tsx
│   │   ├── WorkOrderCard.tsx
│   │   ├── IncidentList.tsx
│   │   ├── IncidentCard.tsx
│   │   ├── AlertList.tsx
│   │   ├── AlertCard.tsx
│   │   ├── DeviceStatusMonitor.tsx
│   │   ├── TimelineView.tsx
│   │   └── StatsCards.tsx
│   ├── hooks/
│   │   └── useOperations.ts
│   ├── services/
│   │   └── operations.service.ts
│   ├── api/
│   │   └── operations.queries.ts
│   ├── stores/
│   │   └── operations.store.ts
│   ├── types/
│   │   └── operations.types.ts
│   ├── utils/
│   │   └── operations.utils.ts
│   └── pages/
│       └── page.tsx
```

---

## Componentes

### 1. OperationsDashboard

Dashboard principal de operaciones.

```typescript
// modules/operations/components/OperationsDashboard.tsx
export interface OperationsDashboardProps {
  stats: OperationsStats;
  workOrders: WorkOrder[];
  incidents: Incident[];
  alerts: Alert[];
  onRefresh: () => void;
}
```

### 2. WorkOrderList / WorkOrderCard

Lista y tarjeta de órdenes de trabajo.

```typescript
// modules/operations/components/WorkOrderCard.tsx
export interface WorkOrderCardProps {
  workOrder: WorkOrder;
  onClick?: () => void;
  onStatusChange?: (status: WorkOrderStatus) => void;
}

export interface WorkOrder {
  id: string;
  title: string;
  description: string;
  status: WorkOrderStatus;
  priority: Priority;
  assignedTo?: string;
  deviceId?: string;
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
}

export type WorkOrderStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type Priority = 'low' | 'medium' | 'high' | 'critical';
```

### 3. IncidentList / IncidentCard

Lista y tarjeta de incidentes.

```typescript
// modules/operations/components/IncidentCard.tsx
export interface IncidentCardProps {
  incident: Incident;
  onClick?: () => void;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: IncidentStatus;
  location?: string;
  deviceId?: string;
  reportedBy?: string;
  createdAt: Date;
  resolvedAt?: Date;
}

export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentStatus = 'open' | 'investigating' | 'resolved' | 'closed';
```

### 4. AlertList / AlertCard

Lista y tarjeta de alertas.

```typescript
// modules/operations/components/AlertCard.tsx
export interface AlertCardProps {
  alert: Alert;
  onAcknowledge?: () => void;
  onDismiss?: () => void;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  type: AlertType;
  severity: Severity;
  acknowledged: boolean;
  deviceId?: string;
  createdAt: Date;
}

export type AlertType = 'warning' | 'error' | 'info' | 'success';
```

### 5. DeviceStatusMonitor

Monitoreo de estado de dispositivos.

```typescript
// modules/operations/components/DeviceStatusMonitor.tsx
export interface DeviceStatusMonitorProps {
  devices: DeviceStatus[];
  onDeviceClick?: (deviceId: string) => void;
}

export interface DeviceStatus {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'warning' | 'maintenance';
  lastSeen: Date;
  location?: string;
}
```

### 6. TimelineView

Vista de timeline de operaciones.

```typescript
// modules/operations/components/TimelineView.tsx
export interface TimelineViewProps {
  events: TimelineEvent[];
}

export interface TimelineEvent {
  id: string;
  type: 'work_order' | 'incident' | 'alert' | 'maintenance';
  title: string;
  description?: string;
  timestamp: Date;
  user?: string;
}
```

### 7. StatsCards

Tarjetas de estadísticas de operaciones.

```typescript
// modules/operations/components/StatsCards.tsx
export interface OperationsStats {
  totalWorkOrders: number;
  pendingWorkOrders: number;
  completedWorkOrders: number;
  totalIncidents: number;
  openIncidents: number;
  totalAlerts: number;
  criticalAlerts: number;
  devicesOnline: number;
  devicesOffline: number;
}
```

---

## Implementaciones

### OperationsService

```typescript
// modules/operations/services/operations.service.ts
export class OperationsService {
  // Work Orders
  async getWorkOrders(filters?: WorkOrderFilters): Promise<WorkOrder[]>;
  async getWorkOrder(id: string): Promise<WorkOrder | null>;
  async createWorkOrder(data: CreateWorkOrderDTO): Promise<WorkOrder>;
  async updateWorkOrder(id: string, data: UpdateWorkOrderDTO): Promise<WorkOrder>;
  async deleteWorkOrder(id: string): Promise<void>;

  // Incidents
  async getIncidents(filters?: IncidentFilters): Promise<Incident[]>;
  async getIncident(id: string): Promise<Incident | null>;
  async createIncident(data: CreateIncidentDTO): Promise<Incident>;
  async updateIncident(id: string, data: UpdateIncidentDTO): Promise<Incident>;

  // Alerts
  async getAlerts(filters?: AlertFilters): Promise<Alert[]>;
  async acknowledgeAlert(id: string): Promise<Alert>;
  async dismissAlert(id: string): Promise<void>;

  // Device Status
  async getDeviceStatuses(): Promise<DeviceStatus[]>;

  // Timeline
  async getTimeline(filters?: TimelineFilters): Promise<TimelineEvent[]>;

  // Stats
  async getStats(): Promise<OperationsStats>;
}
```

### OperationsStore

```typescript
// modules/operations/stores/operations.store.ts
interface OperationsState {
  workOrders: WorkOrder[];
  incidents: Incident[];
  alerts: Alert[];
  deviceStatuses: DeviceStatus[];
  stats: OperationsStats;
  loading: boolean;
  error: string | null;
  filters: OperationsFilters;
}

export const useOperationsStore = create<OperationsState>((set, get) => ({
  // ... actions
}));
```

### useOperations Hook

```typescript
// modules/operations/hooks/useOperations.ts
export function useOperations() {
  const {
    workOrders,
    incidents,
    alerts,
    stats,
    loading,
    error,
    loadData,
    setFilters,
  } = useOperationsStore();

  useEffect(() => {
    loadData();
  }, []);

  return {
    workOrders,
    incidents,
    alerts,
    stats,
    loading,
    error,
    refresh: loadData,
    setFilters,
  };
}
```

---

## Domain Objects

### WorkOrder

```typescript
// modules/operations/types/operations.types.ts
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
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
  completedAt?: Date;
  notes?: string;
  attachments?: Attachment[];
}

export type WorkOrderType = 'preventive' | 'corrective' | 'predictive' | 'inspection';
export type WorkOrderStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
export type Priority = 'low' | 'medium' | 'high' | 'critical';
```

### Incident

```typescript
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
  createdAt: Date;
  updatedAt: Date;
  resolvedAt?: Date;
  closedAt?: Date;
  impact?: string;
  resolution?: string;
}

export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentStatus = 'open' | 'investigating' | 'resolved' | 'closed';
export type IncidentType = 'equipment_failure' | 'safety' | 'compliance' | 'operational' | 'other';
```

### Alert

```typescript
export interface Alert {
  id: string;
  title: string;
  message: string;
  type: AlertType;
  severity: Severity;
  source: AlertSource;
  acknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: Date;
  deviceId?: string;
  deviceName?: string;
  createdAt: Date;
  expiresAt?: Date;
}

export type AlertType = 'warning' | 'error' | 'info' | 'success';
export type AlertSource = 'system' | 'device' | 'user' | 'schedule';
```

### DeviceStatus

```typescript
export interface DeviceStatus {
  id: string;
  name: string;
  serialNumber?: string;
  status: DeviceStatusType;
  lastSeen: Date;
  location?: string;
  establishmentId?: string;
  criticality?: 'low' | 'medium' | 'high';
}

export type DeviceStatusType = 'online' | 'offline' | 'warning' | 'maintenance' | 'unknown';
```

---

## Integración con PHASE 1

```
PHASE 1 (Business Domain)
        │
        ├── Device Context ──▶ DeviceStatus, Alerts
        ├── Incident Context ──▶ Incidents
        ├── WorkOrder Context ──▶ WorkOrders
        └── Maintenance Context ──▶ Maintenance Logs
                │
                ▼
           EPIC 2 (Operations Center)
                │
                ├── WorkOrderList
                ├── IncidentList
                ├── AlertList
                ├── DeviceStatusMonitor
                └── TimelineView
```

### Consumiendo PHASE 1

```typescript
// modules/operations/api/operations.queries.ts
// Consumiendo de PHASE 1 - Business Domain
import { fetchWorkOrders, fetchIncidents, fetchAlerts } from '@/lib/queries';
```

---

## Estado

**🚧 EN PROGRESO**

EPIC 2 está en desarrollo.

---

## Tareas

- [x] Crear documentación EPIC 2
- [x] Crear tipos para operaciones
- [x] Crear servicios del módulo
- [x] Crear store Zustand
- [x] Crear hooks
- [x] Crear componentes
- [x] Crear página de operaciones
- [ ] Crear tests unitarios
- [ ] Integrar con PHASE 1

---

## Próximos Pasos

- EPIC 3: AI Center & Chat
- EPIC 4: Knowledge Center

---

*EREN PHASE 6 - EPIC 2*
*Architecture Board - 2026-07-24*
