"""EPIC 4: Monitoring & Observability.

Provides complete observability stack:
- Prometheus metrics (counters, gauges, histograms)
- Custom business metrics (HTTP, DB, AI, clinical)
- Structured JSON logging
- Log aggregation
- Distributed tracing (OpenTelemetry-style)
- Alert management with notification channels
- SLI/SLO tracking and error budgets
- Operations dashboards

Dependencies:
- EPIC 3 (High Availability): HA metrics, failover events
- EPIC 2 (Multi-Tenant): tenant_id labels throughout
- EPIC 1 (Audit): audit event metrics
"""
from core.PHASE_7.observability.metrics import (
    PrometheusMetricsRegistry, Counter, Gauge, Histogram,
    get_registry, register_counter, register_gauge, register_histogram,
    MetricsCollector, get_metrics_collector,
)
from core.PHASE_7.observability.logging import (
    StructuredLogger, LogLevel, get_logger, LogAggregator, LogEntry, LogSource,
)
from core.PHASE_7.observability.tracing import (
    DistributedTracer, Span, SpanKind, SpanStatus, get_tracer,
)
from core.PHASE_7.observability.alerts import (
    AlertManager, AlertRule, Alert, AlertSeverity, AlertStatus,
    AlertChannel, Incident,
    NotificationChannel, EmailChannel, SlackChannel,
    PagerDutyChannel, WebhookChannel, AlertPayload,
    create_channel,
)
from core.PHASE_7.observability.dashboards import (
    OperationsDashboard, DashboardData,
    SLOManager, SLO, SLOStatus, SLIMetric, SLOStatusRecord,
    get_slo_manager,
)
