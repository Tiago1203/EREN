# EPIC 6: Notifications & Workspace

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Habilitar colaboración y comunicación en tiempo real.**

EPIC 6 es responsable de:
- Gestionar notificaciones del sistema
- Proveer área de trabajo colaborativo
- Gestionar tareas pendientes
- Mostrar feed de actividad
- Sincronizar con eventos de todos los módulos

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
        ├── EPIC 1 (Dashboard)
        ├── EPIC 2 (Operations)
        └── EPIC 5 (Analytics)
                │
                ▼
           EPIC 6 (Notifications & Workspace)
                │
                ▼
           EPIC 7 (Administration)
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 6: Notifications & Workspace                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NOTIFICATIONS MODULE                              │   │
│  │  ├── components/ ──────────── NotificationBell, NotificationPanel   │   │
│  │  ├── hooks/ ─────────────── useNotifications                    │   │
│  │  ├── services/ ──────────── NotificationService                 │   │
│  │  ├── stores/ ───────────── notifications.store                  │   │
│  │  ├── types/ ────────────── notifications.types                  │   │
│  │  └── api/ ─────────────── notifications.api                     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    WORKSPACE MODULE                                 │   │
│  │  ├── components/ ──────────── TaskBoard, ActivityFeed, etc.     │   │
│  │  ├── hooks/ ─────────────── useWorkspace                         │   │
│  │  ├── services/ ──────────── TaskService, ActivityService         │   │
│  │  ├── stores/ ───────────── workspace.store                       │   │
│  │  ├── types/ ────────────── workspace.types                       │   │
│  │  └── pages/ ─────────────── page.tsx                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/modules/
├── notifications/                    # Módulo Notifications
│   ├── components/
│   │   ├── NotificationBell.tsx
│   │   ├── NotificationPanel.tsx
│   │   ├── NotificationItem.tsx
│   │   ├── NotificationPreferences.tsx
│   │   └── NotificationFilters.tsx
│   ├── hooks/
│   │   └── useNotifications.ts
│   ├── services/
│   │   └── notification.service.ts
│   ├── stores/
│   │   └── notifications.store.ts
│   ├── types/
│   │   └── notifications.types.ts
│   └── api/
│       └── notifications.api.ts

├── workspace/                      # Módulo Workspace
│   ├── components/
│   │   ├── TaskBoard.tsx
│   │   ├── TaskCard.tsx
│   │   ├── TaskColumn.tsx
│   │   ├── ActivityFeed.tsx
│   │   ├── ActivityItem.tsx
│   │   ├── CollaborationPanel.tsx
│   │   └── TaskModal.tsx
│   ├── hooks/
│   │   ├── useWorkspace.ts
│   │   └── useTasks.ts
│   ├── services/
│   │   ├── task.service.ts
│   │   └── activity.service.ts
│   ├── stores/
│   │   └── workspace.store.ts
│   ├── types/
│   │   └── workspace.types.ts
│   └── pages/
│       └── page.tsx
```

---

## Componentes

### 1. NotificationBell

Campana de notificaciones con badge.

```typescript
// modules/notifications/components/NotificationBell.tsx
export interface NotificationBellProps {
  count?: number;
  onClick?: () => void;
}
```

### 2. NotificationPanel

Panel deslizable de notificaciones.

```typescript
// modules/notifications/components/NotificationPanel.tsx
export interface NotificationPanelProps {
  open: boolean;
  onClose: () => void;
}
```

### 3. NotificationItem

Elemento individual de notificación.

```typescript
// modules/notifications/components/NotificationItem.tsx
export interface NotificationItemProps {
  notification: Notification;
  onRead?: (id: string) => void;
  onAction?: (id: string, action: string) => void;
}

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
}

export type NotificationType = 'info' | 'success' | 'warning' | 'error';
export type NotificationSource = 'system' | 'operations' | 'ai' | 'analytics';
```

### 4. TaskBoard

Tablero Kanban de tareas.

```typescript
// modules/workspace/components/TaskBoard.tsx
export interface TaskBoardProps {
  tasks: Task[];
  onTaskClick?: (task: Task) => void;
  onTaskMove?: (taskId: string, column: TaskColumn) => void;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee?: User;
  dueDate?: Date;
  tags: string[];
  relatedEntity?: RelatedEntity;
}

