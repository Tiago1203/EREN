"""Execution Trace for EREN OS Cognitive Execution Coordinator.

Provides comprehensive tracing for execution operations.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class TraceEntry:
    """A single trace entry."""

    trace_id: str
    execution_id: str
    operation: str
    phase: str
    correlation_id: str = ""
    session_id: str = ""
    intent_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_ms: int = 0
    success: bool = True
    error: str = ""
    metadata: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "execution_id": self.execution_id,
            "operation": self.operation,
            "phase": self.phase,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "intent_type": self.intent_type,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class ExecutionTrace:
    """Provides comprehensive tracing for executions.

    Tracks:
    - Execution phases
    - Component interactions
    - Timing
    - Errors
    - Correlation
    """

    def __init__(self):
        """Initialize the trace collector."""
        self._entries: list[TraceEntry] = []
        self._by_execution: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_phase: dict[str, list[TraceEntry]] = defaultdict(list)
        self._lock = threading.RLock()
        self._active_traces: dict[str, datetime] = {}

    def start_trace(
        self,
        execution_id: str,
        correlation_id: str = "",
        session_id: str = "",
        intent_type: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Start a new trace.

        Args:
            execution_id: Execution ID.
            correlation_id: Correlation ID.
            session_id: Session ID.
            intent_type: Intent type.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        with self._lock:
            self._active_traces[trace_id] = datetime.now(UTC)

            entry = TraceEntry(
                trace_id=trace_id,
                execution_id=execution_id,
                operation="execution_start",
                phase="initialization",
                correlation_id=correlation_id,
                session_id=session_id,
                intent_type=intent_type,
                metadata=metadata,
            )

            self._entries.append(entry)
            self._by_execution[execution_id].append(entry)
            self._by_phase["initialization"].append(entry)

        return trace_id

    def end_trace(
        self,
        trace_id: str,
        execution_id: str,
        success: bool = True,
        error: str = "",
    ) -> None:
        """End a trace.

        Args:
            trace_id: Trace ID from start_trace.
            execution_id: Execution ID.
            success: Whether operation succeeded.
            error: Error message.
        """
        with self._lock:
            if trace_id not in self._active_traces:
                return

            start_time = self._active_traces[trace_id]
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )

            # Find and update entry
            for entry in reversed(self._entries):
                if entry.trace_id == trace_id and entry.operation == "execution_start":
                    entry.duration_ms = duration_ms
                    entry.success = success
                    entry.error = error
                    break

            del self._active_traces[trace_id]

    def add_phase_entry(
        self,
        execution_id: str,
        phase: str,
        operation: str,
        correlation_id: str = "",
        session_id: str = "",
        intent_type: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Add a phase entry.

        Args:
            execution_id: Execution ID.
            phase: Execution phase.
            operation: Operation name.
            correlation_id: Correlation ID.
            session_id: Session ID.
            intent_type: Intent type.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            error: Error message.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        entry = TraceEntry(
            trace_id=trace_id,
            execution_id=execution_id,
            operation=operation,
            phase=phase,
            correlation_id=correlation_id,
            session_id=session_id,
            intent_type=intent_type,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata,
        )

        with self._lock:
            self._entries.append(entry)
            self._by_execution[execution_id].append(entry)
            self._by_phase[phase].append(entry)

        return trace_id

    def add_session_entry(
        self,
        execution_id: str,
        correlation_id: str = "",
        session_id: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
    ) -> str:
        """Add a session creation entry.

        Args:
            execution_id: Execution ID.
            correlation_id: Correlation ID.
            session_id: Session ID.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            error: Error message.

        Returns:
            Trace ID.
        """
        return self.add_phase_entry(
            execution_id=execution_id,
            phase="session_creation",
            operation="create_session",
            correlation_id=correlation_id,
            session_id=session_id,
            duration_ms=duration_ms,
            success=success,
            error=error,
        )

    def add_routing_entry(
        self,
        execution_id: str,
        pipeline_name: str,
        correlation_id: str = "",
        intent_type: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
    ) -> str:
        """Add a routing entry.

        Args:
            execution_id: Execution ID.
            pipeline_name: Selected pipeline name.
            correlation_id: Correlation ID.
            intent_type: Intent type.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            error: Error message.

        Returns:
            Trace ID.
        """
        return self.add_phase_entry(
            execution_id=execution_id,
            phase="routing",
            operation="select_pipeline",
            correlation_id=correlation_id,
            intent_type=intent_type,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata={"pipeline": pipeline_name},
        )

    def add_pipeline_entry(
        self,
        execution_id: str,
        pipeline_name: str,
        correlation_id: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
    ) -> str:
        """Add a pipeline execution entry.

        Args:
            execution_id: Execution ID.
            pipeline_name: Pipeline name.
            correlation_id: Correlation ID.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            error: Error message.

        Returns:
            Trace ID.
        """
        return self.add_phase_entry(
            execution_id=execution_id,
            phase="pipeline_execution",
            operation="execute_pipeline",
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata={"pipeline": pipeline_name},
        )

    def add_context_update_entry(
        self,
        execution_id: str,
        update_count: int,
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
    ) -> str:
        """Add a context update entry.

        Args:
            execution_id: Execution ID.
            update_count: Number of context updates.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            error: Error message.

        Returns:
            Trace ID.
        """
        return self.add_phase_entry(
            execution_id=execution_id,
            phase="context_update",
            operation="update_context",
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata={"update_count": update_count},
        )

    def get_all_entries(self) -> list[TraceEntry]:
        """Get all trace entries.

        Returns:
            List of all entries.
        """
        with self._lock:
            return list(self._entries)

    def get_entries_by_execution(self, execution_id: str) -> list[TraceEntry]:
        """Get entries for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_execution.get(execution_id, []))

    def get_entries_by_phase(self, phase: str) -> list[TraceEntry]:
        """Get entries for a phase.

        Args:
            phase: Phase name.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_phase.get(phase, []))

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

            # By phase
            by_phase = {}
            for phase, entries in self._by_phase.items():
                by_phase[phase] = {
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
                "by_phase": by_phase,
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
            self._by_execution.clear()
            self._by_phase.clear()
            self._active_traces.clear()


# Global trace instance
_trace: ExecutionTrace | None = None
_trace_lock = threading.Lock()


def get_execution_trace() -> ExecutionTrace:
    """Get the global execution trace instance.

    Returns:
        Global ExecutionTrace instance.
    """
    global _trace
    with _trace_lock:
        if _trace is None:
            _trace = ExecutionTrace()
        return _trace


def reset_execution_trace() -> None:
    """Reset global trace."""
    global _trace
    with _trace_lock:
        if _trace is not None:
            _trace.clear()
