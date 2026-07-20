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


# =============================================================================
# Memory Orchestrator Exceptions
# =============================================================================


class MemoryOrchestratorException(MemoryError):
    """Base exception for memory orchestrator errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class MemoryNotRegisteredError(MemoryOrchestratorException):
    """Raised when memory is not registered."""

    def __init__(self, memory_id: str) -> None:
        super().__init__(f"Memory not registered: {memory_id}")
        self.memory_id = memory_id


class MemoryUnavailableError(MemoryOrchestratorException):
    """Raised when memory is unavailable."""

    def __init__(self, memory_id: str, reason: str = "") -> None:
        super().__init__(f"Memory unavailable: {memory_id}. {reason}")
        self.memory_id = memory_id
        self.reason = reason


class MemoryOperationError(MemoryOrchestratorException):
    """Raised when memory operation fails."""

    def __init__(self, operation: str, memory_id: str, message: str) -> None:
        super().__init__(f"Operation '{operation}' failed on {memory_id}: {message}")
        self.operation = operation
        self.memory_id = memory_id


class MemoryReadError(MemoryOrchestratorException):
    """Raised when memory read fails."""

    def __init__(self, memory_id: str, message: str) -> None:
        super().__init__(f"Read failed on {memory_id}: {message}")
        self.memory_id = memory_id


class MemoryWriteError(MemoryOrchestratorException):
    """Raised when memory write fails."""

    def __init__(self, memory_id: str, message: str) -> None:
        super().__init__(f"Write failed on {memory_id}: {message}")
        self.memory_id = memory_id


class MemorySearchError(MemoryOrchestratorException):
    """Raised when memory search fails."""

    def __init__(self, memory_id: str, message: str) -> None:
        super().__init__(f"Search failed on {memory_id}: {message}")
        self.memory_id = memory_id


class MemorySelectionError(MemoryOrchestratorException):
    """Raised when memory selection fails."""

    def __init__(self, policy: str, message: str) -> None:
        super().__init__(f"Selection error ({policy}): {message}")
        self.policy = policy


class MemoryNoResultsError(MemoryOrchestratorException):
    """Raised when no results found in memory."""

    def __init__(self, query: str) -> None:
        super().__init__(f"No results found for query: {query}")
        self.query = query


class MemoryPolicyError(MemoryOrchestratorException):
    """Raised when memory policy cannot be satisfied."""

    def __init__(self, policy: str, message: str) -> None:
        super().__init__(f"Policy error ({policy}): {message}")
        self.policy = policy
