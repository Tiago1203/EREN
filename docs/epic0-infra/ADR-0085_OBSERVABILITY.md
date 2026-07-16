# ADR-0085: Observability Stack

**Status:** ACCEPTED

**Date:** 2026-07-16

**Deciders:** Infrastructure Team

---

## Context

EREN must be observable in production. When a system fails or degrades, the team needs to:
- **Metrics:** Understand system health (CPU, memory, request rates, error rates, consumer lag)
- **Traces:** Follow a request through the entire system (API → Kafka → Worker → DB)
- **Logs:** Investigate errors and audit access (PHI access, policy violations)

Epic 0 ADR-0031 mentions "Prometheus + Grafana Observability" but does not define the complete stack.

We evaluated the complete observability requirements:

| Layer | Requirement | Options Considered |
|-------|------------|--------------------|
| Metrics | CPU, memory, request latency, business metrics | Prometheus + Grafana |
| Tracing | Distributed request tracing | Jaeger, Zipkin |
| Logs | Centralized log aggregation | Loki, ELK (Elasticsearch) |
| Alerts | Alert routing and management | Alertmanager, PagerDuty |
| APM | Application performance monitoring | OpenTelemetry + backend |

---

## Decision

**We will use the OpenTelemetry-native observability stack:**

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus + Grafana | System + application metrics |
| Tracing | Jaeger (OTLP) | Distributed tracing |
| Logs | Loki + Grafana | Log aggregation |
| Alerts | Alertmanager + PagerDuty | Alert routing |
| Instrumentation | OpenTelemetry SDK | Auto-instrumentation |

Deployment:
- **Production:** Managed Prometheus (AWS/GCP), Grafana Cloud
- **Staging/Development:** Self-hosted on Kubernetes via Helm

---

## Reasons

### Why Prometheus + Grafana (Metrics)

1. **OpenTelemetry compatible:** Prometheus is the recommended backend for OTel metrics
2. **Native K8s support:** Prometheus Operator manages scraping automatically
3. **Rich ecosystem:** Pre-built dashboards for Kafka, PostgreSQL, Celery, FastAPI
4. **Grafana:** Single pane of glass for metrics + logs + traces
5. **Epic 0 ADR-0031:** Explicitly referenced

### Why Jaeger (Tracing)

1. **OTLP native:** Direct integration with OpenTelemetry SDK
2. **Single pane of glass:** Grafana can query Jaeger directly (no separate UI)
3. **Kubernetes native:** Jaeger Operator for K8s deployment
4. **Kafka tracing:** OpenTelemetry Kafka instrumentation for tracing across event bus

### Why Loki (Logs)

1. **Grafana integration:** Logs + metrics + traces in one UI
2. **Label-based:** Structured labels (tenant_id, service, level) make log queries fast
3. **Cost-effective:** Object storage backend (S3), not Elasticsearch
4. **Prometheus co-location:** Same deployment pattern, same team knowledge
5. **Lightweight:** Unlike ELK, Loki has minimal operational overhead

### Why NOT Elasticsearch / ELK

1. **Operational overhead:** Elasticsearch requires significant tuning and resources
2. **Cost:** Elastic Cloud or self-managed ES is expensive
3. **Overkill for our scale:** Loki is purpose-built for cloud-native log aggregation

### Why OpenTelemetry SDK

1. **Vendor-neutral:** Swap backends without re-instrumenting
2. **Auto-instrumentation:** FastAPI, SQLAlchemy, Kafka, Redis — auto-instrumented with minimal code
3. **Single library:** Metrics + traces + logs (with OTel SDK 1.0+)
4. **Future-proof:** Industry standard, adopted by all major vendors

---

## Consequences

### Positive

- Complete observability: metrics + traces + logs in one UI (Grafana)
- OpenTelemetry: vendor-neutral, future-proof
- Kubernetes-native: operators manage deployment and configuration
- Cost-effective: Loki on S3 is cheaper than ELK
- Auto-instrumentation reduces developer effort

### Negative

- **Loki operational knowledge:** Team must learn PromQL-like LogQL
- **Trace sampling:** Need to configure sampling strategy (100% on errors, 5% on success)
- **Storage costs:** Prometheus TSDB + Loki object storage
- **Multiple tools:** 4 components to operate (Prometheus, Grafana, Jaeger, Loki)

### Mitigations

- Use managed services in production (Grafana Cloud, Amazon Managed Prometheus)
- Pre-built Helm values and Grafana dashboards in `infra/`
- Default sampling strategy defined in this ADR

---

## Implementation

### 1. OpenTelemetry SDK Integration

```python
# eren/infrastructure/telemetry.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: "eren-api",
    ResourceAttributes.SERVICE_VERSION: "1.0.0",
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.environ["EREN_ENV"],
})

# Tracing
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)
trace.set_tracer_provider(trace_provider)

# Metrics
metrics_provider = MeterProvider(resource=resource)
metrics.set_meter_provider(metrics_provider)

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
```

### 2. Custom Business Metrics

