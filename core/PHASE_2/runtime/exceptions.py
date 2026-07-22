"""Runtime exceptions for the Cognitive Operating System.

This module defines all exceptions that can be raised during runtime operations.
"""

from __future__ import annotations


class RuntimeException(Exception):
    """Base exception for all runtime errors."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RuntimeInitializationError(RuntimeException):
    """Raised when runtime initialization fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class RuntimeBootError(RuntimeException):
    """Raised when boot process fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class RuntimeValidationError(RuntimeException):
    """Raised when runtime validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class RuntimeStartError(RuntimeException):
    """Raised when runtime start fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class RuntimeExecutionError(RuntimeException):
    """Raised when runtime execution fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class RuntimeShutdownError(RuntimeException):
    """Raised when runtime shutdown fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class SessionCreationError(RuntimeException):
    """Raised when session creation fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class CognitiveCycleError(RuntimeException):
    """Raised when cognitive cycle execution fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class HealthCheckError(RuntimeException):
    """Raised when health check fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class ComponentNotAvailableError(RuntimeException):
    """Raised when a required component is not available."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, details)


class EngineExecutionError(RuntimeException):
    """Raised when engine execution fails."""

    def __init__(self, message: str, engine_name: str = "", details: dict | None = None):
        """Initialize the exception.

        Args:
            message: Error message.
            engine_name: Name of the engine that failed.
            details: Additional error details.
        """
        super().__init__(message, details)
        self.engine_name = engine_name
