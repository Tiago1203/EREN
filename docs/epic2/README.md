# EREN Epic 2 — Core Business Domain
*Version 1.0 - 2026-07-16*

---

## Purpose

Epic 2 implements the **core business domain** of EREN. Everything that makes EREN a medical device management platform lives here — the biomedical engineers, the incidents they handle, the AI recommendations that guide them, and the knowledge that supports them.

Epic 2 builds on **Epic 0** (architecture) and **Epic 1** (infrastructure). It must be completed before any domain EPIC (3-10) that depends on it.

---

## Relationship to Epic 0

Epic 2 implements the domain decisions documented in Epic 0. Read these **in parallel** with Epic 2:

| Epic 0 Document | What Epic 2 Implements |
|----------------|----------------------|
| `EREN_BOUNDED_CONTEXT_MAP.md` | 4 bounded contexts: Device, Incident, Recommendation, Knowledge |
| `EREN_DOMAIN_OWNERSHIP.md` | Biomedical owns Device, Incident, Recommendation; Clinical owns Knowledge |
| `EREN_DOMAIN_EVENTS_CATALOG.md` | All domain events for Device, Incident, Recommendation, Knowledge |
| `EREN_ERROR_CATALOG.md` | Error codes: DEV-*, INC-*, REC-*, KNW-*, SYS-* |
| `EREN_UBIQUITOUS_LANGUAGE.md` | Terminology enforced in domain entities |
| `EREN_CAPABILITY_MAP.md` | Capabilities: DeviceRegistry, IncidentManagement, RecommendationEngine, KnowledgeRetrieval |
| `EREN_MULTITENANCY_STRATEGY.md` | All entities have tenant_id; RLS enforced |
| `EREN_CONSISTENCY_MODEL.md` | PostgreSQL source of truth; Neo4j/Qdrant derived |

---

## Bounded Contexts

Epic 2 delivers **4 bounded contexts**:

### 1. Device Context
**Owner:** Biomedical Domain

**Aggregate Root:** `Device`
- Represents a physical biomedical device in a hospital
- Lifecycle: registered → active → in_maintenance / calibration_due → out_of_service → decommissioned
- Invariants: valid serial number, valid manufacturer, location specified

**Domain Events:**
- `DeviceRegistered` — fired when device is registered
- `DeviceStatusChanged` — fired on operational status change
- `DeviceLocationChanged` — fired on device relocation

**Capabilities served:** DeviceRegistry, CalibrationTracking, AlarmManagement

**Files:** `core/device/domain/entities/device.py`, `core/device/domain/value_objects/`, `core/device/domain/repositories/`, `core/device/domain/services/`

---

### 2. Incident Context
**Owner:** Biomedical Domain

**Aggregate Root:** `EngineeringIncident`
- Represents a problem reported by a biomedical engineer
- Lifecycle: REPORTED → TRIAGED → OPEN → IN_PROGRESS → RESOLVED → CLOSED
- Sub-aggregate: `Investigation` — tracks actions, evidence, and notes
- Invariants: must have device, must have reporter, cannot close without action, closed incidents immutable

**Domain Events:**
- `IncidentReported`, `IncidentTriaged`, `IncidentOpened`, `IncidentProgressed`, `IncidentEscalated`, `IncidentResolved`, `IncidentClosed`

**Capabilities served:** IncidentManagement, Troubleshooting

**Files:** `core/incident/domain/entities/incident.py`, `core/incident/domain/entities/investigation.py`, `core/incident/domain/value_objects/`, `core/incident/domain/repositories/`, `core/incident/domain/services/`

---

### 3. Recommendation Context
**Owner:** Biomedical Domain + AI Core (shared)

**Aggregate Root:** `AIRecommendation`
- Represents an AI-generated recommendation for an incident
- Lifecycle: GENERATED → PENDING_REVIEW → ACCEPTED / REJECTED / PARTIALLY_ACCEPTED / EXPIRED / SUPERSEDED
- Invariants: valid confidence score, cannot accept expired recommendations, only pending can transition

