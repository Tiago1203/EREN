"""Lifecycle trace for the Cognitive Lifecycle Manager."""

from datetime import UTC, datetime


class LifecycleTraceEntry:
    """A single trace entry."""

    def __init__(
        self,
        entry_id: str,
        session_id: str,
        correlation_id: str,
        timestamp: str,
        from_state: str,
        to_state: str,
        event: str,
        reason: str = "",
        actor: str = "",
        metadata: dict = None,
    ):
        self.entry_id = entry_id
        self.session_id = session_id
        self.correlation_id = correlation_id
        self.timestamp = timestamp
        self.from_state = from_state
        self.to_state = to_state
        self.event = event
        self.reason = reason
        self.actor = actor
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "event": self.event,
            "reason": self.reason,
            "actor": self.actor,
            "metadata": self.metadata,
        }


class LifecycleTraceCollector:
    """Collects lifecycle traces."""

    def __init__(self):
        self._entries = []
        self._enabled = True
        self._entry_count = 0

    def add_entry(
        self,
        session_id: str,
        correlation_id: str,
        from_state: str,
        to_state: str,
        event: str,
        reason: str = "",
        actor: str = "",
        metadata: dict = None,
    ) -> LifecycleTraceEntry:
        """Add a trace entry."""
        if not self._enabled:
            return None

        self._entry_count += 1
        entry = LifecycleTraceEntry(
            entry_id=f"lifecycle_trace_{self._entry_count}",
            session_id=session_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC).isoformat(),
            from_state=from_state,
            to_state=to_state,
            event=event,
            reason=reason,
            actor=actor,
            metadata=metadata,
        )

        self._entries.append(entry)
        return entry

    def get_trace(self, session_id: str) -> list:
        """Get trace for a session."""
        return [e for e in self._entries if e.session_id == session_id]

    def get_all_entries(self) -> list:
        """Get all trace entries."""
        return self._entries.copy()

    def clear(self, session_id: str = None):
        """Clear trace entries."""
        if session_id:
            self._entries = [e for e in self._entries if e.session_id != session_id]
        else:
            self._entries.clear()

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True

    @property
    def entry_count(self) -> int:
        return self._entry_count
