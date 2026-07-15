# EREN Event Architecture
## How Events Flow Through the System

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial |

---

## Purpose

This document defines how events flow through EREN, including:
- Event types and their semantics
- Delivery guarantees
- Error handling (DLQ)
- Versioning and replay
- Ordering requirements

---

## Event Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    EVENT CATEGORIES                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DOMAIN EVENTS                                              │
│  ├── Clinical: PatientAdmitted, DiagnosisMade, TreatmentStarted │
│  ├── Biomedical: DeviceAlarm, CalibrationDue, MaintenanceScheduled │
│  └── Hospital: BedAssigned, StaffShiftChanged, OccupancyUpdated │
│                                                              │
│  SYSTEM EVENTS                                              │
│  ├── Authentication: LoginSucceeded, LoginFailed, SessionCreated │
│  ├── Authorization: AccessGranted, AccessDenied             │
│  └── Audit: PHIAccessed, DataExported, PolicyViolated      │
│                                                              │
│  COGNITIVE EVENTS                                           │
│  ├── EvidenceRetrieved, TrustEvaluated, RiskAssessed      │
│  ├── DecisionRecommended, ExplanationGenerated               │
│  └── RecommendationAccepted, RecommendationRejected         │
│                                                              │
│  INFRASTRUCTURE EVENTS                                      │
│  ├── DeviceConnected, DeviceDisconnected                   │
│  ├── ServiceStarted, ServiceStopped                         │
│  └── HealthCheckPassed, HealthCheckFailed                   │
│                                                              │
│  INTEGRATION EVENTS                                         │
│  ├── FHIRSynced, HL7Received, MQTTPublished               │
│  └── DICOMStored, WebhookTriggered                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Delivery Semantics

### The Three Guarantees

| Guarantee | Meaning | Use Cases | Can Lose Data? |
|-----------|---------|-----------|----------------|
| **Exactly Once** | Event processed exactly one time | Audit, PHI Access, Billing | ❌ No |
| **At Least Once** | Event may be processed multiple times | Notifications, Alerts, Alarms | ✅ Yes (must be idempotent) |
| **At Most Once** | Event may not be processed | Telemetry, Metrics, Logs | ✅ Yes |

### EREN Decision Table

```
EVENT TYPE                    │ DELIVERY      │ IDEMPOTENT?
─────────────────────────────┼───────────────┼─────────────
PHI Access                   │ Exactly Once  │ Required
Clinical Decision            │ Exactly Once  │ Required
Audit Log                    │ Exactly Once  │ Required
Device Alarm (CRITICAL)       │ At Least Once │ Required
Device Alarm (WARNING)       │ At Most Once  │ Not required
Notification                 │ At Least Once │ Required
Metrics                      │ At Most Once  │ Not required
Session Created              │ Exactly Once  │ Required
Recommendation Accepted      │ At Least Once │ Required
```

---

## Event Schema

### Base Event

```python
@dataclass(frozen=True)
class ERENEvent:
    """Base event for all EREN events."""
    
    # Identity
    event_id: str              # UUID v7 (time-ordered)
    event_type: str            # "patient.admitted"
    event_version: str         # "1.0"
    
    # Temporal
    occurred_at: datetime      # When event happened
    published_at: datetime     # When event was published
    processed_at: datetime | None  # When event was processed
    
    # Context
    tenant_id: str            # Multi-tenant isolation
    correlation_id: str | None # For tracing
    causation_id: str | None   # What caused this event
    
    # Source
    source_service: str        # Which service published
    source_host: str | None
    
    # Content
    payload: dict             # Event-specific data
    
    # Metadata
    metadata: dict             # Tags, headers
```

### Example: Patient Admitted

```python
@dataclass(frozen=True)
class PatientAdmitted(ERENEvent):
    """Patient admitted to hospital."""
    
    event_type: str = "clinical.patient.admitted"
    event_version: str = "1.0"
    
    payload: dict = field(default_factory=lambda: {
        "patient_id": str,
        "mrn": str,  # Medical Record Number
        "admission_type": str,  # emergency, elective, transfer
        "bed_id": str | None,
        "attending_physician_id": str,
        "department": str,
        "admission_reason": str,
        "icd10_codes": list[str],  # Initial diagnoses
        "allergies": list[str],
        "consent_status": str,
    })
```

### Example: Device Alarm

```python
@dataclass(frozen=True)
class DeviceAlarm(ERENEvent):
    """Medical device generated an alarm."""
    
    event_type: str = "biomedical.device.alarm"
    event_version: str = "1.0"
    
    payload: dict = field(default_factory=lambda: {
        "device_id": str,
        "device_type": str,  # monitor, ventilator, pump
        "alarm_type": str,  # critical, warning, info
        "alarm_code": str,
        "severity": str,  # 1-5
        "patient_id": str | None,
        "bed_id": str | None,
        "alarm_value": float | None,
        "threshold": float | None,
        "timestamp": str,  # ISO 8601
        "acknowledged": bool,
        "acknowledged_by": str | None,
    })
```

