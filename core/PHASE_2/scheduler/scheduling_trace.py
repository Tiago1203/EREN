"""Trace collection for the Cognitive Scheduler.

Collects complete audit trail of scheduling operations.

Architecture only -- no implementations.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class SchedulingTraceEntry:
    """A single entry in the scheduling trace."""

    entry_id: str
    task_id: str
    session_id: str
    correlation_id: str
    timestamp: str
    action: str
    task_state: str
    capability: str
    strategy_used: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(UTC).isoformat())


class SchedulingTraceCollector:
    """Collects and manages scheduling traces."""

    def __init__(self) -> None:
        """Initialize the trace collector."""
        self._entries: list[SchedulingTraceEntry] = []
        self._by_task: dict[str, list[SchedulingTraceEntry]] = {}
        self._by_session: dict[str, list[SchedulingTraceEntry]] = {}
        self._lock = threading.RLock()
        self._enabled = True

    def add_entry(
        self,
        task_id: str,
        session_id: str,
        correlation_id: str,
        action: str,
        task_state: str,
        capability: str,
        strategy_used: str,
        metadata: dict | None = None,
    ) -> SchedulingTraceEntry | None:
        """Add a trace entry."""
        if not self._enabled:
            return None

        entry_id = f"sched_trace_{len(self._entries)}"

        entry = SchedulingTraceEntry(
            entry_id=entry_id,
            task_id=task_id,
            session_id=session_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC).isoformat(),
            action=action,
            task_state=task_state,
            capability=capability,
            strategy_used=strategy_used,
            metadata=metadata or {},
        )

        with self._lock:
            self._entries.append(entry)
            self._by_task.setdefault(task_id, []).append(entry)
            self._by_session.setdefault(session_id, []).append(entry)

        return entry

    def get_trace(self, task_id: str) -> list[SchedulingTraceEntry]:
        """Get trace for a task."""
        with self._lock:
            return list(self._by_task.get(task_id, []))

    def get_session_trace(self, session_id: str) -> list[SchedulingTraceEntry]:
        """Get trace for a session."""
        with self._lock:
            return list(self._by_session.get(session_id, []))

    def get_all_entries(self) -> list[SchedulingTraceEntry]:
        """Get all trace entries."""
        with self._lock:
            return list(self._entries)

    def clear(self, task_id: str | None = None) -> None:
        """Clear trace entries."""
        with self._lock:
            if task_id:
                self._by_task.pop(task_id, None)
                self._entries = [e for e in self._entries if e.task_id != task_id]
            else:
                self._entries.clear()
                self._by_task.clear()
                self._by_session.clear()

    def disable(self) -> None:
        """Disable trace collection."""
        self._enabled = False

    def enable(self) -> None:
        """Enable trace collection."""
        self._enabled = True

    @property
    def entry_count(self) -> int:
        """Get total entry count."""
        with self._lock:
            return len(self._entries)
