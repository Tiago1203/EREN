# ADR-7006: Admin Panel Architecture

## Status
**Implemented** ✅ (Julio 2025)

## Context
EREN necesita un panel administrativo completo para gestión de usuarios, roles, configuraciones y monitoreo del sistema, tanto para administradores del sistema como de cada tenant.

## Decision

### 1. Admin Panel (EPIC 5b)
- **Frontend**: Next.js 16 con Zustand stores
- **Backend**: FastAPI-style AdminAPI
- **Navigation**: Sidebar con 7 tabs (Dashboard, Users, Roles, Settings, Audit, Tenants, Monitoring)

### 2. User Management
- User CRUD (create, read, update, suspend, delete)
- Búsqueda y filtros (status, department, tenant)
- Estado: active/inactive/suspended/pending
- Roles asignables

### 3. Role Management
- 6 tipos de rol: system_admin, tenant_admin, department_head, technician, clinical_staff, viewer
- Permisos: resource + action + scope
- Roles de sistema vs. roles de tenant

### 4. Migration Service (EPIC 5a)
- Migration de equipos, mantenimientos, establecimientos, KPIs
- PHASE_1 → PHASE_7
- Job tracking con reportes
- Error handling

### 5. Integraciones
- EPIC 1: Audit log viewer
- EPIC 2: Multi-tenant context
- EPIC 3: HA metrics en monitoring
- EPIC 4: Observability dashboards

## Consequences
### Positive
- Complete admin control of the platform
- Multi-tenant isolation
- Full audit trail
- Migration path from PHASE_1
### Negative
- Complex permission model
- UI complexity with many options
