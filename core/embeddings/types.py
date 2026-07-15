"""Embedding types for EREN Embedding Provider Layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
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
    # New providers for PR-057
    BGE = "bge"  # BAAI/bge models
    E5 = "e5"  # Microsoft E5 models
    NOMIC = "nomic"  # Nomic Embeddings
    JINA = "jina"  # Jina AI
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    COHERE = "cohere"
    CUSTOM = "custom"
    MOCK = "mock"  # For testing


class EmbeddingProviderType(str, Enum):
    """Types of embedding providers."""

    CLOUD = "cloud"  # API-based
    LOCAL = "local"  # Self-hosted
    HYBRID = "hybrid"  # Both options


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
    QUALITY_FIRST = "quality_first"
    BALANCED = "balanced"


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
    version: str = "1.0"
    normalized: bool = True
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
            "version": self.version,
            "normalized": self.normalized,
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
    last_check: datetime = field(default_factory=lambda: datetime.now(UTC))
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
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
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
        self.end_time = datetime.now(UTC)
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


# =============================================================================
# Embedding Versioning
# =============================================================================


@dataclass
class EmbeddingVersion:
    """Version information for an embedding model."""

    model: str
    version: str
    provider: EmbeddingProvider
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    dimensions: int = 0
    description: str = ""
    changelog: str = ""
    deprecated: bool = False
    replacement_model: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "version": self.version,
            "provider": self.provider.value,
            "created_at": self.created_at.isoformat(),
            "dimensions": self.dimensions,
            "description": self.description,
            "changelog": self.changelog,
            "deprecated": self.deprecated,
            "replacement_model": self.replacement_model,
        }


# =============================================================================
# Batch Processing
# =============================================================================


@dataclass
class BatchConfig:
    """Configuration for batch processing."""

    batch_size: int = 32
    max_batch_size: int = 100
    parallel_batches: int = 4
    retry_on_failure: bool = True
    max_retries: int = 3
    retry_delay_seconds: float = 1.0


@dataclass
class BatchResult:
    """Result of batch processing."""

    batch_id: str
    total_items: int
    successful_items: int
    failed_items: int
    total_tokens: int = 0
    total_cost: float = 0.0
    duration_ms: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "total_items": self.total_items,
            "successful_items": self.successful_items,
            "failed_items": self.failed_items,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "duration_ms": self.duration_ms,
            "errors": self.errors,
            "metadata": self.metadata,
        }


# =============================================================================
# Deduplication
# =============================================================================


@dataclass
class DeduplicationConfig:
    """Configuration for embedding deduplication."""

    enabled: bool = True
    similarity_threshold: float = 0.99  # Cosine similarity
    hash_based: bool = True  # Use hash for fast comparison
    min_text_length: int = 10  # Minimum text to consider


@dataclass
class DeduplicationResult:
    """Result of deduplication."""

    original_count: int
    unique_count: int
    duplicates_removed: int
    duplicate_indices: list[tuple[int, int]] = field(default_factory=list)  # (original, duplicate)

    @property
    def deduplication_rate(self) -> float:
        """Calculate deduplication rate."""
        if self.original_count == 0:
            return 0.0
        return (self.duplicates_removed / self.original_count) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "original_count": self.original_count,
            "unique_count": self.unique_count,
            "duplicates_removed": self.duplicates_removed,
            "duplicate_indices": self.duplicate_indices,
            "deduplication_rate": self.deduplication_rate,
        }


# =============================================================================
# Normalization
# =============================================================================


class NormalizationMethod(str, Enum):
    """Methods for vector normalization."""

    L2 = "l2"  # Euclidean
    L1 = "l1"  # Manhattan
    MAX = "max"  # Max normalization
    NONE = "none"


# =============================================================================
# Embedding Cache Entry
# =============================================================================


@dataclass
class EmbeddingCacheEntry:
    """Cache entry for embeddings."""

    text_hash: str
    embedding: Embedding
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        """Update last accessed time."""
        self.access_count += 1
        self.last_accessed = datetime.now(UTC)

    def is_expired(self, ttl_seconds: float) -> bool:
        """Check if entry is expired."""
        if ttl_seconds <= 0:
            return False
        age = (datetime.now(UTC) - self.created_at).total_seconds()
        return age >= ttl_seconds

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "text_hash": self.text_hash,
            "embedding": self.embedding.to_dict(),
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
        }


# =============================================================================
# Embedding Health
# =============================================================================


@dataclass
class EmbeddingHealthStatus:
    """Health status for embedding providers."""

    provider: EmbeddingProvider
    is_healthy: bool = True
    latency_ms: int = 0
    error_count: int = 0
    consecutive_failures: int = 0
    last_success: datetime | None = None
    last_failure: datetime | None = None
    circuit_breaker_state: str = "closed"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider": self.provider.value,
            "is_healthy": self.is_healthy,
            "latency_ms": self.latency_ms,
            "error_count": self.error_count,
            "consecutive_failures": self.consecutive_failures,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "circuit_breaker_state": self.circuit_breaker_state,
        }
