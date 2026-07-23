# EPIC 11: Knowledge Governance & Lifecycle

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Administrar el ciclo de vida completo del conocimiento biomédico.

---

## Responsabilidad

**Gobernanza, versionado, auditoría, políticas de retención, archivado, rollback y compliance.**

EPIC 11 es responsable de:
- Gestión del ciclo de vida del conocimiento
- Auditoría completa de cambios
- Políticas de retención y cumplimiento
- Rollback y recuperación
- Versionado de snapshots
- Preparación para PHASE 5

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence

### EPICs
- **EPIC 10**: Consume Knowledge Synchronization

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│            EPIC 11: Knowledge Governance & Lifecycle                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     Sync Jobs + Repository (from EPIC 10)              │   │
│  │     Knowledge Assets                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      LIFECYCLE                             │   │
│  │  ├── KnowledgeSnapshot ────────────► Version snapshots    │   │
│  │  ├── InMemoryLifecycleManager ────► Manage lifecycle      │   │
│  │  └── RollbackManager ──────────────► Rollback handling   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      COMPLIANCE                             │   │
│  │  ├── GovernancePolicy ─────────────► Policy model        │   │
│  │  ├── InMemoryComplianceManager ────► Manage compliance   │   │
│  │  └── RetentionEnforcer ────────────► Retention rules    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        AUDIT                                 │   │
│  │  ├── AuditEntry ──────────────────► Audit record          │   │
│  │  ├── InMemoryAuditManager ────────► Manage audit        │   │
│  │  └── AuditReporter ───────────────► Generate reports      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     Governed Knowledge (ready for PHASE 5)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic11_governance/
├── __init__.py                    # Módulo principal
├── lifecycle/                      # Gestión de ciclo de vida
│   └── __init__.py              # LifecycleManager, Snapshot, etc.
├── compliance/                   # Gestión de compliance
│   └── __init__.py            # ComplianceManager, Policy, etc.
└── audit/                      # Gestión de auditoría
    └── __init__.py           # AuditManager, Entry, etc.
```

---

## Componentes

### 1. Lifecycle

| Componente | Descripción |
|------------|-------------|
| `KnowledgeSnapshot` | Snapshot de conocimiento |
| `RollbackPlan` | Plan de rollback |
| `InMemoryLifecycleManager` | Gestor de ciclo de vida |
| `RollbackManager` | Gestor de rollbacks |

**Etapas:**
- `DRAFT` - Borrador
- `REVIEW` - En revisión
- `PUBLISHED` - Publicado
- `ARCHIVED` - Archivado
- `DEPRECATED` - Deprecado

### 2. Compliance

| Componente | Descripción |
|------------|-------------|
| `GovernancePolicy` | Política de gobernanza |
| `ComplianceReport` | Reporte de compliance |
| `InMemoryComplianceManager` | Gestor de compliance |
| `RetentionEnforcer` | Aplicador de retención |

**Políticas de retención:**
- `PERMANENT` - Nunca eliminar
- `STANDARD` - 7 años (clínico)
- `SHORT_TERM` - 2 años
- `REVIEW_REQUIRED` - Requiere revisión

**Estados:**
- `COMPLIANT` - Cumpliendo
- `NON_COMPLIANT` - No cumpliendo
- `PENDING_REVIEW` - Pendiente de revisión
- `EXEMPT` - Exento

### 3. Audit

| Componente | Descripción |
|------------|-------------|
| `AuditEntry` | Entrada de auditoría |
| `AuditQuery` | Consulta de auditoría |
| `InMemoryAuditManager` | Gestor de auditoría |
| `AuditReporter` | Generador de reportes |

**Acciones:**
- `CREATED`, `UPDATED`, `DELETED`
- `PUBLISHED`, `ARCHIVED`, `SUPERSEDED`
- `VIEWED`, `EXPORTED`, `ROLLED_BACK`
- `STATUS_CHANGED`, `POLICY_APPLIED`

---

## Uso

### Gestión de ciclo de vida

```python
from core.PHASE_4.epic11_governance import InMemoryLifecycleManager

manager = InMemoryLifecycleManager()

snapshot = await manager.create_snapshot(
    document_id="doc_1",
    content="Document content..."
)

print(f"Snapshot: {snapshot.snapshot_id}")
```

### Rollback

```python
from core.PHASE_4.epic11_governance import RollbackManager

rollback = RollbackManager(manager)

plan = await rollback.create_plan(
    document_id="doc_1",
    target_snapshot_id="snap_123",
)

if plan.is_safe:
    await rollback.execute_plan(plan)
```

### Compliance

```python
from core.PHASE_4.epic11_governance import InMemoryComplianceManager, GovernancePolicy

manager = InMemoryComplianceManager()

policy = GovernancePolicy(
    policy_id="pol_1",
    name="Clinical Standard",
    retention_policy=RetentionPolicy.STANDARD,
)

await manager.add_policy(policy)
await manager.apply_policy("doc_1", "pol_1")

status = await manager.check_compliance("doc_1")
```

### Auditoría

```python
from core.PHASE_4.epic11_governance import InMemoryAuditManager, AuditAction

manager = InMemoryAuditManager()

entry = await manager.log(
    action=AuditAction.CREATED,
    entity_type="KnowledgeAsset",
    entity_id="asset_1",
    user_id="user_123",
)

entries = await manager.query(AuditQuery(entity_id="asset_1"))
```

---

## Flujo de Gobernanza

```
1. INPUT: Sync Jobs + Repository (from EPIC 10)
          │
          ▼
2. LIFECYCLE: InMemoryLifecycleManager
          │ Create snapshots
          │ Track stages
          │ Manage versions
          │
          ▼
3. COMPLIANCE: InMemoryComplianceManager
          │ Apply policies
          │ Enforce retention
          │ Check compliance
          │
          ▼
4. AUDIT: InMemoryAuditManager
          │ Log all actions
          │ Query entries
          │ Generate reports
          │
          ▼
5. OUTPUT: Governed Knowledge (ready for PHASE 5)
```

---

## Concatenación

```
EPIC 10 ──► EPIC 11 (consume SyncJobs)
FASE 3 ───► EPIC 11 (usa Clinical Intelligence)
EPIC 0 ──► EPIC 11 (usa Foundation types)
EPIC 11 ──► PHASE 5 (Multi-Agent System)
```

---

## Estado

**✅ COMPLETO**

---

## Hacia PHASE 5

EPIC 11 completa PHASE 4 y prepara el conocimiento para PHASE 5:

```
PHASE 4 Output:
├── Knowledge Package
├── Evidence Package
├── Clinical Context
├── Verified Citations
└── Knowledge Repository
         │
         ▼
    PHASE 5
Multi-Agent System
```

---

*EREN PHASE 4 - EPIC 11*
*Architecture Board - 2026-07-23*