export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
```

### 5. ActivityFeed

Feed de actividad en tiempo real.

```typescript
// modules/workspace/components/ActivityFeed.tsx
export interface ActivityFeedProps {
  activities: Activity[];
  loading?: boolean;
}

export interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description?: string;
  user: User;
  timestamp: Date;
  entityType?: string;
  entityId?: string;
}

export type ActivityType = 'created' | 'updated' | 'deleted' | 'commented' | 'assigned' | 'completed';
```

### 6. CollaborationPanel

Panel de colaboración.

```typescript
// modules/workspace/components/CollaborationPanel.tsx
export interface CollaborationPanelProps {
  users: User[];
  activeUsers?: User[];
}
```

---

## Implementaciones

### NotificationService

```typescript
// modules/notifications/services/notification.service.ts
export class NotificationService {
  async getNotifications(): Promise<Notification[]>;
  async markAsRead(id: string): Promise<void>;
  async markAllAsRead(): Promise<void>;
  async deleteNotification(id: string): Promise<void>;
  async getUnreadCount(): Promise<number>;
  async subscribe(callback: (notification: Notification) => void): Promise<void>;
}
```

### TaskService

```typescript
// modules/workspace/services/task.service.ts
export class TaskService {
  async getTasks(filters?: TaskFilters): Promise<Task[]>;
  async getTask(id: string): Promise<Task | null>;
  async createTask(data: CreateTaskDTO): Promise<Task>;
  async updateTask(id: string, data: UpdateTaskDTO): Promise<Task>;
  async deleteTask(id: string): Promise<void>;
  async moveTask(id: string, newStatus: TaskStatus): Promise<Task>;
}
```

### ActivityService

```typescript
// modules/workspace/services/activity.service.ts
export class ActivityService {
  async getActivities(filters?: ActivityFilters): Promise<Activity[]>;
  async subscribe(callback: (activity: Activity) => void): Promise<void>;
}
```

---

## Domain Objects

### Notification

```typescript
// modules/notifications/types/notifications.types.ts
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
  metadata?: Record<string, any>;
}

export type NotificationType = 'info' | 'success' | 'warning' | 'error';
export type NotificationSource = 'system' | 'operations' | 'ai' | 'analytics';

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
```

### Task

```typescript
// modules/workspace/types/workspace.types.ts
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee?: User;
  reporter?: User;
  dueDate?: Date;
  tags: string[];
  relatedEntity?: RelatedEntity;
  comments?: Comment[];
  attachments?: Attachment[];
  createdAt: Date;
  updatedAt: Date;
}

export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface RelatedEntity {
  type: 'work_order' | 'incident' | 'device' | 'article';
  id: string;
  name: string;
}
```

### Activity

```typescript
export interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description?: string;
  user: User;
  timestamp: Date;
  entityType?: string;
  entityId?: string;
  metadata?: Record<string, any>;
}

export type ActivityType = 'created' | 'updated' | 'deleted' | 'commented' | 'assigned' | 'completed';
```

---

## Integración con EPICs

```
EPIC 1 (Dashboard) ───────→ NotificationService
EPIC 2 (Operations) ──────→ NotificationService
EPIC 3 (AI Center) ───────→ NotificationService
EPIC 5 (Analytics) ───────→ NotificationService
        │
        ▼
   NotificationBell (Global Component)
        │
        ▼
   NotificationPanel
```

### Event Subscription

```typescript
// Ejemplo de suscripción a eventos
notificationService.subscribe((notification) => {
  // Mostrar toast o actualizar badge
});

// Desde otros módulos
eventBus.emit('notification', {
  type: 'warning',
  title: 'Nuevo incidente',
  message: 'Se ha reportado un incidente crítico',
  source: 'operations',
});
```

---

## Estado

**🚧 EN PROGRESO**

EPIC 6 está en desarrollo.

---

## Tareas

- [x] Crear documentación EPIC 6
- [x] Crear tipos para notifications y workspace
- [x] Crear servicios
- [x] Crear stores Zustand
- [x] Crear hooks
- [x] Crear componentes
- [x] Crear página de Workspace
- [ ] Crear tests unitarios

---

## Próximos Pasos

- EPIC 7: Administration & Connectors

---

*EREN PHASE 6 - EPIC 6*
*Architecture Board - 2026-07-24*
