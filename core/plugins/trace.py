"""Plugin Trace for EREN OS Cognitive Plugin Framework.

Provides comprehensive tracing for plugin operations.
"""

from __future__ import annotations

import threading
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TraceEntry:
    """A single trace entry."""

    trace_id: str
    plugin_id: str
    operation: str
    phase: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    success: bool = True
    error: str = ""
    metadata: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "plugin_id": self.plugin_id,
            "operation": self.operation,
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class PluginTrace:
    """Provides comprehensive tracing for plugins.

    Tracks:
    - Plugin lifecycle operations
    - Load/unload operations
    - Dependency resolution
    - Errors
    """

    def __init__(self):
        """Initialize the trace collector."""
        self._entries: list[TraceEntry] = []
        self._by_plugin: dict[str, list[TraceEntry]] = defaultdict(list)
        self._by_phase: dict[str, list[TraceEntry]] = defaultdict(list)
        self._lock = threading.RLock()
        self._active_traces: dict[str, datetime] = {}

    def start_trace(
        self,
        plugin_id: str,
        operation: str,
        metadata: dict | None = None,
    ) -> str:
        """Start a new trace.

        Args:
            plugin_id: Plugin ID.
            operation: Operation name.
            metadata: Additional metadata.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        with self._lock:
            self._active_traces[trace_id] = datetime.now(timezone.utc)

            entry = TraceEntry(
                trace_id=trace_id,
                plugin_id=plugin_id,
                operation=operation,
                phase="start",
                metadata=metadata,
            )

            self._entries.append(entry)
            self._by_plugin[plugin_id].append(entry)

        return trace_id

    def end_trace(
        self,
        trace_id: str,
        plugin_id: str,
        success: bool = True,
        error: str = "",
    ) -> None:
        """End a trace.

        Args:
            trace_id: Trace ID from start_trace.
            plugin_id: Plugin ID.
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
                if entry.trace_id == trace_id and entry.operation in ("load", "initialize", "activate"):
                    entry.duration_ms = duration_ms
                    entry.success = success
                    entry.error = error
                    break

            del self._active_traces[trace_id]

    def add_load_entry(
        self,
        plugin_id: str,
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
        metadata: dict | None = None,
    ) -> str:
        """Add a load operation entry.

        Args:
            plugin_id: Plugin ID.
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
            plugin_id=plugin_id,
            operation="load",
            phase="loading",
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata,
        )

        with self._lock:
            self._entries.append(entry)
            self._by_plugin[plugin_id].append(entry)
            self._by_phase["loading"].append(entry)

        return trace_id

    def add_init_entry(
        self,
        plugin_id: str,
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
    ) -> str:
        """Add an init operation entry.

        Args:
            plugin_id: Plugin ID.
            duration_ms: Duration in milliseconds.
            success: Whether operation succeeded.
            error: Error message.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        entry = TraceEntry(
            trace_id=trace_id,
            plugin_id=plugin_id,
            operation="initialize",
            phase="initialization",
            duration_ms=duration_ms,
            success=success,
            error=error,
        )

        with self._lock:
            self._entries.append(entry)
            self._by_plugin[plugin_id].append(entry)
            self._by_phase["initialization"].append(entry)

        return trace_id

    def add_activation_entry(
        self,
        plugin_id: str,
        success: bool = True,
        error: str = "",
    ) -> str:
        """Add an activation entry.

        Args:
            plugin_id: Plugin ID.
            success: Whether operation succeeded.
            error: Error message.

        Returns:
            Trace ID.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:16]}"

        entry = TraceEntry(
            trace_id=trace_id,
            plugin_id=plugin_id,
            operation="activate",
            phase="activation",
            success=success,
            error=error,
        )

        with self._lock:
            self._entries.append(entry)
            self._by_plugin[plugin_id].append(entry)
            self._by_phase["activation"].append(entry)

        return trace_id

    def get_all_entries(self) -> list[TraceEntry]:
        """Get all trace entries.

        Returns:
            List of all entries.
        """
        with self._lock:
            return list(self._entries)

    def get_entries_by_plugin(self, plugin_id: str) -> list[TraceEntry]:
        """Get entries for a plugin.

        Args:
            plugin_id: Plugin ID.

        Returns:
            List of entries.
        """
        with self._lock:
            return list(self._by_plugin.get(plugin_id, []))

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

            return {
                "total_entries": total,
                "succeeded": succeeded,
                "failed": failed,
                "success_rate": (succeeded / total * 100) if total > 0 else 0,
                "active_traces": len(self._active_traces),
                "plugins_traced": len(self._by_plugin),
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
            self._by_plugin.clear()
            self._by_phase.clear()
            self._active_traces.clear()


# Global trace instance
_trace: PluginTrace | None = None
_trace_lock = threading.Lock()


def get_plugin_trace() -> PluginTrace:
    """Get the global plugin trace instance.

    Returns:
        Global PluginTrace instance.
    """
    global _trace
    with _trace_lock:
        if _trace is None:
            _trace = PluginTrace()
        return _trace


def reset_plugin_trace() -> None:
    """Reset global trace."""
    global _trace
    with _trace_lock:
        if _trace is not None:
            _trace.clear()
