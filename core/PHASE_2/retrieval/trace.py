"""Retrieval trace for EREN Semantic Retrieval Engine.

Traces retrieval operations for debugging and analysis.
"""

from __future__ import annotations

import threading
import uuid
from typing import TYPE_CHECKING

from core.PHASE_2.retrieval.types import RetrievalTrace

if TYPE_CHECKING:
    pass


class RetrievalTracer:
    """Traces retrieval operations.

    Responsibilities:
    - Create traces
    - Record steps
    - Record errors
    - Store traces for analysis
    """

    def __init__(self, max_traces: int = 100):
        """Initialize tracer.

        Args:
            max_traces: Maximum traces to keep.
        """
        self._lock = threading.RLock()
        self._traces: dict[str, RetrievalTrace] = {}
        self._max_traces = max_traces

    def create_trace(self, query: str) -> RetrievalTrace:
        """Create a new trace.

        Args:
            query: Query string.

        Returns:
            New trace.
        """
        trace = RetrievalTrace(
            trace_id=str(uuid.uuid4()),
            query=query,
        )

        with self._lock:
            self._traces[trace.trace_id] = trace

            # Clean up old traces
            if len(self._traces) > self._max_traces:
                oldest = min(self._traces.keys(), key=lambda k: self._traces[k].start_time)
                del self._traces[oldest]

        return trace

    def get_trace(self, trace_id: str) -> RetrievalTrace | None:
        """Get a trace by ID.

        Args:
            trace_id: Trace ID.

        Returns:
            Trace or None.
        """
        with self._lock:
            return self._traces.get(trace_id)

    def list_traces(self, limit: int = 10) -> list[RetrievalTrace]:
        """List recent traces.

        Args:
            limit: Maximum traces to return.

        Returns:
            List of traces.
        """
        with self._lock:
            traces = sorted(
                self._traces.values(),
                key=lambda t: t.start_time,
                reverse=True,
            )
            return traces[:limit]

    def clear(self) -> None:
        """Clear all traces."""
        with self._lock:
            self._traces.clear()


# Global tracer
_global_tracer: RetrievalTracer | None = None
_tracer_lock = threading.Lock()


def get_retrieval_tracer() -> RetrievalTracer:
    """Get the global tracer.

    Returns:
        Global RetrievalTracer instance.
    """
    global _global_tracer
    with _tracer_lock:
        if _global_tracer is None:
            _global_tracer = RetrievalTracer()
        return _global_tracer


def reset_retrieval_tracer() -> None:
    """Reset the global tracer."""
    global _global_tracer
    with _tracer_lock:
        if _global_tracer is not None:
            _global_tracer.clear()
        _global_tracer = None
