"""RAG Pipeline exceptions for EREN OS."""

from __future__ import annotations


class RAGError(Exception):
    """Base exception for RAG errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class RetrievalError(RAGError):
    """Raised when retrieval fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Retrieval failed: {reason}")
        self.reason = reason


class NoContextError(RAGError):
    """Raised when no relevant context is found."""

    def __init__(self, query: str = ""):
        super().__init__(f"No relevant context found for query: {query}")
        self.query = query


class PromptBuildError(RAGError):
    """Raised when prompt building fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Prompt build failed: {reason}")
        self.reason = reason


class TokenBudgetExceededError(RAGError):
    """Raised when token budget is exceeded."""

    def __init__(self, required: int, available: int):
        super().__init__(
            f"Token budget exceeded: required {required}, available {available}"
        )
        self.required = required
        self.available = available


class ModelSelectionError(RAGError):
    """Raised when model selection fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Model selection failed: {reason}")
        self.reason = reason


class GenerationError(RAGError):
    """Raised when generation fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Generation failed: {reason}")
        self.reason = reason


class CitationError(RAGError):
    """Raised when citation building fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Citation failed: {reason}")
        self.reason = reason


class ValidationError(RAGError):
    """Raised when validation fails."""

    def __init__(self, field: str, reason: str = ""):
        super().__init__(f"Validation error on {field}: {reason}")
        self.field = field
        self.reason = reason


class ProviderError(RAGError):
    """Raised when provider interaction fails."""

    def __init__(self, provider: str, reason: str = ""):
        super().__init__(f"Provider {provider} error: {reason}")
        self.provider = provider
        self.reason = reason


class TimeoutError(RAGError):
    """Raised when operation times out."""

    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds}s"
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds
