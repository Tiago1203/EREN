"""EREN Embedding Provider Layer (EPL).

The official abstraction layer for embedding generation in EREN.

Philosophy:
    The Kernel Cognitivo never knows a specific provider.
    All embedding generation occurs through common contracts.

Capabilities:
    - Generate embedding
    - Generate batch embeddings
    - Query dimensions
    - Query model
    - Health check
    - Cost estimation
    - Streaming (if applicable)
    - Intelligent selection
    - Caching and deduplication
"""

from __future__ import annotations

from core.PHASE_2.embeddings.batch import (
    BatchConfig,
    BatchProcessor,
    BatchResult,
    EmbeddingCache,
    EmbeddingDeduplicator,
    compute_text_hash,
    normalize_vector,
    cosine_similarity,
)
from core.PHASE_2.embeddings.configuration import (
    EmbeddingConfiguration,
    ProviderConfiguration,
)
from core.PHASE_2.embeddings.events import (
    EmbeddingEvent,
    EmbeddingEventBus,
    get_embedding_event_bus,
    reset_embedding_event_bus,
)
from core.PHASE_2.embeddings.exceptions import (
    AuthenticationError,
    ConfigurationError,
    EmbeddingError,
    GenerationError,
    HealthCheckError,
    ModelNotFoundError,
    ProviderNotFoundError,
    ProviderUnavailableError,
    RateLimitError,
    RegistryError,
    SelectionError,
    ValidationError,
)
from core.PHASE_2.embeddings.manager import (
    EmbeddingManager,
    get_embedding_manager,
    reset_embedding_manager,
)
from core.PHASE_2.embeddings.metrics import (
    EmbeddingMetricsCollector,
    get_embedding_metrics,
    reset_embedding_metrics,
)
from core.PHASE_2.embeddings.provider import (
    BaseEmbeddingProvider,
    OllamaEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from core.PHASE_2.embeddings.registry import (
    EmbeddingRegistry,
    get_embedding_registry,
    reset_embedding_registry,
)
from core.PHASE_2.embeddings.selector import (
    EmbeddingSelector,
)
from core.PHASE_2.embeddings.trace import (
    EmbeddingTracer,
    get_embedding_tracer,
    reset_embedding_tracer,
)
from core.PHASE_2.embeddings.types import (
    BatchConfig,
    BatchResult,
    DeduplicationConfig,
    DeduplicationResult,
    Embedding,
    EmbeddingCacheEntry,
    EmbeddingHealthStatus,
    EmbeddingMetrics,
    EmbeddingModelInfo,
    EmbeddingPolicy,
    EmbeddingProvider,
    EmbeddingProviderType,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingTrace,
    EmbeddingVersion,
    NormalizationMethod,
    ProviderHealth,
)

__all__ = [
    # Types
    "EmbeddingProvider",
    "EmbeddingProviderType",
    "EmbeddingPolicy",
    "Embedding",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "EmbeddingModelInfo",
    "ProviderHealth",
    "EmbeddingMetrics",
    "EmbeddingTrace",
    "EmbeddingVersion",
    "BatchConfig",
    "BatchResult",
    "DeduplicationConfig",
    "DeduplicationResult",
    "NormalizationMethod",
    "EmbeddingCacheEntry",
    "EmbeddingHealthStatus",
    # Exceptions
    "EmbeddingError",
    "ProviderNotFoundError",
    "ModelNotFoundError",
    "ProviderUnavailableError",
    "GenerationError",
    "ValidationError",
    "ConfigurationError",
    "HealthCheckError",
    "RateLimitError",
    "AuthenticationError",
    "RegistryError",
    "SelectionError",
    # Provider
    "BaseEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "OllamaEmbeddingProvider",
    # Registry
    "EmbeddingRegistry",
    "get_embedding_registry",
    "reset_embedding_registry",
    # Selector
    "EmbeddingSelector",
    # Manager
    "EmbeddingManager",
    "get_embedding_manager",
    "reset_embedding_manager",
    # Configuration
    "EmbeddingConfiguration",
    "ProviderConfiguration",
    # Metrics
    "EmbeddingMetricsCollector",
    "get_embedding_metrics",
    "reset_embedding_metrics",
    # Events
    "EmbeddingEvent",
    "EmbeddingEventBus",
    "get_embedding_event_bus",
    "reset_embedding_event_bus",
    # Trace
    "EmbeddingTracer",
    "get_embedding_tracer",
    "reset_embedding_tracer",
    # Batch Processing
    "BatchProcessor",
    "EmbeddingCache",
    "EmbeddingDeduplicator",
    "compute_text_hash",
    "normalize_vector",
    "cosine_similarity",
]
