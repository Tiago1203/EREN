"""Router Trace for EREN OS Cognitive Capability Router.

Provides comprehensive tracing for router operations.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class TraceEntry:
    """A single trace entry."""

    trace_id: str
    operation: str
    category: str
    correlation_id: str = ""
    session_id: str = ""
    intent_type: str = ""
    pipeline_name: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    success: bool = True
    error: str = ""
    metadata: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "operation": self.operation,
            "category": self.category,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "intent_type": self.intent_type,
            "pipeline_name": self.pipeline_name,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class RouterTrace:
    """Provides comprehensive tracing for routers.

    Tracks:
    - Routing operations
    - Pipeline matching
    - Policy selection
    - Timing
    - Errors
    - Correlation
    """

    def __init__(self):
        """Initialize the trace collector."""
        self._entries: list[TraceEntry] = []
        self._by_correlation: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_intent: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_pipeline: dict[str, list[TraceEntry]] = defaultdict(list)
        self._lock = threading.RLock()
        self._active_traces: dict[str, datetime] = {}

    def start_trace(
        self,
        correlation_id: str = "",
        session_id: str = "",
        intent_type: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Start a new trace.

        Args:
            correlation_id: Correlation ID.
            session_id: Session ID.
            intent_type: Intent type.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        with self._lock:
            self._active_traces[trace_id] = datetime.now(timezone.utc)

            entry = TraceEntry(
                trace_id=trace_id,
                operation="routing_start",
                category="routing",
                correlation_id=correlation_id,
                session_id=session_id,
                intent_type=intent_type,
                metadata=metadata,
            )

            self._entries.append(entry)

            if correlation_id:
                self._by_correlation[correlation_id].append(entry)
            if intent_type:
                self._by_intent[intent_type].append(entry)

        return trace_id

    def end_trace(
        self,
        trace_id: str,
        success: bool = True,
        error: str = "",
    ) -> None:
        """End a trace.

        Args:
            trace_id: Trace ID from start_trace.
            success: Whether operation succeeded.
            error: Error message.
        """
        with self._lock:
            if trace_id not in self._active_traces:
                return

            start_time = self._active_traces[trace_id]
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )

            # Find and update entry
            for entry in reversed(self._entries):
                if entry.trace_id == trace_id and entry.operation == "routing_start":
                    entry.duration_ms = duration_ms
                    entry.success = success
                    entry.error = error
                    break

            del self._active_traces[trace_id]

    def add_matching_entry(
        self,
        correlation_id: str = "",
        intent_type: str = "",
        pipeline_name: str = "",
        score: float = 0.0,
        match_result: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Add a pipeline matching entry.

        Args:
            correlation_id: Correlation ID.
            intent_type: Intent type.
            pipeline_name: Pipeline name.
            score: Match score.
            match_result: Match result.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        entry = TraceEntry(
            trace_id=trace_id,
            operation="pipeline_matched",
            category="matching",
            correlation_id=correlation_id,
            intent_type=intent_type,
            pipeline_name=pipeline_name,
            metadata={
                "score": score,
                "match_result": match_result,
                **(metadata or {}),
            },
        )

        with self._lock:
            self._entries.append(entry)
            if pipeline_name:
                self._by_pipeline[pipeline_name].append(entry)
            if correlation_id:
                self._by_correlation[correlation_id].append(entry)

        return trace_id

    def add_selection_entry(
        self,
        correlation_id: str = "",
        intent_type: str = "",
        pipeline_name: str = "",
        policy_used: str = "",
        duration_ms: int = 0,
        success: bool = True,
        metadata: dict | None = None,
    ) -> str:
        """Add a pipeline selection entry.

        Args:
            correlation_id: Correlation ID.
            intent_type: Intent type.
            pipeline_name: Selected pipeline name.
            policy_used: Policy used for selection.
            duration_ms: Duration in milliseconds.
            success: Whether selection succeeded.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        entry = TraceEntry(
            trace_id=trace_id,
            operation="pipeline_selected",
            category="selection",
            correlation_id=correlation_id,
            intent_type=intent_type,
            pipeline_name=pipeline_name,
            duration_ms=duration_ms,
            success=success,
            metadata={
                "policy_used": policy_used,
                **(metadata or {}),
            },
        )

        with self._lock:
            self._entries.append(entry)
            if pipeline_name:
                self._by_pipeline[pipeline_name].append(entry)
            if correlation_id:
                self._by_correlation[correlation_id].append(entry)

        return trace_id

    def get_all_entries(self) -> list[TraceEntry]:
        """Get all trace entries.

        Returns:
            List of all entries.
        """
        with self._lock:
            return list(self._entries)

    def get_entries_by_correlation(self, correlation_id: str) -> list[TraceEntry]:
        """Get entries for a correlation ID.

        Args:
            correlation_id: Correlation ID.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_correlation.get(correlation_id, []))

    def get_entries_by_intent(self, intent_type: str) -> list[TraceEntry]:
        """Get entries for an intent type.

        Args:
            intent_type: Intent type.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_intent.get(intent_type, []))

    def get_entries_by_pipeline(self, pipeline_name: str) -> list[TraceEntry]:
        """Get entries for a pipeline.

        Args:
            pipeline_name: Pipeline name.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_pipeline.get(pipeline_name, []))

    def get_failed_entries(self) -> list[TraceEntry]:
        """Get all failed trace entries.

        Returns:
            List of failed entries.
        """
        with self._lock:
            return [e for e in self._entries if not e.success]

    def get_summary(self) -> dict:
        """Get trace summary.

        Returns:
            Dictionary with summary.
        """
        with self._lock:
            total = len(self._entries)
            succeeded = len([e for e in self._entries if e.success])
            failed = total - succeeded

            # By category
            by_category = {}
            for category in ("routing", "matching", "selection"):
                entries = [e for e in self._entries if e.category == category]
                by_category[category] = {
                    "total": len(entries),
                    "succeeded": len([e for e in entries if e.success]),
                    "failed": len([e for e in entries if not e.success]),
                }

            # By pipeline
            by_pipeline = {}
            for pipeline, entries in self._by_pipeline.items():
                by_pipeline[pipeline] = {
                    "total": len(entries),
                    "succeeded": len([e for e in entries if e.success]),
                }

            # Timing
            durations = [e.duration_ms for e in self._entries if e.duration_ms > 0]
            timing_stats = {}
            if durations:
                timing_stats = {
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                    "avg_ms": sum(durations) / len(durations),
                }

            return {
                "total_entries": total,
                "succeeded": succeeded,
                "failed": failed,
                "success_rate": (succeeded / total * 100) if total > 0 else 0,
                "by_category": by_category,
                "by_pipeline": by_pipeline,
                "timing_stats": timing_stats,
                "active_traces": len(self._active_traces),
            }

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "entries": [e.to_dict() for e in self._entries],
                "summary": self.get_summary(),
            }

    def clear(self) -> None:
        """Clear all trace data."""
        with self._lock:
            self._entries.clear()
            self._by_correlation.clear()
            self._by_intent.clear()
            self._by_pipeline.clear()
            self._active_traces.clear()


# Global trace instance
_trace: RouterTrace | None = None
_trace_lock = threading.Lock()


def get_router_trace() -> RouterTrace:
    """Get the global router trace instance.

    Returns:
        Global RouterTrace instance.
    """
    global _trace
    with _trace_lock:
        if _trace is None:
            _trace = RouterTrace()
        return _trace


def reset_router_trace() -> None:
    """Reset global trace."""
    global _trace
    with _trace_lock:
        if _trace is not None:
            _trace.clear()
