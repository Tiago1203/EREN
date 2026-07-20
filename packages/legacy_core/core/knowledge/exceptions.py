"""Exceptions for the Cognitive Knowledge Engine.

Architecture only -- no business logic.
"""

from __future__ import annotations


class KnowledgeError(Exception):
    """Base class for knowledge errors."""

    def __init__(self, message: str = "", **kwargs) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class SourceNotFoundError(KnowledgeError):
    """Raised when a knowledge source is not found."""

    def __init__(self, source_id: str = "") -> None:
        super().__init__(f"Knowledge source '{source_id}' not found")
        self.source_id = source_id


class SourceNotAvailableError(KnowledgeError):
    """Raised when a knowledge source is not available."""

    def __init__(self, source_id: str = "", reason: str = "") -> None:
        super().__init__(f"Knowledge source '{source_id}' not available: {reason}")
        self.source_id = source_id
        self.reason = reason


class QueryFailedError(KnowledgeError):
    """Raised when a knowledge query fails."""

    def __init__(self, query_id: str = "", reason: str = "") -> None:
        super().__init__(f"Knowledge query '{query_id}' failed: {reason}")
        self.query_id = query_id
        self.reason = reason


class SourceRegistrationError(KnowledgeError):
    """Raised when source registration fails."""

    def __init__(self, source_id: str = "", reason: str = "") -> None:
        super().__init__(f"Failed to register source '{source_id}': {reason}")
        self.source_id = source_id
        self.reason = reason


class NoSourcesAvailableError(KnowledgeError):
    """Raised when no sources are available for a query."""

    def __init__(self, query_type: str = "") -> None:
        super().__init__(f"No knowledge sources available for query type: {query_type}")
        self.query_type = query_type


class RoutingError(KnowledgeError):
    """Raised when query routing fails."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(f"Query routing failed: {reason}")
        self.reason = reason


class KnowledgeNotFoundError(KnowledgeError):
    """Raised when requested knowledge is not found."""

    def __init__(self, query: str = "") -> None:
        super().__init__(f"Knowledge not found for query: {query}")
        self.query = query


class ValidationError(KnowledgeError):
    """Raised when validation fails."""

    def __init__(self, field: str = "", reason: str = "") -> None:
        super().__init__(f"Validation failed for '{field}': {reason}")
        self.field = field
        self.reason = reason


class TimeoutError(KnowledgeError):
    """Raised when a knowledge operation times out."""

    def __init__(self, operation: str = "", timeout_ms: int = 0) -> None:
        super().__init__(f"Operation '{operation}' timed out after {timeout_ms}ms")
        self.operation = operation
        self.timeout_ms = timeout_ms
