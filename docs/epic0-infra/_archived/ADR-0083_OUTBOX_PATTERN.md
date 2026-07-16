# ADR-0083: Outbox Pattern for Event Publishing

**Status:** ACCEPTED

**Date:** 2026-07-16

**Deciders:** Architecture Board

---

## Context

When EREN processes a business transaction (e.g., a new incident is created), it must:
1. **Commit the transaction** to PostgreSQL (incident record)
2. **Publish an event** to Kafka (IncidentCreated)

The naive approach — commit to DB then publish to Kafka — creates a problem: **if Kafka publish fails after DB commit, the event is lost.** The system has the data but no event, breaking downstream consumers.

We evaluated:
1. **Outbox Pattern** (transactional outbox)
2. **Change Data Capture (CDC)** (Debezium → Kafka)
3. **Dual write** (commit both in same transaction) — technically impossible across different systems

---

## Decision

**We will implement the Outbox Pattern for all event publishing.**

Every domain service that publishes events will write to an `outbox` table in PostgreSQL within the same transaction as the business entity. A separate process (the **Outbox Publisher**) reads from the outbox table and publishes to Kafka.

CDC (Debezium) will be evaluated as an alternative for EPIC 6 (Integrations) where high-throughput CDC from external databases is needed.

---

## Reasons

### Outbox Pattern (Chosen)

1. **Atomicity:** Event and entity are committed in the same DB transaction. No event loss possible
2. **Simplicity:** Standard PostgreSQL + a background worker. No additional infrastructure beyond what we already have
3. **Idempotency:** The outbox publisher marks events as "published" with a version column. Can be safely re-run
4. **Testing:** Events can be inspected directly from the outbox table — easier to test
5. **Transactional ordering:** Events are published in the same order as the transactions that created them
6. **Multi-tenant safe:** Each outbox entry is tenant-scoped via `tenant_id`
7. **Epic 0 alignment:** `EREN_EVENT_ARCHITECTURE.md` specifies at-least-once delivery — outbox achieves this

### CDC / Debezium (Deferred)

- Adds infrastructure complexity (Debezium connector, Kafka Connect)
- Better suited for **reading from external databases** (e.g., hospital HIS system)
- Not needed for our own PostgreSQL — outbox is sufficient
- May be reconsidered for EPIC 6 when integrating with external HL7/FHIR systems

### Dual Write (Rejected)

- Not possible: cannot commit to both PostgreSQL and Kafka in the same distributed transaction without a 2PC coordinator
- Creates split-brain scenarios

---

## Consequences

### Positive

- Guaranteed at-least-once delivery: if the DB transaction commits, the event will be published
- No distributed transaction coordinator needed
- Events visible in the outbox table for debugging and testing
- Retries are idempotent (same event ID = no duplicate publish)

### Negative

- **Eventual delay:** Events are not published immediately — there's a small delay (typically < 1 second) until the outbox publisher picks them up
- **Infrastructure:** Requires the outbox publisher process (a Celery task or separate worker)
- **At-least-once, not exactly-once:** Consumers must handle duplicates via idempotency keys

### Mitigations

- Outbox publisher runs every 100ms (configurable)
- For critical alerts (P0), use synchronous notification (email/SMS) in addition to events
- All consumers must be idempotent (use `event_id` as deduplication key)

---

## Implementation

### 1. Outbox Table

```python
# Every bounded context has its own schema with an outbox table
class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    aggregate_type = Column(String(100), nullable=False)  # e.g., "Incident"
    aggregate_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String(200), nullable=False)       # e.g., "IncidentCreated"
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)                # Event data
    version = Column(Integer, nullable=False, default=1)   # For idempotency
    created_at = Column(TimestampTZ, nullable=False, default=utcnow)
    published_at = Column(TimestampTZ, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    error = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_outbox_unpublished", "tenant_id", "published_at", "id",
              postgresql_where=(Column("published_at") == None)),  # noqa
    )
```

### 2. Unit of Work Integration

```python
class UnitOfWork:
    async def __aenter__(self):
        self._conn = await get_connection()
        await set_tenant_context(self._conn, self.tenant_id)
        self._transaction = self._conn.transaction()
        await self._transaction.start()
        self.incidents = IncidentRepository(self._conn, self.outbox)
        return self

    async def commit(self):
        # Outbox entries are written to the same transaction
        # They only become visible to the publisher after commit
        await self._transaction.commit()

    async def rollback(self):
        await self._transaction.rollback()
```

