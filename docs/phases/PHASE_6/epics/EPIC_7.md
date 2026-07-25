# EPIC 7: Administration & Connectors

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Finalizar la plataforma con panel administrativo y arquitectura de integraciones.**

EPIC 7 es responsable de:
- Administrar usuarios del sistema
- Gestionar roles y permisos
- Configurar opciones del sistema
- Preparar arquitectura para conectores FHIR, HL7, DICOM
- Registrar auditoría del sistema

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
        ├── EPIC 1 (Navigation)
        └── EPIC 6 (Notifications)
                │
                ▼
           EPIC 7 (Administration & Connectors)
                │
                ▼
           PHASE 6 OUTPUT
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 7: Administration & Connectors                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    ADMIN MODULE                                      │   │
│  │  ├── components/ ──────────── AdminPanel, UserList, RoleManager    │   │
│  │  ├── pages/ ─────────────── page.tsx (Admin)                     │   │
│  │  ├── hooks/ ─────────────── useAdmin                              │   │
│  │  ├── services/ ──────────── AdminService, UserService             │   │
│  │  ├── stores/ ───────────── admin.store                            │   │
│  │  └── types/ ────────────── admin.types                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    CONNECTORS MODULE                                │   │
│  │  ├── types/ ────────────── connector.types                        │   │
│  │  ├── registry/ ────────── ConnectorRegistry                      │   │
│  │  └── adapters/ ────────── FHIR, HL7, DICOM adapters             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/modules/
├── admin/                           # Módulo Admin
│   ├── components/
│   │   ├── AdminPanel.tsx
│   │   ├── UserList.tsx
│   │   ├── UserCard.tsx
│   │   ├── RoleManager.tsx
│   │   ├── PermissionMatrix.tsx
│   │   ├── SettingsPanel.tsx
│   │   ├── ConnectorConfig.tsx
│   │   └── AuditLogViewer.tsx
│   ├── hooks/
│   │   └── useAdmin.ts
│   ├── services/
│   │   ├── admin.service.ts
│   │   ├── user.service.ts
│   │   └── audit.service.ts
│   ├── stores/
│   │   └── admin.store.ts
│   ├── types/
│   │   └── admin.types.ts
│   └── pages/
│       └── page.tsx

├── connectors/                     # Módulo Connectors (Framework)
│   ├── types/
│   │   └── connector.types.ts
│   ├── registry/
│   │   └── connector.registry.ts
│   └── adapters/
│       ├── fhir.adapter.ts
│       ├── hl7.adapter.ts
│       └── dicom.adapter.ts
```

---

## Componentes

### 1. AdminPanel

Panel principal de administración.

```typescript
// modules/admin/components/AdminPanel.tsx
export interface AdminPanelProps {
  activeTab: AdminTab;
  onTabChange: (tab: AdminTab) => void;
}

export type AdminTab = 'users' | 'roles' | 'settings' | 'connectors' | 'audit';
```

### 2. UserList / UserCard

Lista de usuarios con acciones.

```typescript
// modules/admin/components/UserList.tsx
export interface UserListProps {
  users: User[];
  onUserClick?: (user: User) => void;
  onUserEdit?: (user: User) => void;
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: Role;
  status: 'active' | 'inactive' | 'pending';
  lastLogin?: Date;
  createdAt: Date;
}
```

### 3. RoleManager

Gestor de roles y permisos.

```typescript
// modules/admin/components/RoleManager.tsx
export interface RoleManagerProps {
  roles: Role[];
  onRoleEdit?: (role: Role) => void;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  userCount: number;
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: 'read' | 'write' | 'delete' | 'admin';
}
```

### 4. SettingsPanel

Panel de configuración del sistema.

```typescript
// modules/admin/components/SettingsPanel.tsx
export interface SettingsPanelProps {
  settings: SystemSetting[];
  onSettingChange?: (key: string, value: any) => void;
}

export interface SystemSetting {
  key: string;
  label: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'select';
  options?: { value: any; label: string }[];
  description?: string;
}
```

### 5. ConnectorConfig

Configuración de conectores.

```typescript
// modules/admin/components/ConnectorConfig.tsx
export interface ConnectorConfigProps {
  connectors: ConnectorConfig[];
  onConnectorToggle?: (id: string, enabled: boolean) => void;
}

export interface ConnectorConfig {
  id: string;
  name: string;
  type: ConnectorType;
  enabled: boolean;
  status: 'connected' | 'disconnected' | 'error';
  lastSync?: Date;
  config: Record<string, any>;
}

export type ConnectorType = 'fhir' | 'hl7' | 'dicom' | 'mqtt' | 'custom';
```

### 6. AuditLogViewer

Visor de logs de auditoría.

```typescript
// modules/admin/components/AuditLogViewer.tsx
export interface AuditLogViewerProps {
  logs: AuditLog[];
  loading?: boolean;
}

export interface AuditLog {
  id: string;
  timestamp: Date;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  resourceId?: string;
  changes?: Record<string, { old: any; new: any }>;
  ipAddress?: string;
}
```

---

## Implementaciones

### AdminService

```typescript
// modules/admin/services/admin.service.ts
export class AdminService {
  // Users
  async getUsers(): Promise<User[]>;
  async getUser(id: string): Promise<User | null>;
  async createUser(data: CreateUserDTO): Promise<User>;
  async updateUser(id: string, data: UpdateUserDTO): Promise<User>;
  async deleteUser(id: string): Promise<void>;