```python
# eren/application/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics (auto-instrumented)
# CDS metrics (custom)
cds_recommendations_total = Counter(
    "eren_cds_recommendations_total",
    "CDS recommendations generated",
    ["decision_type", "confidence_band", "tenant_id"]
)

cds_recommendation_duration = Histogram(
    "eren_cds_recommendation_duration_seconds",
    "CDS recommendation generation time",
    ["decision_type"]
)

# Device metrics
device_events_total = Counter(
    "eren_device_events_total",
    "Device events received",
    ["device_type", "event_type", "tenant_id"]
)

alarm_escalations_total = Counter(
    "eren_alarm_escalations_total",
    "Alarm escalations triggered",
    ["alarm_type", "escalation_level", "tenant_id"]
)

# Multi-tenant gauges
active_patients = Gauge(
    "eren_active_patients",
    "Active patients per tenant",
    ["tenant_id"]
)

open_incidents = Gauge(
    "eren_open_incidents",
    "Open incidents per tenant and priority",
    ["tenant_id", "priority"]
)

# Usage in code
def record_cds_recommendation(decision_type: str, confidence: float):
    band = "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
    cds_recommendations_total.labels(
        decision_type=decision_type,
        confidence_band=band,
        tenant_id=current_tenant_id
    ).inc()
```

### 3. Tracing Configuration

```python
# Kafka consumer tracing
from opentelemetry.instrumentation.kafka_python import KafkaConsumerInstrumentor

KafkaConsumerInstrumentor().instrument()
KafkaProducerInstrumentor().instrument()

# Celery tracing
from opentelemetry.instrumentation.celery import CeleryInstrumentor
CeleryInstrumentor().instrument()
```

### 4. Sampling Strategy

```python
# eren/infrastructure/sampling.py
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    SamplingResult,
    Decision,
)

# Production sampling
SAMPLING_RATE = 0.05  # 5% of successful traces

sampler = ParentBased(root=TraceIdRatioBased(SAMPLING_RATE))

# Always sample:
# - 100% of errors (via trace.filter or exporter)
# - Traces with "critical" flag
# - All traces in development/staging
```

### 5. Grafana Dashboards

Pre-built dashboards in `infra/grafana/dashboards/`:

| Dashboard | Panels |
|-----------|--------|
| EREN Overview | Requests/sec, Error rate, Latency P50/P95/P99, Active users |
| API Performance | Endpoint latency, Status codes, Top 10 slow endpoints |
| CDS Quality | Recommendation volume, Confidence distribution, Acceptance rate |
| Kafka Consumers | Consumer lag per group, Messages/sec, Partition rebalancing |
| PostgreSQL | Query latency, Connection pool, Slow queries, RLS enforcement |
| Redis | Memory usage, Hit rate, Connection count |
| Multi-Tenant Health | Per-tenant request rate, Error rate, Latency |
| Celery Workers | Task queue depth, Task duration, Failed tasks |
| Alarm Volume | Alarms by type, Resolution time, Escalation rate |

### 6. Alert Rules

```yaml
# infra/prometheus/alerts/erenalerts.yaml
groups:
  - name: eren-api
    rules:
      - alert: HighErrorRate
        expr: rate(eren_http_requests_total{status_code=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on EREN API"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: histogram_quantile(0.95, eren_http_request_duration_seconds) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High P95 latency"
          description: "P95 latency is {{ $value }}s"

      - alert: CDSLowConfidenceRate
        expr: |
          rate(eren_cds_recommendations_total{confidence_band="low"}[1h]) /
          rate(eren_cds_recommendations_total[1h]) > 0.2
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "High rate of low-confidence CDS recommendations"
          description: "More than 20% of CDS recommendations have low confidence"

      - alert: KafkaConsumerLag
        expr: kafka_consumer_lag_consumer_group_topic_partition > 100000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Kafka consumer lag critical"
          description: "Consumer lag is {{ $value }} messages"

      - alert: MultiTenantIsolationViolation
        expr: |
          rate(eren_cross_tenant_access_attempts_total[1m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Cross-tenant access detected!"
          description: "{{ $value }} cross-tenant access attempts in the last minute"
```

### 7. Loki Log Format

```python
import structlog

# Structured logging with tenant context
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

# Log output (JSON → Loki)
logger = structlog.get_logger()

# Example log entry
logger.info(
    "cds_recommendation_generated",
    tenant_id=str(tenant_id),
    patient_id=str(patient_id),
    device_id=str(device_id),
    decision_type="risk_assessment",
    confidence=0.87,
    trace_id=trace.get_current_span().context.trace_id,
    span_id=trace.get_current_span().context.span_id,
)
```

---

## Alert Routing

```
Alertmanager
    │
    ├── P0 (Critical) ──────────────────► PagerDuty ──► On-call engineer
    │                                        │
    │                                        └── SMS + Phone + Email
    │
    ├── P1 (Warning) ──────────────────────► Slack #alerts-prod
    │
    └── P2 (Info) ────────────────────────► Slack #alerts-info
```

---

*Infrastructure Team - 2026-07-16*
