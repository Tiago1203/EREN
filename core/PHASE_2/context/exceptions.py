"""Exceptions for the Cognitive Context System.

Provides a typed exception hierarchy for context operations.

Architecture only — no business logic.
"""

from __future__ import annotations


class ContextError(Exception):
    """Base class for all context errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class ContextNotFoundError(ContextError):
    """Raised when a context is not found.

    Attributes:
        context_id: The ID of the context that was not found.
    """

    def __init__(self, context_id: str) -> None:
        super().__init__(f"Context '{context_id}' not found")
        self.context_id = context_id


class ContextAlreadyExistsError(ContextError):
    """Raised when attempting to create a duplicate context.

    Attributes:
        context_id: The ID of the existing context.
    """

    def __init__(self, context_id: str) -> None:
        super().__init__(f"Context '{context_id}' already exists")
        self.context_id = context_id


class ContextImmutableError(ContextError):
    """Raised when attempting to modify an immutable context.

    Contexts are immutable. To "modify" a context, create a new one
    with the changes applied.
    """

    def __init__(self, context_id: str = "") -> None:
        super().__init__(
            f"Context '{context_id}' is immutable. "
            "Use the update methods to create a new context."
        )
        self.context_id = context_id


class ContextStatusError(ContextError):
    """Raised when an operation is invalid for the current context status.

    Attributes:
        context_id: The context ID.
        current_status: Current status of the context.
        required_status: Status required for the operation.
    """

    def __init__(
        self,
        context_id: str = "",
        current_status: str = "",
        required_status: str = "",
    ) -> None:
        super().__init__(
            f"Context '{context_id}' has status '{current_status}', "
            f"but requires '{required_status}' for this operation"
        )
        self.context_id = context_id
        self.current_status = current_status
        self.required_status = required_status


class ContextValidationError(ContextError):
    """Raised when context validation fails.

    Attributes:
        context_id: The context that failed validation.
        violations: List of validation violations.
    """

    def __init__(
        self,
        context_id: str = "",
        violations: list[str] | None = None,
    ) -> None:
        violations_str = "; ".join(violations or [])
        super().__init__(
            f"Validation failed for context '{context_id}': {violations_str}"
        )
        self.context_id = context_id
        self.violations = violations or []


class BlackboardError(ContextError):
    """Base class for blackboard errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.context = kwargs


class BlackboardEntryNotFoundError(BlackboardError):
    """Raised when a blackboard entry is not found."""

    def __init__(self, entry_id: str) -> None:
        super().__init__(f"Blackboard entry '{entry_id}' not found")
        self.entry_id = entry_id


class BlackboardWriteError(BlackboardError):
    """Raised when writing to the blackboard fails."""

    def __init__(self, entry_id: str = "", reason: str = "") -> None:
        super().__init__(f"Failed to write entry '{entry_id}': {reason}")
        self.entry_id = entry_id
        self.reason = reason


class ContextMergeError(ContextError):
    """Raised when merging contexts fails.

    Attributes:
        context_ids: IDs of contexts that failed to merge.
        reason: Why the merge failed.
    """

    def __init__(
        self,
        context_ids: list[str] | None = None,
        reason: str = "",
    ) -> None:
        ids_str = ", ".join(context_ids or [])
        super().__init__(f"Failed to merge contexts [{ids_str}]: {reason}")
        self.context_ids = context_ids or []
        self.reason = reason


class ContextSnapshotError(ContextError):
    """Raised when context snapshot operations fail."""

    def __init__(self, context_id: str = "", reason: str = "") -> None:
        super().__init__(f"Snapshot error for context '{context_id}': {reason}")
        self.context_id = context_id
        self.reason = reason


class ContextExpiredError(ContextError):
    """Raised when accessing an expired context.

    Attributes:
        context_id: The expired context ID.
        expired_at: When the context expired.
    """

    def __init__(self, context_id: str = "", expired_at: str = "") -> None:
        super().__init__(
            f"Context '{context_id}' expired at {expired_at}"
        )
        self.context_id = context_id
        self.expired_at = expired_at


class ContextCapacityError(ContextError):
    """Raised when context storage exceeds capacity.

    Attributes:
        current_count: Current number of contexts.
        max_count: Maximum allowed contexts.
    """

    def __init__(self, current_count: int = 0, max_count: int = 0) -> None:
        super().__init__(
            f"Context storage full ({current_count}/{max_count})"
        )
        self.current_count = current_count
        self.max_count = max_count


class ConfidenceError(ContextError):
    """Raised when confidence operations fail.

    Attributes:
        context_id: The context ID.
        reason: Why confidence calculation failed.
    """

    def __init__(self, context_id: str = "", reason: str = "") -> None:
        super().__init__(f"Confidence error for context '{context_id}': {reason}")
        self.context_id = context_id
        self.reason = reason
