"""Error types and Result monad for EREN."""

from .domain import (
    AuthorizationError,
    ConcurrencyError,
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    InvariantViolationError,
    InvalidStateTransitionError,
    ValidationError,
)
from .result import Err, Ok, Result

__all__ = [
    # Result monad
    "Result",
    "Ok",
    "Err",
    # Domain errors
    "DomainError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "InvalidStateTransitionError",
    "InvariantViolationError",
    "ValidationError",
    "ConcurrencyError",
    "AuthorizationError",
]