**Domain Events:**
- `RecommendationCreated`, `RecommendationAcceptedV2`, `RecommendationRejectedV2`, `RecommendationFeedbackReceived`, `FeedbackReceived`

**Capabilities served:** RecommendationEngine, ClinicalDecisionSupport

**Files:** `core/recommendation/domain/entities/recommendation.py`, `core/recommendation/domain/value_objects/`, `core/recommendation/domain/repositories/`, `core/recommendation/domain/services/`

---

### 4. Knowledge Context
**Owner:** Clinical Domain

**Aggregate Root:** `KnowledgeArticle`
- Represents a curated institutional knowledge article
- Used by AI for evidence retrieval
- Invariants: valid content, valid metadata, valid category

**Capabilities served:** KnowledgeRetrieval, EvidenceRetrieval

**Files:** `core/knowledge/domain/entities/knowledge_article.py`, `core/knowledge/domain/value_objects/`, `core/knowledge/domain/repositories/`, `core/knowledge/domain/services/`

---

## Shared Kernel

All bounded contexts share the **Shared Kernel** (`core/shared/`):

```
core/shared/
├── entities/base.py           ← BaseEntity, AggregateRoot
├── primitives/entity_id.py   ← EntityId, IncidentId, DeviceId, KnowledgeId,
│                               EngineerId, TenantId, RecommendationId, etc.
├── value_objects/            ← ValueObject base, Priority, SafetyLevel
├── events/domain.py          ← All shared domain events (frozen dataclasses)
├── errors/domain.py          ← DomainError, EntityNotFound, DuplicateEntity,
│                               InvalidStateTransition, ConcurrencyError,
│                               AuthorizationError, ValidationError, InvariantViolation
└── errors/result.py         ← Result[T, E], Ok, Err (monad)
```

**Key rules:**
- All entity IDs use UUID v7 (time-ordered for database performance)
- All value objects are immutable (frozen=True)
- All aggregates use optimistic locking (version field)
- All domain errors extend DomainError with code + details
- Result[T, E] monad for all repository and service returns

---

## Document Index

| Document | Purpose | Status |
|---------|---------|--------|
| [README.md](./README.md) | This index | READY |
| `core/device/README.md` | Device bounded context | TODO |
| `core/incident/README.md` | Incident bounded context | TODO |
| `core/recommendation/README.md` | Recommendation bounded context | TODO |
| `core/knowledge/README.md` | Knowledge bounded context | TODO |
| `core/shared/README.md` | Shared Kernel | TODO |
| `docs/adr/epic2/` | EPIC 2 ADRs | IN PROGRESS |

---

## Architecture

Epic 2 follows **Hexagonal Architecture** (Ports and Adapters):

```
apps/api/ (application/infrastructure)
  ├── routers/         FastAPI endpoints (no business logic)
  ├── middleware/      Auth, audit, request context
  ├── tasks/           Celery tasks
  ├── infrastructure/
  │   ├── models/      SQLAlchemy ORM models
  │   ├── repositories/ Repository implementations
  │   ├── messaging/   RabbitMQ, Redis cache, Outbox
  │   └── observability/ Logging, tracing
  └── domain/          THIN orchestration only — no business logic here

core/ (domain — framework-independent)
  ├── device/          Device bounded context
  ├── incident/         Incident bounded context
  ├── recommendation/   Recommendation bounded context
  ├── knowledge/        Knowledge bounded context
  └── shared/           Shared Kernel (types only, no infra)
```

**Architectural rule (INVIOLABLE):**
- `core/` is the **ONLY** source of truth for domain logic
- `core/` must remain framework-independent (no FastAPI, no SQLAlchemy imports)
- `apps/api/app/domain/` is strictly orchestration — no business rules
- No entity, repository interface, or business rule in `apps/api/`

---

## Bounded Context Integration

```
Device Context ──publishes──▶ Incident Context ──publishes──▶ Recommendation Context
                                    │
                                    ▼
                              Knowledge Context
```

**Integration pattern:** Domain Events via RabbitMQ (Outbox pattern for reliability)

