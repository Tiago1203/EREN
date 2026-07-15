"""Tracing for EREN OS Multi-Provider Layer.

Implements distributed tracing for provider requests.
"""

from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class SpanStatus(str, Enum):
    """Span status."""

    OK = "ok"
    ERROR = "error"
    CLIENT_ERROR = "client_error"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class SpanKind(str, Enum):
    """Span kind."""

    CLIENT = "client"
    SERVER = "server"
    PRODUCER = "producer"
    CONSUMER = "consumer"


@dataclass
class SpanEvent:
    """An event within a span."""

    name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    attributes: dict = field(default_factory=dict)


@dataclass
class SpanLink:
    """A link to another span."""

    trace_id: str
    span_id: str
    attributes: dict = field(default_factory=dict)


@dataclass
class Span:
    """A trace span."""

    name: str
    trace_id: str
    span_id: str
    kind: SpanKind = SpanKind.CLIENT

    # Timing
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None

    # Status
    status: SpanStatus = SpanStatus.OK
    status_message: str = ""

    # Hierarchy
    parent_span_id: str | None = None

    # Data
    attributes: dict = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)
    links: list[SpanLink] = field(default_factory=list)

    # Provider-specific
    provider_id: str = ""
    model: str = ""
    request_hash: str = ""
    response_hash: str = ""

    def set_attribute(self, key: str, value: Any) -> None:
        """Set attribute.

        Args:
            key: Attribute key.
            value: Attribute value.
        """
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict | None = None) -> None:
        """Add event to span.

        Args:
            name: Event name.
            attributes: Optional event attributes.
        """
        self.events.append(SpanEvent(name=name, attributes=attributes or {}))

    def set_status(self, status: SpanStatus, message: str = "") -> None:
        """Set span status.

        Args:
            status: Status code.
            message: Status message.
        """
        self.status = status
        self.status_message = message

    def finish(self, status: SpanStatus | None = None, message: str = "") -> None:
        """Finish the span.

        Args:
            status: Optional final status.
            message: Optional status message.
        """
        self.end_time = datetime.now(UTC)
        if status:
            self.status = status
            self.status_message = message

    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if not self.end_time:
            end = datetime.now(UTC)
        else:
            end = self.end_time

        delta = end - self.start_time
        return delta.total_seconds() * 1000

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "kind": self.kind.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "status_message": self.status_message,
            "parent_span_id": self.parent_span_id,
            "attributes": self.attributes,
            "events": [
                {"name": e.name, "timestamp": e.timestamp.isoformat(), "attributes": e.attributes}
                for e in self.events
            ],
            "links": [
                {"trace_id": l.trace_id, "span_id": l.span_id, "attributes": l.attributes}
                for l in self.links
            ],
            "provider_id": self.provider_id,
            "model": self.model,
            "request_hash": self.request_hash,
            "response_hash": self.response_hash,
        }


@dataclass
class TraceContext:
    """Context for a trace."""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    attributes: dict = field(default_factory=dict)

    @classmethod
    def new(cls) -> TraceContext:
        """Create new trace context."""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())[:16]
        return cls(trace_id=trace_id, span_id=span_id)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "attributes": self.attributes,
        }


