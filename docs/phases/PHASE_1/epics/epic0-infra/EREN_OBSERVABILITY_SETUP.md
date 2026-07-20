# EREN Observability Setup Guide
## Prometheus, Grafana, Jaeger, Loki

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Infrastructure Team | Initial |

---

## Purpose

This document provides the detailed setup guide for EREN's observability stack. It complements [`ADR-0085`](../adr/epic0-infra/ADR-0085.md) by providing concrete configuration files and deployment manifests.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Application Layer                          │
│  eren-api (FastAPI) │ eren-worker (Celery)                  │
│                                                              │
│  OpenTelemetry SDK (auto-instrumented)                      │
│  ├── Metrics: prometheus_client                             │
│  ├── Traces: opentelemetry-sdk-trace                        │
│  └── Logs: structlog (JSON → stdout)                        │
└──────────────────────────────┬───────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        OTLP Exporter                 stdout / JSON
                │                             │
                ▼                             ▼
        ┌──────────────────┐         ┌──────────────┐
        │   Prometheus     │         │    Loki      │
        │   (metrics)      │         │   (logs)     │
        └────────┬─────────┘         └──────┬───────┘
                 │                            │
                 ▼                            ▼
        ┌──────────────────┐         ┌──────────────┐
        │    Grafana       │         │   Grafana    │
        │   (dashboards)   │◄────────│   (logs UI)  │
        └────────┬─────────┘         └──────────────┘
                 │
                 ▼
        ┌──────────────────┐
        │    Jaeger        │
        │   (traces)       │
        └──────────────────┘
```

---

## Helm Installation

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

# Install kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace eren-monitoring \
  --create-namespace \
  --values infra/helm/kube-prometheus-stack/values.yaml

# Install Loki
helm install loki grafana/loki \
  --namespace eren-monitoring \
  --values infra/helm/loki/values.yaml

# Install OpenTelemetry Collector
helm install otel-collector open-telemetry/opentelemetry-collector \
  --namespace eren-monitoring \
  --values infra/helm/otel-collector/values.yaml
```

---

## OpenTelemetry Collector Configuration

```yaml
# infra/helm/otel-collector/values.yaml
mode: deployment
config:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

  processors:
    batch:
      timeout: 5s
      send_batch_size: 1024

    memory_limiter:
      check_interval: 1s
      limit_mib: 512

    # Tenant attribute extraction
    resource:
      attributes:
        - action: upsert
          key: tenant.id
          from_attribute: tenant_id

  exporters:
    prometheus:
      endpoint: "0.0.0.0:8889"
      namespace: eren
      const_labels:
        app: eren

    otlp:
      endpoint: "http://jaeger-collector:4317"
      tls:
        insecure: true

    loki:
      endpoint: "http://loki-gateway:3100/loki/api/v1/push"
      labels:
        attributes:
          service.name: service.name
          tenant.id: tenant.id

  service:
    pipelines:
      traces:
        receivers: [otlp]
        processors: [memory_limiter, batch]
        exporters: [otlp]
      metrics:
        receivers: [otlp]
        processors: [memory_limiter, batch]
        exporters: [prometheus]
      logs:
        receivers: [otlp]
        processors: [memory_limiter, batch, resource]
        exporters: [loki]
```

---

## Prometheus Scrape Configuration

```yaml
# infra/helm/kube-prometheus-stack/values.yaml

prometheus:
  prometheusSpec:
    retention: 30d
    retentionSize: 50GB
    scrapeInterval: 15s

    ruleFiles:
      - /etc/prometheus/rules/*.yaml

    additionalScrapeConfigs:
      - job_name: "eren-api"
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: eren-api
          - source_labels: [__meta_kubernetes_pod_container_port_number]
            action: keep
            regex: "8000"
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: pod
          - source_labels: [__meta_kubernetes_pod_label_tenant_id]
            action: replace
            target_label: tenant_id

      - job_name: "kafka"
        static_configs:
          - targets: ["kafka-headless:9308"]  # JMX metrics
        metrics_path: /metrics

      - job_name: "postgres"
        static_configs:
          - targets: ["postgres-exporter:9187"]

      - job_name: "redis"
        static_configs:
          - targets: ["redis-exporter:9121"]
```

---

## Grafana Datasources

```yaml
# infra/helm/grafana/datasources.yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: 15s

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    jsonData:
      derivedFields:
        - name: TraceID
          matcherRegex: '"trace_id":"(\w+)"'
          url: "$${__value}"
          datasourceUid: Jaeger

  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger-query:16686
    jsonData:
      tracesToLogs:
        datasourceUid: Loki
        mapTags: true
        tags: [trace_id, span_id, tenant_id]
```

---

## Grafana Dashboard Examples

### EREN Overview Dashboard