---

## Error Handling

### Dead Letter Queue (DLQ)

```
┌─────────────────────────────────────────────────────────────┐
│                    EVENT PROCESSING                            │
│                                                              │
│  Event Bus                                                   │
│      ↓                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Event Processor                           │   │
│  │                                                       │   │
│  │  try:                                                  │   │
│  │      process(event)                                    │   │
│  │  except RetryableError:                                │   │
│  │      retry_with_backoff()                              │   │
│  │  except NonRetryableError:                            │   │
│  │      send_to_dlq()  ← ← ← ← ← ← ← ← ← ← ← ← ← ←    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  DLQ                                                         │
│      ↓                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Dead Letter Queue                                    │   │
│  │  ├── Original event                                  │   │
│  │  ├── Error details                                    │   │
│  │  ├── Retry count                                     │   │
│  │  ├── First failure timestamp                          │   │
│  │  └── Last failure timestamp                           │   │
│  │                                                       │   │
│  │  Alert if: DLQ depth > 100 OR DLQ age > 1 hour      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Retry Policy

```python
@dataclass
class RetryPolicy:
    """Retry configuration per event type."""
    
    # Critical events (Exactly Once)
    PHI_ACCESS: RetryConfig = RetryConfig(
        max_retries=5,
        backoff_multiplier=2,
        initial_delay_ms=100,
        max_delay_ms=30000,
        jitter=True,
        retryable_errors=["timeout", "connection_error"],
    )
    
    # Important events (At Least Once)
    ALARM: RetryConfig = RetryConfig(
        max_retries=3,
        backoff_multiplier=1.5,
        initial_delay_ms=500,
        max_delay_ms=10000,
        jitter=True,
        retryable_errors=["timeout", "connection_error", "service_unavailable"],
    )
    
    # Non-critical events (At Most Once)
    METRICS: RetryConfig = RetryConfig(
        max_retries=0,  # No retries
    )
```

### Error Classification

```python
class RetryableError(Exception):
    """Error that should be retried."""
    pass

class NonRetryableError(Exception):
    """Error that should go directly to DLQ."""
    pass

# Examples
class SchemaValidationError(NonRetryableError):
    """Malformed event - cannot be fixed by retry."""
    pass

class ServiceUnavailableError(RetryableError):
    """Temporary service failure - retry may fix."""
    pass

class DuplicateEventError(NonRetryableError):
    """Event already processed - idempotency check."""
    pass

class TenantNotFoundError(NonRetryableError):
    """Invalid tenant - cannot be fixed by retry."""
    pass
```

---

## Idempotency

### Why Idempotency Matters

```
WITHOUT IDEMPOTENCY:
Event A ──→ Process ──→ Database (Patient created)
Event A ──→ Process ──→ Database (DUPLICATE! Patient created again)

WITH IDEMPOTENCY:
Event A ──→ Check: Already processed? ──→ Skip (return success)
Event A ──→ Check: Already processed? ──→ Skip (return success)
```

### Implementation

```python
async def process_event(event: ERENEvent) -> None:
    """Process event with idempotency."""
    
    # Check if already processed
    processed = await idempotency_store.exists(event.event_id)
    if processed:
        logger.info(f"Event {event.event_id} already processed, skipping")
        return
    
    try:
        # Process the event
        await handle_event(event)
        
        # Mark as processed (atomic)
        await idempotency_store.set(event.event_id, processed_at=datetime.now())
        
    except Exception as e:
        # Error handling
        if is_retryable(e):
            raise
        else:
            await send_to_dlq(event, error=e)
            raise

# Idempotency store (Redis)
class IdempotencyStore:
    """Stores processed event IDs with TTL."""
    
    TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days (HIPAA)
    
    async def exists(self, event_id: str) -> bool:
        return await self.redis.exists(f"idempotency:{event_id}")
    
    async def set(self, event_id: str, processed_at: datetime) -> None:
        await self.redis.setex(
            f"idempotency:{event_id}",
            self.TTL_SECONDS,
            json.dumps({"processed_at": processed_at.isoformat()})
        )
