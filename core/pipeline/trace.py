"""Pipeline Trace for EREN OS Cognitive Capability Pipeline.

Provides comprehensive tracing for pipeline operations.
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
    pipeline_id: str
    stage_name: str = ""
    status: str = "info"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    correlation_id: str = ""
    session_id: str = ""
    success: bool = True
    error: str = ""
    metadata: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "operation": self.operation,
            "category": self.category,
            "pipeline_id": self.pipeline_id,
            "stage_name": self.stage_name,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class PipelineTrace:
    """Provides comprehensive tracing for pipelines.

    Tracks:
    - Pipeline execution
    - Stage execution
    - Timing
    - Errors
    - Correlation
    """

    def __init__(self):
        """Initialize the trace collector."""
        self._entries: list[TraceEntry] = []
        self._by_pipeline: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_stage: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_correlation: dict[str, list[TraceEntry]] = defaultdict(list)
        self._lock = threading.RLock()
        self._active_traces: dict[str, datetime] = {}

    def start_trace(
        self,
        pipeline_id: str,
        operation: str,
        correlation_id: str = "",
        session_id: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Start a new trace.

        Args:
            pipeline_id: Pipeline ID.
            operation: Operation name.
            correlation_id: Correlation ID.
            session_id: Session ID.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        with self._lock:
            self._active_traces[trace_id] = datetime.now(timezone.utc)

            entry = TraceEntry(
                trace_id=trace_id,
                operation=operation,
                category="pipeline",
                pipeline_id=pipeline_id,
                status="started",
                correlation_id=correlation_id,
                session_id=session_id,
                metadata=metadata,
            )

            self._entries.append(entry)
            self._by_pipeline[pipeline_id].append(entry)
            if correlation_id:
                self._by_correlation[correlation_id].append(entry)

        return trace_id

    def end_trace(
        self,
        trace_id: str,
        status: str = "completed",
        success: bool = True,
        error: str = "",
    ) -> None:
        """End a trace.

        Args:
            trace_id: Trace ID from start_trace.
            status: Final status.
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
                if entry.trace_id == trace_id and entry.status == "started":
                    entry.status = status
                    entry.duration_ms = duration_ms
                    entry.success = success
                    entry.error = error
                    break

            del self._active_traces[trace_id]

    def add_stage_entry(
        self,
        pipeline_id: str,
        stage_name: str,
        status: str,
        duration_ms: int = 0,
        correlation_id: str = "",
        session_id: str = "",
        success: bool = True,
        error: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Add a stage execution entry.

        Args:
            pipeline_id: Pipeline ID.
            stage_name: Stage name.
            status: Execution status.
            duration_ms: Duration in milliseconds.
            correlation_id: Correlation ID.
            session_id: Session ID.
            success: Whether stage succeeded.
            error: Error message.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        entry = TraceEntry(
            trace_id=trace_id,
            operation=f"stage:{stage_name}",
            category="stage",
            pipeline_id=pipeline_id,
            stage_name=stage_name,
            status=status,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            session_id=session_id,
            success=success,
            error=error,
            metadata=metadata,
        )

        with self._lock:
            self._entries.append(entry)
            self._by_pipeline[pipeline_id].append(entry)
            self._by_stage[stage_name].append(entry)
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

    def get_entries_by_pipeline(self, pipeline_id: str) -> list[TraceEntry]:
        """Get entries for a specific pipeline.

        Args:
            pipeline_id: Pipeline ID.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_pipeline.get(pipeline_id, []))

    def get_entries_by_stage(self, stage_name: str) -> list[TraceEntry]:
        """Get entries for a specific stage.

        Args:
            stage_name: Stage name.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_stage.get(stage_name, []))

    def get_entries_by_correlation(self, correlation_id: str) -> list[TraceEntry]:
        """Get entries for a correlation ID.

        Args:
            correlation_id: Correlation ID.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_correlation.get(correlation_id, []))

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
            for category in ("pipeline", "stage"):
                entries = [e for e in self._entries if e.category == category]
                by_category[category] = {
                    "total": len(entries),
                    "succeeded": len([e for e in entries if e.success]),
                    "failed": len([e for e in entries if not e.success]),
                }

            # By stage
            by_stage = {}
            for stage_name, entries in self._by_stage.items():
                by_stage[stage_name] = {
                    "total": len(entries),
                    "succeeded": len([e for e in entries if e.success]),
                    "failed": len([e for e in entries if not e.success]),
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
                "by_stage": by_stage,
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
            self._by_pipeline.clear()
            self._by_stage.clear()
            self._by_correlation.clear()
            self._active_traces.clear()


# Global trace instance
_trace: PipelineTrace | None = None
_trace_lock = threading.Lock()


def get_pipeline_trace() -> PipelineTrace:
    """Get the global pipeline trace instance.

    Returns:
        Global PipelineTrace instance.
    """
    global _trace
    with _trace_lock:
        if _trace is None:
            _trace = PipelineTrace()
        return _trace


def reset_pipeline_trace() -> None:
    """Reset global trace."""
    global _trace
    with _trace_lock:
        if _trace is not None:
            _trace.clear()
