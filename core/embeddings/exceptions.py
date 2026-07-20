"""Embedding exceptions for EREN Embedding Provider Layer."""

from __future__ import annotations


class EmbeddingError(Exception):
    """Base exception for embedding errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class ProviderNotFoundError(EmbeddingError):
    """Raised when a provider is not found."""

    def __init__(self, provider: str):
        super().__init__(f"Embedding provider not found: {provider}")
        self.provider = provider


class ModelNotFoundError(EmbeddingError):
    """Raised when a model is not found."""

    def __init__(self, model: str):
        super().__init__(f"Embedding model not found: {model}")
        self.model = model


class ProviderUnavailableError(EmbeddingError):
    """Raised when a provider is unavailable."""

    def __init__(self, provider: str, reason: str = ""):
        super().__init__(f"Provider {provider} is unavailable: {reason}")
        self.provider = provider
        self.reason = reason


class GenerationError(EmbeddingError):
    """Raised when embedding generation fails."""

    def __init__(self, message: str = "", provider: str = ""):
        super().__init__(f"Embedding generation failed: {message}")
        self.provider = provider


class ValidationError(EmbeddingError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}")


class ConfigurationError(EmbeddingError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class HealthCheckError(EmbeddingError):
    """Raised when health check fails."""

    def __init__(self, provider: str, message: str = ""):
        super().__init__(f"Health check failed for {provider}: {message}")
        self.provider = provider
        self.message = message


class RateLimitError(EmbeddingError):
    """Raised when rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: int = 0):
        super().__init__(f"Rate limit exceeded for {provider}")
        self.provider = provider
        self.retry_after = retry_after


class AuthenticationError(EmbeddingError):
    """Raised when authentication fails."""

    def __init__(self, provider: str):
        super().__init__(f"Authentication failed for {provider}")
        self.provider = provider


class RegistryError(EmbeddingError):
    """Raised when registry operation fails."""

    def __init__(self, operation: str, reason: str = ""):
        super().__init__(f"Registry error during {operation}: {reason}")
        self.operation = operation
        self.reason = reason


class SelectionError(EmbeddingError):
    """Raised when provider selection fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Provider selection failed: {reason}")
        self.reason = reason