```

---

## Event Versioning

### Schema Evolution

```
v1.0: {"patient_id": "123", "name": "John"}
v1.1: {"patient_id": "123", "name": "John", "email": "john@email.com"}  ← ADD
v2.0: {"patient_uuid": "abc", "full_name": "John Doe"}  ← BREAKING
```

### Version Handling

```python
class EventVersionHandler:
    """Handles event schema versioning."""
    
    SCHEMA_REGISTRY = {
        "clinical.patient.admitted": {
            "1.0": PatientAdmittedV1,
            "1.1": PatientAdmittedV1_1,  # Added email
            "2.0": PatientAdmittedV2,     # Breaking change
        }
    }
    
    def deserialize(self, event_type: str, version: str, payload: dict):
        schema_class = self.SCHEMA_REGISTRY.get(event_type, {}).get(version)
        if schema_class is None:
            raise UnknownEventVersion(event_type, version)
        return schema_class(**payload)
    
    def migrate(self, event: ERENEvent) -> ERENEvent:
        """Migrate event to latest version."""
        latest_version = self.get_latest_version(event.event_type)
        if event.event_version == latest_version:
            return event
        
        # Apply migrations sequentially
        migrations = self.get_migrations(event.event_type, latest_version)
        for migration in migrations:
            event = migration.apply(event)
        
        return event
```

---

## Event Replay

### When to Replay

```
✓ Database corruption (replay from healthy source)
✓ Bug in event handler (fix code, replay events)
✓ Service down during event (catch-up replay)
✓ Schema migration (replay old events with new schema)

✗ Business logic change (don't replay, reprocess)
✗ GDPR deletion (events must be deleted, not replayed)
```

### Replay Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EVENT REPLAY                              │
│                                                              │
│  Source: Event Store (immutable)                            │
│      ↓                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Replay Controller                                    │   │
│  │  ├── Filter: event_type, time_range, tenant_id       │   │
│  │  ├── Transform: schema migration                     │   │
│  │  ├── Rate limit: prevent overwhelming downstream    │   │
│  │  └── Dry run: validate before production            │   │
│  └─────────────────────────────────────────────────────┘   │
│      ↓                                                      │
│  Target: Event Handlers (can be different versions)         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Ordering

### Per-Stream Ordering

```
✓ Events within same patient_id are ordered
✓ Events within same device_id are ordered
✗ Events across different patients are NOT ordered

Example:
Patient A: Event A1 → Event A2 → Event A3  ✓ (ordered)
Patient B: Event B1 → Event B2 → Event B3  ✓ (ordered)
Patient A & B interleaved: A1, B1, A2, B2   ✓ (correct)
```

### Implementation

```python
class StreamPartitioner:
    """Partition events by ordering key."""
    
    ORDERING_KEYS = {
        "clinical.patient.*": "patient_id",
        "biomedical.device.*": "device_id",
        "session.*": "session_id",
        "audit.*": "tenant_id",  # All tenant events ordered
    }
    
    def get_partition_key(self, event: ERENEvent) -> str:
        """Get partition key for ordering."""
        pattern = self.get_matching_pattern(event.event_type)
        if pattern is None:
            return event.event_id  # Each event its own partition
        
        key_field = self.ORDERING_KEYS[pattern]
        return event.payload.get(key_field)
```

---

## Retention & Storage

### HIPAA Requirements

```
Hot Storage (Fast access):
├── Events < 30 days
├── Indexed by: tenant_id, event_type, timestamp
└── Storage: SSD-backed database

Cold Storage (Slow access):
├── Events 30 days - 7 years
├── Indexed by: tenant_id, timestamp
└── Storage: Object storage (S3, GCS)

Archival:
├── Events > 7 years
├── Compliance archive
└── Retrieval: On-demand (hours to days)
```

### Retention Config

```python
@dataclass
class RetentionConfig:
    """Event retention by type."""
    
    PHI_ACCESS: RetentionPolicy = RetentionPolicy(
        hot_days=30,
        cold_days=2555,  # 7 years HIPAA
        archive=True,
    )
    
    DEVICE_ALARM: RetentionPolicy = RetentionPolicy(
        hot_days=90,
        cold_days=2555,
        archive=True,
    )
    
    METRICS: RetentionPolicy = RetentionPolicy(
        hot_days=7,
        cold_days=30,
        archive=False,
    )
```

---

## Monitoring

### Key Metrics

```yaml
event_bus:
  events_published_total:
    description: Total events published
    labels: [event_type, service]
  
  events_processed_total:
    description: Total events processed
    labels: [event_type, status]
  
  events_failed_total:
    description: Total events sent to DLQ
    labels: [event_type, error_type]
  
  dlq_depth:
    description: Current DLQ depth
    labels: [event_type]
  
  processing_latency_seconds:
    description: Event processing latency
    labels: [event_type]
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]
  
  retry_count:
    description: Number of retries per event
    labels: [event_type]
```

### Alerts

```yaml
alerts:
  - name: DLQ_Growing
    condition: dlq_depth > 100
    severity: warning
  
  - name: DLQ_Critical
    condition: dlq_depth > 1000
    severity: critical
  
  - name: DLQ_Aging
    condition: dlq_oldest_age_hours > 1
    severity: warning
  
  - name: ProcessingLatencyHigh
    condition: processing_latency_p95 > 5s
    severity: warning
```

---

*EREN Event Architecture v1.0*
*Architecture Board - 2026-07-15*
