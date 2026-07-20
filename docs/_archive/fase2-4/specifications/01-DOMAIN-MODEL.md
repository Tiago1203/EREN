# EREN - Especificación Técnica Completa
## Fase 1: Domain Model

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  
> **Autor:** Architecture Team

---

## Tabla de Contenidos

1. [Shared Kernel](#1-shared-kernel)
2. [Incident Context](#2-incident-context)
3. [Recommendation Context](#3-recommendation-context)
4. [Device Context](#4-device-context)
5. [Knowledge Context](#5-knowledge-context)
6. [Cross-Context Integration Model](#6-cross-context-integration-model)

---

## Supuestos Declarados

1. **Multi-tenancy:** Todos los aggregates incluyen `tenant_id` como raíz de aislamiento.
2. **Versioning:** Todo aggregate implementa optimistic locking con `version` (int).
3. **Audit:** Todo aggregate incluye `created_at` y `updated_at` (UTC, ISO 8601).
4. **Id Generation:** Los IDs de dominio son UUID v7 (time-ordered) generados en la aplicación.
5. **No Event Sourcing obligatorio:** Los aggregates son snapshots, los eventos son para integración.
6. **Hard Delete prohibido:** Toda entidad usa soft delete (`deleted_at`).
7. **Timestamps:** Fechas en UTC. Display en timezone del tenant.
8. **Naming:** Usamos el idioma del dominio: español para clinical terms, inglés para technical terms.

---

## 1. SHARED KERNEL

### 1.1 Propósito

El Shared Kernel contiene los tipos fundamentales que todos los bounded contexts comparten. Cualquier cambio en el Shared Kernel requiere revisión de todos los equipos de contexto. El Shared Kernel NO contiene lógica de negocio.

### 1.2 Entity ID Types

#### EntityId (Abstract Base)
```
Abstract: Sí
Type: UUID v7 (string representation)
Format: lowercase, no dashes
Example: "0191a2b3c4d5e6f7a8b9c0d1e"
Validation: Must be valid UUID v7
Ordering: Lexicographic by timestamp
```

#### Domain ID Types

| Type | Bounded Context | Prefix | Example |
|------|----------------|--------|---------|
| `TenantId` | Shared | N/A | `0191a2b3...` |
| `UserId` | Shared | `usr_` | `usr_0191a2b3...` |
| `EngineerId` | Shared | `eng_` | `eng_0191a2b3...` |
| `OrganizationId` | Shared | `org_` | `org_0191a2b3...` |
| `LocationId` | Shared | `loc_` | `loc_0191a2b3...` |
| `IncidentId` | Incident | `inc_` | `inc_0191a2b3...` |
| `DeviceId` | Device | `dev_` | `dev_0191a2b3...` |
| `MaintenanceId` | Device | `mnt_` | `mnt_0191a2b3...` |
| `RecommendationId` | Recommendation | `rec_` | `rec_0191a2b3...` |
| `KnowledgeId` | Knowledge | `kno_` | `kno_0191a2b3...` |
| `SessionId` | Session | `ses_` | `ses_0191a2b3...` |
| `ConversationId` | Session | `cnv_` | `cnv_0191a2b3...` |

**Decisión:** El prefijo es solo para legibilidad humana en logs y UI. La validación ocurre en la capa de dominio.

### 1.3 Value Objects del Shared Kernel

#### TenantInfo
```
Attributes:
  - tenant_id: TenantId (required)
  - organization_name: str (required, max 200)
  - industry: str (enum: healthcare, research, veterinary)
  - tier: str (enum: basic, standard, enterprise)
  - max_devices: int (positive)
  - max_users: int (positive)
  - timezone: str (IANA timezone, default "UTC")
  - locale: str (ISO 639-1 + ISO 3166-1, default "en-US")
  - created_at: datetime
  - updated_at: datetime

Equality: tenant_id
Invariants:
  - organization_name cannot be blank
  - max_devices >= 1
  - max_users >= 1
  - timezone must be valid IANA timezone
```

#### AuditInfo (Embedded)
```
Attributes:
  - created_by: EngineerId
  - created_at: datetime
  - updated_by: EngineerId | null
  - updated_at: datetime
  - deleted_by: EngineerId | null
  - deleted_at: datetime | null

Equality: N/A (embedded, no identity)
```

#### Priority
```
Type: Enum Value Object
Values:
  - P1_CRITICAL: "p1_critical" - Patient safety at immediate risk
  - P2_HIGH: "p2_high" - Service disruption, workaround exists
  - P3_MEDIUM: "p3_medium" - Degraded performance, no patient impact
  - P4_LOW: "p4_low" - Cosmetic, informational

Factory Methods:
  - Priority.critical() → P1_CRITICAL
  - Priority.high() → P2_HIGH
  - Priority.medium() → P3_MEDIUM
  - Priority.low() → P4_LOW

Methods:
  - numeric_value(): int  # 1-4 for sorting
  - sla_deadline_hours(): int  # P1=4h, P2=24h, P3=72h, P4=168h
  - escalation_required(): bool  # P1 and P2 require escalation path
```

#### SafetyLevel
```
Type: Enum Value Object
Values:
  - CLASS_A: "class_a" - Low risk (diagnostic equipment)
  - CLASS_B: "class_b" - Low-medium risk (monitoring devices)
  - CLASS_C: "class_c" - Medium-high risk (therapeutic equipment)
  - CLASS_D: "class_d" - High risk (life support systems)

Factory Methods:
  - SafetyLevel.class_a() / .low()
  - SafetyLevel.class_b() / .low_medium()
  - SafetyLevel.class_c() / .medium_high()
  - SafetyLevel.class_d() / .high()

Methods:
  - requires_certified_engineer(): bool  # Class C and D require certification
  - requires_incident_report(): bool  # All classes require incident documentation
  - inspection_frequency_days(): int  # D=30, C=90, B=180, A=365
```

#### Confidence
```
Type: Value Object
Attributes:
  - value: float [0.0, 1.0]
  - level: ConfidenceLevel (enum)
  - calculated_at: datetime
  - method: str  # "ai_model_v1", "rule_based", "heuristic"

Validation:
  - 0.0 <= value <= 1.0
  - value must be within level bounds

Levels:
  - VERY_LOW: [0.0, 0.2)
  - LOW: [0.2, 0.4)
  - MEDIUM: [0.4, 0.6)
  - HIGH: [0.6, 0.8)
  - VERY_HIGH: [0.8, 1.0]

Factory Methods:
  - Confidence.very_low(value, method) → Confidence
  - Confidence.low(value, method) → Confidence
  - Confidence.medium(value, method) → Confidence
  - Confidence.high(value, method) → Confidence
  - Confidence.very_high(value, method) → Confidence

Methods:
  - meets_threshold(minimum: float): bool
  - requires_human_review(): bool  # true if level is LOW or VERY_LOW
  - requires_evidence(): bool  # true if level is MEDIUM or below
  - confidence_band(): str  # "low", "medium", "high"
```

### 1.4 Base Classes

#### ValueObject<T>
```
Purpose: Base for all value objects
Characteristics:
  - Immutable after construction
  - No identity (equality by value)
  - No side effects
  - Self-validating in __post_init__

Contract:
  - Must implement __eq__, __hash__
  - Must implement __post_init__ with validation
  - Should implement __str__ for display
  - Should implement to_primitive() for serialization
```

#### BaseEntity<TId>
```
Purpose: Base for all entities
Characteristics:
  - Has identity (id: TId)
  - Version for optimistic locking
  - Audit trail (created_at, updated_at)
  - Domain events collection
  - Lock mechanism post-construction

Attributes:
  - id: TId (required, kw_only)
  - version: int (default 1, kw_only)
  - created_at: datetime (kw_only, default=now)
  - updated_at: datetime (kw_only, default=now)
  - deleted_at: datetime | null (kw_only, default=null)
  - _pending_events: list[DomainEvent] (private, init=False)

Lock Mechanism:
  - After __post_init__, entity is locked
  - __setattr__ is overridden to prevent mutation
  - Domain methods call _unlock_for_mutation() → mutate → _relock_after_mutation()

Methods:
  - _unlock_for_mutation(): void
  - _relock_after_mutation(): void
  - _assert_version(expected: int): void  # raises ConcurrencyError
  - pop_pending_events(): list[DomainEvent]
  - has_pending_events(): bool
  - is_deleted(): bool
  - mark_deleted(deleted_by: EngineerId): void

Invariant Enforcement:
  - Protected attributes cannot be modified directly
  - Use domain methods only
  - Validation in _validate() called from __post_init__
```

#### AggregateRoot<TId>
```
Purpose: Root of an aggregate
Extends: BaseEntity<TId>

Characteristics:
  - Single entry point for external access
  - All mutations go through the aggregate root
  - Invariants span the entire aggregate
  - Repository persists aggregates as atomic units

Contract:
  - Must define the aggregate boundary
  - Internal entities can only be modified via root methods
  - All invariants must be satisfied on every state transition
```

### 1.5 Result Type

#### Result<T, E>
```
Purpose: Explicit error handling without exceptions in domain layer

Variants:
  - Ok(value: T): Success case
  - Err(error: E): Failure case

Methods:
  - is_ok(): bool
  - is_err(): bool
  - unwrap() -> T  # raises if Err
  - unwrap_or(default: T) -> T
  - unwrap_err() -> E  # raises if Ok
  - map(fn: T -> U) -> Result[U, E]
  - flat_map(fn: T -> Result[U, E]) -> Result[U, E]
  - map_err(fn: E -> F) -> Result[T, F]

Factory:
  - Result.ok(value: T) -> Ok[T, E]
  - Result.err(error: E) -> Err[T, E]
  - Result.safe(fn: Callable) -> Result[T, E]  # wraps exceptions as Err

Usage Pattern:
  Domain methods return Result[T, DomainError]
  Application services unwrap and map to application errors
  Controllers convert to HTTP responses
```

### 1.6 Domain Event Base

#### DomainEvent
```
Purpose: Base for all domain events
Characteristics:
  - Immutable
  - Contains event metadata
  - Serializable to JSON

Attributes:
  - event_id: UUID v7 (unique per event)
  - event_type: str (full class name)
  - occurred_at: datetime (UTC, when event was created)
  - tenant_id: TenantId
  - version: int (event schema version, starts at 1)
  - correlation_id: UUID | null (for tracing related events)
  - causation_id: UUID | null (what triggered this event)

Methods:
  - to_primitive() -> dict
  - from_primitive(data: dict) -> DomainEvent
  - aggregate_version() -> int | null  # version of aggregate at event time

Naming Convention:
  - Past tense, past participle
  - Format: {Entity}{Action}Event
  - Examples: IncidentReportedEvent, DeviceActivatedEvent, RecommendationAcceptedEvent
```

### 1.7 Domain Events del Shared Kernel

```
IncidentReportedEvent
  - incident_id: IncidentId
  - tenant_id: TenantId
  - reported_by: EngineerId
  - device_id: DeviceId | null
  - title: str
  - priority: Priority
  - occurred_at: datetime
  - correlation_id: UUID

IncidentTriagedEvent
  - incident_id: IncidentId
  - tenant_id: TenantId
  - triaged_by: EngineerId
  - assigned_priority: Priority
  - category: str
  - correlation_id: UUID

IncidentOpenedEvent
  - incident_id: IncidentId
  - tenant_id: TenantId
  - opened_by: EngineerId
  - correlation_id: UUID

IncidentProgressedEvent
  - incident_id: IncidentId
  - tenant_id: TenantId
  - progressed_by: EngineerId
  - progress_note: str
  - next_action: str | null
  - correlation_id: UUID

IncidentEscalatedEvent
  - incident_id: IncidentId
  - tenant_id: TenantId
  - escalated_by: EngineerId
  - reason: str
  - escalated_to: str
  - previous_priority: Priority
  - new_priority: Priority
  - correlation_id: UUID

IncidentResolvedEvent
  - incident_id: IncidentId
  - tenant_id: TenantId
  - resolved_by: EngineerId
  - resolution_type: str
  - resolution_summary: str
  - resolution_details: str
  - correlation_id: UUID

IncidentClosedEvent
  - incident_id: IncidentId
  - tenant_id: TenantId
  - closed_by: EngineerId
  - closure_note: str | null
  - duration_hours: float
  - correlation_id: UUID

RecommendationGeneratedEvent
  - recommendation_id: RecommendationId
  - tenant_id: TenantId
  - incident_id: IncidentId | null
  - category: str
  - urgency: str
  - confidence: Confidence
  - generated_by: str (AI model identifier)
  - correlation_id: UUID

RecommendationAcceptedEvent
  - recommendation_id: RecommendationId
  - tenant_id: TenantId
  - accepted_by: EngineerId
  - reason: str | null
  - correlation_id: UUID

RecommendationRejectedEvent
  - recommendation_id: RecommendationId
  - tenant_id: TenantId
  - rejected_by: EngineerId
  - reason: str
  - correlation_id: UUID

DeviceRegisteredEvent
  - device_id: DeviceId
  - tenant_id: TenantId
  - registered_by: EngineerId
  - device_type: str
  - serial_number: str
  - correlation_id: UUID

DeviceStatusChangedEvent
  - device_id: DeviceId
  - tenant_id: TenantId
  - changed_by: EngineerId
  - previous_status: str
  - new_status: str
  - reason: str | null
  - correlation_id: UUID

DeviceLocationChangedEvent
  - device_id: DeviceId
  - tenant_id: TenantId
  - changed_by: EngineerId
  - previous_location: str
  - new_location: str
  - correlation_id: UUID
```

### 1.8 Errors del Shared Kernel

```
DomainError (abstract base)
  - message: str
  - code: str (machine-readable)
  - details: dict | null

ValidationError
  - code: "VALIDATION_ERROR"
  - field: str
  - constraint: str

EntityNotFoundError
  - code: "ENTITY_NOT_FOUND"
  - entity_type: str
  - entity_id: str

DuplicateEntityError
  - code: "DUPLICATE_ENTITY"
  - entity_type: str
  - identifier: str

InvalidStateTransitionError
  - code: "INVALID_STATE_TRANSITION"
  - entity_type: str
  - current_state: str
  - attempted_state: str

ConcurrencyError
  - code: "CONCURRENCY_ERROR"
  - entity_type: str
  - expected_version: int
  - actual_version: int

InvariantViolationError
  - code: "INVARIANT_VIOLATION"
  - entity_type: str
  - invariant_name: str
  - violation_description: str

AuthorizationError
  - code: "AUTHORIZATION_ERROR"
  - action: str
  - resource: str
  - required_permission: str
```

---

## 2. INCIDENT CONTEXT

### 2.1 Propósito del Contexto

Gestionar el ciclo de vida completo de incidentes de ingeniería clínica desde la detección hasta la resolución, incluyendo investigación, escalamiento y cierre formal con auditoría completa para cumplimiento regulatorio.

### 2.2 Aggregate: EngineeringIncident

#### Identidad
```
Aggregate Root: EngineeringIncident
ID: IncidentId (prefix: inc_)
Tenant: TenantId (required)
```

#### Atributos

| Atributo | Tipo | Requerido | Mutable | Descripción |
|----------|------|----------|---------|-------------|
| `id` | IncidentId | Sí | No | Identificador único |
| `tenant_id` | TenantId | Sí | No | Aislamiento multi-tenant |
| `version` | int | Sí | Sí | Optimistic locking |
| `title` | str | Sí | Sí | Título breve del incidente (max 200 chars) |
| `description` | str | Sí | Sí | Descripción detallada (max 5000 chars) |
| `status` | IncidentStatus | Sí | Sí | Estado actual |
| `priority` | Priority | Sí | Sí | Prioridad P1-P4 |
| `safety_level` | SafetyLevel | Sí | No | Clasificación de riesgo |
| `category` | IncidentCategory | Sí | Sí | Categorización clínica |
| `device_id` | DeviceId | No | Sí | Dispositivo relacionado (nullable) |
| `device_name` | str | No | Sí | Nombre descriptivo del dispositivo |
| `device_location` | str | No | Sí | Ubicación física del dispositivo |
| `patient_impact` | PatientImpact | No | Sí | Impacto en paciente si aplica |
| `occurred_at` | datetime | Sí | No | Cuándo ocurrió |
| `detected_at` | datetime | Sí | No | Cuándo se detectó |
| `reported_by` | EngineerId | Sí | No | Quién lo reportó |
| `assigned_to` | EngineerId | No | Sí | Ingeniero asignado (nullable) |
| `assigned_at` | datetime | No | Sí | Cuándo se asignó |
| `resolved_at` | datetime | No | Sí | Cuándo se resolvió |
| `closed_at` | datetime | No | Sí | Cuándo se cerró |
| `resolution` | Resolution | No | Sí | Resolución formal (nullable) |
| `escalation_path` | list[EngineerId] | No | Sí | Cadena de escalamiento |
| `symptoms` | list[Symptom] | No | Sí | Síntomas reportados |
| `tags` | tuple[str, ...] | No | Sí | Tags para búsqueda (max 20) |
| `metadata` | dict | No | Sí | Datos adicionales (max 50 keys) |
| `related_incident_ids` | tuple[IncidentId, ...] | No | Sí | Incidentes relacionados |
| `created_at` | datetime | Sí | No | Auditoría |
| `updated_at` | datetime | Sí | Sí | Auditoría |
| `deleted_at` | datetime | No | No | Soft delete |

#### Factory Method
```
EngineeringIncident.create(
    tenant_id: TenantId,
    title: str,
    description: str,
    priority: Priority,
    safety_level: SafetyLevel,
    category: IncidentCategory,
    reported_by: EngineerId,
    device_id: DeviceId | None,
    device_name: str | None,
    device_location: str | None,
    patient_impact: PatientImpact | None,
    occurred_at: datetime,
    detected_at: datetime,
    tags: list[str] | None,
    correlation_id: UUID | None,
) -> Result[EngineeringIncident, ValidationError]
```

#### Invariants (Reglas de Negocio Inviolables)

1. **I-IN-001:** `reported_at` <= `occurred_at` + 24 hours
2. **I-IN-002:** No puede existir un `Incident` con `status=active` si `priority=P1` sin `assigned_to`
3. **I-IN-003:** Un `Incident` solo puede resolverse si `status ∈ {active, escalated}`
4. **I-IN-004:** Un `Incident` solo puede cerrarse si `status = resolved`
5. **I-IN-005:** El campo `device_id` debe referenciar un `Device` activo del mismo `tenant_id`
6. **I-IN-006:** Si `safety_level = CLASS_D`, entonces `priority` debe ser `P1_CRITICAL` o `P2_HIGH`
7. **I-IN-007:** No puede haber dos `Incidents` con `status ∈ {active, escalated, triaged}` para el mismo `device_id` a menos que sean de diferentes categorías
8. **I-IN-008:** `symptoms` no puede estar vacío si `patient_impact` indica `harm_occurred`
9. **I-IN-009:** `resolution.resolution_type` debe ser compatible con `category`
10. **I-IN-010:** Un `Incident` no puede ser reabierto si `closed_at` + 30 days < now

#### Business Rules

| BR-IN-001 | Priorización Automática |
|-----------|------------------------|
| **Regla** | Si `patient_impact = harm_occurred`, forzar `priority = P1_CRITICAL` |
| **Condición** | Solo si `priority < P1_CRITICAL` |
| **Acción** | Auto-upgrade de prioridad con logged event |

| BR-IN-002 | Asignación por Spécialité |
|-----------|---------------------------|
| **Regla** | `Incident` con `category = life_support` debe asignarse a engineer con `certification = clinical_life_support` |
| **Condición** | Si `assigned_to` is null y `status = triaged` |
| **Acción** | Suggest assignment based on engineer certifications |

| BR-IN-003 | SLA Tracking |
|-----------|-------------|
| **Regla** | Si `updated_at - occurred_at > priority.sla_deadline_hours()`, marcar como breached |
| **Condición** | Estado `active` o `escalated` |
| **Acción** | Publish IncidentSlaBreachedEvent |

### 2.3 State Machine: IncidentStatus

```
States: REPORTED, TRIAGED, ACTIVE, ESCALATED, RESOLVED, CLOSED

Diagram:
┌──────────┐
│ REPORTED │
└────┬─────┘
     │ triage() ───────────────────────────────────────┐
     │ resolve() [with auto-triage flag]               │
     └──────────────────────────────────────────────────│
     │                                                     │
     ▼                                                     ▼
┌──────────┐    open()    ┌───────┐    escalate()    ┌──────────┐
│ TRIAGED  │─────────────►│ ACTIVE│◄────────────────│ ESCALATED│
└────┬─────┘              └───┬───┘                  └────┬─────┘
     │                       │                              │
     │                       │ resolve()                     │ resolve()
     │                       ▼                              ▼
     │                  ┌──────────┐                   ┌──────────┐
     │                  │ RESOLVED│                   │ RESOLVED │
     │                  └────┬────┘                   └────┬─────┘
     │                       │                              │
     │                       │ close()                      │ close()
     │                       ▼                              ▼
     │                  ┌──────────┐                   ┌──────────┐
     └──────────────────►│  CLOSED  │                   │  CLOSED  │
                        └──────────┘                   └──────────┘

Transitions:

| From       | To         | Trigger         | Guard Conditions           | Side Effects                        |
|------------|------------|-----------------|----------------------------|-------------------------------------|
| REPORTED   | TRIAGED    | triage()        | priority, category set     | IncidentTriagedEvent                |
| REPORTED   | ACTIVE     | triage()        | auto_open=True flag        | IncidentTriagedEvent + IncidentOpenedEvent |
| REPORTED   | RESOLVED   | triage()        | quick_resolution=True      | IncidentTriagedEvent + IncidentResolvedEvent |
| TRIAGED    | ACTIVE     | open()          | assigned_to != null        | IncidentOpenedEvent                 |
| ACTIVE     | ESCALATED  | escalate()      | escalation_path not empty  | IncidentEscalatedEvent               |
| ACTIVE     | RESOLVED   | resolve()       | resolution != null          | IncidentResolvedEvent                |
| ESCALATED  | ACTIVE     | deescalate()    | human_review_complete=True | IncidentDeescalatedEvent             |
| ESCALATED  | RESOLVED   | resolve()       | resolution != null          | IncidentResolvedEvent                |
| RESOLVED   | ACTIVE     | reopen()        | I-IN-010 satisfied         | IncidentReopenedEvent                 |
| RESOLVED   | CLOSED     | close()         | none                       | IncidentClosedEvent                  |
| ACTIVE     | RESOLVED   | resolve()       | resolution != null          | IncidentResolvedEvent                |

Invalid Transitions (must raise InvalidStateTransitionError):
- REPORTED → ESCALATED (must be TRIAGED or ACTIVE first)
- REPORTED → RESOLVED (unless quick_resolution)
- TRIAGED → ESCALATED (must be ACTIVE first)
- TRIAGED → CLOSED (must go through RESOLVED)
- ACTIVE → TRIAGED (no backward transitions)
- RESOLVED → TRIAGED (no backward transitions)
- CLOSED → any (terminal state)
```

#### IncidentStatus Value Object

```
Type: Enum
Values:
  - REPORTED: "reported"
  - TRIAGED: "triaged"
  - ACTIVE: "active"
  - ESCALATED: "escalated"
  - RESOLVED: "resolved"
  - CLOSED: "closed"

Methods:
  - is_open(): bool  # ACTIVE or ESCALATED
  - is_terminal(): bool  # CLOSED only
  - is_workable(): bool  # ACTIVE, ESCALATED, TRIAGED
  - can_be_resolved(): bool  # ACTIVE, ESCALATED
  - can_be_escalated(): bool  # ACTIVE
  - can_be_reopened(): bool  # RESOLVED (within SLA)
```

### 2.4 Sub-Aggregate: Investigation

#### Identidad
```
Entity: Investigation
ID: InvestigationId (prefix: inv_)
Parent Aggregate: EngineeringIncident (owns lifecycle)
```

#### Atributos

| Atributo | Tipo | Requerido | Mutable |
|----------|------|----------|---------|
| `id` | InvestigationId | Sí | No |
| `incident_id` | IncidentId | Sí | No |
| `tenant_id` | TenantId | Sí | No |
| `status` | InvestigationStatus | Sí | Sí |
| `phase` | InvestigationPhase | Sí | Sí |
| `lead_investigator` | EngineerId | Sí | Sí |
| `started_at` | datetime | Sí | No |
| `findings` | list[Finding] | No | Sí |
| `actions` | list[Action] | No | Sí |
| `messages` | list[ConversationMessage] | No | Sí |
| `root_cause` | RootCause | No | Sí |
| `completed_at` | datetime | No | Sí |
| `version` | int | Sí | Sí |

#### InvestigationPhase
```
Values:
  - INITIAL_ASSESSMENT: "initial_assessment"
  - DATA_COLLECTION: "data_collection"
  - ANALYSIS: "analysis"
  - ROOT_CAUSE_IDENTIFICATION: "root_cause_identification"
  - CORRECTIVE_ACTION: "corrective_action"
  - VERIFICATION: "verification"
  - CLOSED: "closed"
```

#### Finding
```
Type: Entity (within Investigation)
Attributes:
  - finding_id: FindingId
  - finding_type: enum(physical, operational, environmental, software, procedural)
  - description: str (max 2000)
  - severity: enum(low, medium, high, critical)
  - discovered_at: datetime
  - discovered_by: EngineerId
  - evidence: list[Evidence]
```

#### Action
```
Type: Value Object
Attributes:
  - action_type: ActionType (enum: repair, replacement, adjustment, calibration, software_update, procedure_change, training, monitoring)
  - description: str (max 1000)
  - assigned_to: EngineerId
  - due_date: datetime
  - status: ActionStatus (enum: pending, in_progress, completed, deferred, cancelled)
  - completed_at: datetime | null
  - result: ActionResult | null
  - priority: Priority
```

### 2.5 Value Objects del Incident Context

#### IncidentCategory
```
Type: Enum Value Object
Values:
  - HARDWARE_FAILURE: "hardware_failure"
  - SOFTWARE_FAULT: "software_fault"
  - CALIBRATION_ISSUE: "calibration_issue"
  - SAFETY_ALERT: "safety_alert"
  - PERFORMANCE_DEGRADATION: "performance_degradation"
  - LIFE_SUPPORT: "life_support"
  - DIAGNOSTIC_ERROR: "diagnostic_error"
  - NETWORK_CONNECTIVITY: "network_connectivity"
  - POWER_SUPPLY: "power_supply"
  - ENVIRONMENTAL: "environmental"
  - PROCEDURAL: "procedural"
  - OTHER: "other"

Methods:
  - is_safety_critical(): bool  # LIFE_SUPPORT, SAFETY_ALERT
  - requires_specialist(): bool  # LIFE_SUPPORT, CALIBRATION_ISSUE
  - sla_category(): str  # Maps to SLA tier
```

#### PatientImpact
```
Type: Enum Value Object
Values:
  - NO_IMPACT: "no_impact" - No patient involvement
  - MONITORING_AFFECTED: "monitoring_affected" - Monitoring disrupted
  - TREATMENT_DELAYED: "treatment_delayed" - Treatment rescheduled
  - TREATMENT_INTERRUPTED: "treatment_interrupted" - Active treatment stopped
  - HARM_NEAR_MISS: "harm_near_miss" - Potential harm avoided
  - HARM_OCCURRED: "harm_occurred" - Patient harm documented

Methods:
  - severity_score(): int  # 0-5
  - requires_documentation(): bool  # true if severity >= 2
  - mandatory_escalation(): bool  # true if severity >= 3
```

#### Symptom
```
Type: Value Object
Attributes:
  - symptom_id: UUID
  - description: str (max 500)
  - category: SymptomCategory (enum: mechanical, electrical, software, user_error, environmental, unknown)
  - severity: SymptomSeverity (enum: minor, moderate, severe, critical)
  - duration_minutes: int | null
  - first_observed_at: datetime
  - last_observed_at: datetime | null
  - frequency: SymptomFrequency (enum: once, intermittent, continuous)
  - reproducible: bool
  - workarounds: tuple[str, ...]
```

#### Resolution
```
Type: Value Object
Attributes:
  - resolution_id: UUID
  - resolution_type: ResolutionType (enum: repaired, replaced, calibrated, software_fixed, procedure_changed, training_provided, monitoring_enhanced, root_cause_eliminated, workaround_implemented, no_action_required)
  - summary: str (max 500)  # One-line summary for reports
  - details: str (max 5000)  # Detailed explanation
  - actions_taken: tuple[str, ...]  # List of action descriptions
  - parts_replaced: tuple[PartInfo, ...]  # If applicable
  - downtime_minutes: int
  - cost: Money | null  # If tracked
  - verified_by: EngineerId
  - verified_at: datetime | null
  - recurrence_prevention: tuple[str, ...]  # Steps to prevent recurrence
```

### 2.6 Domain Service: IncidentService

```
Responsibilities:
  - Coordinate cross-aggregate operations
  - Enforce business rules spanning multiple entities
  - Provide query operations that cross entity boundaries

Methods:

  create_incident(cmd: CreateIncidentCommand) -> Result[EngineeringIncident, IncidentError]
    Steps:
      1. Validate device exists and is active (via DeviceRepository)
      2. Check for duplicate incidents (BR-IN-007)
      3. Apply priority auto-upgrade (BR-IN-001)
      4. Create aggregate
      5. Persist via IncidentRepository
      6. Publish IncidentReportedEvent
      7. If auto-assign rules match, call assign_incident()
      8. Return Result

  triage_incident(cmd: TriageIncidentCommand) -> Result[EngineeringIncident, IncidentError]
    Steps:
      1. Load incident by ID
      2. Validate transition is valid
      3. Apply BR-IN-001 if applicable
      4. Validate category-specific rules (BR-IN-002)
      5. Update status
      6. Persist
      7. Publish IncidentTriagedEvent
      8. If auto_open, call open_incident()

  assign_incident(incident_id, engineer_id) -> Result[EngineeringIncident, IncidentError]
    Steps:
      1. Load incident
      2. Validate engineer exists and has required certifications (BR-IN-002)
      3. Update assigned_to
      4. Persist
      5. Publish IncidentAssignedEvent (new event)
      6. Return Result

  escalate_incident(cmd: EscalateIncidentCommand) -> Result[EngineeringIncident, IncidentError]
    Steps:
      1. Load incident
      2. Validate escalation_path is not empty
      3. Validate current_status allows escalation
      4. Update status, priority if needed
      5. Persist
      6. Publish IncidentEscalatedEvent
      7. Notify escalation_path via NotificationService
      8. Return Result

  resolve_incident(cmd: ResolveIncidentCommand) -> Result[EngineeringIncident, IncidentError]
    Steps:
      1. Load incident
      2. Validate status allows resolution
      3. Validate resolution details
      4. Create Investigation if not exists
      5. Update status, set resolved_at
      6. Persist
      7. Publish IncidentResolvedEvent
      8. If linked to open Recommendations, trigger review
      9. Return Result

  get_incident_summary(incident_id) -> Result[IncidentSummary, IncidentError]
    Aggregates data from:
      - Incident aggregate
      - Investigation sub-aggregate
      - Linked Recommendations
      - Linked Knowledge Articles
      - Device information (from DeviceContext)

  search_incidents(query: IncidentSearchQuery) -> Result[list[EngineeringIncident], IncidentError]
    Filters:
      - tenant_id (required)
      - status (optional)
      - priority (optional)
      - category (optional)
      - date_range (optional)
      - device_id (optional)
      - assigned_to (optional)
      - tags (optional, fuzzy match)
```

### 2.7 Repository Interface: IncidentRepository

```
Methods:

  async save(incident: EngineeringIncident) -> Result[EngineeringIncident, RepositoryError]
    Behavior:
      - Upsert operation
      - Optimistic locking via version
      - Raises ConcurrencyError if version mismatch
      - Publishes pending domain events
      - Writes to outbox table atomically

  async get_by_id(incident_id: IncidentId, tenant_id: TenantId) -> Result[EngineeringIncident | None, RepositoryError]

  async get_by_status(
    tenant_id: TenantId,
    status: IncidentStatus | list[IncidentStatus],
    limit: int = 100,
    offset: int = 0
  ) -> Result[list[EngineeringIncident], RepositoryError]

  async get_by_device(
    tenant_id: TenantId,
    device_id: DeviceId,
    include_resolved: bool = false
  ) -> Result[list[EngineeringIncident], RepositoryError]

  async get_by_assignee(
    tenant_id: TenantId,
    engineer_id: EngineerId,
    status_filter: list[IncidentStatus] | None = None
  ) -> Result[list[EngineeringIncident], RepositoryError]

  async search(
    tenant_id: TenantId,
    query: str,  # Full-text search on title, description
    filters: IncidentSearchFilters | None = None,
    pagination: Pagination
  ) -> Result[SearchResult[EngineeringIncident], RepositoryError]

  async get_open_incidents_by_priority(
    tenant_id: TenantId
  ) -> Result[list[EngineeringIncident], RepositoryError]
    # Ordered by priority (P1 first), then by occurred_at

  async get_active_incidents_count(tenant_id: TenantId) -> Result[int, RepositoryError]

  async get_sla_breached_incidents(tenant_id: TenantId) -> Result[list[EngineeringIncident], RepositoryError]

  async get_incident_history(
    incident_id: IncidentId,
    tenant_id: TenantId
  ) -> Result[list[DomainEvent], RepositoryError]
    # Reconstructs incident from event history (for event sourcing backup)
```

---

## 3. RECOMMENDATION CONTEXT

### 3.1 Propósito del Contexto

Generar, gestionar y rastrear recomendaciones de IA para incidentes de ingeniería clínica. Cada recomendación incluye explicabilidad completa, confianza calculada, linaje de evidencia y mecanismo de feedback para mejora continua del modelo.

### 3.2 Aggregate: AIRecommendation

#### Identidad
```
Aggregate Root: AIRecommendation
ID: RecommendationId (prefix: rec_)
Tenant: TenantId
```

#### Atributos

| Atributo | Tipo | Requerido | Mutable | Descripción |
|----------|------|----------|---------|-------------|
| `id` | RecommendationId | Sí | No | Identificador único |
| `tenant_id` | TenantId | Sí | No | Aislamiento multi-tenant |
| `version` | int | Yes | Yes | Optimistic locking |
| `incident_id` | IncidentId | No | No | Incidente relacionado |
| `title` | str | Sí | No | Título de la recomendación (max 200) |
| `description` | str | Yes | No | Descripción detallada (max 3000) |
| `category` | RecommendationCategory | Yes | No | Categorización |
| `urgency` | RecommendationUrgency | Yes | No | Urgencia clínica |
| `status` | RecommendationStatus | Yes | Yes | Estado actual |
| `confidence` | Confidence | Yes | No | Nivel de confianza |
| `explanation` | Explanation | Yes | No | Explicabilidad completa |
| `actions` | tuple[RecommendedAction, ...] | Yes | No | Pasos recomendados |
| `contraindications` | tuple[Contraindication, ...] | No | No | Warnings o contraindicaciones |
| `evidence` | tuple[Evidence, ...] | Yes | No | Evidencia base |
| `sources` | tuple[Source, ...] | Yes | No | Fuentes de conocimiento |
| `device_ids` | tuple[DeviceId, ...] | No | No | Dispositivos relacionados |
| `knowledge_article_ids` | tuple[KnowledgeId, ...] | No | No | Artículos relevantes |
| `generated_by` | str | Yes | No | Identificador del modelo AI |
| `generation_method` | str | Yes | No | Método: "rule_based", "ai_model", "hybrid" |
| `prompt_version` | str | Yes | No | Versión del prompt usado |
| `model_version` | str | Yes | No | Versión del modelo AI |
| `accepted_by` | EngineerId | No | Yes | Quién aceptó |
| `accepted_at` | datetime | No | Yes | Cuándo se aceptó |
| `rejected_by` | EngineerId | No | Yes | Quién rechazó |
| `rejected_at` | datetime | No | Yes | Cuándo se rechazó |
| `rejection_reason` | RejectionReason | No | Yes | Razón del rechazo |
| `feedback` | Feedback | No | Yes | Feedback del clínico |
| `outcome` | RecommendationOutcome | No | Yes | Resultado tras ejecución |
| `execution_started_at` | datetime | No | Yes | Cuándo se empezó a ejecutar |
| `completed_at` | datetime | No | Yes | Cuándo se completó |
| `expires_at` | datetime | No | No | Cuándo expira la recomendación |
| `created_at` | datetime | Yes | No | Auditoría |
| `updated_at` | datetime | Yes | Yes | Auditoría |
| `deleted_at` | datetime | No | No | Soft delete |

#### Factory Method
```
AIRecommendation.generate(
    tenant_id: TenantId,
    incident_id: IncidentId | None,
    title: str,
    description: str,
    category: RecommendationCategory,
    urgency: RecommendationUrgency,
    confidence: Confidence,
    explanation: Explanation,
    actions: list[RecommendedAction],
    evidence: list[Evidence],
    sources: list[Source],
    generated_by: str,
    generation_method: str,
    prompt_version: str,
    model_version: str,
    device_ids: list[DeviceId] | None = None,
    knowledge_article_ids: list[KnowledgeId] | None = None,
    contraindications: list[Contraindication] | None = None,
    correlation_id: UUID | None = None,
) -> Result[AIRecommendation, ValidationError]
```

#### Invariants

1. **I-REC-001:** Si `confidence.level = VERY_LOW`, `status` no puede ser `pending` por más de 1 hora
2. **I-REC-002:** Una recomendación no puede estar `accepted` y `rejected` simultáneamente
3. **I-REC-003:** `explanation.reasoning_chain` no puede estar vacío
4. **I-REC-004:** `evidence` debe contener al menos una evidencia con `type = device_data` si `category = HARDWARE`
5. **I-REC-005:** Si `urgency = CRITICAL`, `confidence` debe ser al menos `MEDIUM` o tener `human_review_required = true`
6. **I-REC-006:** `expiration` solo aplica si `status = pending`
7. **I-REC-007:** Una recomendación `rejected` no puede ser `accepted` sin pasar por `pending` de nuevo

### 3.3 State Machine: RecommendationStatus

```
States: GENERATED, PENDING, ACCEPTED, REJECTED, ACTIVE, COMPLETED, EXPIRED, CANCELLED

Diagram:
┌───────────┐
│ GENERATED │ (transient, auto → PENDING)
└─────┬─────┘
      │
      ▼
┌──────────┐    accept()     ┌──────────┐
│  PENDING │────────────────►│ ACCEPTED │
└────┬─────┘                 └────┬─────┘
     │                            │ start_execution()
     │ reject()                   ▼
     │                            ┌──────────┐
     │                       ┌────│  ACTIVE  │
     ▼                       │    └────┬─────┘
┌──────────┐                  │         │ complete_execution()
│ REJECTED │ (terminal or     │         ▼
└────┬─────┘  re-generate)   │    ┌──────────┐
     │                        │    │ COMPLETED│
     │ regenerate()           │    └──────────┘
     │ (returns new rec)     │
     └────────────────────────┘

Alternative flows:
- PENDING → CANCELLED (system cancellation, e.g., incident closed)
- PENDING → EXPIRED (timeout reached)
- ACTIVE → CANCELLED (incident resolved without execution)
```

### 3.4 Explainability Model

#### Explanation
```
Type: Value Object (Embedded)
Attributes:
  - reasoning_chain: ReasoningChain
  - confidence_breakdown: ConfidenceBreakdown
  - safety_classification: SafetyClassification
  - provenance: Provenance
  - citations: tuple[Citation, ...]
  - caveats: tuple[str, ...]  # Important limitations
  - confidence_score: float  # Aggregated confidence
  - human_review_required: bool
  - review_reason: str | null  # Why human review is required
  - ai_disclosure: str  # Required disclosure text for AI-generated content

Methods:
  - to_clinical_format() -> ClinicalExplanation  # Formatted for clinicians
  - to_engineering_format() -> EngineeringExplanation  # Formatted for engineers
  - to_audit_format() -> AuditExplanation  # Formatted for regulators
```

#### ReasoningChain
```
Type: Value Object
Attributes:
  - steps: tuple[ReasoningStep, ...]  # Ordered list of reasoning steps
  - total_confidence: float
  - confidence_trend: str  # "increasing", "stable", "decreasing"
  - alternative_paths_considered: tuple[str, ...]  # Other hypotheses considered
  - confidence_factors: tuple[ConfidenceFactor, ...]

Validation:
  - steps must be in temporal order
  - Each step must reference evidence or prior step
  - Chain must be coherent (conclusion must follow from steps)
```

#### ReasoningStep
```
Type: Value Object
Attributes:
  - step_number: int (1-indexed)
  - description: str (max 500)
  - logic: str (max 1000)  # The logical reasoning
  - evidence_references: tuple[str, ...]  # IDs of evidence used
  - prior_step_references: tuple[int, ...]  # Step numbers referenced
  - confidence_contribution: float  # How much this step contributes to total
  - is_key_step: bool  # Critical step in the chain
  - is_controversial: bool  # Step that may be disputed
  - alternative_explanations: tuple[str, ...]  # Alternative interpretations
```

#### Evidence
```
Type: Value Object
Attributes:
  - evidence_id: UUID
  - evidence_type: EvidenceType (enum: device_data, incident_history, knowledge_article, clinical_guideline, manufacturer_spec, sensor_reading, maintenance_log, user_report, test_result)
  - content: str (max 2000)
  - source: Source
  - relevance_score: float [0.0, 1.0]
  - reliability_score: float [0.0, 1.0]  # Based on source credibility
  - temporal_relevance: str  # "current", "recent", "historical"
  - device_id: DeviceId | null
  - captured_at: datetime
  - metadata: dict | null

Methods:
  - is_reliable(): bool  # reliability_score >= 0.7
  - is_current(): bool  # temporal_relevance != "historical"
  - is_strong(): bool  # is_reliable() and is_current() and relevance_score >= 0.7
```

#### Source
```
Type: Value Object
Attributes:
  - source_type: SourceType (enum: internal_db, knowledge_base, manufacturer_docs, clinical_guidelines, external_expert, ai_model, sensor, user_input)
  - source_id: str
  - source_name: str
  - source_url: str | null
  - last_updated: datetime | null
  - version: str | null
  - credibility: CredibilityLevel (enum: verified, curated, community, inferred)
  - access_method: str  # "direct", "rag_retrieval", "api", "manual"
```

#### Citation
```
Type: Value Object
Attributes:
  - citation_id: UUID
  - source: Source
  - quoted_text: str | null
  - page_reference: str | null
  - access_date: datetime
  - relevance_to_recommendation: float [0.0, 1.0]
  - extracted_at: datetime

Methods:
  - format_apa() -> str
  - format_hospital_style() -> str  # Hospital-specific citation format
```

#### SafetyClassification
```
Type: Value Object
Attributes:
  - safety_class: SafetyClass (enum: SAFE, CAUTION, WARNING, CRITICAL, UNSAFE)
  - risk_factors: tuple[str, ...]
  - mitigation_steps: tuple[str, ...]
  - monitoring_requirements: tuple[str, ...]
  - reversibility: str  # "full", "partial", "none"
  - time_sensitivity: str  # "immediate", "within_hours", "within_days", "flexible"
  - alternative_approaches: tuple[str, ...]

Methods:
  - requires_verbal_confirmation(): bool  # true if class >= CAUTION
  - requires_sign_off(): bool  # true if class >= WARNING
  - get_waiting_period(): int  # Hours to wait before action
```

### 3.5 Value Objects del Recommendation Context

#### RecommendationCategory
```
Values:
  - HARDWARE_REPAIR: "hardware_repair"
  - CALIBRATION: "calibration"
  - SOFTWARE_UPDATE: "software_update"
  - REPLACEMENT: "replacement"
  - PREVENTIVE_MAINTENANCE: "preventive_maintenance"
  - PROCEDURE_CHANGE: "procedure_change"
  - MONITORING_ENHANCEMENT: "monitoring_enhancement"
  - ESCALATION: "escalation"
  - INVESTIGATION: "investigation"
  - NO_ACTION: "no_action"

Methods:
  - is_invasive(): bool  # HARDWARE_REPAIR, REPLACEMENT
  - requires_downtime(): bool
  - estimated_duration_minutes(): int | null
```

#### RecommendationUrgency
```
Values:
  - LOW: "low"  # Can wait for next maintenance window
  - NORMAL: "normal"  # Within 72 hours
  - HIGH: "high"  # Within 24 hours
  - CRITICAL: "critical"  # Immediate action required

Methods:
  - response_deadline_minutes(): int
  - escalation_path(): list[str]  # Who to notify at each urgency
```

#### ConfidenceBreakdown
```
Type: Value Object
Attributes:
  - overall_score: float [0.0, 1.0]
  - level: ConfidenceLevel
  - data_quality_score: float
  - model_confidence_score: float
  - evidence_sufficiency_score: float
  - historical_accuracy_score: float  # Based on past recommendations
  - contributing_factors: tuple[ContributionFactor, ...]
  - detracting_factors: tuple[str, ...]

Methods:
  - needs_human_review(): bool
  - primary_uncertainty(): str
  - improvement_suggestions(): tuple[str, ...]
```

#### Feedback
```
Type: Value Object
Attributes:
  - feedback_id: UUID
  - engineer_id: EngineerId
  - submitted_at: datetime
  - rating: int [1-5]  # 1=very poor, 5=excellent
  - was_accurate: bool
  - was_actionable: bool
  - was_safe: bool
  - was_timely: bool
  - comments: str | null
  - what_was_wrong: str | null
  - what_was_right: str | null
  - alternative_action_taken: str | null
  - outcome_confirmed: bool | null  # Did the recommendation work?

Methods:
  - is_positive(): bool  # rating >= 4 and was_accurate
  - is_negative(): bool  # rating <= 2 or not was_accurate
  - sentiment(): str  # "positive", "neutral", "negative"
  - contributes_to_model_improvement(): bool
```

#### RejectionReason
```
Values:
  - INACCURATE: "inaccurate"
  - INCOMPLETE: "incomplete"
  - ALREADY_TRIED: "already_tried"
  - NOT_APPLICABLE: "not_applicable"
  - DANGEROUS: "dangerous"
  - OUTDATED: "outdated"
  - OTHER: "other"

Additional Attributes:
  - details: str (max 1000)
  - suggested_correction: str | null
```

#### RecommendationOutcome
```
Type: Value Object
Attributes:
  - outcome_type: OutcomeType (enum: success, partial_success, failure, inconclusive, pending)
  - actual_duration_minutes: int | null
  - steps_completed: int
  - steps_failed: int
  - result_description: str (max 2000)
  - follow_up_required: bool
  - follow_up_actions: tuple[str, ...] | null
  - lessons_learned: tuple[str, ...] | null
  - device_id_after: DeviceId | null  # If device was replaced
  - verified_by: EngineerId | null
  - verified_at: datetime | null

Methods:
  - success_rate(): float  # steps_completed / (steps_completed + steps_failed)
```

### 3.6 Domain Service: RecommendationService

```
Methods:

  generate_recommendations(
    incident_id: IncidentId,
    tenant_id: TenantId,
    context: RecommendationContext,
  ) -> Result[list[AIRecommendation], RecommendationError]
    Steps:
      1. Load incident data
      2. Retrieve relevant device data
      3. Query knowledge base for relevant articles
      4. Load incident history for pattern matching
      5. Build prompt for AI model
      6. Generate recommendations (may be multiple)
      7. Calculate confidence scores
      8. Generate explanations
      9. Apply safety classification
      10. Persist recommendations
      11. Publish RecommendationGeneratedEvent(s)
      12. Return Result

  accept_recommendation(
    recommendation_id: RecommendationId,
    engineer_id: EngineerId,
    reason: str | None,
  ) -> Result[AIRecommendation, RecommendationError]
    Steps:
      1. Load recommendation
      2. Validate transition
      3. Apply BR-REC-001 if confidence is very low
      4. Update status
      5. Persist
      6. Publish RecommendationAcceptedEvent
      7. Trigger KnowledgeArticle link update
      8. Return Result

  submit_feedback(
    recommendation_id: RecommendationId,
    feedback: Feedback,
  ) -> Result[AIRecommendation, RecommendationError]
    Steps:
      1. Load recommendation
      2. Validate feedback is from authorized user
      3. Update feedback
      4. Recalculate confidence (rolling average)
      5. If feedback is negative, flag for review
      6. Persist
      7. Trigger model feedback loop (async)
      8. Return Result

  get_recommendation_explanation(
    recommendation_id: RecommendationId,
    format: ExplanationFormat,  # "clinical", "engineering", "audit"
  ) -> Result[Explanation, RecommendationError]
```

---

## 4. DEVICE CONTEXT

### 4.1 Propósito del Contexto

Gestionar el registro, ciclo de vida, ubicación, calibración y mantenimiento de dispositivos biomédicos. Acts as the single source of truth for device information across all bounded contexts.

### 4.2 Aggregate: Device

#### Identidad
```
Aggregate Root: Device
ID: DeviceId (prefix: dev_)
Tenant: TenantId
```

#### Atributos

| Atributo | Tipo | Requerido | Mutable | Descripción |
|----------|------|----------|---------|-------------|
| `id` | DeviceId | Sí | No | Identificador único |
| `tenant_id` | TenantId | Sí | No | Aislamiento multi-tenant |
| `version` | int | Sí | Sí | Optimistic locking |
| `serial_number` | SerialNumber | Sí | No | Número de serie del fabricante |
| `device_type` | DeviceType | Sí | No | Tipo de dispositivo |
| `risk_class` | SafetyLevel | Sí | No | Clase de riesgo |
| `name` | str | Sí | Yes | Nombre descriptivo (max 200) |
| `manufacturer` | ManufacturerInfo | Sí | No | Información del fabricante |
| `model_number` | str | Sí | No | Modelo del fabricante (max 100) |
| `status` | DeviceStatus | Sí | Yes | Estado actual |
| `location` | LocationInfo | Sí | Yes | Ubicación actual |
| `installation_date` | datetime | No | No | Cuándo se instaló |
| `warranty_expiry` | datetime | No | Yes | Fecha de expiración de garantía |
| `calibration` | CalibrationInfo | No | Yes | Información de calibración |
| `maintenance_schedule` | MaintenanceSchedule | No | Yes | Programa de mantenimiento preventivo |
| `last_maintenance` | MaintenanceRecord | No | Yes | Última maintenance |
| `usage_hours` | float | No | Yes | Horas de uso acumuladas |
| `uptime_percentage` | UptimePercentage | No | Yes | Porcentaje de disponibilidad |
| `network_info` | NetworkInfo | No | Yes | Información de red |
| `power_requirements` | PowerRequirements | No | No | Requisitos eléctricos |
| `operating_parameters` | OperatingParameters | No | Yes | Parámetros operativos actuales |
| `certifications` | tuple[Certification, ...] | No | No | Certificaciones del dispositivo |
| `connected_devices` | tuple[DeviceId, ...] | No | Yes | Dispositivos conectados |
| `parent_device_id` | DeviceId | No | Yes | Dispositivo padre si es componente |
| `notes` | str | No | Yes | Notas adicionales (max 2000) |
| `metadata` | dict | No | Yes | Datos adicionales (max 30 keys) |
| `created_at` | datetime | Sí | No | Auditoría |
| `updated_at` | datetime | Sí | Yes | Auditoría |
| `deleted_at` | datetime | No | No | Soft delete |
| `registered_by` | EngineerId | Sí | No | Quién lo registró |

#### Factory Method
```
Device.register(
    tenant_id: TenantId,
    serial_number: SerialNumber,
    device_type: DeviceType,
    name: str,
    manufacturer: ManufacturerInfo,
    model_number: str,
    risk_class: SafetyLevel,
    location: LocationInfo,
    registered_by: EngineerId,
    installation_date: datetime | None = None,
    warranty_expiry: datetime | None = None,
    power_requirements: PowerRequirements | None = None,
    certifications: list[Certification] | None = None,
    parent_device_id: DeviceId | None = None,
    metadata: dict | None = None,
    correlation_id: UUID | None = None,
) -> Result[Device, DeviceError]
```

#### Invariants

1. **I-DEV-001:** `serial_number` debe ser único dentro del mismo `tenant_id`
2. **I-DEV-002:** `device_type` debe ser compatible con `risk_class`
3. **I-DEV-003:** No puede haber dos `Devices` activos con el mismo `serial_number` dentro del mismo tenant
4. **I-DEV-004:** Si `status = in_maintenance`, `last_maintenance` debe ser reciente (< 7 días)
5. **I-DEV-005:** Si `calibration.next_calibration_date <= now`, `status` debe incluir `calibration_due`
6. **I-DEV-006:** `connected_devices` no puede contener referencias circulares
7. **I-DEV-007:** Si `device_type` es `life_support`, entonces `risk_class = CLASS_D`
8. **I-DEV-008:** `uptime_percentage` debe estar en rango [0.0, 100.0]
9. **I-DEV-009:** `warranty_expiry` debe ser posterior a `installation_date`
10. **I-DEV-010:** Si `parent_device_id` está seteado, el dispositivo padre debe estar activo

### 4.3 State Machine: DeviceStatus

```
States:
  REGISTERED, ACTIVE, CALIBRATION_DUE, IN_MAINTENANCE,
  OUT_OF_SERVICE, DECOMMISSIONED

Diagram:
┌────────────┐
│ REGISTERED │
└─────┬──────┘
      │ activate()
      ▼
┌───────────┐◄──────────────┐
│  ACTIVE   │               │
└─────┬─────┘               │ deactivate()
      │                     │
      │         ┌───────────┴───────────┐
      │         │                       │
      │   maintenance()          take_out_of_service()
      │         │                       │
      │         ▼                       ▼
      │  ┌─────────────────┐   ┌─────────────────┐
      │  │ IN_MAINTENANCE  │   │  OUT_OF_SERVICE │
      │  └────────┬────────┘   └────────┬────────┘
      │           │                     │
      │    complete_maintenance()       │ restore_service()
      │           │                     │
      └───────────┴─────────────────────┘
                          │
                          ▼
               ┌──────────────────────┐
               │    CALIBRATION_DUE   │─────► calibrate() ───► ACTIVE
               └──────────────────────┘
                          │
                          ▼
               ┌──────────────────────┐
               │   DECOMMISSIONED     │ (terminal)
               └──────────────────────┘

Status Methods:
  - is_active(): bool  # ACTIVE only
  - is_operational(): bool  # ACTIVE or CALIBRATION_DUE
  - is_available(): bool  # ACTIVE, CALIBRATION_DUE (not out_of_service)
  - is_in_service(): bool  # ACTIVE, CALIBRATION_DUE, IN_MAINTENANCE
  - requires_attention(): bool  # CALIBRATION_DUE, IN_MAINTENANCE, OUT_OF_SERVICE
  - is_terminal(): bool  # DECOMMISSIONED
```

### 4.4 Value Objects del Device Context

#### DeviceType
```
Type: Enum Value Object
Values (by category):
  DIAGNOSTIC:
    - X_RAY: "x_ray"
    - CT_SCANNER: "ct_scanner"
    - MRI: "mri"
    - ULTRASOUND: "ultrasound"
    - PET_SCANNER: "pet_scanner"
    - MAMMOGRAPHY: "mammography"
  
  THERAPEUTIC:
    - INFUSION_PUMP: "infusion_pump"
    - VENTILATOR: "ventilator"
    - DEFIBRILLATOR: "defibrillator"
    - DIALYSIS_MACHINE: "dialysis_machine"
    - RADIATION_THERAPY: "radiation_therapy"
    - CARDIAC_STIMULATOR: "cardiac_stimulator"
  
  MONITORING:
    - PATIENT_MONITOR: "patient_monitor"
    - ECG_MACHINE: "ecg_machine"
    - PULSE_OXIMETER: "pulse_oximeter"
    - BLOOD_PRESSURE_MONITOR: "blood_pressure_monitor"
    - EEG_MACHINE: "eeg_machine"
  
  LIFE_SUPPORT:
    - ICU_VENTILATOR: "icu_ventilator"
    - ECMO_MACHINE: "ecmo_machine"
    - CARDIAC_ASSIST: "cardiac_assist"
    - ARTIFICIAL_ORGAN: "artificial_organ"
  
  LABORATORY:
    - BLOOD_ANALYZER: "blood_analyzer"
    - CENTRIFUGE: "centrifuge"
    - INCUBATOR: "incubator"
    - AUTOMATED_BIOMEDICAL_ANALYZER: "automated_biomedical_analyzer"
  
  SURGICAL:
    - ANESTHESIA_MACHINE: "anesthesia_machine"
    - SURGICAL_ROBOT: "surgical_robot"
    - ELECTROSURGICAL_UNIT: "electrosurgical_unit"
    - SURGICAL_LIGHT: "surgical_light"
    - OPERATING_TABLE: "operating_table"

Methods:
  - category(): DeviceCategory
  - risk_class(): SafetyLevel  # Default risk class
  - requires_network(): bool
  - requires_calibration(): bool
  - has_consumables(): bool
  - maintenance_frequency_days(): int
```

#### SerialNumber
```
Type: Value Object
Attributes:
  - value: str (max 100)
  - format: str | null  # Manufacturer format regex

Validation:
  - Cannot be blank
  - Cannot exceed 100 characters
  - Must match manufacturer's format if specified
  - Normalized to uppercase before storage

Methods:
  - normalize() -> SerialNumber
  - matches_pattern(pattern: str) -> bool
```

#### ManufacturerInfo
```
Type: Value Object
Attributes:
  - name: str (max 200, required)
  - model: str (max 100, required)
  - manufacturing_date: datetime | null
  - country_of_origin: str (ISO 3166-1 alpha-3, max 3)
  - contact_email: str | null
  - contact_phone: str | null
  - website: str | null
  - support_contract: bool  # Manufacturer support available

Validation:
  - name cannot be blank
  - model cannot be blank
  - country_of_origin must be valid ISO code if provided
```

#### LocationInfo
```
Type: Value Object
Attributes:
  - building: str (max 100)
  - floor: str (max 20)
  - room: str (max 50)
  - department: str (max 100)
  - address_line_1: str | null
  - address_line_2: str | null
  - city: str | null
  - state: str | null
  - postal_code: str | null
  - country: str | null
  - latitude: float | null
  - longitude: float | null
  - gps_coordinates: str | null  # "lat,lon" format

Methods:
  - full_address() -> str
  - short_location() -> str  # "Building - Floor - Room"
  - department_path() -> str  # "Building/Floor/Department/Room"
  - has_coordinates(): bool
```

#### CalibrationInfo
```
Type: Value Object
Attributes:
  - last_calibration_date: datetime | null
  - next_calibration_date: datetime | null
  - calibration_interval_days: int | null
  - calibration_certificate: str | null
  - calibrated_by: EngineerId | null
  - calibration_method: str | null
  - calibration_equipment: str | null
  - tolerance: str | null  # Manufacturer tolerance spec
  - result: CalibrationResult (enum: passed, failed, adjusted, not_required)
  - notes: str | null

Validation:
  - If last_calibration_date exists, next_calibration_date must be future
  - calibration_interval_days must be positive
  - If result = failed, alert must be triggered

Methods:
  - is_due(): bool  # next_calibration_date <= now
  - is_overdue(): bool  # next_calibration_date < now - 7 days
  - days_until_due(): int | null
  - needs_attention(): bool
```

#### MaintenanceSchedule
```
Type: Value Object
Attributes:
  - schedule_type: MaintenanceScheduleType (enum: preventive, corrective, predictive, conditional)
  - frequency_days: int | null
  - next_maintenance_date: datetime | null
  - last_maintenance_date: datetime | null
  - maintenance_procedure_id: KnowledgeId | null  # Links to knowledge article
  - estimated_duration_hours: float | null
  - required_parts: tuple[PartInfo, ...]
  - required_tools: tuple[str, ...]
  - required_certifications: tuple[str, ...]
  - cost_estimate: Money | null
  - priority: MaintenancePriority (enum: routine, urgent, emergency)

Methods:
  - is_due(): bool  # next_maintenance_date <= now
  - is_overdue(): bool  # next_maintenance_date < now
  - calculate_next_date() -> datetime | null
```

#### MaintenanceRecord
```
Type: Value Object
Attributes:
  - maintenance_id: MaintenanceId
  - maintenance_type: MaintenanceType (enum: preventive, corrective, emergency, calibration, inspection, upgrade)
  - performed_by: EngineerId
  - performed_at: datetime
  - duration_hours: float
  - description: str (max 2000)
  - parts_replaced: tuple[PartInfo, ...]
  - tools_used: tuple[str, ...]
  - outcome: MaintenanceOutcome (enum: completed, partially_completed, failed)
  - recommendations: tuple[str, ...]  # Future recommendations
  - next_steps: tuple[str, ...]
  - cost: Money | null
  - work_order_id: str | null
  - signature: str | null  # Digital signature of engineer
```

#### UptimePercentage
```
Type: Value Object
Attributes:
  - value: float [0.0, 100.0]
  - calculated_from: datetime
  - calculated_to: datetime
  - calculation_period_days: int
  - downtime_minutes: int
  - uptime_minutes: int

Methods:
  - meets_sla(sla_target: float): bool
  - risk_level(): str  # "green" (>99.5%), "yellow" (95-99.5%), "red" (<95%)
  - trend(): str  # "improving", "stable", "declining"
```

### 4.5 Domain Service: DeviceService

```
Methods:

  register_device(cmd: RegisterDeviceCommand) -> Result[Device, DeviceError]
    Steps:
      1. Validate serial_number uniqueness (I-DEV-001, I-DEV-003)
      2. Validate device_type/risk_class compatibility (I-DEV-002)
      3. Create Device aggregate in REGISTERED status
      4. Persist via DeviceRepository
      5. Publish DeviceRegisteredEvent
      6. If predictive maintenance available, calculate initial schedule
      7. Return Result

  activate_device(device_id, engineer_id) -> Result[Device, DeviceError]
    Steps:
      1. Load device
      2. Validate current status allows activation
      3. Update status to ACTIVE
      4. Set installation_date if not set
      5. Persist
      6. Publish DeviceActivatedEvent
      7. Return Result

  schedule_maintenance(
    device_id, maintenance_type, scheduled_date, engineer_id,
  ) -> Result[Device, DeviceError]
    Steps:
      1. Load device
      2. Validate device is not decommissioned
      3. Update maintenance_schedule
      4. Persist
      5. Publish DeviceMaintenanceScheduledEvent (new event)
      6. Trigger calendar notification
      7. Return Result

  relocate_device(
    device_id, new_location, engineer_id, reason,
  ) -> Result[Device, DeviceError]
    Steps:
      1. Load device
      2. Validate device is active or calibration_due (not decommissioned)
      3. Record old location
      4. Update location
      5. Persist
      6. Publish DeviceLocationChangedEvent
      7. Update any linked incidents with new location
      8. Return Result

  deactivate_device(
    device_id, engineer_id, reason, deactivation_type,
  ) -> Result[Device, DeviceError]
    Steps:
      1. Load device
      2. Check for open incidents on this device
      3. Update status based on deactivation_type
      4. Persist
      5. Publish DeviceStatusChangedEvent
      6. Return Result

  decommission_device(device_id, engineer_id, reason) -> Result[Device, DeviceError]
    Steps:
      1. Load device
      2. Validate no open incidents
      3. Validate no active connections to other devices
      4. Update status to DECOMMISSIONED
      5. Persist
      6. Publish DeviceDecommissionedEvent (new event)
      7. Return Result

  get_device_health_summary(device_id) -> Result[DeviceHealthSummary, DeviceError]
    Aggregates:
      - Device status and calibration info
      - Open incidents count
      - Recent maintenance history
      - Uptime percentage trend
      - Predicted failures (from analytics)
```

---

## 5. KNOWLEDGE CONTEXT

### 5.1 Propósito del Contexto

Gestionar la base de conocimientos técnicos de ingeniería clínica, incluyendo artículos, procedimientos, guías de seguridad, manuales de dispositivos y mejores prácticas. Acts as the institutional memory of the organization.

### 5.2 Aggregate: KnowledgeArticle

#### Identidad
```
Aggregate Root: KnowledgeArticle
ID: KnowledgeId (prefix: kno_)
Tenant: TenantId
```

#### Atributos

| Atributo | Tipo | Requerido | Mutable | Descripción |
|----------|------|----------|---------|-------------|
| `id` | KnowledgeId | Sí | No | Identificador único |
| `tenant_id` | TenantId | Sí | No | Aislamiento multi-tenant |
| `version` | int | Yes | Yes | Optimistic locking |
| `article_number` | str | Yes | No | Número legible KB-XXXXX |
| `title` | str | Yes | Yes | Título (max 300 chars) |
| `summary` | str | Yes | Yes | Resumen (max 500 chars) |
| `body` | str | Yes | Yes | Contenido completo (max 50000 chars) |
| `content_format` | ContentFormat | Yes | No | Markdown, HTML, plain |
| `tags` | tuple[str, ...] | No | Yes | Tags de búsqueda (max 30) |
| `category` | KnowledgeCategory | Yes | Yes | Categorización |
| `status` | KnowledgeStatus | Yes | Yes | Estado del artículo |
| `device_ids` | tuple[DeviceId, ...] | No | Yes | Dispositivos relacionados |
| `incident_type_tags` | tuple[str, ...] | No | Yes | Tipos de incidente relacionados |
| `references` | tuple[KnowledgeReference, ...] | No | Yes | Referencias cruzadas |
| `author_id` | EngineerId | Yes | No | Autor original |
| `author_name` | str | Yes | No | Nombre del autor |
| `reviewer_id` | EngineerId | No | Yes | Revisor asignado |
| `review_info` | ReviewInfo | No | Yes | Info de revisión |
| `approval_workflow` | ApprovalWorkflow | No | Yes | Workflow de aprobación |
| `statistics` | UsageStatistics | No | Yes | Estadísticas de uso |
| `content_metadata` | ContentMetadata | No | Yes | Metadatos del contenido |
| `language` | str | Yes | No | ISO 639-1, default "en" |
| `translations` | tuple[Translation, ...] | No | Yes | Traducciones disponibles |
| `effective_date` | datetime | No | Yes | Cuándo entra en vigor |
| `expiration_date` | datetime | No | Yes | Cuándo expira |
| `supersedes` | KnowledgeId | No | No | Artículo que reemplaza |
| `superseded_by` | KnowledgeId | No | Yes | Artículo que lo reemplaza |
| `related_article_ids` | tuple[KnowledgeId, ...] | No | Yes | Artículos relacionados |
| `attachment_ids` | tuple[str, ...] | No | Yes | Archivos adjuntos (S3 keys) |
| `custom_fields` | dict | No | Yes | Campos personalizados |
| `created_at` | datetime | Yes | No | Auditoría |
| `updated_at` | datetime | Yes | Yes | Auditoría |
| `published_at` | datetime | No | Yes | Auditoría |
| `deleted_at` | datetime | No | No | Soft delete |

#### Factory Method
```
KnowledgeArticle.create(
    tenant_id: TenantId,
    article_number: str,  # KB-XXXXX format
    title: str,
    summary: str,
    body: str,
    category: KnowledgeCategory,
    author_id: EngineerId,
    author_name: str,
    content_format: ContentFormat = ContentFormat.MARKDOWN,
    tags: list[str] | None = None,
    device_ids: list[DeviceId] | None = None,
    language: str = "en",
    metadata: ContentMetadata | None = None,
    correlation_id: UUID | None = None,
) -> Result[KnowledgeArticle, KnowledgeError]
```

#### Invariants

1. **I-KNO-001:** `article_number` debe ser único dentro del `tenant_id`
2. **I-KNO-002:** Si `status = published`, entonces `review_info.is_approved = true`
3. **I-KNO-003:** Un artículo no puede ser `published` si `body` está vacío
4. **I-KNO-004:** Si `superseded_by` está seteado, el artículo debe estar en `deprecated` o `archived`
5. **I-KNO-005:** Si `category` es regulatorio (safety_guideline, regulatory_compliance, emergency_protocol), el workflow de aprobación requiere al menos 2 aprobadores
6. **I-KNO-006:** Si `effective_date` está seteado, no puede ser futuro si `status = published`
7. **I-KNO-007:** Referencias circulares están prohibidas (A→B→A)
8. **I-KNO-008:** Un artículo `archived` no puede volver a `published` sin pasar por revisión

### 5.3 State Machine: KnowledgeStatus

```
States: DRAFT, IN_REVIEW, APPROVED, PUBLISHED, ARCHIVED, DEPRECATED

Diagram:
┌────────┐   submit()    ┌───────────┐
│ DRAFT  │──────────────►│ IN_REVIEW │
└────────┘              └─────┬─────┘
     ▲                        │
     │                        │ approve()
     │ reject()               ▼
     │                        ┌──────────┐
     │                        │ APPROVED │
     │                        └────┬─────┘
     │                             │ publish()
     │                             ▼
     │                        ┌───────────┐
     │                         │ PUBLISHED │
     │                         └─────┬─────┘
     │                               │
     │             ┌─────────────────┼─────────────────┐
     │             │                 │                 │
     │       archive()         supersede()      update_content()
     │             │                 │                 │
     │             ▼                 ▼                 ▼
     │      ┌──────────┐   ┌────────────┐     ┌────────┐
     │      │ ARCHIVED │   │ DEPRECATED │     │ DRAFT  │
     │      └──────────┘   └────────────┘     └────────┘
     │             │             │                   │
     │             │             │     (new version) │
     │             │             │                   │
     │             │             └───────────────────┘
     │             │                                    
     └─────────────┘                                    
       (restore() → DRAFT)                              

Terminal States: DEPRECATED
Revocable: ARCHIVED (can go back to DRAFT via restore())
```

### 5.4 Approval Workflow

#### ApprovalWorkflow
```
Type: Value Object
Attributes:
  - workflow_type: ApprovalWorkflowType (enum: single_approver, dual_approver, management_approval, regulatory_review, no_approval)
  - required_approvers: tuple[ApproverRole, ...]
  - current_approvers: tuple[ApproverInfo, ...]
  - approval_deadline: datetime | null
  - escalation_policy: EscalationPolicy | null
  - min_approvals_required: int
  - sequential_approval: bool  # true = one by one, false = parallel

Methods:
  - is_approved(): bool  # min_approvals_required reached
  - pending_approvals(): list[ApproverRole]
  - approval_progress(): tuple[approved_count, total_required]
```

#### ApproverInfo
```
Type: Value Object
Attributes:
  - engineer_id: EngineerId
  - role: ApproverRole (enum: author, reviewer, department_head, safety_officer, clinical_engineer, regulatory_specialist)
  - status: ApproverStatus (enum: pending, approved, rejected, skipped)
  - approved_at: datetime | null
  - comments: str | null
  - signature: str | null  # Digital signature hash
```

### 5.5 Value Objects del Knowledge Context

#### KnowledgeCategory
```
Values:
  - TROUBLESHOOTING: "troubleshooting"  # Step-by-step problem resolution
  - MAINTENANCE_PROCEDURE: "maintenance_procedure"  # Preventive/corrective procedures
  - SAFETY_GUIDELINE: "safety_guideline"  # Safety protocols (regulatory)
  - DEVICE_MANUAL: "device_manual"  # Manufacturer documentation
  - INCIDENT_REPORT: "incident_report"  # Post-incident reports
  - BEST_PRACTICE: "best_practice"  # Recommended approaches
  - TRAINING_MATERIAL: "training_material"  # Educational content
  - REGULATORY_COMPLIANCE: "regulatory_compliance"  # Compliance documentation (regulatory)
  - EMERGENCY_PROTOCOL: "emergency_protocol"  # Emergency response (regulatory)
  - REFERENCE_DOCUMENT: "reference_document"  # General reference
  - POLICY: "policy"  # Organizational policies
  - KNOWLEDGE_MAP: "knowledge_map"  # Links between articles

Methods:
  - is_regulatory(): bool  # SAFETY_GUIDELINE, REGULATORY_COMPLIANCE, EMERGENCY_PROTOCOL
  - requires_multi_approver(): bool  # regulatory categories
  - template(): str | null  # Document template name if applicable
  - review_frequency_days(): int | null  # Required review cadence
```

#### KnowledgeReference
```
Type: Value Object
Attributes:
  - reference_type: ReferenceType (enum: internal_article, external_url, device_manual, standard_document, regulation, manufacturer_spec, form, video, tool)
  - reference_id: str  # Internal ID or URL
  - description: str | null
  - url: str | null
  - page_reference: str | null
  - is_critical: bool  # Required for understanding
  - access_restricted: bool  # Requires special permission

Methods:
  - is_accessible(user: EngineerId) -> bool
  - is_broken(): bool  # Reference target exists?
```

#### ReviewInfo
```
Type: Value Object
Attributes:
  - reviewed_by: EngineerId
  - reviewed_at: datetime
  - approval_status: ApprovalStatus (enum: approved, rejected, needs_revision)
  - comments: str | null
  - review_round: int  # How many review cycles
  - previous_versions_reviewed: int

Methods:
  - is_approved(): bool
  - needs_revision(): bool
```

#### UsageStatistics
```
Type: Value Object
Attributes:
  - view_count: int
  - unique_viewers: int
  - helpful_count: int
  - not_helpful_count: int
  - bookmark_count: int
  - share_count: int
  - feedback_count: int
  - last_accessed: datetime | null
  - average_rating: float | null  # [1.0, 5.0]
  - search_impressions: int
  - search_click_through_rate: float

Methods:
  - helpfulness_ratio(): float
  - engagement_score(): float  # Composite metric
  - quality_score(): float  # Based on ratings and feedback
```

#### ContentMetadata
```
Type: Value Object
Attributes:
  - reading_time_minutes: int
  - difficulty_level: DifficultyLevel (enum: beginner, intermediate, advanced, expert)
  - audience: tuple[str, ...]  # "biomedical_engineers", "nurses", "physicians"
  - last_content_review: datetime | null
  - content_hash: str  # SHA-256 of content for change detection
  - word_count: int
  - image_count: int
  - table_count: int
  - code_snippet_count: int
  - has_video: bool
  - has_attachments: bool
```

### 5.6 Domain Service: KnowledgeService

```
Methods:

  create_article(cmd: CreateArticleCommand) -> Result[KnowledgeArticle, KnowledgeError]

  update_article(cmd: UpdateArticleCommand) -> Result[KnowledgeArticle, KnowledgeError]
    Validates:
      - Article is in editable state (DRAFT, ARCHIVED)
      - User has edit permission
      - I-KNO-003: body not empty
    Creates new version if PUBLISHED article is updated

  submit_for_review(article_id, reviewer_id) -> Result[KnowledgeArticle, KnowledgeError]
    Steps:
      1. Load article
      2. Validate status transition
      3. Assign reviewer based on workflow
      4. Update approval_workflow
      5. Persist
      6. Notify reviewer
      7. Return Result

  approve_article(article_id, approver_id, comments) -> Result[KnowledgeArticle, KnowledgeError]

  publish_article(article_id, publisher_id) -> Result[KnowledgeArticle, KnowledgeError]
    Validates:
      - I-KNO-002: review_info.is_approved
      - I-KNO-003: body not empty
      - I-KNO-006: effective_date
    Updates: status=PUBLISHED, published_at

  archive_article(article_id, archiver_id, reason) -> Result[KnowledgeArticle, KnowledgeError]
    If article supersedes another, update superseded_by link

  deprecate_article(
    article_id, deprecator_id, replacement_id, reason,
  ) -> Result[KnowledgeArticle, KnowledgeError]
    Steps:
      1. Validate replacement exists and is PUBLISHED
      2. Update I-KNO-004 on both articles
      3. Set status=DEPRECATED
      4. Update related_incidents to suggest new article
      5. Return Result

  search_knowledge(
    tenant_id, query, filters, pagination,
  ) -> Result[SearchResult[KnowledgeArticle], KnowledgeError]
    Full-text search on: title, summary, body, tags
    Filters: category, status, device_id, date_range, language
    Reranking by: relevance, quality_score, helpfulness_ratio

  get_device_knowledge(device_id, tenant_id) -> Result[list[KnowledgeArticle], KnowledgeError]
    Retrieves all published articles linked to device
    Ordered by: relevance, last_updated, quality_score

  get_incident_knowledge(incident_category, tenant_id) -> Result[list[KnowledgeArticle], KnowledgeError]
    Retrieves troubleshooting and incident_report articles matching incident category

  link_article_to_device(article_id, device_id) -> Result[KnowledgeArticle, KnowledgeError]

  add_cross_reference(source_id, target_id) -> Result[KnowledgeArticle, KnowledgeError]
    Validates I-KNO-007: no circular references

  get_related_articles(article_id, limit) -> Result[list[KnowledgeArticle], KnowledgeError]
    Uses: shared tags, shared device_ids, incident_type_tags, explicit relations
```

---

## 6. CROSS-CONTEXT INTEGRATION MODEL

### 6.1 Interaction Map

```
┌──────────────┐     IncidentCreated     ┌──────────────┐
│   INCIDENT   │────────────────────────►│  INCIDENT    │
│   Context    │◄────────────────────────│  Context     │
└──────────────┘     IncidentResolved    └──────────────┘
        │                                        │
        │                                         │
        ▼                                         ▼
┌──────────────┐     DeviceQueried      ┌──────────────┐
│   INCIDENT   │────────────────────────►│    DEVICE    │
│   Context    │◄────────────────────────│   Context    │
└──────────────┘     DeviceInfo         └──────────────┘
        │
        │ RecomendationRequested
        ▼
┌──────────────────┐     RecommendationGenerated
│ RECOMMENDATION   │────────────────────────►
│    Context       │◄────────────────────────
└──────────────────┘     RecommendationFeedback
        │
        │ KnowledgeQueried
        ▼
┌──────────────┐     KnowledgeRetrieved
│  KNOWLEDGE   │────────────────────────►
│   Context    │◄────────────────────────
└──────────────┘     KnowledgeUpdated

SHARED KERNEL (used by all)
  └── Domain Events, Entity IDs, Value Objects
```

### 6.2 Incident → Device Interaction

```
Query:
  DeviceContext.get_device_info(device_id, tenant_id) -> DeviceInfoDTO
  
Events Consumed by Incident:
  - DeviceRegisteredEvent: Link new devices to incidents
  - DeviceStatusChangedEvent: Alert if device goes out of service
  - DeviceDecommissionedEvent: Auto-close non-critical incidents on decommissioned device
  - DeviceLocationChangedEvent: Update incident location info

Events Consumed by Device:
  - IncidentCreatedEvent: Link device to incident
  - IncidentResolvedEvent: Update device status if it was out_of_service
  - IncidentClosedEvent: Log incident history on device record
```

### 6.3 Incident → Recommendation Interaction

```
Query:
  RecommendationContext.get_for_incident(incident_id) -> list[AIRecommendation]
  
Commands:
  RecommendationContext.generate_for_incident(incident_id) -> list[RecommendationId]

Events Consumed by Recommendation:
  - IncidentTriagedEvent: Trigger recommendation generation
  - IncidentResolvedEvent: Close pending recommendations
  - IncidentClosedEvent: Archive recommendations linked to closed incident

Events Consumed by Incident:
  - RecommendationAcceptedEvent: Log in incident timeline
  - RecommendationRejectedEvent: Log in incident timeline
  - RecommendationCompletedEvent: Auto-add resolution to incident
```

### 6.4 Recommendation → Knowledge Interaction

```
Query:
  KnowledgeContext.search_relevant(query, context) -> list[KnowledgeArticle]

Commands:
  KnowledgeContext.create_from_incident(incident_id) -> KnowledgeId  # Generate KB article from incident

Events Consumed by Recommendation:
  - KnowledgePublishedEvent: Include published articles in evidence
  - KnowledgeUpdatedEvent: Re-evaluate recommendations if source changed
  - KnowledgeArchivedEvent: Mark recommendations as potentially outdated

Events Consumed by Knowledge:
  - RecommendationCompletedEvent: Suggest KB article creation from successful resolution
  - RecommendationFeedbackEvent: Update article quality metrics
```

### 6.5 Cross-Context Business Rules

```
BR-XC-001: Device Incident Cascade
  When DeviceStatusChanged to DECOMMISSIONED:
    1. Query all open incidents for this device
    2. For each incident:
       - If priority < P2: auto-close with reason "Device decommissioned"
       - If priority >= P2: escalate and require manual review

BR-XC-002: Recommendation Evidence Linking
  When AIRecommendation is accepted:
    1. Extract device_ids from recommendation
    2. For each device_id:
       - Query recent incidents for device
       - Link resolved incident to KnowledgeArticle if resolution is novel
    3. Trigger KnowledgeService.create_from_resolution()

BR-XC-003: Incident → Knowledge Knowledge Map
  When Incident is closed with resolution:
    1. Extract device_id, category, symptoms from incident
    2. Query KnowledgeContext for related articles
    3. If no matching troubleshooting article exists and incident is P1/P2:
       - Flag for KnowledgeArticle creation from incident report
       - Assign to KnowledgeAuthor role

BR-XC-004: Knowledge Article Quality Feedback Loop
  When KnowledgeArticle receives positive feedback:
    1. Record which recommendations cited this article
    2. Increase recommendation priority for articles with high helpfulness
  When KnowledgeArticle receives negative feedback:
    1. Alert KnowledgeAuthor
    2. Mark recommendations that cited this article for review
    3. If feedback rate < 50%, consider deprecation
```

---

*Documento generado para implementación. Cada sección es un entregable completo listo para desarrollo.*
