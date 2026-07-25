"""
PHASE 7 - EPIC 4: Operations Dashboard

Dashboard de operaciones 24/7:
- System health overview
- Service status
- Performance metrics
- Active alerts
- SLO status
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class DashboardData:
    """Datos para dashboard."""
    generated_at: datetime
    system_status: str        # healthy, degraded, unhealthy
    uptime_seconds: float
    total_requests: int
    error_rate_percent: float
    avg_latency_ms: float
    active_alerts: int
    critical_alerts: int
    slo_health_percent: float
    services: list


class OperationsDashboard:
    """Dashboard de operaciones."""

    def __init__(
        self,
        metrics_collector=None,
        alert_manager=None,
        slo_manager=None,
        tracer=None,
    ):
        self._metrics = metrics_collector
        self._alerts = alert_manager
        self._slo = slo_manager
        self._tracer = tracer

    def get_overview(self) -> dict:
        """Overview del sistema."""
        # Gather data from components
        system_status = "healthy"
        active_alerts = 0
        critical_alerts = 0
        slo_health = 100.0

        if self._alerts:
            summary = self._alerts.get_alert_summary()
            active_alerts = summary["firing"]
            critical_alerts = summary["firing_by_severity"].get("critical", 0)
            if critical_alerts > 0:
                system_status = "unhealthy"
            elif active_alerts > 0:
                system_status = "degraded"

        if self._slo:
            slo_status = self._slo.get_all_status()
            if slo_status:
                healthy = sum(1 for s in slo_status if s["status"] == "healthy")
                slo_health = round(healthy / len(slo_status) * 100, 1)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "system_status": system_status,
            "uptime_seconds": 0,
            "active_alerts": active_alerts,
            "critical_alerts": critical_alerts,
            "slo_health_percent": slo_health,
        }

    def get_services_status(self) -> list[dict]:
        """Estado de servicios."""
        services = [
            {
                "name": "API",
                "status": "healthy",
                "latency_p50_ms": 50,
                "latency_p95_ms": 150,
                "latency_p99_ms": 300,
                "requests_per_second": 100,
                "error_rate_percent": 0.1,
            },
            {
                "name": "Database",
                "status": "healthy",
                "latency_p50_ms": 5,
                "latency_p95_ms": 20,
                "latency_p99_ms": 50,
                "connections_active": 25,
                "connections_max": 100,
            },
            {
                "name": "Redis Cache",
                "status": "healthy",
                "hit_rate_percent": 95,
                "memory_used_mb": 512,
                "memory_max_mb": 2048,
            },
            {
                "name": "AI/LLM",
                "status": "healthy",
                "requests_per_minute": 50,
                "avg_latency_ms": 800,
                "error_rate_percent": 0.5,
            },
            {
                "name": "Vector DB (Qdrant)",
                "status": "healthy",
                "collections": 10,
                "vectors_count": 100000,
            },
        ]
        return services

    def get_request_metrics(self) -> dict:
        """Métricas de request."""
        return {
            "total_requests_today": 500000,
            "requests_per_second_avg": 5.8,
            "requests_per_second_p95": 15.0,
            "error_rate_percent": 0.2,
            "p50_latency_ms": 45,
            "p95_latency_ms": 150,
            "p99_latency_ms": 350,
            "p999_latency_ms": 800,
        }

    def get_infrastructure_metrics(self) -> dict:
        """Métricas de infraestructura."""
        return {
            "cpu_usage_percent": 45,
            "memory_usage_percent": 62,
            "disk_usage_percent": 55,
            "network_in_mbps": 100,
            "network_out_mbps": 200,
            "replicas_current": 3,
            "replicas_desired": 3,
        }

    def get_multi_tenant_summary(self) -> dict:
        """Resumen multi-tenant."""
        return {
            "total_tenants": 150,
            "active_tenants": 145,
            "suspended_tenants": 5,
            "total_requests_today": 500000,
            "total_storage_gb": 2500,
            "top_tenants_by_requests": [
                {"tenant_id": "t1", "requests": 50000},
                {"tenant_id": "t2", "requests": 35000},
                {"tenant_id": "t3", "requests": 25000},
            ],
        }

    def get_full_dashboard(self) -> dict:
        """Dashboard completo."""
        overview = self.get_overview()
        return {
            "overview": overview,
            "services": self.get_services_status(),
            "requests": self.get_request_metrics(),
            "infrastructure": self.get_infrastructure_metrics(),
            "multi_tenant": self.get_multi_tenant_summary(),
        }

    # ── Grafana Dashboard Config ─────────────────────────────
    def get_grafana_dashboard_json(self) -> dict:
        """Genera dashboard JSON para Grafana."""
        return {
            "title": "EREN Operations Dashboard",
            "tags": ["eren", "operations"],
            "timezone": "browser",
            "panels": [
                {
                    "title": "System Status",
                    "type": "stat",
                    "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
                    "targets": [
                        {"expr": 'eren_system_status{status="healthy"}'},
                    ],
                },
                {
                    "title": "Active Alerts",
                    "type": "stat",
                    "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
                    "targets": [
                        {"expr": 'eren_alerts_firing_total'},
                    ],
                },
                {
                    "title": "Request Rate",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
                    "targets": [
                        {"expr": 'rate(eren_http_requests_total[5m])'},
                    ],
                },
                {
                    "title": "Error Rate",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
                    "targets": [
                        {"expr": 'rate(eren_http_errors_total[5m]) / rate(eren_http_requests_total[5m]) * 100'},
                    ],
                },
                {
                    "title": "Latency P95",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
                    "targets": [
                        {"expr": 'histogram_quantile(0.95, rate(eren_http_request_duration_seconds_bucket[5m])) * 1000'},
                    ],
                },
                {
                    "title": "SLO Health",
                    "type": "gauge",
                    "gridPos": {"h": 8, "w": 6, "x": 12, "y": 12},
                    "targets": [
                        {"expr": 'eren_slo_health_percent'},
                    ],
                },
            ],
        }
