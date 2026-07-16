# ADR-0081: Kafka as Primary Message Broker

**Status:** ACCEPTED

**Date:** 2026-07-16

**Deciders:** Infrastructure Team, Architecture Board

---

## Context

EREN publishes and consumes events across bounded contexts. The system needs a message broker that:
- Supports event streaming with durability (events must not be lost)
- Handles high throughput (thousands of device events per second from MQTT)
- Provides replay capability (new consumers should be able to read historical events)
- Supports multiple consumer groups per topic
- Integrates with the observability stack (metrics on consumer lag)

We evaluated **Apache Kafka** and **RabbitMQ**.

---

## Decision

**We will use Apache Kafka as the primary message broker.**

Celery will use Kafka as its broker via `celery[kafka]`.

RabbitMQ will NOT be used as the primary broker. It may be used for specific lightweight use cases (e.g., internal pub/sub for real-time notifications) but not as the event backbone.

---

## Reasons

### Apache Kafka (Chosen)

1. **Event replay:** New services can consume from the beginning of a topic. Critical for onboarding new contexts or recovering from failures
2. **Throughput:** Designed for high-throughput streaming (100K+ messages/second per broker). Handles MQTT device events at scale
3. **Consumer groups:** Independent consumer groups per service, each with own offset. Multiple CDSS services can consume the same events independently
4. **Durability:** Messages are replicated (3 replicas by default). P0 events (alarms, CDS) are not lost
5. **Consumer lag metrics:** Native Prometheus metrics for monitoring consumer lag. Critical for SLA monitoring
6. **Schema registry:** Avro/JSON Schema enforcement prevents schema drift
7. **Log compaction:** Retain only the latest value per key — enables stateful consumers
8. **Epic 0 alignment:** `EREN_EVENT_ARCHITECTURE.md` specifies "Kafka or equivalent" — this formalizes the choice
9. **Celery support:** `celery-kafka` makes Kafka a first-class Celery broker

### RabbitMQ (Rejected)

1. **No replay:** Once consumed, messages are gone. New services cannot replay historical events
2. **Throughput ceiling:** 50K-100K messages/second requires significant tuning and clustering
3. **Consumer group model:** Exchange-based routing is less suited for event streaming than Kafka's topic-partition model
4. **Operational complexity of clustering:** RabbitMQ clustering requires careful configuration and monitoring
5. **Consumer lag:** No native consumer lag metrics without plugins
6. **Schema management:** No native schema registry integration
7. **Acknowledgment complexity:** Negative acknowledgments (nack) with requeue creates duplicate processing risk

---

## Consequences

### Positive

- Full event replay for any bounded context
- High throughput for device telemetry from MQTT integration
- Native Prometheus metrics for consumer lag monitoring
- Schema registry integration prevents event schema drift
- Event sourcing capability for audit trail
- Multiple independent consumers per topic

### Negative

- **Operational complexity:** Kafka requires more operational expertise than RabbitMQ
- **Cost:** Kafka clusters (managed or self-hosted) cost more than RabbitMQ
- **Latency:** Kafka has slightly higher per-message latency than RabbitMQ for very low-throughput scenarios (milliseconds vs microseconds)
- **Overhead for small queues:** Kafka is overkill for simple point-to-point queues

### Mitigations

- Use **Confluent Cloud** (managed Kafka) for production — reduces operational burden
- Use **Kraft mode** for development/staging (no Zookeeper needed)
- Separate Kafka cluster from Celery workers — workers use Celery abstraction, not Kafka directly
- Use Kafka **consumer groups** for independent scaling

---

## Kafka Topic Naming Convention

```
{domain}.{bounded_context}.{event_type}

Examples:
eren-clinical.patients.created
eren-clinical.cds.recommendation_generated
eren-biomedical.device.telemetry
eren-biomedical.alarm.critical
eren-hospital.capacity.bed_updated
eren-system.audit.access
```

### DLQ Topics

```
eren-dlq.{domain}.{bounded_context}
```

### Topic Configuration

```yaml
# retention
clinical events:    30 days   (CDSS needs recent history)
biomedical events:  90 days   (compliance for device records)
hospital events:    30 days
audit events:       7 years   (HIPAA compliance)

# replication factor
production: 3
staging:    1

# partitions
default: 6
high-volume (telemetry): 12
```

---

## Integration with Celery

Celery workers use Kafka as the transport broker:

```python
# celeryconfig.py
broker_url = "kafka://kafka:9092"
result_backend = "redis://redis:6379/1"

# Kafka-specific settings
kafka_consumer_config = {
    "bootstrap.servers": "kafka:9092",
    "group.id": "eren-worker",
    "auto.offset.reset": "earliest",
}
```

This provides:
- Celery tasks as the programming model (familiar for Python devs)
- Kafka as the transport (high throughput, durability)
- Redis for task results (Celery backend)

---

## Schema Management

All Kafka messages use **JSON Schema** with Confluent Schema Registry:

```python
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSchema

# Register schema on topic creation
schema = JSONSchema("""
{
  "type": "object",
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "tenant_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string"},
    "occurred_at": {"type": "string", "format": "date-time"},
    "payload": {"type": "object"}
  }
}
""")
```

Schema evolution: **BACKWARD_COMPATIBLE** only. New fields must have defaults.

---

## Monitoring

```yaml
# Kafka consumer lag (Prometheus)
kafka_consumer_lag_consumer_group_topic_partition
kafka_topic_messages_total
kafka_consumer_records_lag_max

# Alert thresholds
- Consumer lag > 10,000 messages: WARNING
- Consumer lag > 100,000 messages: CRITICAL
- Broker disk > 80%: WARNING
- Broker disk > 90%: CRITICAL
```

---

## Related ADRs

- ADR-0083: Outbox Pattern for Event Publishing
- ADR-0031: Prometheus + Grafana Observability (Epic 0)

---

*Infrastructure Team, Architecture Board - 2026-07-16*
