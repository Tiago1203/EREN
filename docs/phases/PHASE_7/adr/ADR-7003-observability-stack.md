# ADR-7003: Observability Stack Selection

## Status
Proposed

## Context
EREN needs comprehensive observability for 24/7 hospital operations with SLA guarantees.

## Decision
We adopt the following observability stack:

1. **Metrics** - Prometheus + Grafana
2. **Logging** - Structured JSON logs → ELK Stack (Elasticsearch, Logstash, Kibana)
3. **Tracing** - OpenTelemetry with Jaeger/ Tempo backend
4. **Alerting** - Alertmanager + PagerDuty integration

## Consequences
### Positive
- Industry-standard tools with good ecosystem
- Grafana dashboards for clinical and operational metrics
- OpenTelemetry vendor-agnostic
- Centralized log correlation with trace IDs

### Negative
- Multiple systems to operate
- Storage costs for metrics and traces
- Dashboard maintenance overhead
- Alert fatigue risk without proper tuning
