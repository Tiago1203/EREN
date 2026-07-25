"""
PHASE 7 - EPIC 4: Custom Metrics

Business metrics para EREN:
- HTTP request metrics
- Database metrics
- AI/LLM metrics
- Clinical workflow metrics
- Multi-tenant metrics (EPIC 2)
- HA metrics (EPIC 3)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import time


class MetricsCollector:
    """Collector de métricas custom de negocio."""

    def __init__(self):
        self._counters = {}
        self._gauges = {}
        self._histograms = {}
        self._start_times = {}

    # ── HTTP Metrics ────────────────────────────────────────
    def record_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra request HTTP."""
        prefix = f"http_{method.lower()}"
        c = self._counters.setdefault(prefix, {})
        key = (path, status_code, tenant_id or "")
        c[key] = c.get(key, 0) + 1

        # Latency histogram
        h_key = "http_request_duration"
        h = self._histograms.setdefault(h_key, [])
        h.append(duration_ms)
        if len(h) > 1000:
            self._histograms[h_key] = h[-1000:]

    def record_http_error(
        self,
        method: str,
        path: str,
        status_code: int,
        error_type: str,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra error HTTP."""
        key = ("http_errors", method, status_code, error_type, tenant_id or "")
        c = self._counters.setdefault("http_errors", {})
        c[key] = c.get(key, 0) + 1

    # ── Database Metrics ────────────────────────────────────
    def record_db_query(
        self,
        query_type: str,
        table: str,
        duration_ms: float,
        rows_affected: int,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra query de base de datos."""
        key = (query_type, table, tenant_id or "")
        c = self._counters.setdefault("db_queries", {})
        c[key] = c.get(key, 0) + 1

        h_key = f"db_query_duration_{query_type.lower()}"
        h = self._histograms.setdefault(h_key, [])
        h.append(duration_ms)
        if len(h) > 1000:
            self._histograms[h_key] = h[-1000:]

    def record_db_connection(
        self,
        status: str,          # acquired, released, error
        pool_name: str,
        wait_time_ms: float,
    ) -> None:
        """Registra uso de connection pool."""
        key = (status, pool_name)
        c = self._counters.setdefault("db_connections", {})
        c[key] = c.get(key, 0) + 1

        if status == "wait":
            h = self._histograms.setdefault("db_connection_wait_time", [])
            h.append(wait_time_ms)

    # ── AI/LLM Metrics ───────────────────────────────────────
    def record_llm_request(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        duration_ms: float,
        success: bool,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra request a LLM."""
        key = (model, success, tenant_id or "")
        c = self._counters.setdefault("llm_requests", {})
        c[key] = c.get(key, 0) + 1

        # Tokens
        tk_key = ("llm_tokens", model, tenant_id or "")
        tc = self._counters.setdefault("llm_tokens", {})
        tc[tk_key] = tc.get(tk_key, 0) + prompt_tokens + completion_tokens

        # Latency
        h = self._histograms.setdefault("llm_request_duration", [])
        h.append(duration_ms)
        if len(h) > 1000:
            self._histograms["llm_request_duration"] = h[-1000:]

    def record_rag_query(
        self,
        query_type: str,
        documents_retrieved: int,
        citations_found: int,
        duration_ms: float,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra query RAG."""
        key = (query_type, tenant_id or "")
        c = self._counters.setdefault("rag_queries", {})
        c[key] = c.get(key, 0) + 1

        h = self._histograms.setdefault("rag_query_duration", [])
        h.append(duration_ms)

    # ── Clinical Workflow Metrics ─────────────────────────────
    def record_clinical_action(
        self,
        action: str,
        context: str,        # diagnosis, treatment, equipment
        outcome: str,       # success, partial, failed
        duration_ms: float,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra acción clínica."""
        key = (action, context, outcome, tenant_id or "")
        c = self._counters.setdefault("clinical_actions", {})
        c[key] = c.get(key, 0) + 1

        h = self._histograms.setdefault("clinical_action_duration", [])
        h.append(duration_ms)

    # ── Multi-Tenant Metrics (EPIC 2) ────────────────────────
    def record_tenant_operation(
        self,
        operation: str,
        tenant_id: str,
        success: bool,
        duration_ms: float,
    ) -> None:
        """Registra operación multi-tenant."""
        key = (operation, tenant_id, success)
        c = self._counters.setdefault("tenant_operations", {})
        c[key] = c.get(key, 0) + 1

        h = self._histograms.setdefault("tenant_operation_duration", [])
        h.append(duration_ms)

    def record_quota_usage(
        self,
        resource_type: str,
        tenant_id: str,
        used: float,
        limit: float,
    ) -> None:
        """Registra uso de quota."""
        g = self._gauges.setdefault("quota_usage_percent", {})
        key = (resource_type, tenant_id)
        g[key] = (used / limit * 100) if limit > 0 else 0

    # ── HA Metrics (EPIC 3) ─────────────────────────────────
    def record_health_check(
        self,
        service: str,
        status: str,       # healthy, degraded, unhealthy
        response_time_ms: float,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra health check."""
        key = (service, status, tenant_id or "")
        c = self._counters.setdefault("health_checks", {})
        c[key] = c.get(key, 0) + 1

        h = self._histograms.setdefault("health_check_duration", [])
        h.append(response_time_ms)

    def record_failover(
        self,
        cluster: str,
        trigger: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        """Registra failover."""
        key = (cluster, trigger, success)
        c = self._counters.setdefault("failovers", {})
        c[key] = c.get(key, 0) + 1

    def record_circuit_breaker(
        self,
        circuit_name: str,
        from_state: str,
        to_state: str,
    ) -> None:
        """Registra cambio de estado de circuit breaker."""
        key = (circuit_name, from_state, to_state)
        c = self._counters.setdefault("circuit_breaker_transitions", {})
        c[key] = c.get(key, 0) + 1

    def record_scaling_event(
        self,
        service: str,
        old_replicas: int,
        new_replicas: int,
        trigger: str,      # cpu, memory, manual
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra evento de scaling."""
        key = (service, trigger, tenant_id or "")
        c = self._counters.setdefault("scaling_events", {})
        c[key] = c.get(key, 0) + 1

        g = self._gauges.setdefault("current_replicas", {})
        g[(service, tenant_id or "")] = new_replicas

    # ── Audit Metrics (EPIC 1) ───────────────────────────────
    def record_audit_event(
        self,
        category: str,
        action: str,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Registra evento de auditoría."""
        key = (category, action, tenant_id or "")
        c = self._counters.setdefault("audit_events", {})
        c[key] = c.get(key, 0) + 1

    # ── Get Metrics ──────────────────────────────────────────
    def get_all_metrics(self) -> dict:
        """Obtiene todas las métricas."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                k: {"count": len(v), "values": v[-100:]}
                for k, v in self._histograms.items()
            },
        }

    def get_histogram_stats(self, name: str) -> dict:
        """Obtiene estadísticas de un histograma."""
        values = self._histograms.get(name, [])
        if not values:
            return {}

        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return {
            "count": n,
            "sum": sum(sorted_vals),
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "avg": sum(sorted_vals) / n,
            "p50": sorted_vals[n // 2],
            "p95": sorted_vals[int(n * 0.95)],
            "p99": sorted_vals[int(n * 0.99)],
        }

    def reset(self) -> None:
        """Resetea métricas."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._start_times.clear()


# Global collector
_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Obtiene el collector global."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


# Decorator for automatic timing
def timed_operation(operation_name: str, tenant_id: Optional[str] = None):
    """Decorador para medir duración de operaciones."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                get_metrics_collector().record_clinical_action(
                    action=operation_name,
                    context="system",
                    outcome="success",
                    duration_ms=duration_ms,
                    tenant_id=tenant_id,
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                get_metrics_collector().record_clinical_action(
                    action=operation_name,
                    context="system",
                    outcome="failed",
                    duration_ms=duration_ms,
                    tenant_id=tenant_id,
                )
                raise
        return wrapper
    return decorator