class Tracer:
    """Distributed tracer for provider requests.

    Features:
    - Span creation and management
    - Context propagation
    - Event recording
    - Span exporters
    """

    def __init__(self, service_name: str = "eren"):
        """Initialize tracer.

        Args:
            service_name: Name of the service.
        """
        self._service_name = service_name
        self._spans: dict[str, Span] = {}
        self._active_spans: dict[str, Span] = {}  # thread -> span
        self._lock = threading.RLock()

        # Exporters
        self._exporters: list[Callable[[Span], None]] = []

    @property
    def service_name(self) -> str:
        """Get service name."""
        return self._service_name

    def add_exporter(self, exporter: Callable[[Span], None]) -> None:
        """Add a span exporter.

        Args:
            exporter: Exporter function(span).
        """
        with self._lock:
            if exporter not in self._exporters:
                self._exporters.append(exporter)

    def remove_exporter(self, exporter: Callable[[Span], None]) -> None:
        """Remove a span exporter.

        Args:
            exporter: Exporter function.
        """
        with self._lock:
            if exporter in self._exporters:
                self._exporters.remove(exporter)

    def start_span(
        self,
        name: str,
        context: TraceContext | None = None,
        kind: SpanKind = SpanKind.CLIENT,
        attributes: dict | None = None,
    ) -> Span:
        """Start a new span.

        Args:
            name: Span name.
            context: Optional parent context.
            kind: Span kind.
            attributes: Initial attributes.

        Returns:
            New span.
        """
        if context is None:
            context = TraceContext.new()

        span = Span(
            name=name,
            trace_id=context.trace_id,
            span_id=context.span_id,
            kind=kind,
            parent_span_id=context.parent_span_id,
            attributes=attributes or {},
        )

        with self._lock:
            self._spans[span.span_id] = span
            self._active_spans[threading.current_thread().ident or 0] = span

        span.add_event("span_started", {"service": self._service_name})

        return span

    def get_current_span(self) -> Span | None:
        """Get the current active span.

        Returns:
            Current span or None.
        """
        with self._lock:
            return self._active_spans.get(threading.current_thread().ident or 0)

    def end_span(self, span: Span) -> None:
        """End a span.

        Args:
            span: Span to end.
        """
        span.finish()

        with self._lock:
            self._active_spans.pop(threading.current_thread().ident or 0, None)

            # Export span
            for exporter in self._exporters:
                try:
                    exporter(span)
                except Exception:
                    pass

    def get_span(self, span_id: str) -> Span | None:
        """Get a span by ID.

        Args:
            span_id: Span identifier.

        Returns:
            Span or None.
        """
        with self._lock:
            return self._spans.get(span_id)

    def get_trace(self, trace_id: str) -> list[Span]:
        """Get all spans for a trace.

        Args:
            trace_id: Trace identifier.

        Returns:
            List of spans in the trace.
        """
        with self._lock:
            return [s for s in self._spans.values() if s.trace_id == trace_id]

    def record_exception(self, span: Span, exception: Exception) -> None:
        """Record an exception in a span.

        Args:
            span: Span to record in.
            exception: Exception to record.
        """
        span.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
                "exception.stacktrace": getattr(exception, "__traceback__", None),
            },
        )
        span.set_status(SpanStatus.ERROR, str(exception))

    def create_context(self, span: Span) -> TraceContext:
        """Create trace context from span.

        Args:
            span: Span to create context from.

        Returns:
            Trace context.
        """
        return TraceContext(
            trace_id=span.trace_id,
            span_id=str(uuid.uuid4())[:16],
            parent_span_id=span.span_id,
        )

    def clear(self) -> None:
        """Clear all spans."""
        with self._lock:
            self._spans.clear()
            self._active_spans.clear()

    def get_stats(self) -> dict:
        """Get tracer statistics."""
        with self._lock:
            active = len(self._active_spans)
            completed = sum(1 for s in self._spans.values() if s.end_time)

            status_counts: dict[str, int] = {}
            for span in self._spans.values():
                if span.end_time:
                    status = span.status.value
                    status_counts[status] = status_counts.get(status, 0) + 1

            return {
                "service_name": self._service_name,
                "total_spans": len(self._spans),
                "active_spans": active,
                "completed_spans": completed,
                "status_counts": status_counts,
            }


# Global tracer instance
_global_tracer: Tracer | None = None
_tracer_lock = threading.Lock()


def get_tracer(service_name: str = "eren") -> Tracer:
    """Get the global tracer.

    Args:
        service_name: Service name for new tracer.

    Returns:
        Global tracer instance.
    """
    global _global_tracer
    with _tracer_lock:
        if _global_tracer is None:
            _global_tracer = Tracer(service_name)
        return _global_tracer


def reset_tracer() -> None:
    """Reset the global tracer."""
    global _global_tracer
    with _tracer_lock:
        if _global_tracer is not None:
            _global_tracer.clear()
        _global_tracer = None
