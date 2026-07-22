"""Composition Trace for the Cognitive Composition Root.

Collects complete audit trail of composition operations.

Architecture only -- no implementations.
"""

from datetime import UTC, datetime


class CompositionTraceEntry:
    """A single trace entry."""

    def __init__(
        self,
        entry_id: str,
        timestamp: str,
        operation: str,
        module_name: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
        correlation_id: str = "",
        metadata: dict = None,
    ):
        self.entry_id = entry_id
        self.timestamp = timestamp
        self.operation = operation
        self.module_name = module_name
        self.duration_ms = duration_ms
        self.success = success
        self.error = error
        self.correlation_id = correlation_id
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "module_name": self.module_name,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


class CompositionTraceCollector:
    """Collects composition traces."""

    def __init__(self):
        self._entries = []
        self._enabled = True
        self._entry_count = 0

    def add_entry(
        self,
        operation: str,
        module_name: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
        correlation_id: str = "",
        metadata: dict = None,
    ) -> CompositionTraceEntry:
        """Add a trace entry."""
        if not self._enabled:
            return None

        self._entry_count += 1
        entry = CompositionTraceEntry(
            entry_id=f"composition_trace_{self._entry_count}",
            timestamp=datetime.now(UTC).isoformat(),
            operation=operation,
            module_name=module_name,
            duration_ms=duration_ms,
            success=success,
            error=error,
            correlation_id=correlation_id,
            metadata=metadata,
        )

        self._entries.append(entry)
        return entry

    def get_all_entries(self) -> list:
        """Get all trace entries."""
        return self._entries.copy()

    def get_by_module(self, module_name: str) -> list:
        """Get trace entries for a module."""
        return [e for e in self._entries if e.module_name == module_name]

    def get_by_operation(self, operation: str) -> list:
        """Get trace entries for an operation."""
        return [e for e in self._entries if e.operation == operation]

    def get_failures(self) -> list:
        """Get failed trace entries."""
        return [e for e in self._entries if not e.success]

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
