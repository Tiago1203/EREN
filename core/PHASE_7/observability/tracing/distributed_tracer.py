"""
PHASE 7 - EPIC 4: Distributed Tracer

OpenTelemetry-style distributed tracing:
- Spans
- Trace context propagation
- Multi-service traces
- Integration con EPIC 2 (multi-tenant)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import threading
import time
import uuid


class SpanKind(str, Enum):
    """Tipo de span."""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(str, Enum):
    """Estado de span."""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class Span:
    """Span de tracing."""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    kind: SpanKind
    start_time: datetime
    end_time: Optional[datetime] = None
    status: SpanStatus = SpanStatus.UNSET
    attributes: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    links: list = field(default_factory=list)

    def set_attribute(self, key: str, value) -> None:
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[dict] = None) -> None:
        self.events.append({
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attributes": attributes or {},
        })

    def set_status(self, status: SpanStatus, message: str = "") -> None:
        self.status = status
        if message:
            self.attributes["status_message"] = message

    def record_exception(self, exception: Exception) -> None:
        self.status = SpanStatus.ERROR
        self.attributes["exception.type"] = type(exception).__name__
        self.attributes["exception.message"] = str(exception)
        self.add_event("exception", {"exception.type": type(exception).__name__})

    def end(self) -> None:
        self.end_time = datetime.now(timezone.utc)

    def duration_ms(self) -> float:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0


class DistributedTracer:
    """Tracer distribuido."""

    def __init__(self, service_name: str):
        self._service_name = service_name
        self._spans: list[Span] = []
        self._active_spans: dict[str, Span] = {}
        self._lock = threading.Lock()

    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[dict] = None,
    ) -> Span:
        """Inicia un nuevo span."""
        if trace_id is None:
            trace_id = str(uuid.uuid4()).replace("-", "")

        span_id = str(uuid.uuid4()).replace("-", "")[:16]

        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            kind=kind,
            start_time=datetime.now(timezone.utc),
            attributes=attributes or {},
        )

        with self._lock:
            self._active_spans[span_id] = span

        return span

    def end_span(self, span: Span) -> None:
        """Finaliza un span."""
        span.end()
        with self._lock:
            if span.span_id in self._active_spans:
                del self._active_spans[span.span_id]
            self._spans.append(span)
            if len(self._spans) > 10000:
                self._spans = self._spans[-5000:]

    def get_current_span(self) -> Optional[Span]:
        """Obtiene el span activo actual."""
        with self._lock:
            if self._active_spans:
                return list(self._active_spans.values())[-1]
        return None

    def trace(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[dict] = None,
    ):
        """Decorador/context manager para tracing."""
        class TraceContext:
            def __init__(self, tracer, name, kind, attrs):
                self._tracer = tracer
                self._name = name
                self._kind = kind
                self._attrs = attrs or {}
                self._span = None

            def __enter__(self):
                parent = self._tracer.get_current_span()
                parent_id = parent.span_id if parent else None
                trace_id = parent.trace_id if parent else None
                self._span = self._tracer.start_span(
                    self._name, trace_id, parent_id, self._kind, self._attrs
                )
                return self._span

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_val:
                    self._span.record_exception(exc_val)
                self._tracer.end_span(self._span)
                return False

        return TraceContext(self, name, kind, attributes)

    def query_traces(
        self,
        trace_id: Optional[str] = None,
        span_name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Query traces."""
        with self._lock:
            results = self._spans

            if trace_id:
                results = [s for s in results if s.trace_id == trace_id]
            if span_name:
                results = [s for s in results if span_name in s.name]
            if tenant_id:
                results = [s for s in results if s.attributes.get("tenant_id") == tenant_id]
            if start_time:
                results = [s for s in results if s.start_time >= start_time]
            if end_time:
                results = [s for s in results if s.start_time <= end_time]

            # Group by trace_id
            traces = {}
            for s in sorted(results, key=lambda x: x.start_time):
                if s.trace_id not in traces:
                    traces[s.trace_id] = []
                traces[s.trace_id].append(s)

            return [
                {
                    "trace_id": tid,
                    "spans": [
                        {
                            "name": s.name,
                            "span_id": s.span_id,
                            "parent_span_id": s.parent_span_id,
                            "kind": s.kind.value,
                            "status": s.status.value,
                            "start_time": s.start_time.isoformat(),
                            "end_time": s.end_time.isoformat() if s.end_time else None,
                            "duration_ms": s.duration_ms(),
                            "attributes": s.attributes,
                        }
                        for s in spans
                    ],
                    "total_spans": len(spans),
                    "total_duration_ms": max(s.duration_ms() for s in spans),
                }
                for tid, spans in list(traces.items())[:limit]
            ]

    def get_span_statistics(self, tenant_id: Optional[str] = None) -> dict:
        """Estadísticas de spans."""
        with self._lock:
            spans = self._spans
            if tenant_id:
                spans = [s for s in spans if s.attributes.get("tenant_id") == tenant_id]

            durations = [s.duration_ms() for s in spans if s.end_time]
            errors = sum(1 for s in spans if s.status == SpanStatus.ERROR)

            return {
                "total_spans": len(spans),
                "completed_spans": sum(1 for s in spans if s.end_time),
                "error_spans": errors,
                "error_rate_percent": round(errors / len(spans) * 100, 2) if spans else 0,
                "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
                "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                "p99_duration_ms": sorted(durations)[int(len(durations) * 0.99)] if durations else 0,
            }


# Global tracer
_global_tracer: Optional[DistributedTracer] = None


def get_tracer(service_name: str = "eren") -> DistributedTracer:
    """Obtiene tracer global."""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = DistributedTracer(service_name)
    return _global_tracer
