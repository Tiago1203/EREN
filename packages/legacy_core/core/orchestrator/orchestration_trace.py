"""Trace collection for the Cognitive Orchestrator.

Collects complete audit trail of orchestration.

Architecture only -- no implementations.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Trace Entry
# =============================================================================


@dataclass(frozen=True)
class OrchestrationTraceEntry:
    """A single entry in the orchestration trace."""

    entry_id: str
    session_id: str
    correlation_id: str
    timestamp: str
    from_state: str | None
    to_state: str
    reason: str
    motor_active: str = ""
    phase: str = ""
    events_count: int = 0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(UTC).isoformat())


# =============================================================================
# Trace Collector
# =============================================================================


class OrchestrationTraceCollector:
    """Collects and manages orchestration traces."""

    def __init__(self) -> None:
        """Initialize the trace collector."""
        self._entries: list[OrchestrationTraceEntry] = []
        self._by_session: dict[str, list[OrchestrationTraceEntry]] = {}
        self._lock = threading.RLock()
        self._enabled = True

    def add_entry(
        self,
        session_id: str,
        correlation_id: str,
        from_state: str | None,
        to_state: str,
        reason: str,
        motor_active: str = "",
        phase: str = "",
        metadata: dict | None = None,
    ) -> OrchestrationTraceEntry:
        """Add a trace entry.

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.
            from_state: Previous state.
            to_state: New state.
            reason: Reason for entry.
            motor_active: Active motor.
            phase: Active phase.
            metadata: Additional metadata.

        Returns:
            The trace entry.
        """
        if not self._enabled:
            return None

        entry_id = f"trace_{len(self._entries)}"

        entry = OrchestrationTraceEntry(
            entry_id=entry_id,
            session_id=session_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC).isoformat(),
            from_state=from_state,
            to_state=to_state,
            reason=reason,
            motor_active=motor_active,
            phase=phase,
            metadata=metadata or {},
        )

        with self._lock:
            self._entries.append(entry)
            self._by_session.setdefault(session_id, []).append(entry)

        return entry

    def get_trace(self, session_id: str) -> list[OrchestrationTraceEntry]:
        """Get trace for a session.

        Args:
            session_id: Session ID.

        Returns:
            Trace entries.
        """
        with self._lock:
            return list(self._by_session.get(session_id, []))

    def get_all_entries(self) -> list[OrchestrationTraceEntry]:
        """Get all trace entries.

        Returns:
            All trace entries.
        """
        with self._lock:
            return list(self._entries)

    def get_entries_by_correlation(
        self,
        correlation_id: str,
    ) -> list[OrchestrationTraceEntry]:
        """Get trace entries by correlation ID.

        Args:
            correlation_id: Correlation ID.

        Returns:
            Matching entries.
        """
        with self._lock:
            return [
                e for e in self._entries
                if e.correlation_id == correlation_id
            ]

    def get_entries_by_state(
        self,
        state: str,
    ) -> list[OrchestrationTraceEntry]:
        """Get trace entries for a specific state.

        Args:
            state: State to filter by.

        Returns:
            Matching entries.
        """
        with self._lock:
            return [
                e for e in self._entries
                if e.to_state == state
            ]

    def clear(self, session_id: str | None = None) -> None:
        """Clear trace entries.

        Args:
            session_id: Session ID to clear, or None for all.
        """
        with self._lock:
            if session_id:
                self._by_session.pop(session_id, None)
                self._entries = [
                    e for e in self._entries
                    if e.session_id != session_id
                ]
            else:
                self._entries.clear()
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

    @property
    def session_count(self) -> int:
        """Get number of sessions tracked."""
        with self._lock:
            return len(self._by_session)


# =============================================================================
# Trace Analyzer
# =============================================================================


class TraceAnalyzer:
    """Analyzes orchestration traces."""

    def __init__(self, collector: OrchestrationTraceCollector) -> None:
        """Initialize the analyzer.

        Args:
            collector: Trace collector.
        """
        self._collector = collector

    def analyze_session(self, session_id: str) -> dict:
        """Analyze a session trace.

        Args:
            session_id: Session ID.

        Returns:
            Analysis results.
        """
        entries = self._collector.get_trace(session_id)

        if not entries:
            return {}

        # Calculate statistics
        state_counts: dict[str, int] = {}
        motor_usage: dict[str, int] = {}

        for entry in entries:
            state_counts[entry.to_state] = state_counts.get(entry.to_state, 0) + 1
            if entry.motor_active:
                motor_usage[entry.motor_active] = (
                    motor_usage.get(entry.motor_active, 0) + 1
                )

        return {
            "session_id": session_id,
            "total_entries": len(entries),
            "state_distribution": state_counts,
            "motor_usage": motor_usage,
            "start_time": entries[0].timestamp if entries else None,
            "end_time": entries[-1].timestamp if entries else None,
        }

    def get_common_paths(self) -> list[tuple[str, ...]]:
        """Get common execution paths.

        Returns:
            Common paths as state tuples.
        """
        entries = self._collector.get_all_entries()

        # Group by session
        by_session: dict[str, list[OrchestrationTraceEntry]] = {}
        for entry in entries:
            by_session.setdefault(entry.session_id, []).append(entry)

        # Extract paths
        paths: list[tuple[str, ...]] = []
        for session_entries in by_session.values():
            path = tuple(e.to_state for e in session_entries)
            paths.append(path)

        return paths
