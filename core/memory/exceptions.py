"""Exception types for the Memory engine."""

from __future__ import annotations


class MemoryError(Exception):
    """Base class for all memory-related errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class MemoryNotFoundError(MemoryError):
    """Raised when a memory is not found."""

    def __init__(self, memory_id: str) -> None:
        super().__init__(f"Memory '{memory_id}' not found")
        self.memory_id = memory_id


class MemoryAlreadyExistsError(MemoryError):
    """Raised when attempting to create a duplicate memory."""

    def __init__(self, memory_id: str) -> None:
        super().__init__(f"Memory '{memory_id}' already exists")
        self.memory_id = memory_id


class MemoryCapacityError(MemoryError):
    """Raised when memory store exceeds capacity."""

    def __init__(
        self,
        memory_type: str = "",
        current_size: int = 0,
        max_size: int = 0,
    ) -> None:
        super().__init__(
            f"Memory store '{memory_type}' exceeded capacity "
            f"({current_size}/{max_size})"
        )
        self.memory_type = memory_type
        self.current_size = current_size
        self.max_size = max_size


class MemoryConsolidationError(MemoryError):
    """Raised when memory consolidation fails."""

    def __init__(self, memory_id: str = "", reason: str = "") -> None:
        super().__init__(
            f"Failed to consolidate memory '{memory_id}': {reason}"
        )
        self.memory_id = memory_id
        self.reason = reason


class MemoryDecayError(MemoryError):
    """Raised when memory decay processing fails."""

    def __init__(self, memory_id: str = "") -> None:
        super().__init__(f"Failed to process decay for memory '{memory_id}'")
        self.memory_id = memory_id


class MemoryRetrievalError(MemoryError):
    """Raised when memory retrieval fails."""

    def __init__(self, query: str = "", reason: str = "") -> None:
        super().__init__(f"Failed to retrieve memory for query '{query}': {reason}")
        self.query = query
        self.reason = reason


class MemoryRelationshipError(MemoryError):
    """Raised when memory relationship operations fail."""

    def __init__(
        self,
        memory_id: str = "",
        target_id: str = "",
        reason: str = "",
    ) -> None:
        super().__init__(
            f"Relationship error between '{memory_id}' and '{target_id}': {reason}"
        )
        self.memory_id = memory_id
        self.target_id = target_id
        self.reason = reason


class MemoryValidationError(MemoryError):
    """Raised when memory validation fails."""

    def __init__(
        self,
        memory_id: str = "",
        violations: list[str] | None = None,
    ) -> None:
        violations_str = "; ".join(violations or [])
        super().__init__(
            f"Validation failed for memory '{memory_id}': {violations_str}"
        )
        self.memory_id = memory_id
        self.violations = violations or []


class MemorySnapshotError(MemoryError):
    """Raised when memory snapshot operations fail."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(f"Failed to create memory snapshot: {reason}")
