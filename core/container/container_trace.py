"""Container Trace for the Cognitive Dependency Injection Container.

Collects complete audit trail of container operations.

Architecture only -- no implementations.
"""

from datetime import datetime, timezone


class ContainerTraceEntry:
    """A single trace entry."""

    def __init__(
        self,
        entry_id: str,
        timestamp: str,
        operation: str,
        contract: str,
        scope_id: str = "",
        correlation_id: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
        metadata: dict = None,
    ):
        self.entry_id = entry_id
        self.timestamp = timestamp
        self.operation = operation
        self.contract = contract
        self.scope_id = scope_id
        self.correlation_id = correlation_id
        self.duration_ms = duration_ms
        self.success = success
        self.error = error
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "contract": self.contract,
            "scope_id": self.scope_id,
            "correlation_id": self.correlation_id,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


class ContainerTraceCollector:
    """Collects container traces."""

    def __init__(self):
        self._entries = []
        self._enabled = True
        self._entry_count = 0

    def add_entry(
        self,
        operation: str,
        contract: str,
        scope_id: str = "",
        correlation_id: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str = "",
        metadata: dict = None,
    ) -> ContainerTraceEntry:
        """Add a trace entry."""
        if not self._enabled:
            return None

        self._entry_count += 1
        entry = ContainerTraceEntry(
            entry_id=f"container_trace_{self._entry_count}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
            contract=contract,
            scope_id=scope_id,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata,
        )

        self._entries.append(entry)
        return entry

    def get_all_entries(self) -> list:
        """Get all trace entries."""
        return self._entries.copy()

    def get_by_contract(self, contract: str) -> list:
        """Get trace entries for a contract."""
        return [e for e in self._entries if e.contract == contract]

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
