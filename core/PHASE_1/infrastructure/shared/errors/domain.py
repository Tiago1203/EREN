"""Domain-specific errors for EREN.

All domain errors should inherit from DomainError to enable
consistent error handling across the application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class DomainError(Exception):
    """Base class for all domain errors in EREN.

    Domain errors represent violations of business rules and invariants.
    They should be used instead of generic exceptions for domain logic.

    Attributes:
        message: Human-readable error message.
        code: Machine-readable error code.
        details: Additional context about the error.
    """

    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"[{self.code}] {self.message}: {self.details}"
        return f"[{self.code}] {self.message}"


class EntityNotFoundError(DomainError):
    """Raised when an entity cannot be found by its identifier."""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            code="ENTITY_NOT_FOUND",
            details=details or {"entity_type": entity_type, "entity_id": entity_id},
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEntityError(DomainError):
    """Raised when attempting to create a duplicate entity."""

    def __init__(
        self,
        entity_type: str,
        identifier: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=f"{entity_type} with identifier '{identifier}' already exists",
            code="DUPLICATE_ENTITY",
            details=details or {"entity_type": entity_type, "identifier": identifier},
        )
        self.entity_type = entity_type
        self.identifier = identifier


class InvalidStateTransitionError(DomainError):
    """Raised when an invalid state transition is attempted."""

    def __init__(
        self,
        entity_type: str,
        current_state: str,
        target_state: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=f"Invalid transition from {current_state} to {target_state} for {entity_type}",
            code="INVALID_STATE_TRANSITION",
            details=details
            or {"entity_type": entity_type, "current_state": current_state, "target_state": target_state},
        )
        self.entity_type = entity_type
        self.current_state = current_state
        self.target_state = target_state


class InvariantViolationError(DomainError):
    """Raised when a domain invariant is violated."""

    def __init__(
        self,
        invariant: str,
        entity_type: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=f"Invariant '{invariant}' violated in {entity_type}",
            code="INVARIANT_VIOLATION",
            details=details or {"invariant": invariant, "entity_type": entity_type},
        )
        self.invariant = invariant
        self.entity_type = entity_type


class ValidationError(DomainError):
    """Raised when domain validation fails."""

    def __init__(
        self,
        field: str,
        value: str,
        reason: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=f"Validation failed for field '{field}': {reason}",
            code="VALIDATION_ERROR",
            details=details or {"field": field, "value": value, "reason": reason},
        )
        self.field = field
        self.value = value
        self.reason = reason


class ConcurrencyError(DomainError):
    """Raised when optimistic locking detects a conflict."""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        expected_version: int,
        actual_version: int,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=f"Concurrency conflict in {entity_type} '{entity_id}': "
            f"expected version {expected_version}, got {actual_version}",
            code="CONCURRENCY_ERROR",
            details=details
            or {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "expected_version": expected_version,
                "actual_version": actual_version,
            },
        )
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.expected_version = expected_version
        self.actual_version = actual_version


class AuthorizationError(DomainError):
    """Raised when an unauthorized action is attempted."""

    def __init__(
        self,
        action: str,
        subject: str,
        reason: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=f"Not authorized to {action} on {subject}: {reason}",
            code="AUTHORIZATION_ERROR",
            details=details or {"action": action, "subject": subject, "reason": reason},
        )
        self.action = action
        self.subject = subject
        self.reason = reason