### 3. Publishing from the Unit of Work

```python
class IncidentRepository:
    def __init__(self, connection, outbox: list[OutboxEntry]):
        self._conn = connection
        self._outbox = outbox

    async def create(self, incident: Incident) -> Incident:
        # Business logic
        await self._conn.execute(
            incidents_table.insert().values(...)
        )

        # Add to outbox — committed in the SAME transaction
        self._outbox.append(OutboxEntry(
            aggregate_type="Incident",
            aggregate_id=incident.id,
            event_type="IncidentCreated",
            payload={
                "incident_id": str(incident.id),
                "tenant_id": str(self.tenant_id),
                "device_id": str(incident.device_id),
                "priority": incident.priority.value,
                "occurred_at": incident.occurred_at.isoformat(),
            }
        ))

        return incident
```

### 4. Outbox Publisher (Background Task)

```python
# eren-worker/src/tasks/outbox_publisher.py
from celery import shared_task
from kafka import KafkaProducer
import asyncio

@shared_task(name="outbox.publish")
def publish_outbox_events(batch_size: int = 100):
    """Reads unpublished events from outbox and publishes to Kafka."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_publish_batch(batch_size))
    finally:
        loop.close()

async def _publish_batch(batch_size: int):
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKERS,
        value_serializer=lambda v: json.dumps(v).encode(),
    )

    # SELECT unpublished events ordered by created_at
    events = await db.fetch("""
        SELECT id, aggregate_type, aggregate_id, event_type,
               tenant_id, payload, version
        FROM outbox_events
        WHERE published_at IS NULL
          AND retry_count < 5
        ORDER BY created_at
        LIMIT $1
        FOR UPDATE SKIP LOCKED
    """, batch_size)

    for event in events:
        topic = f"eren-{event['aggregate_type'].lower()}s.events"

        try:
            await producer.send_and_wait(
                topic,
                value=event["payload"],
                headers=[
                    ("event_id", str(event["id"]).encode()),
                    ("version", str(event["version"]).encode()),
                ]
            )

            # Mark as published
            await db.execute("""
                UPDATE outbox_events
                SET published_at = NOW(), error = NULL
                WHERE id = $1
            """, event["id"])

        except Exception as e:
            await db.execute("""
                UPDATE outbox_events
                SET retry_count = retry_count + 1, error = $2
                WHERE id = $1
            """, event["id"], str(e))
```

### 5. Celery Beat Schedule

```python
# celeryconfig.py
beat_schedule = {
    "outbox-publish-every-100ms": {
        "task": "outbox.publish",
        "schedule": 0.1,  # Every 100ms
        "kwargs": {"batch_size": 100},
    },
    "outbox-cleanup-daily": {
        "task": "outbox.cleanup",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
        "kwargs": {"retention_days": 30},
    },
}
```

---

## Idempotency

Every event has a unique `event_id` (UUID). The outbox publisher uses:

```python
# Kafka message header: event_id
headers = [("event_id", str(event["id"]).encode())]

# Consumer deduplication (every consumer implements this)
async def consume(event, headers):
    event_id = headers.get("event_id")
    if await is_event_processed(event_id):
        return  # Already processed, skip
    await process_event(event)
    await mark_event_processed(event_id)
```

---

## DLQ for Failed Events

If an event fails after 5 retries:

```python
# After 5 failures, move to DLQ
if event["retry_count"] >= 5:
    await move_to_dlq(event)
    await mark_as_dlq(event["id"])

    # Alert
    await send_alert(
        severity="P1",
        message=f"Outbox event {event['id']} moved to DLQ after 5 retries",
        context={"event_type": event["event_type"]}
    )
```

---

## Testing the Outbox

```python
async def test_incident_creation_creates_outbox_event():
    async with UnitOfWork(tenant_id=TEST_TENANT) as uow:
        incident = await uow.incidents.create(
            device_id=TEST_DEVICE_ID,
            priority=Priority.HIGH,
        )
        await uow.commit()

    # Verify: incident was created
    assert incident.id is not None

    # Verify: outbox entry was created
    outbox_entries = await db.fetch(
        "SELECT * FROM outbox_events WHERE aggregate_id = $1",
        incident.id
    )
    assert len(outbox_entries) == 1
    assert outbox_entries[0]["event_type"] == "IncidentCreated"
```

---

*Architecture Board - 2026-07-16*
