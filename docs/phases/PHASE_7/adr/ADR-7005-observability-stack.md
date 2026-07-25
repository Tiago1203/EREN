# ADR-7005: Observability Stack

## Status
**Implemented** ✅ (Julio 2025)

## Context
EREN needs comprehensive observability for production 24/7 operations across multiple hospital tenants. Regulatory requirements (HIPAA, FDA CFR Part 11) demand audit trails and operational transparency.

## Decision
Three pillars of observability:

### 1. Metrics — Prometheus-compatible
- **PrometheusMetricsRegistry**: Counters, Gauges, Histograms
- **MetricsCollector**: HTTP, DB, AI/LLM, clinical, HA metrics
- Labels: tenant_id throughout (EPIC 2 integration)
- Integration: EPIC 3 (health checks, failover, scaling events)

### 2. Logging — Structured JSON
- **StructuredLogger**: JSON format, correlation IDs
- **LogAggregator**: Centralized ingestion, query/filter
- Sources: application, API, database, infrastructure, security, audit
- Integration: EPIC 1 (audit events), EPIC 2 (tenant operations)

### 3. Tracing — OpenTelemetry-style
- **DistributedTracer**: Spans, trace context propagation
- Multi-service traces with tenant_id
- Performance analysis

### 4. Alerting
- **AlertManager**: 8 default rules (error rate, latency, CPU, memory, quota, failover)
- **Notification channels**: Email, Slack, PagerDuty, Webhook
- **SLOManager**: 6 SLOs (availability 99.9%, latency P95 99%, error rate 99.5%)

### 5. Dashboards
- **OperationsDashboard**: System overview, service status, Grafana JSON
- Multi-tenant aggregation
- Grafana-ready JSON output

## Consequences
### Positive
- Complete observability for 24/7 operations
- Multi-tenant metric isolation via labels
- Prometheus/Grafana-compatible
- HIPAA-compliant audit trail
### Negative
- Increased storage for metrics/logs
- Alert fatigue if not tuned
- Complexity in multi-tenant correlation
