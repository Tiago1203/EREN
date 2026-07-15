# Event System Review
## EREN OS — Audit 05

---

## Executive Summary

EREN OS implementa un sistema de eventos en `core/events/` con 30 imports detectados en el codebase. El sistema usa EventBus centralizado.

**Event System Score: 58/100**

El sistema de eventos existe pero no está verificado completamente. Faltan features críticas como dead letter queue, retry policies, y tracing.

---

## Event System Components

| Componente | Ubicación | Estado |
|------------|-----------|--------|
| EventBus | core/events/ | Implementado |
| Providers Events | core/providers/events.py | Implementado |
| Workflow Events | core/workflows/events.py | Implementado |
| Biomedical Events | core/biomedical/*/ | Implementado |

---

## EventBus Analysis

### providers/events.py
```python
class EventBus:
    def publish(self, event: str, data: dict): ...
    def subscribe(self, event: str, handler): ...
```

### Usage Stats
- 30 módulos importan eventos
- Publishers: Providers, RAG, Tools
- Subscribers: Audit, Metrics

---

## Critical Issues

### 1. No Dead Letter Queue
**Severidad: ALTA**

Sin handling para eventos fallidos:
- ❌ No retry
- ❌ No DLQ
- ❌ No persistence

### 2. No Event Ordering
**Severidad: MEDIA**

Sin garantía de orden:
- ❌ No sequence numbers
- ❌ No ordering keys
- ❌ No partition keys

### 3. No Event Tracing
**Severidad: MEDIA**

Sin distributed tracing:
- ❌ No trace_id propagation
- ❌ No span context
- ❌ No correlation_id

---

## Event Flow Analysis

### Provider Lifecycle Events
```python
# Probable flujo
ProviderCreated → ProviderRegistered → ProviderReady
                                           ↓
                                     ProviderHealthCheck
                                           ↓
                                     ProviderFailed (on error)
```

### Issues
- ❌ No event schema
- ❌ No versioning
- ❌ No schema validation

---

## Pub/Sub Analysis

### Current Implementation
```
Publisher → EventBus → Subscribers
                    ↓
              (sin filtering)
```

### Issues
- ❌ No topic filtering
- ❌ No wildcard subscriptions
- ❌ No regex patterns

---

## Scalability Analysis

### Current Limitations
- ❌ In-memory only
- ❌ No clustering
- ❌ No partitioning
- ❌ Single-threaded dispatch

### Recommendations for Scale
1. Redis Pub/Sub
2. Kafka for event streaming
3. MQTT for IoT events

---

## Orphan Events

### Detection
- ❌ No monitoring de eventos no consumidos
- ❌ No metrics de consumo
- ❌ No alerting

### Event Categories
| Category | Published | Consumed |
|----------|-----------|----------|
| provider.lifecycle | ✅ | ? |
| provider.metrics | ✅ | ? |
| memory.operations | ✅ | ? |
| rag.pipeline | ✅ | ? |

---

## Event Schema

### Missing Standards
- ❌ No schema registry
- ❌ No JSON Schema
- ❌ No Avro/Protobuf
- ❌ No validation

---

## Recommendations

### 1. Dead Letter Queue
```python
class EventBus:
    def __init__(self):
        self.dlq = DeadLetterQueue()
    
    async def handle_failure(self, event, error):
        await self.dlq.push(event, error)
```

### 2. Event Tracing
```python
class Event:
    trace_id: str
    span_id: str
    correlation_id: str
```

### 3. Event Schema Registry
```python
@dataclass
class ProviderCreatedEvent:
    event_id: str
    provider_id: str
    provider_type: str
    timestamp: datetime
```

### 4. Monitoring
```python
metrics = {
    "events_published_total": Counter(),
    "events_consumed_total": Counter(),
    "events_failed_total": Counter(),
}
```

---

## Conclusion

El sistema de eventos necesita:
1. Dead Letter Queue
2. Event tracing
3. Schema validation
4. Monitoring
5. Persistence

**Recomendación: Implementar DLQ y tracing antes de producción.**

---

*Audit realizado: 2026-07-15*
