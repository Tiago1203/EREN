"""Session trace for the Cognitive Session Manager.

Collects complete audit trail of session operations.

Architecture only -- no implementations.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class SessionTraceEntry:
    """A single entry in the session trace."""

    entry_id: str
    session_id: str
    correlation_id: str
    timestamp: str
    action: str
    session_state: str
    previous_state: str | None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(UTC).isoformat())


class SessionTraceCollector:
    """Collects and manages session traces."""

    def __init__(self) -> None:
        """Initialize the trace collector."""
        self._entries: list[SessionTraceEntry] = []
        self._by_session: dict[str, list[SessionTraceEntry]] = {}
        self._lock = threading.RLock()
        self._enabled = True

    def add_entry(
        self,
        session_id: str,
        correlation_id: str,
        action: str,
        session_state: str,
        previous_state: str | None = None,
        metadata: dict | None = None,
    ) -> SessionTraceEntry:
        """Add a trace entry.

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.
            action: Action performed.
            session_state: Current state.
            previous_state: Previous state.
            metadata: Additional metadata.

        Returns:
            The trace entry.
        """
        if not self._enabled:
            return None

        entry_id = f"session_trace_{len(self._entries)}"

        entry = SessionTraceEntry(
            entry_id=entry_id,
            session_id=session_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC).isoformat(),
            action=action,
            session_state=session_state,
            previous_state=previous_state,
            metadata=metadata or {},
        )

        with self._lock:
            self._entries.append(entry)
            self._by_session.setdefault(session_id, []).append(entry)

        return entry

    def get_trace(self, session_id: str) -> list[SessionTraceEntry]:
        """Get trace for a session.

        Args:
            session_id: Session ID.

        Returns:
            Trace entries.
        """
        with self._lock:
            return list(self._by_session.get(session_id, []))

    def get_all_entries(self) -> list[SessionTraceEntry]:
        """Get all trace entries.

        Returns:
            All trace entries.
        """
        with self._lock:
            return list(self._entries)

    def get_entries_by_correlation(self, correlation_id: str) -> list[SessionTraceEntry]:
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

    def get_entries_by_state(self, state: str) -> list[SessionTraceEntry]:
        """Get trace entries for a specific state.

        Args:
            state: State to filter by.

        Returns:
            Matching entries.
        """
        with self._lock:
            return [
                e for e in self._entries
                if e.session_state == state
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
