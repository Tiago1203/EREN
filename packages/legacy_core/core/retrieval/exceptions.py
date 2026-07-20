"""Retrieval exceptions for EREN Semantic Retrieval Engine."""

from __future__ import annotations


class RetrievalError(Exception):
    """Base exception for retrieval errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class RetrievalPlanError(RetrievalError):
    """Raised when planning fails."""

    def __init__(self, query: str, reason: str = ""):
        super().__init__(f"Failed to plan retrieval for '{query}': {reason}")
        self.query = query
        self.reason = reason


class RetrievalExecutionError(RetrievalError):
    """Raised when retrieval execution fails."""

    def __init__(self, source: str, reason: str = ""):
        super().__init__(f"Retrieval failed from {source}: {reason}")
        self.source = source
        self.reason = reason


class NoResultsError(RetrievalError):
    """Raised when no results are found."""

    def __init__(self, query: str):
        super().__init__(f"No results found for query: {query}")
        self.query = query


class MemorySourceUnavailableError(RetrievalError):
    """Raised when a memory source is unavailable."""

    def __init__(self, source: str):
        super().__init__(f"Memory source unavailable: {source}")
        self.source = source


class PolicyNotSupportedError(RetrievalError):
    """Raised when a policy is not supported."""

    def __init__(self, policy: str):
        super().__init__(f"Retrieval policy not supported: {policy}")
        self.policy = policy


class ContextOverflowError(RetrievalError):
    """Raised when context exceeds limits."""

    def __init__(self, tokens: int, max_tokens: int):
        super().__init__(f"Context overflow: {tokens} tokens exceeds max {max_tokens}")
        self.tokens = tokens
        self.max_tokens = max_tokens


class RankingError(RetrievalError):
    """Raised when ranking fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Ranking failed: {reason}")
        self.reason = reason


class RegistryError(RetrievalError):
    """Raised when registry operation fails."""

    def __init__(self, operation: str, reason: str = ""):
        super().__init__(f"Registry error during {operation}: {reason}")
        self.operation = operation
        self.reason = reason
