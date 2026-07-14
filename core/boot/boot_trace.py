"""Boot trace for the Cognitive Boot Manager.

Collects complete audit trail of boot operations.

Architecture only -- no implementations.
"""

from datetime import UTC, datetime


class BootTraceEntry:
    """A single trace entry."""

    def __init__(
        self,
        entry_id: str,
        timestamp: str,
        step_name: str,
        state: str,
        status: str,
        error: str = "",
        duration_ms: int = 0,
        metadata: dict = None,
    ):
        self.entry_id = entry_id
        self.timestamp = timestamp
        self.step_name = step_name
        self.state = state
        self.status = status
        self.error = error
        self.duration_ms = duration_ms
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "step_name": self.step_name,
            "state": self.state,
            "status": self.status,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class BootTraceCollector:
    """Collects boot traces."""

    def __init__(self):
        self._entries = []
        self._enabled = True
        self._entry_count = 0

    def add_entry(
        self,
        step_name: str,
        state: str,
        status: str,
        error: str = "",
        duration_ms: int = 0,
        metadata: dict = None,
    ) -> BootTraceEntry:
        """Add a trace entry."""
        if not self._enabled:
            return None

        self._entry_count += 1
        entry = BootTraceEntry(
            entry_id=f"boot_trace_{self._entry_count}",
            timestamp=datetime.now(UTC).isoformat(),
            step_name=step_name,
            state=state,
            status=status,
            error=error,
            duration_ms=duration_ms,
            metadata=metadata,
        )

        self._entries.append(entry)
        return entry

    def get_all_entries(self) -> list:
        """Get all trace entries."""
        return self._entries.copy()

    def clear(self):
        """Clear trace entries."""
        self._entries.clear()

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True

    @property
    def entry_count(self) -> int:
        return self._entry_count
