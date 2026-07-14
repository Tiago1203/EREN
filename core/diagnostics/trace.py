"""Diagnostics Trace for EREN OS Diagnostics.

Provides comprehensive tracing for diagnostic operations:
- Operation execution traces
- Validation traces
- Error traces
- Correlation tracking

Philosophy:
    Every diagnostic action must be traceable. Trace enables debugging.
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
    operation: str
    category: str  # validation, health, runtime, etc.
    component: str
    status: str  # started, completed, failed, etc.
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_ms: int = 0
    correlation_id: str = ""
    session_id: str = ""
    success: bool = True
    error: str = ""
    metadata: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "operation": self.operation,
            "category": self.category,
            "component": self.component,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class DiagnosticsTrace:
    """Provides comprehensive tracing for diagnostics.

    Tracks:
    - Operation execution
    - Validation traces
    - Error traces
    - Correlation between operations
    """

    def __init__(self):
        self._entries: list[TraceEntry] = []
        self._by_operation: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_category: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_correlation: dict[str, list[TraceEntry]] = defaultdict(list)
        self._lock = threading.RLock()
        self._current_trace_id: str | None = None
        self._active_operations: dict[str, datetime] = {}

    def start_trace(
        self,
        operation: str,
        category: str,
        component: str,
        correlation_id: str = "",
        session_id: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Start a new trace entry.

        Args:
            operation: Operation name.
            category: Category (validation, health, etc.).
            component: Component being traced.
            correlation_id: Correlation ID for tracking.
            session_id: Session ID if applicable.
            metadata: Additional metadata.

        Returns:
            Trace ID for this trace.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        with self._lock:
            self._current_trace_id = trace_id
            self._active_operations[trace_id] = datetime.now(UTC)

            entry = TraceEntry(
                trace_id=trace_id,
                operation=operation,
                category=category,
                component=component,
                status="started",
                correlation_id=correlation_id,
                session_id=session_id,
                metadata=metadata,
            )

            self._entries.append(entry)
            self._by_operation[operation].append(entry)
            self._by_category[category].append(entry)
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
        """End a trace entry.

        Args:
            trace_id: Trace ID from start_trace.
            status: Final status.
            success: Whether operation succeeded.
            error: Error message if failed.
        """
        with self._lock:
            if trace_id not in self._active_operations:
                return

            start_time = self._active_operations[trace_id]
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )

            # Find and update the entry
            for entry in self._entries:
                if entry.trace_id == trace_id and entry.status == "started":
                    entry.status = status
                    entry.duration_ms = duration_ms
                    entry.success = success
                    entry.error = error
                    break

            del self._active_operations[trace_id]
            if self._current_trace_id == trace_id:
                self._current_trace_id = None

    def add_entry(
        self,
        operation: str,
        category: str,
        component: str,
        status: str = "info",
        correlation_id: str = "",
        session_id: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Add a trace entry.

        Args:
            operation: Operation name.
            category: Category.
            component: Component.
            status: Entry status.
            correlation_id: Correlation ID.
            session_id: Session ID.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            error: Error message.
            metadata: Additional metadata.

        Returns:
            Trace ID for this entry.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        with self._lock:
            entry = TraceEntry(
                trace_id=trace_id,
                operation=operation,
                category=category,
                component=component,
                status=status,
                correlation_id=correlation_id,
                session_id=session_id,
                duration_ms=duration_ms,
                success=success,
                error=error,
                metadata=metadata,
            )

            self._entries.append(entry)
            self._by_operation[operation].append(entry)
            self._by_category[category].append(entry)
            if correlation_id:
                self._by_correlation[correlation_id].append(entry)

        return trace_id

    def get_all_entries(self) -> list[TraceEntry]:
        """Get all trace entries.

        Returns:
            List of all trace entries.
        """
        with self._lock:
            return list(self._entries)

    def get_entries_by_operation(self, operation: str) -> list[TraceEntry]:
        """Get entries for a specific operation.

        Args:
            operation: Operation name.

        Returns:
            List of trace entries.
        """
        with self._lock:
            return list(self._by_operation.get(operation, []))

    def get_entries_by_category(self, category: str) -> list[TraceEntry]:
        """Get entries for a specific category.

        Args:
            category: Category name.

        Returns:
            List of trace entries.
        """
        with self._lock:
            return list(self._by_category.get(category, []))

    def get_entries_by_correlation(self, correlation_id: str) -> list[TraceEntry]:
        """Get entries for a correlation ID.

        Args:
            correlation_id: Correlation ID.

        Returns:
            List of trace entries.
        """
        with self._lock:
            return list(self._by_correlation.get(correlation_id, []))

    def get_failed_entries(self) -> list[TraceEntry]:
        """Get all failed trace entries.

        Returns:
            List of failed trace entries.
        """
        with self._lock:
            return [e for e in self._entries if not e.success]

    def get_summary(self) -> dict:
        """Get trace summary.

        Returns:
            Dictionary with trace summary.
        """
        with self._lock:
            total = len(self._entries)
            succeeded = len([e for e in self._entries if e.success])
            failed = total - succeeded

            # Group by category
            by_category = {}
            for category, entries in self._by_category.items():
                by_category[category] = {
                    "total": len(entries),
                    "succeeded": len([e for e in entries if e.success]),
                    "failed": len([e for e in entries if not e.success]),
                }

            # Group by operation
            by_operation = {}
            for operation, entries in self._by_operation.items():
                by_operation[operation] = {
                    "total": len(entries),
                    "succeeded": len([e for e in entries if e.success]),
                    "failed": len([e for e in entries if not e.success]),
                }

            # Calculate timing stats
            all_durations = [e.duration_ms for e in self._entries if e.duration_ms > 0]
            timing_stats = {}
            if all_durations:
                timing_stats = {
                    "min_ms": min(all_durations),
                    "max_ms": max(all_durations),
                    "avg_ms": sum(all_durations) / len(all_durations),
                    "total_ms": sum(all_durations),
                }

            return {
                "total_entries": total,
                "succeeded": succeeded,
                "failed": failed,
                "success_rate": (succeeded / total * 100) if total > 0 else 0,
                "by_category": by_category,
                "by_operation": by_operation,
                "timing_stats": timing_stats,
                "active_operations": len(self._active_operations),
            }

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with complete trace data.
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
            self._by_operation.clear()
            self._by_category.clear()
            self._by_correlation.clear()
            self._active_operations.clear()
            self._current_trace_id = None


# Global trace instance
_trace: DiagnosticsTrace | None = None
_trace_lock = threading.Lock()


def get_trace() -> DiagnosticsTrace:
    """Get the global diagnostics trace instance.

    Returns:
        Global DiagnosticsTrace instance.
    """
    global _trace
    with _trace_lock:
        if _trace is None:
            _trace = DiagnosticsTrace()
        return _trace


def reset_trace() -> None:
    """Reset global trace."""
    global _trace
    with _trace_lock:
        if _trace is not None:
            _trace.clear()
