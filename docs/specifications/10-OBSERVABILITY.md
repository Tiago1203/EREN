# EREN - Especificación Técnica Completa
## Fase 10: Observabilidad

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  

---

## 1. LOGGING

### 1.1 Log Levels

```
DEBUG: Detailed debugging information
  - SQL queries (dev only)
  - Function entry/exit
  - Variable values (sanitized)

INFO: Normal operation
  - API requests/responses
  - Business events
  - State transitions

WARNING: Potential issues
  - Rate limit approaching
  - Validation failures
  - Performance degradation

ERROR: Errors that need attention
  - Failed operations
  - External service failures
  - Business rule violations

CRITICAL: System-level failures
  - Database unavailable
  - Security incidents
  - Complete service failure
```

### 1.2 Log Format

```json
{
  "timestamp": "2026-07-15T14:30:00.123Z",
  "level": "INFO",
  "service": "incident-service",
  "version": "1.0.0",
  "environment": "production",
  
  "trace_id": "abc123def456",
  "span_id": "xyz789",
  "correlation_id": "corr-uuid",
  "tenant_id": "tenant-uuid",
  
  "message": "Incident created successfully",
  "context": {
    "incident_id": "inc-uuid",
    "action": "create",
    "duration_ms": 145
  },
  
  "user": {
    "id": "user-uuid",
    "roles": ["biomedical_engineer"]
  },
  
  "request": {
    "method": "POST",
    "path": "/api/v1/incidents",
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

### 1.3 Structured Logging Rules

```
DO:
  - Use structured JSON logs
  - Include correlation_id in every log
  - Include tenant_id in every log
  - Log at appropriate level
  - Include relevant context

DON'T:
  - Log sensitive data (passwords, tokens, PHI)
  - Log stack traces in ERROR (use error tracking)
  - Use string interpolation for log messages
  - Log debug in production
  - Log at CRITICAL for recoverable errors
```

---

## 2. TRACING

### 2.1 Distributed Tracing

```
Trace Structure:
  - Root Span: API request entry
  - Child Spans: Service calls, DB queries, external calls
  - Propagation: W3C Trace Context via headers

Header Format:
  traceparent: 00-{trace-id}-{span-id}-{flags}
  tracestate: tenant=tenant-uuid

Sampling:
  - 100% for errors
  - 10% for normal requests (adjustable)
  - 100% for critical operations
```

### 2.2 Span Naming

```
Pattern: {service}.{operation}

Examples:
  - incident-service.create_incident
  - device-service.get_device
  - recommendation-service.generate
  - postgres.query
  - rabbitmq.publish
  - external.openai.chat
```

---

## 3. METRICS

### 3.1 Business Metrics

```python
# Incident Metrics
INCIDENTS_CREATED = Counter(
    "incidents_created_total",
    "Total incidents created",
    ["tenant_id", "priority", "category", "device_type"]
)

INCIDENTS_RESOLVED = Counter(
    "incidents_resolved_total",
    "Total incidents resolved",
    ["tenant_id", "priority", "resolution_type"]
)

INCIDENT_RESOLUTION_TIME = Histogram(
    "incident_resolution_time_hours",
    "Time to resolve incidents",
    ["tenant_id", "priority", "category"],
    buckets=[1, 4, 8, 24, 48, 72, 168, 336]  # hours
)

INCIDENT_SLA_BREACH_RATE = Gauge(
    "incident_sla_breach_rate",
    "Percentage of incidents breaching SLA",
    ["tenant_id", "priority"]
)

# Device Metrics
DEVICES_REGISTERED = Counter(
    "devices_registered_total",
    "Total devices registered",
    ["tenant_id", "device_type", "risk_class"]
)

DEVICE_UPTIME = Gauge(
    "device_uptime_percentage",
    "Device uptime percentage",
    ["tenant_id", "device_id", "device_type"]
)

DEVICE_CALIBRATION_DUE = Gauge(
    "devices_calibration_due",
    "Devices with calibration due",
    ["tenant_id", "device_type"]
)

# Recommendation Metrics
RECOMMENDATIONS_GENERATED = Counter(
    "recommendations_generated_total",
    "Total recommendations generated",
    ["tenant_id", "category", "urgency", "confidence_level"]
)

RECOMMENDATION_ACCEPTANCE_RATE = Gauge(
    "recommendation_acceptance_rate",
    "Percentage of recommendations accepted",
    ["tenant_id", "category", "urgency"]
)

RECOMMENDATION_CONFIDENCE_ACCURACY = Gauge(
    "recommendation_confidence_accuracy",
    "Accuracy of AI confidence vs actual accuracy",
    ["tenant_id", "category"],
    buckets=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
)

# AI Metrics
AI_LATENCY = Histogram(
    "ai_generation_latency_seconds",
    "Time to generate AI response",
    ["tenant_id", "capability", "model"]
)

AI_ERROR_RATE = Counter(
    "ai_errors_total",
    "Total AI generation errors",
    ["tenant_id", "error_type", "model"]
)

TOKEN_USAGE = Counter(
    "ai_tokens_used_total",
    "Total tokens used",
    ["tenant_id", "model", "token_type"]  # token_type: input|output
)
```

### 3.2 System Metrics

```python
# Infrastructure
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "path", "status_code", "service"]
)

DATABASE_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["operation", "table"]
)

MESSAGE_BROKER_LATENCY = Histogram(
    "message_broker_latency_seconds",
    "Message publish/consume latency",
    ["exchange", "routing_key"]
)

# Health
SERVICE_HEALTH = Gauge(
    "service_health",
    "Service health status (1=healthy, 0=unhealthy)",
    ["service"]
)

DEPENDENCY_HEALTH = Gauge(
    "dependency_health",
    "Dependency health status",
    ["dependency", "type"]
)

# Resources
MEMORY_USAGE = Gauge(
    "memory_usage_bytes",
    "Memory usage",
    ["service", "pod"]
)

CPU_USAGE = Gauge(
    "cpu_usage_percent",
    "CPU usage percentage",
    ["service", "pod"]
)
```

---

## 4. ALERTING

### 4.1 Alert Definitions

```yaml
# Critical Alerts
- alert: IncidentCriticalSLABreach
  expr: incident_sla_breach_rate > 0.1
  for: 5m
  labels: [severity: critical]
  annotations:
    summary: "Critical SLA breach rate above 10%"
    dashboard: "incidents/sla"

- alert: AIErrorRateHigh
  expr: rate(ai_errors_total[5m]) / rate(ai_requests_total[5m]) > 0.05
  for: 5m
  labels: [severity: critical]
  annotations:
    summary: "AI error rate above 5%"

- alert: DatabaseUnavailable
  expr: service_health{dependency="postgres"} == 0
  for: 1m
  labels: [severity: critical]
  annotations:
    summary: "Database is unavailable"

# Warning Alerts
- alert: IncidentResolutionTimeHigh
  expr: histogram_quantile(0.95, incident_resolution_time_hours) > 72
  for: 15m
  labels: [severity: warning]
  annotations:
    summary: "P95 incident resolution time above 72 hours"

- alert: DeviceCalibrationOverdue
  expr: devices_calibration_due > 10
  for: 1h
  labels: [severity: warning]
  annotations:
    summary: "More than 10 devices have overdue calibration"

- alert: RecommendationAccuracyDrift
  expr: abs(recommendation_confidence_accuracy - 0.8) > 0.15
  for: 1h
  labels: [severity: warning]
  annotations:
    summary: "Recommendation confidence accuracy drifting"
```

---

*Documento generado para implementación. Fase 10 completa.*
