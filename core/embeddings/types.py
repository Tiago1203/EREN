"""Embedding types for EREN Embedding Provider Layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Embedding Providers
# =============================================================================


class EmbeddingProvider(str, Enum):
    """Supported embedding providers."""

    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"


# =============================================================================
# Embedding Policies
# =============================================================================


class EmbeddingPolicy(str, Enum):
    """Embedding provider selection policies."""

    DEFAULT = "default"
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    FAILOVER = "failover"
    ROUND_ROBIN = "round_robin"
    HEALTHY_FIRST = "healthy_first"


# =============================================================================
# Embedding
# =============================================================================


@dataclass
class Embedding:
    """A single embedding vector."""

    vector: list[float]
    model: str
    provider: EmbeddingProvider
    dimensions: int = 0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Post initialization."""
        if self.dimensions == 0:
            self.dimensions = len(self.vector)

    @property
    def size(self) -> int:
        """Get embedding size."""
        return len(self.vector)

    def to_list(self) -> list[float]:
        """Convert to list."""
        return self.vector

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "vector": self.vector,
            "model": self.model,
            "provider": self.provider.value,
            "dimensions": self.dimensions,
            "metadata": self.metadata,
        }


# =============================================================================
# Embedding Request
# =============================================================================


@dataclass
class EmbeddingRequest:
    """Request for generating embeddings."""

    texts: list[str]
    model: str | None = None
    provider: EmbeddingProvider | None = None
    normalize: bool = True
    batch_size: int = 1
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "texts": self.texts,
            "model": self.model,
            "provider": self.provider.value if self.provider else None,
            "normalize": self.normalize,
            "batch_size": self.batch_size,
            "metadata": self.metadata,
        }


# =============================================================================
# Embedding Response
# =============================================================================


@dataclass
class EmbeddingResponse:
    """Response from embedding generation."""

    embeddings: list[Embedding]
    model: str
    provider: EmbeddingProvider
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    success: bool = True
    error: str | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def count(self) -> int:
        """Get number of embeddings."""
        return len(self.embeddings)

    @property
    def dimensions(self) -> int:
        """Get embedding dimensions."""
        if self.embeddings:
            return self.embeddings[0].dimensions
        return 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "embeddings": [e.to_dict() for e in self.embeddings],
            "model": self.model,
            "provider": self.provider.value,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


# =============================================================================
# Embedding Model Info
# =============================================================================


@dataclass
class EmbeddingModelInfo:
    """Information about an embedding model."""

    name: str
    provider: EmbeddingProvider
    dimensions: int
    max_tokens: int
    cost_per_1k_tokens: float = 0.0
    supports_normalization: bool = True
    is_local: bool = False
    description: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "provider": self.provider.value,
            "dimensions": self.dimensions,
            "max_tokens": self.max_tokens,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "supports_normalization": self.supports_normalization,
            "is_local": self.is_local,
            "description": self.description,
        }


# =============================================================================
# Provider Health
# =============================================================================


@dataclass
class ProviderHealth:
    """Health status of a provider."""

    provider: EmbeddingProvider
    is_healthy: bool = True
    latency_ms: int = 0
    error_count: int = 0
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status_message: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "is_healthy": self.is_healthy,
            "latency_ms": self.latency_ms,
            "error_count": self.error_count,
            "last_check": self.last_check.isoformat(),
            "status_message": self.status_message,
        }


# =============================================================================
# Embedding Metrics
# =============================================================================


@dataclass
class EmbeddingMetrics:
    """Metrics for embedding operations."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    average_latency_ms: float = 0.0
    providers_used: dict[str, int] = field(default_factory=dict)
    models_used: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "average_latency_ms": self.average_latency_ms,
            "providers_used": self.providers_used,
            "models_used": self.models_used,
        }


# =============================================================================
# Embedding Trace
# =============================================================================


@dataclass
class EmbeddingTrace:
    """Trace for embedding operations."""

    trace_id: str
    request: EmbeddingRequest
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime | None = None
    provider_used: EmbeddingProvider | None = None
    model_used: str | None = None
    steps: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_step(self, step: dict) -> None:
        """Add a step to the trace."""
        self.steps.append(step)

    def add_error(self, error: str) -> None:
        """Add an error to the trace."""
        self.errors.append(error)

    def finish(
        self,
        provider: EmbeddingProvider | None = None,
        model: str | None = None,
    ) -> None:
        """Mark trace as finished."""
        self.end_time = datetime.now(timezone.utc)
        if provider:
            self.provider_used = provider
        if model:
            self.model_used = model

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "request": self.request.to_dict(),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "provider_used": self.provider_used.value if self.provider_used else None,
            "model_used": self.model_used,
            "steps": self.steps,
            "errors": self.errors,
        }