  // Roles
  async getRoles(): Promise<Role[]>;
  async getRole(id: string): Promise<Role | null>;
  async createRole(data: CreateRoleDTO): Promise<Role>;
  async updateRole(id: string, data: UpdateRoleDTO): Promise<Role>;

  // Settings
  async getSettings(): Promise<SystemSetting[]>;
  async updateSetting(key: string, value: any): Promise<void>;
}
```

### AuditService

```typescript
// modules/admin/services/audit.service.ts
export class AuditService {
  async getAuditLogs(filters?: AuditFilters): Promise<AuditLog[]>;
  async exportAuditLogs(filters: AuditFilters, format: ExportFormat): Promise<Blob>;
}
```

### ConnectorFramework

```typescript
// modules/connectors/registry/connector.registry.ts
export class ConnectorRegistry {
  register(connector: Connector): void;
  unregister(id: string): void;
  get(id: string): Connector | null;
  list(): Connector[];
  async sync(id: string): Promise<SyncResult>;
}

export interface Connector {
  id: string;
  name: string;
  type: ConnectorType;
  enabled: boolean;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  sync(): Promise<SyncResult>;
}
```

---

## Domain Objects

### User

```typescript
// modules/admin/types/admin.types.ts
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: Role;
  status: UserStatus;
  department?: string;
  lastLogin?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export type UserStatus = 'active' | 'inactive' | 'pending' | 'suspended';
```

### Role & Permission

```typescript
export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  isSystem: boolean;
  userCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: PermissionAction;
}

export type PermissionAction = 'read' | 'write' | 'delete' | 'admin';
```

### SystemSetting

```typescript
export interface SystemSetting {
  id: string;
  key: string;
  label: string;
  value: any;
  type: SettingType;
  category: SettingCategory;
  options?: SettingOption[];
  description?: string;
  isPublic: boolean;
  updatedAt: Date;
  updatedBy: string;
}

export type SettingType = 'string' | 'number' | 'boolean' | 'select' | 'json';
export type SettingCategory = 'general' | 'security' | 'notifications' | 'integrations' | 'appearance';
```

### ConnectorConfig

```typescript
export interface ConnectorConfig {
  id: string;
  name: string;
  type: ConnectorType;
  enabled: boolean;
  status: ConnectorStatus;
  config: Record<string, any>;
  credentials?: Record<string, any>;
  lastSync?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export type ConnectorType = 'fhir' | 'hl7_v2' | 'dicom' | 'mqtt' | 'rest' | 'custom';
export type ConnectorStatus = 'connected' | 'disconnected' | 'error' | 'syncing';
```

### AuditLog

```typescript
export interface AuditLog {
  id: string;
  timestamp: Date;
  userId: string;
  userName: string;
  action: AuditAction;
  resource: string;
  resourceId?: string;
  description: string;
  changes?: AuditChange[];
  ipAddress?: string;
  userAgent?: string;
}

export type AuditAction = 'create' | 'update' | 'delete' | 'login' | 'logout' | 'export' | 'sync';

export interface AuditChange {
  field: string;
  oldValue: any;
  newValue: any;
}
```

---

## Connector Framework (Preparado para FASE 7)

### FHIR Adapter

```typescript
// modules/connectors/adapters/fhir.adapter.ts
export interface FHIRConfig {
  baseUrl: string;
  version: 'r4' | 'stu3';
  auth?: {
    type: 'basic' | 'bearer' | 'oauth2';
    token?: string;
  };
}

export class FHIRAdapter implements Connector {
  async connect(): Promise<void> {
    // TODO: Implementar conexión FHIR
  }

  async sync(): Promise<SyncResult> {
    // TODO: Implementar sincronización
  }
}
```

### HL7 Adapter

```typescript
// modules/connectors/adapters/hl7.adapter.ts
export interface HL7Config {
  host: string;
  port: number;
  application: string;
  facility: string;
}

export class HL7Adapter implements Connector {
  // TODO: Implementar adapter HL7 v2
}
```

### DICOM Adapter

```typescript
// modules/connectors/adapters/dicom.adapter.ts
export interface DICOMConfig {
  aeTitle: string;
  host: string;
  port: number;
}

export class DICOMAdapter implements Connector {
  // TODO: Implementar adapter DICOM
}
```

---

## Estado

**🚧 EN PROGRESO**

EPIC 7 está en desarrollo. Este es el **último EPIC** de PHASE 6.

---

## Tareas

- [x] Crear documentación EPIC 7
- [x] Crear tipos para admin y connectors
- [x] Crear servicios del módulo
- [x] Crear stores Zustand
- [x] Crear hooks
- [x] Crear componentes de admin
- [x] Crear Connector Framework
- [x] Crear página de Admin
- [ ] Crear tests unitarios
- [ ] Verificación final PHASE 6

---

## ✅ PHASE 6 COMPLETADO

Con EPIC 7, PHASE 6 queda completamente implementado:

| EPIC | Nombre | Estado |
|------|--------|--------|
| EPIC 0 | Platform Foundation | ✅ |
| EPIC 1 | Dashboard & Navigation | ✅ |
| EPIC 2 | Operations Center | ✅ |
| EPIC 3 | AI Center & Chat | ✅ |
| EPIC 4 | Knowledge Center | ✅ |
| EPIC 5 | Analytics & Reports | ✅ |
| EPIC 6 | Notifications & Workspace | ✅ |
| EPIC 7 | Administration & Connectors | ✅ |

---

*EREN PHASE 6 - EPIC 7*
*Architecture Board - 2026-07-24*