```json
{
  "dashboard": {
    "title": "EREN Overview",
    "panels": [
      {
        "title": "Requests per Second",
        "type": "timeseries",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "targets": [{
          "expr": "sum(rate(eren_http_requests_total[5m])) by (tenant_id)",
          "legendFormat": "Tenant {{tenant_id}}"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "custom": {"lineWidth": 2, "fillOpacity": 10}
          }
        }
      },
      {
        "title": "Error Rate",
        "type": "gauge",
        "gridPos": {"x": 12, "y": 0, "w": 6, "h": 8},
        "targets": [{
          "expr": "sum(rate(eren_http_requests_total{status_code=~\"5..\"}[5m])) / sum(rate(eren_http_requests_total[5m]))"
        }],
        "fieldConfig": {
          "defaults": {
            "unit": "percentunit",
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 0.01, "color": "yellow"},
                {"value": 0.05, "color": "red"}
              ]
            }
          }
        }
      },
      {
        "title": "P95 Latency",
        "type": "timeseries",
        "gridPos": {"x": 18, "y": 0, "w": 6, "h": 8},
        "targets": [{
          "expr": "histogram_quantile(0.95, sum(rate(eren_http_request_duration_seconds_bucket[5m])) by (le))"
        }],
        "fieldConfig": {
          "defaults": {"unit": "s"}
        }
      },
      {
        "title": "CDS Recommendations by Confidence",
        "type": "piechart",
        "gridPos": {"x": 0, "y": 8, "w": 8, "h": 8},
        "targets": [{
          "expr": "sum(increase(eren_cds_recommendations_total[1h])) by (confidence_band)"
        }]
      },
      {
        "title": "Active Incidents by Priority",
        "type": "bargauge",
        "gridPos": {"x": 8, "y": 8, "w": 8, "h": 8},
        "targets": [{
          "expr": "eren_open_incidents"
        }]
      },
      {
        "title": "Kafka Consumer Lag",
        "type": "timeseries",
        "gridPos": {"x": 16, "y": 8, "w": 8, "h": 8},
        "targets": [{
          "expr": "kafka_consumer_lag_consumer_group_topic_partition"
        }],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 10000, "color": "yellow"},
                {"value": 100000, "color": "red"}
              ]
            }
          }
        }
      }
    ]
  }
}
```

---

## LogQL Examples

```logql
# All errors in the last hour
{app="eren-api"} |= "level"="error"

# Logs for a specific tenant
{app="eren-api"} | json | tenant_id="00000000-0000-0000-0000-000000000001"

# CDS recommendation logs with high latency
{app="eren-api"} | json | event_type="cds_recommendation" | duration_s > 5

# PHI access audit logs
{app="eren-api"} | json | event_type="phi_access" | audit_action="export"

# Alarm logs for a specific device
{app="eren-worker"} | json | event_type="alarm_critical" | device_id="abc123"

# Slow database queries
{app="eren-api"} | json | logger="sqlalchemy.engine" | duration_ms > 1000

# Cross-tenant access attempts (CRITICAL)
{app="eren-api"} |= "CROSS_TENANT_ACCESS"
```

---

## Alert Examples

```yaml
# infra/prometheus/rules/eren-alerts.yaml
groups:
  - name: eren-critical
    rules:
      - alert: ERENAPIDown
        expr: up{job="eren-api"} == 0
        for: 1m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "EREN API is down"
          runbook_url: "https://docs.eren.io/runbooks/eren-api-down"

      - alert: High5xxErrorRate
        expr: |
          sum(rate(eren_http_requests_total{status_code=~"5.."}[5m])) by (tenant_id)
          / sum(rate(eren_http_requests_total[5m])) by (tenant_id) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High 5xx error rate for tenant {{ $labels.tenant_id }}"

      - alert: CDSLowConfidenceThreshold
        expr: |
          sum(rate(eren_cds_recommendations_total{confidence_band="low"}[1h])) by (tenant_id)
          / sum(rate(eren_cds_recommendations_total[1h])) by (tenant_id) > 0.3
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "CDS confidence is degrading for tenant {{ $labels.tenant_id }}"

      - alert: KafkaConsumerLagCritical
        expr: kafka_consumer_lag_consumer_group_topic_partition > 100000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Kafka consumer lag is {{ $value }} messages"
          runbook_url: "https://docs.eren.io/runbooks/kafka-lag"

      - alert: MultiTenantIsolationBreach
        expr: increase(eren_cross_tenant_access_total[1m]) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Cross-tenant access detected!"
          description: "{{ $value }} cross-tenant access attempts in the last minute"
          runbook_url: "https://docs.eren.io/runbooks/cross-tenant-breach"
```

---

*Infrastructure Team - 2026-07-16*