**Integration rules:**
- Device → Incident: device status changes may trigger incident creation
- Incident → Recommendation: incident report triggers AI recommendation generation
- Incident → Knowledge: incident needs evidence from knowledge base
- Recommendation → Knowledge: recommendations cite evidence from knowledge articles

---

## Epic Dependencies

```
Epic 0 ───────────────────────────────▶ Epic 2
  ├── Bounded Context Map ────────▶ 4 contexts defined
  ├── Domain Ownership ────────────▶ Biomedical owns Device/Incident/Recommendation
  ├── Domain Events Catalog ──────▶ 17 domain events catalogued
  ├── Ubiquitous Language ────────▶ Terminology enforced in entities
  └── Error Catalog ──────────────▶ DEV-*, INC-*, REC-*, KNW-* codes

Epic 1 ───────────────────────────────▶ Epic 2
  ├── PostgreSQL + Alembic ────────▶ Persistence
  ├── Repository Pattern ──────────▶ Repo interfaces in core/
  ├── Unit of Work ────────────────▶ Transactions
  ├── Outbox Pattern ─────────────▶ Reliable event publishing
  └── RLS ────────────────────────▶ Multi-tenant enforcement

Epic 2 ───────────────────────────────▶ Epic 3
  └── All 4 bounded contexts ───────▶ Hospital domain depends on Device/Incident

Epic 2 ───────────────────────────────▶ Epic 4
  └── Recommendation Context ────────▶ AI Core consumes recommendations

Epic 2 ───────────────────────────────▶ Epic 5
  └── Knowledge + Recommendation ──────▶ CD Intelligence builds on both
```

---

## What IS in Epic 2

| Component | Location | Status |
|-----------|----------|--------|
| Device aggregate | `core/device/domain/` | DONE |
| Incident aggregate + Investigation | `core/incident/domain/` | DONE |
| Recommendation aggregate | `core/recommendation/domain/` | DONE |
| Knowledge aggregate | `core/knowledge/domain/` | DONE |
| Shared Kernel | `core/shared/` | DONE |
| Repository implementations | `apps/api/app/infrastructure/repositories/` | DONE |
| SQLAlchemy models | `apps/api/app/infrastructure/models/` | DONE |
| API routers | `apps/api/app/routers/` | DONE |
| Unit tests | `tests/unit/core/` | DONE |
| Migrations | `apps/api/migrations/versions/001-007` | DONE |

---

## What is NOT in Epic 2

| Item | Belongs to | Why |
|------|-----------|------|
| Patient domain | EPIC 5 (Clinical) | Not biomedical |
| Diagnosis domain | EPIC 5 (Clinical) | Not biomedical |
| Hospital entities | EPIC 3 | Not in scope |
| AI reasoning engine | EPIC 4 | Not domain logic |
| External integrations | EPIC 6 | Infrastructure |

---

## Status: COMPLETE ✅

All core domain aggregates, repositories, and integration points are implemented and tested.

Completed in PR #128:
- ✅ WorkOrder aggregate created in `core/incident/domain/work_order/` (FSM, SLA, 7 domain events)
- ✅ Patient + Diagnosis moved to `apps/api/app/clinical/` (EPIC 5 scope)
- ✅ 8 ADRs created in `docs/adr/epic2/` (ADR-0200 to ADR-0207)
- ✅ README concatenations: EPIC 0, 0-Infra, 1, ADR index updated
- ✅ WorkOrder SQLAlchemy repository implemented
- ✅ Knowledge SQLAlchemy repository implemented
- ✅ Recommendation SQLAlchemy repository implemented
- ✅ 228+ unit and integration tests passing

Follow-up work (not blocking EPIC 3):
- [ ] Move Device and WorkOrder events from `apps/api/app/domain/` to `core/shared/events/`
- [ ] Add specification tests for aggregate lifecycle
- [ ] Add integration tests for context-to-context events

**Next:** Epic 3 — Hospital Management Platform 🚧

---

*EREN Epic 2 v1.1*
*Architecture Board - 2026-07-16*
