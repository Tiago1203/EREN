# EREN - Especificación Técnica Completa
## Fase 6: Sistema de Eventos

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  
> **Depende de:** Fase 1 (Domain Events), Fase 2 (Integration Events)

---

## Tabla de Contenidos

1. [Arquitectura de Eventos](#1-arquitectura-de-eventos)
2. [Domain Events](#2-domain-events)
3. [Integration Events](#3-integration-events)
4. [Outbox Pattern](#4-outbox-pattern)
5. [Event Versioning](#5-event-versioning)
6. [Naming Conventions](#6-naming-conventions)
7. [Idempotencia](#7-idempotencia)
8. [Ordering](#8-ordering)
9. [Retries & Dead Letter Queue](#9-retries--dead-letter-queue)
10. [Event Schema Registry](#10-event-schema-registry)
11. [Monitoring & Alerting](#11-monitoring--alerting)

---

## Supuestos Declarados

1. **Message Broker:** RabbitMQ (primary), con soporte para Kafka en v2
2. **Outbox Storage:** PostgreSQL (misma base que los aggregates)
3. **Event Storage:** PostgreSQL para audit trail, Redis para replay
4. **Schema Registry:** Custom con versioning semántico
5. **Monitoring:** Prometheus metrics + OpenTelemetry tracing
6. **No Event Sourcing obligatorio:** Los eventos son para integración, no para state reconstruction
7. **Delivery Guarantee:** At-least-once
8. **Ordering:** FIFO por aggregate, no cross-aggregate

---

## 1. ARQUITECTURA DE EVENTOS

### 1.1 Event Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│  │  Aggregate   │────►│ Domain Event │────►│    Outbox    │  │
│  │   Root      │     │  (in-memory)│     │   Table      │  │
│  └──────────────┘     └──────────────┘     └──────┬───────┘  │
│                                                   │            │
│  ┌──────────────┐     ┌──────────────┐            │            │
│  │ Application  │────►│Integration   │            │            │
│  │  Service     │     │   Event      │────────────┤            │
│  └──────────────┘     └──────┬───────┘            │            │
└──────────────────────────────┼────────────────────┼────────────┘
                               │                    │
                               ▼                    ▼
                     ┌─────────────────┐  ┌─────────────────┐
                     │  Event Bus      │  │   Outbox        │
                     │  (Publisher)    │  │   Processor     │
                     │  RabbitMQ       │  │   (Poll/CDC)   │
                     └────────┬────────┘  └────────┬────────┘
                              │                     │
                              ▼                     ▼
                     ┌─────────────────────────────────────┐
                     │           Message Broker             │
                     │              RabbitMQ                 │
                     │                                       │
                     │  Exchanges:                           │
                     │    - incident.events                  │
                     │    - device.events                   │
                     │    - recommendation.events            │
                     │    - knowledge.events                 │
                     │    - shared.events                   │
                     └────────────┬───────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
     ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
     │    Consumer    │  │    Consumer    │  │    Consumer    │
     │  IncidentCtx   │  │   DeviceCtx    │  │RecommendationCtx│
     └────────────────┘  └────────────────┘  └────────────────┘
```

### 1.2 Event Flow

```
Synchronous Flow (Command side):
  User → API → Application Service → Aggregate → Domain Event
         ← Result ← Application Service ← Aggregate ←

Asynchronous Flow (Event side):
  Domain Event → Outbox → Event Processor → Message Broker → Consumer
                                                          ← Consumer
                                                          ← Consumer

Note: Domain Events are captured in-memory by aggregate.
      Outbox ensures they reach the broker reliably.
```

---

## 2. DOMAIN EVENTS

### 2.1 Base Event Structure

```python
@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""
    
    # Identity
    event_id: UUID  # UUID v7 (time-ordered)
    event_type: str  # Full class name
    version: int  # Starts at 1
    
    # Context
    tenant_id: TenantId
    occurred_at: datetime  # UTC
    correlation_id: UUID | None
    causation_id: UUID | None
    
    # Schema
    schema_version: str  # "1.0.0"
    content_type: str  # "application/json"
    
    # Methods
    def to_primitive(self) -> dict:
        """Serialize to dictionary for transport."""
        
    def to_json(self) -> str:
        """Serialize to JSON string."""
        
    def get_aggregate_id(self) -> UUID:
        """Get the aggregate ID this event belongs to."""
        
    def get_aggregate_type(self) -> str:
        """Get the aggregate type name."""
        
    def get_event_category(self) -> str:
        """Get the event category for routing."""
```

### 2.2 Event Envelope

```python
@dataclass(frozen=True)
class EventEnvelope:
    """Wrapper around events for transport."""
    
    # Envelope metadata
    envelope_id: UUID
    created_at: datetime
    
    # Event
    event: DomainEvent
    event_type: str
    event_version: int
    
    # Routing
    exchange: str  # Target exchange
    routing_key: str  # Routing key
    headers: dict  # Custom headers
    
    # Delivery
    delivery_mode: DeliveryMode  # PERSISTENT, TRANSIENT
    priority: int  # 0-9
    expiration_ms: int | None  # TTL
    
    # Tracing
    trace_id: str
    span_id: str
    baggage: dict  # Correlation data
    
    # Serialization
    content_encoding: str  # "utf-8", "gzip"
    content_type: str  # "application/json"
```

### 2.3 Incident Domain Events

```python
# Incident Domain Events

class IncidentReportedEvent(DomainEvent):
    event_type: str = "IncidentReportedEvent"
    
    incident_id: IncidentId
    title: str
    description: str
    priority: Priority
    safety_level: SafetyLevel
    category: IncidentCategory
    device_id: DeviceId | None
    device_name: str | None
    patient_impact: PatientImpact | None
    occurred_at: datetime
    detected_at: datetime
    reported_by: EngineerId
    tags: tuple[str, ...]


class IncidentTriagedEvent(DomainEvent):
    event_type: str = "IncidentTriagedEvent"
    
    incident_id: IncidentId
    assigned_priority: Priority
    category: IncidentCategory
    assigned_to: EngineerId | None
    triage_notes: str | None
    triaged_by: EngineerId
    triage_duration_minutes: int


class IncidentOpenedEvent(DomainEvent):
    event_type: str = "IncidentOpenedEvent"
    
    incident_id: IncidentId
    assigned_to: EngineerId
    opened_by: EngineerId


class IncidentProgressedEvent(DomainEvent):
    event_type: str = "IncidentProgressedEvent"
    
    incident_id: IncidentId
    progress_note: str
    next_action: str | None
    attachments: tuple[str, ...] | None
    progressed_by: EngineerId


class IncidentEscalatedEvent(DomainEvent):
    event_type: str = "IncidentEscalatedEvent"
    
    incident_id: IncidentId
    previous_priority: Priority
    new_priority: Priority
    escalation_reason: str
    escalation_path: tuple[EngineerId, ...]
    escalated_by: EngineerId


class IncidentResolvedEvent(DomainEvent):
    event_type: str = "IncidentResolvedEvent"
    
    incident_id: IncidentId
    resolution_type: ResolutionType
    resolution_summary: str
    resolution_details: str
    downtime_minutes: int
    actions_taken: tuple[str, ...]
    parts_replaced: tuple[str, ...] | None
    resolved_by: EngineerId


class IncidentClosedEvent(DomainEvent):
    event_type: str = "IncidentClosedEvent"
    
    incident_id: IncidentId
    closure_note: str | None
    total_duration_hours: float
    was_sla_met: bool
    closed_by: EngineerId


class IncidentReopenedEvent(DomainEvent):
    event_type: str = "IncidentReopenedEvent"
    
    incident_id: IncidentId
    previous_resolution_summary: str
    reopen_reason: str
    reopened_by: EngineerId
    reopened_at: datetime


class IncidentSlaBreachedEvent(DomainEvent):
    event_type: str = "IncidentSlaBreachedEvent"
    
    incident_id: IncidentId
    priority: Priority
    sla_target_hours: int
    actual_hours: float
    breach_duration_hours: float
    notified_roles: tuple[str, ...]
```

### 2.4 Device Domain Events

```python
class DeviceRegisteredEvent(DomainEvent):
    event_type: str = "DeviceRegisteredEvent"
    
    device_id: DeviceId
    serial_number: str
    device_type: DeviceType
    device_name: str
    risk_class: SafetyLevel
    registered_by: EngineerId


class DeviceActivatedEvent(DomainEvent):
    event_type: str = "DeviceActivatedEvent"
    
    device_id: DeviceId
    activated_by: EngineerId
    installation_date: datetime | None


class DeviceStatusChangedEvent(DomainEvent):
    event_type: str = "DeviceStatusChangedEvent"
    
    device_id: DeviceId
    previous_status: DeviceStatus
    new_status: DeviceStatus
    reason: str | None
    changed_by: EngineerId


class DeviceLocationChangedEvent(DomainEvent):
    event_type: str = "DeviceLocationChangedEvent"
    
    device_id: DeviceId
    previous_location: str
    new_location: str
    changed_by: EngineerId


class DeviceCalibrationDueEvent(DomainEvent):
    event_type: str = "DeviceCalibrationDueEvent"
    
    device_id: DeviceId
    calibration_type: str
    due_date: datetime
    days_until_due: int
    assigned_engineer: EngineerId | None


class DeviceCalibrationOverdueEvent(DomainEvent):
    event_type: str = "DeviceCalibrationOverdueEvent"
    
    device_id: DeviceId
    calibration_type: str
    due_date: datetime
    overdue_days: int
    priority: str  # "normal", "high", "critical"


class DeviceMaintenanceScheduledEvent(DomainEvent):
    event_type: str = "DeviceMaintenanceScheduledEvent"
    
    device_id: DeviceId
    maintenance_id: MaintenanceId
    maintenance_type: MaintenanceType
    scheduled_date: datetime
    estimated_duration_hours: float
    assigned_engineer: EngineerId | None


class DeviceMaintenanceCompletedEvent(DomainEvent):
    event_type: str = "DeviceMaintenanceCompletedEvent"
    
    device_id: DeviceId
    maintenance_id: MaintenanceId
    maintenance_type: MaintenanceType
    outcome: MaintenanceOutcome
    completed_by: EngineerId
    duration_hours: float


class DeviceDecommissionedEvent(DomainEvent):
    event_type: str = "DeviceDecommissionedEvent"
    
    device_id: DeviceId
    decommission_reason: str
    decommissioned_by: EngineerId
    open_incidents_count: int
    data_retention_days: int


class DeviceUptimeUpdatedEvent(DomainEvent):
    event_type: str = "DeviceUptimeUpdatedEvent"
    
    device_id: DeviceId
    uptime_percentage: float
    calculation_period_days: int
    downtime_minutes: int
    previous_uptime: float | None
```

### 2.5 Recommendation Domain Events

```python
class RecommendationGeneratedEvent(DomainEvent):
    event_type: str = "RecommendationGeneratedEvent"
    
    recommendation_id: RecommendationId
    incident_id: IncidentId | None
    title: str
    category: RecommendationCategory
    urgency: RecommendationUrgency
    confidence_value: float
    confidence_level: ConfidenceLevel
    safety_class: SafetyClass
    generated_by: str  # Model identifier
    generation_method: str
    human_review_required: bool


class RecommendationAcceptedEvent(DomainEvent):
    event_type: str = "RecommendationAcceptedEvent"
    
    recommendation_id: RecommendationId
    accepted_by: EngineerId
    acceptance_reason: str | None
    expected_outcome: str | None


class RecommendationRejectedEvent(DomainEvent):
    event_type: str = "RecommendationRejectedEvent"
    
    recommendation_id: RecommendationId
    rejected_by: EngineerId
    rejection_reason: RejectionReason
    details: str | None


class RecommendationCompletedEvent(DomainEvent):
    event_type: str = "RecommendationCompletedEvent"
    
    recommendation_id: RecommendationId
    outcome: RecommendationOutcome
    actual_duration_minutes: int | None
    completed_by: EngineerId
    steps_completed: int
    steps_failed: int
    follow_up_required: bool


class RecommendationExpiredEvent(DomainEvent):
    event_type: str = "RecommendationExpiredEvent"
    
    recommendation_id: RecommendationId
    expired_at: datetime
    original_expiration: datetime
    reason: str  # "timeout", "incident_resolved", "superseded"


class RecommendationFeedbackReceivedEvent(DomainEvent):
    event_type: str = "RecommendationFeedbackReceivedEvent"
    
    recommendation_id: RecommendationId
    feedback: Feedback
    feedback_submitted_by: EngineerId
    is_positive: bool
    quality_impact: float  # How this affects knowledge quality
```

---

## 3. INTEGRATION EVENTS

### 3.1 Integration Event Structure

```python
@dataclass(frozen=True)
class IntegrationEvent:
    """
    Events published outside the bounded context.
    These are the events other contexts consume.
    """
    
    # Inherits from DomainEvent
    # Plus integration-specific fields
    
    # Routing
    source_context: str  # "incident", "device", "recommendation", "knowledge"
    target_contexts: tuple[str, ...]  # Who should consume this
    is_broadcast: bool  # Send to all or specific targets
    
    # Schema
    compatibility_mode: str  # "forward", "backward", "full"
    requires_ack: bool  # Consumer must acknowledge
    
    # Versioning
    deprecated: bool
    sunset_date: datetime | None
    replacement_event_type: str | None


@dataclass(frozen=True)
class CrossContextIntegrationEvent(IntegrationEvent):
    """
    Events that cross bounded context boundaries.
    """
    
    # Source
    source_aggregate_id: str
    source_aggregate_type: str
    
    # Payload (full payload for consumer)
    payload_version: str
    payload: dict  # Full DTO serialized
    
    # Additional routing
    partition_key: str | None  # For ordering within aggregate
```

### 3.2 Integration Event Examples

```json
// IncidentReportedIntegrationEvent
{
  "event_id": "0191a2b3c4d5e6f7a8b9c0d1e",
  "event_type": "IncidentReportedIntegrationEvent",
  "version": 1,
  "occurred_at": "2026-07-15T14:30:00Z",
  "tenant_id": "tenant_uuid",
  "correlation_id": "corr_uuid",
  "causation_id": "inc_uuid",
  
  "source_context": "incident",
  "target_contexts": ["device", "recommendation", "knowledge"],
  "is_broadcast": false,
  "requires_ack": true,
  
  "payload_version": "1.0",
  "payload": {
    "incident_id": "inc_uuid",
    "title": "MRI Scanner display flickering",
    "description": "...",
    "priority": "P2_HIGH",
    "safety_level": "CLASS_C",
    "category": "HARDWARE_FAILURE",
    "device_id": "dev_uuid",
    "device_name": "MRI Scanner Unit 3",
    "occurred_at": "2026-07-15T08:30:00Z",
    "reported_by": "eng_uuid",
    "patient_impact": "NO_IMPACT",
    "tags": ["mri", "display", "hardware"]
  },
  
  "compatibility_mode": "forward",
  "deprecated": false
}
```

### 3.3 Cross-Context Event Mapping

```
Event Bridge: Incident → Device

Domain Event: IncidentOpenedEvent
  Published when: incident status changes to ACTIVE
  Published by: IncidentContext.IncidentService

Integration Event: IncidentActiveIntegrationEvent
  Translated by: IncidentContext.IntegrationEventMapper
  Routing: device.events exchange, routing_key=device.incident.active

DeviceContext Handler: DeviceIncidentActiveHandler
  Action: Updates device.last_active_incident, logs incident reference
  Side effects:
    - Creates incident summary on device record
    - Triggers notification if priority P1

Event Bridge: Incident → Recommendation

Domain Event: IncidentTriagedEvent
  Published when: incident triage completes
  Integration Event: IncidentTriagedIntegrationEvent
  Routing: recommendation.events exchange
  
RecommendationContext Handler: RecommendationTriggerHandler
  Action: Triggers recommendation generation pipeline
  Side effects:
    - Creates generation job
    - Notifies AI Layer
    - Tracks generation latency SLA
```

---

## 4. OUTBOX PATTERN

### 4.1 Outbox Table Schema

```sql
CREATE TABLE outbox (
    outbox_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL UNIQUE,
    event_type VARCHAR(200) NOT NULL,
    event_version INT NOT NULL DEFAULT 1,
    
    -- Routing
    exchange VARCHAR(200) NOT NULL,
    routing_key VARCHAR(500) NOT NULL,
    headers JSONB DEFAULT '{}',
    
    -- Payload
    payload JSONB NOT NULL,
    content_type VARCHAR(100) NOT NULL DEFAULT 'application/json',
    content_encoding VARCHAR(50) DEFAULT 'utf-8',
    
    -- Delivery
    delivery_mode VARCHAR(50) NOT NULL DEFAULT 'PERSISTENT',
    priority INT NOT NULL DEFAULT 5,
    expiration_ms INT,
    
    -- Processing
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 5,
    last_attempt_at TIMESTAMPTZ,
    last_error TEXT,
    next_retry_at TIMESTAMPTZ,
    locked_by VARCHAR(200),
    locked_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    tenant_id UUID NOT NULL,
    
    CONSTRAINT chk_status CHECK (status IN ('PENDING', 'PROCESSING', 'PUBLISHED', 'FAILED', 'DEAD_LETTERED'))
);

CREATE INDEX idx_outbox_status ON outbox(status);
CREATE INDEX idx_outbox_next_retry ON outbox(next_retry_at) WHERE status = 'FAILED';
CREATE INDEX idx_outbox_tenant ON outbox(tenant_id);
CREATE INDEX idx_outbox_event_type ON outbox(event_type);
CREATE INDEX idx_outbox_created ON outbox(created_at DESC);
```

### 4.2 Outbox Processor

```python
class OutboxProcessor:
    """
    Processes outbox table and publishes to message broker.
    Implements exactly-once semantics via idempotency.
    """
    
    def __init__(
        self,
        db_pool: Pool,
        rabbitmq: Connection,
        batch_size: int = 100,
        poll_interval_ms: int = 100,
        lock_timeout_seconds: int = 30,
    ):
        ...
    
    async def process_batch(self) -> ProcessResult:
        """
        Process a batch of pending outbox events.
        """
        
        # 1. Claim events (SELECT FOR UPDATE SKIP LOCKED)
        events = await self._claim_events()
        
        # 2. Publish each event
        results = []
        for event in events:
            result = await self._publish_event(event)
            results.append(result)
        
        # 3. Update status based on results
        await self._update_statuses(results)
        
        # 4. Return summary
        return ProcessResult(
            total=len(events),
            published=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            dead_lettered=sum(1 for r in results if r.dead_lettered),
        )
    
    async def _claim_events(self) -> list[OutboxEvent]:
        """Claim events for processing using pessimistic locking."""
        
        query = """
            SELECT * FROM outbox
            WHERE status IN ('PENDING', 'FAILED')
              AND (next_retry_at IS NULL OR next_retry_at <= NOW())
              AND attempts < max_attempts
            ORDER BY created_at ASC
            LIMIT :batch_size
            FOR UPDATE SKIP LOCKED
        """
        
        # Update status to PROCESSING
        update_query = """
            UPDATE outbox
            SET status = 'PROCESSING',
                locked_by = :processor_id,
                locked_at = NOW(),
                attempts = attempts + 1
            WHERE outbox_id = ANY(:claimed_ids)
        """
    
    async def _publish_event(self, event: OutboxEvent) -> PublishResult:
        """Publish a single event to RabbitMQ."""
        
        try:
            # 1. Prepare message
            message = self._prepare_message(event)
            
            # 2. Publish with publisher confirms
            channel = self._get_channel()
            channel.basic_publish(
                exchange=event.exchange,
                routing_key=event.routing_key,
                body=message.body,
                properties=message.properties,
                mandatory=True,
            )
            
            # 3. Wait for confirmation (with timeout)
            confirmed = await channel.wait_for_confirm(timeout=5.0)
            
            if confirmed:
                return PublishResult(success=True, event_id=event.event_id)
            else:
                raise PublishFailedError("Publisher confirm not received")
                
        except Exception as e:
            # Calculate next retry
            next_retry = self._calculate_next_retry(event, str(e))
            return PublishResult(
                success=False,
                event_id=event.event_id,
                error=str(e),
                next_retry_at=next_retry,
            )
    
    def _calculate_next_retry(
        self,
        event: OutboxEvent,
        error: str,
    ) -> datetime:
        """Calculate next retry time with exponential backoff."""
        
        base_delay_seconds = 1
        max_delay_seconds = 300  # 5 minutes
        backoff_multiplier = 2
        
        attempts = event.attempts
        delay = min(
            base_delay_seconds * (backoff_multiplier ** attempts),
            max_delay_seconds,
        )
        
        # Add jitter (±10%)
        import random
        jitter = delay * 0.1
        delay += random.uniform(-jitter, jitter)
        
        return datetime.now(UTC) + timedelta(seconds=delay)
```

### 4.3 Transactional Write

```python
async def save_incident_and_publish(
    db_pool: Pool,
    incident: EngineeringIncident,
) -> Result[EngineeringIncident, IncidentError]:
    """
    Save incident and publish event in single transaction.
    Uses outbox pattern for reliable delivery.
    """
    
    async with db_pool.connection() as conn:
        async with conn.transaction():
            # 1. Save incident aggregate
            await incident_repository.save(conn, incident)
            
            # 2. Capture domain events
            events = incident.pop_pending_events()
            
            # 3. Write to outbox (same transaction)
            for event in events:
                outbox_entry = OutboxEntry(
                    event_id=event.event_id,
                    event_type=event.event_type,
                    event_version=event.version,
                    exchange="incident.events",
                    routing_key=f"incident.{event.event_type.lower().replace('event', '')}",
                    payload=json.dumps(event.to_primitive()),
                    tenant_id=incident.tenant_id,
                    delivery_mode="PERSISTENT",
                    priority=get_priority_for_event(event),
                    status="PENDING",
                    max_attempts=5,
                )
                
                await outbox_repository.save(conn, outbox_entry)
            
            # 4. Commit transaction
            # Outbox entries are committed atomically with aggregate
    
    # Event will be published by outbox processor
    return Result.Ok(incident)
```

---

## 5. EVENT VERSIONING

### 5.1 Versioning Rules

```
Semantic Versioning for Events: MAJOR.MINOR.PATCH

MAJOR (Breaking Changes):
  - Removed required fields
  - Changed field semantics
  - Changed field types
  - Changed event name
  - Requires: Version bump + migration

MINOR (Backward-Compatible Additions):
  - Added optional fields
  - Added new event types
  - Requires: Version bump, consumers ignore unknown fields

PATCH (Bug Fixes):
  - No schema change
  - Documentation changes
  - No consumer action needed
```

### 5.2 Version Compatibility Modes

```python
class CompatibilityMode(Enum):
    """
    How the event producer maintains compatibility.
    """
    
    FORWARD = "forward"
    """
    New versions can be read by old consumers.
    Only add optional fields.
    Never remove or change existing fields.
    """
    
    BACKWARD = "backward"
    """
    Old versions can be processed by new consumers.
    Consumer handles missing fields gracefully.
    Producer can add/remove fields.
    """
    
    FULL = "full"
    """
    Both directions compatible.
    Default for most events.
    """
```

### 5.3 Version Negotiation

```
Version Negotiation Flow:

Producer creates event (version 2):
  {
    "event_type": "IncidentReportedEvent",
    "version": 2,
    "payload": {
      "incident_id": "...",
      "new_field": "value",  // New field
      "existing_field": "value"
    }
  }

Consumer supports versions [1, 2]:
  1. Check compatibility_mode
  2. If FORWARD: process normally (new field ignored)
  3. If BACKWARD: use defaults for missing fields
  4. If incompatible: 
     - Log warning
     - Send to dead letter queue with version mismatch flag
     - Alert operations
```

### 5.4 Schema Evolution Examples

```
Version 1 → Version 2 (Minor - Additive):
  
  Added: patient_impact field (optional)
  
  V1: {"incident_id": "...", "priority": "P2_HIGH"}
  V2: {"incident_id": "...", "priority": "P2_HIGH", "patient_impact": "NO_IMPACT"}
  
  Consumers:
    - V1 consumers: Ignore new field ✓
    - V2 consumers: Read new field ✓

Version 2 → Version 3 (Major - Breaking):

  Changed: priority field renamed to severity_level
  
  V2: {"incident_id": "...", "priority": "P2_HIGH"}
  V3: {"incident_id": "...", "severity_level": "P2_HIGH"}
  
  Migration:
    - Emit both V2 and V3 during transition (1 major version)
    - V2 consumers: Continue with V2
    - V3 consumers: Process V3
    - After transition: Deprecate V2
```

---

## 6. NAMING CONVENTIONS

### 6.1 Event Type Naming

```
Pattern: {EntityName}{PastTenseAction}Event

Rules:
  1. Entity name in PascalCase
  2. Action in past tense
  3. Suffix "Event" always present
  4. No abbreviations
  5. No numbers in name

Correct Examples:
  - IncidentReportedEvent ✓
  - DeviceActivatedEvent ✓
  - RecommendationGeneratedEvent ✓
  - IncidentTriagedEvent ✓

Incorrect Examples:
  - IncidentReported ✗ (missing Event suffix)
  - incident_reported_event ✗ (wrong casing)
  - IncReportEvent ✗ (abbreviation)
  - IncidentReportEvent ✗ (wrong tense: "report" vs "reported")
```

### 6.2 Routing Key Pattern

```
Pattern: {context}.{domain}.{entity}.{action}

Examples:
  incident.incident.reported
  incident.incident.triaged
  device.device.registered
  device.device.status_changed
  recommendation.recommendation.generated
  recommendation.recommendation.accepted
  knowledge.article.published
  shared.notification.sla_breached

Wildcard Patterns:
  incident.incident.#         # All incident events
  incident.#                  # All events from incident context
  #.reported                   # All reported events (use sparingly)
```

### 6.3 Exchange Naming

```
Exchange Pattern: {context}.events

Exchanges:
  incident.events     # All incident domain events
  device.events      # All device domain events
  recommendation.events  # All recommendation events
  knowledge.events    # All knowledge events
  shared.events      # Shared/cross-context events
  notification.events # Notification events

Exchange Types:
  topic: For routing key based routing (primary)
  direct: For point-to-point (used internally)
  fanout: For broadcasting (rarely used)
```

---

## 7. IDEMPOTENCIA

### 7.1 Idempotency Table

```sql
CREATE TABLE event_idempotency (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(200) NOT NULL,
    
    -- Processing state
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processor_id VARCHAR(200) NOT NULL,
    result VARCHAR(50) NOT NULL,  -- SUCCESS, DUPLICATE, FAILED
    
    -- Result details
    result_details JSONB,
    
    -- Cleanup
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '90 days'),
    
    CONSTRAINT chk_result CHECK (result IN ('SUCCESS', 'DUPLICATE', 'FAILED'))
);

CREATE INDEX idx_idempotency_expires ON event_idempotency(expires_at);
CREATE INDEX idx_idempotency_processed ON event_idempotency(processed_at);
```

### 7.2 Consumer Idempotency Implementation

```python
class IdempotentEventConsumer:
    """
    Base consumer that ensures idempotent processing.
    """
    
    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool
    
    async def process_with_idempotency(
        self,
        event: IntegrationEvent,
        handler: Callable,
    ) -> ProcessingResult:
        """
        Process event with idempotency guarantee.
        """
        
        # 1. Check if already processed
        existing = await self._get_processing_state(event.event_id)
        
        if existing:
            if existing.result == "SUCCESS":
                logger.info(f"Event {event.event_id} already processed successfully")
                return ProcessingResult.duplicate(existing)
            elif existing.result == "FAILED" and not self._should_retry(existing):
                logger.warning(f"Event {event.event_id} previously failed, skipping")
                return ProcessingResult.skipped(existing)
        
        # 2. Record attempt
        await self._record_attempt(event.event_id)
        
        # 3. Process event
        try:
            result = await handler(event)
            
            # 4. Record success
            await self._record_success(event.event_id, result)
            return ProcessingResult.success(result)
            
        except Exception as e:
            # 5. Record failure
            await self._record_failure(event.event_id, str(e))
            return ProcessingResult.failure(str(e))
    
    async def _record_success(
        self,
        event_id: UUID,
        result: Any,
    ) -> None:
        """Record successful processing."""
        
        await self.db_pool.execute("""
            INSERT INTO event_idempotency (event_id, result, result_details)
            VALUES ($1, 'SUCCESS', $2)
            ON CONFLICT (event_id) DO UPDATE
            SET result = 'SUCCESS',
                result_details = $2,
                processed_at = NOW()
        """, event_id, json.dumps({"result": str(result)}))
    
    async def _record_failure(
        self,
        event_id: UUID,
        error: str,
    ) -> None:
        """Record failed processing."""
        
        await self.db_pool.execute("""
            INSERT INTO event_idempotency (event_id, result, result_details)
            VALUES ($1, 'FAILED', $2)
            ON CONFLICT (event_id) DO UPDATE
            SET result = 'FAILED',
                result_details = $2,
                processed_at = NOW()
        """, event_id, json.dumps({"error": error}))
```

---

## 8. ORDERING

### 8.1 Ordering Guarantees

```
Ordering Guarantees:

WITHIN an aggregate: GUARANTEED
  - Events from the same aggregate are delivered in order
  - Achieved via consistent partition key
  
ACROSS aggregates: NOT GUARANTEED
  - Events from different aggregates may arrive out of order
  - Consumers must handle out-of-order if needed
  
WITHIN a tenant: BEST EFFORT
  - Events for the same tenant try to maintain order
  - Use tenant_id as partition key
```

### 8.2 Partition Strategy

```python
class EventPartitioner:
    """
    Determines partition key for event routing.
    """
    
    def get_partition_key(
        self,
        event: IntegrationEvent,
    ) -> str:
        """
        Get partition key for ordering guarantees.
        """
        
        # For aggregate-level ordering: use aggregate ID
        if self._has_aggregate_id(event):
            return str(event.aggregate_id)
        
        # For tenant-level ordering: use tenant ID
        return str(event.tenant_id)
    
    def get_exchange(self, event: IntegrationEvent) -> str:
        """Get target exchange for event."""
        return f"{event.source_context}.events"
    
    def get_routing_key(self, event: IntegrationEvent) -> str:
        """Get routing key for event."""
        action = event.event_type.lower().replace("event", "").replace("integration", "")
        return f"{event.source_context}.{event.source_context}.{action}"
```

### 8.3 Handling Out-of-Order Events

```python
class OutOfOrderHandler:
    """
    Handles events that arrive out of expected order.
    """
    
    async def handle_incident_status_changed(
        self,
        event: IncidentStatusChangedEvent,
    ) -> None:
        """
        Handle status change events, checking for out-of-order.
        """
        
        # Load current incident state
        current_incident = await incident_repo.get(event.incident_id)
        
        if current_incident.version > event.aggregate_version:
            # This event is stale (we're ahead)
            logger.warning(
                f"Out-of-order event: {event.event_id} "
                f"version {event.aggregate_version} < current {current_incident.version}"
            )
            
            # Options:
            # 1. Ignore stale event
            return
            
            # 2. Compare and update if beneficial
            # if event.has_relevant_new_data(current_incident):
            #     await apply_merging(event, current_incident)
        
        elif current_incident.version == event.aggregate_version:
            # Normal case: apply event
            await self._apply_event(current_incident, event)
        
        else:
            # Shouldn't happen: we're behind
            logger.error(
                f"Event version mismatch: "
                f"event {event.aggregate_version} > current {current_incident.version}"
            )
            raise ConcurrencyError("Event version mismatch")
```

---

## 9. RETRIES & DEAD LETTER QUEUE

### 9.1 Retry Policy

```python
class RetryPolicy:
    """
    Configurable retry policy for event processing.
    """
    
    def __init__(
        self,
        max_attempts: int = 5,
        base_delay_seconds: float = 1.0,
        max_delay_seconds: float = 300.0,
        backoff_multiplier: float = 2.0,
        jitter_percentage: float = 10.0,
        retryable_errors: set[str] | None = None,
        non_retryable_errors: set[str] | None = None,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay_seconds
        self.max_delay = max_delay_seconds
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter_percentage / 100.0
        self.retryable = retryable_errors
        self.non_retryable = non_retryable_errors
    
    def should_retry(
        self,
        error: Exception,
        attempt: int,
    ) -> bool:
        """Determine if error should be retried."""
        
        if attempt >= self.max_attempts:
            return False
        
        error_type = type(error).__name__
        
        if self.non_retryable and error_type in self.non_retryable:
            return False
        
        if self.retryable and error_type not in self.retryable:
            return False
        
        return True
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        
        delay = min(
            self.base_delay * (self.backoff_multiplier ** attempt),
            self.max_delay,
        )
        
        # Add jitter
        jitter_range = delay * self.jitter
        delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)


DEFAULT_RETRY_POLICY = RetryPolicy(
    max_attempts=5,
    base_delay_seconds=1.0,
    max_delay_seconds=300.0,
    backoff_multiplier=2.0,
    retryable_errors={
        "ConnectionError",
        "TimeoutError",
        "ServiceUnavailableError",
        "TransientError",
    },
    non_retryable_errors={
        "ValidationError",
        "NotFoundError",
        "AuthorizationError",
        "InvalidEventSchemaError",
    },
)
```

### 9.2 Dead Letter Queue

```sql
-- Dead Letter Queue Table
CREATE TABLE dead_letter_queue (
    dlq_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Original event
    original_event_id UUID NOT NULL,
    original_event_type VARCHAR(200) NOT NULL,
    original_exchange VARCHAR(200),
    original_routing_key VARCHAR(500),
    original_payload JSONB NOT NULL,
    
    -- Failure details
    failure_reason TEXT NOT NULL,
    failure_exception_type VARCHAR(200),
    failure_trace TEXT,
    last_attempt_at TIMESTAMPTZ NOT NULL,
    attempts INT NOT NULL,
    
    -- Processing state
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    assigned_to VARCHAR(200),
    resolution VARCHAR(100),
    resolution_notes TEXT,
    resolved_at TIMESTAMPTZ,
    resolved_by VARCHAR(200),
    
    -- Alerting
    alert_sent BOOLEAN DEFAULT FALSE,
    alert_sent_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id UUID NOT NULL,
    
    CONSTRAINT chk_dlq_status CHECK (status IN ('PENDING', 'INVESTIGATING', 'RESOLVED', 'REPLAYED', 'DISCARDED'))
);

CREATE INDEX idx_dlq_status ON dead_letter_queue(status);
CREATE INDEX idx_dlq_created ON dead_letter_queue(created_at DESC);
CREATE INDEX idx_dlq_original_type ON dead_letter_queue(original_event_type);
CREATE INDEX idx_dlq_alert ON dead_letter_queue(created_at) WHERE alert_sent = FALSE AND status = 'PENDING';
```

### 9.3 DLQ Processing

```python
class DLQProcessor:
    """
    Processes dead letter queue events.
    """
    
    async def process_dlq(self, dlq_id: UUID) -> DLQResult:
        """
        Process a single DLQ entry.
        """
        
        entry = await self._get_entry(dlq_id)
        
        # Analyze failure
        analysis = self._analyze_failure(entry)
        
        if analysis.can_retry:
            # Retry with fix
            return await self._retry_entry(entry, analysis.fix)
        
        elif analysis.should_discard:
            # Discard with approval
            await self._discard_entry(entry, analysis.reason)
            return DLQResult.discarded()
        
        else:
            # Manual investigation needed
            await self._mark_for_investigation(entry)
            return DLQResult.needs_investigation(analysis)
    
    def _analyze_failure(self, entry: DLQEntry) -> FailureAnalysis:
        """
        Analyze why the event failed.
        """
        
        error_type = entry.failure_exception_type
        
        # Pattern: ValidationError → usually schema issue
        if error_type == "ValidationError":
            return FailureAnalysis(
                can_retry=False,
                should_discard=False,
                reason="Schema validation failed - manual review needed",
                fix=None,
            )
        
        # Pattern: ConnectionError → transient
        if error_type in {"ConnectionError", "TimeoutError"}:
            return FailureAnalysis(
                can_retry=True,
                should_discard=False,
                reason="Transient error",
                fix=RetryFix(delay_seconds=60),
            )
        
        # Pattern: NotFoundError → target doesn't exist
        if error_type == "NotFoundError":
            return FailureAnalysis(
                can_retry=False,
                should_discard=True,
                reason="Referenced entity not found",
            )
        
        # Unknown error
        return FailureAnalysis(
            can_retry=False,
            should_discard=False,
            reason="Unknown error type - manual review needed",
        )
```

---

## 10. EVENT SCHEMA REGISTRY

### 10.1 Schema Storage

```sql
CREATE TABLE event_schemas (
    schema_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Schema identity
    event_type VARCHAR(200) NOT NULL,
    version INT NOT NULL,
    major_version INT GENERATED ALWAYS AS (version / 100) STORED,
    minor_version INT GENERATED ALWAYS AS (version % 100 / 10) STORED,
    patch_version INT GENERATED ALWAYS AS (version % 10) STORED,
    
    -- Schema
    schema_definition JSONB NOT NULL,  # JSON Schema
    schema_hash VARCHAR(64) NOT NULL,  # SHA-256 of schema
    
    -- Compatibility
    compatibility_mode VARCHAR(50) NOT NULL DEFAULT 'forward',
    previous_version INT,
    migration_script TEXT,
    
    -- Lifecycle
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE, DEPRECATED, RETIRED
    
    deprecated_at TIMESTAMPTZ,
    sunset_date TIMESTAMPTZ,
    replacement_version INT,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(200) NOT NULL,
    description TEXT,
    
    UNIQUE (event_type, version)
);

CREATE INDEX idx_schemas_event_type ON event_schemas(event_type);
CREATE INDEX idx_schemas_status ON event_schemas(status);
CREATE INDEX idx_schemas_lookup ON event_schemas(event_type, version);
```

### 10.2 Schema Validation

```python
class EventSchemaValidator:
    """
    Validates events against registered schemas.
    """
    
    def __init__(self, schema_registry: SchemaRegistry):
        self.registry = schema_registry
    
    async def validate(
        self,
        event: IntegrationEvent,
    ) -> ValidationResult:
        """
        Validate event against registered schema.
        """
        
        # 1. Get schema
        schema = await self.registry.get_schema(
            event.event_type,
            event.version,
        )
        
        if not schema:
            return ValidationResult.invalid(
                error=f"No schema found for {event.event_type} v{event.version}",
                error_code="SCHEMA_NOT_FOUND",
            )
        
        # 2. Parse JSON
        try:
            payload = json.loads(event.payload)
        except json.JSONDecodeError as e:
            return ValidationResult.invalid(
                error=f"Invalid JSON: {e}",
                error_code="INVALID_JSON",
            )
        
        # 3. Validate against schema
        try:
            jsonschema.validate(instance=payload, schema=schema.schema_definition)
            return ValidationResult.valid()
            
        except jsonschema.ValidationError as e:
            return ValidationResult.invalid(
                error=str(e.message),
                error_code="SCHEMA_VALIDATION_FAILED",
                path=e.absolute_path,
            )
        
        except jsonschema.SchemaError as e:
            return ValidationResult.invalid(
                error=f"Schema error: {e}",
                error_code="INVALID_SCHEMA",
            )
```

---

## 11. MONITORING & ALERTING

### 11.1 Event Metrics

```python
# Prometheus metrics for event system

# Event publishing
EVENTS_PUBLISHED = Counter(
    "events_published_total",
    "Total events published",
    ["context", "event_type", "status"]
)

EVENTS_PUBLISH_DURATION = Histogram(
    "events_publish_duration_seconds",
    "Time to publish events",
    ["context", "event_type"]
)

# Event consumption
EVENTS_CONSUMED = Counter(
    "events_consumed_total",
    "Total events consumed",
    ["context", "event_type", "status"]
)

EVENTS_CONSUME_DURATION = Histogram(
    "events_consume_duration_seconds",
    "Time to process events",
    ["context", "event_type", "status"]
)

# Outbox
OUTBOX_PENDING = Gauge(
    "outbox_pending_events",
    "Pending events in outbox",
    ["context"]
)

OUTBOX_PROCESSING = Gauge(
    "outbox_processing_events",
    "Events currently being processed",
    ["context"]
)

OUTBOX_FAILED = Gauge(
    "outbox_failed_events",
    "Failed events in outbox",
    ["context"]
)

# Dead letter queue
DLQ_SIZE = Gauge(
    "dead_letter_queue_size",
    "Size of dead letter queue",
    ["context", "event_type"]
)

DLQ_AGE_HOURS = Histogram(
    "dead_letter_queue_age_hours",
    "Age of DLQ entries",
    ["context", "event_type"]
)
```

### 11.2 Alerting Rules

```yaml
# Alerting rules for event system

groups:
  - name: event_system
    rules:
      - alert: OutboxBacklog
        expr: outbox_pending_events > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Outbox backlog growing"
          description: "{{ $value }} events pending for > 5 minutes"
      
      - alert: DLQEntries
        expr: dead_letter_queue_size > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Dead letter queue has entries"
          description: "{{ $value }} events in DLQ"
      
      - alert: EventPublishLatency
        expr: histogram_quantile(0.95, events_publish_duration_seconds) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Event publish latency high"
          description: "P95 publish latency is {{ $value }}s"
      
      - alert: EventConsumeFailureRate
        expr: rate(events_consumed{status="error"}[5m]) / rate(events_consumed_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High event consume failure rate"
          description: "{{ $value | humanizePercentage }} of events failing"
      
      - alert: DLQEntryOld
        expr: dead_letter_queue_age_hours > 24
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "DLQ entries older than 24 hours"
          description: "{{ $value }} events in DLQ for > 24 hours"
```

---

*Documento generado para implementación. Fase 6 completa.*
