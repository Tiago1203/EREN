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
"""

from __future__ import annotations

from core.embeddings.types import (
    EmbeddingProvider,
    EmbeddingPolicy,
    Embedding,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingModelInfo,
    ProviderHealth,
    EmbeddingMetrics,
    EmbeddingTrace,
)
from core.embeddings.exceptions import (
    EmbeddingError,
    ProviderNotFoundError,
    ModelNotFoundError,
    ProviderUnavailableError,
    GenerationError,
    ValidationError,
    ConfigurationError,
    HealthCheckError,
    RateLimitError,
    AuthenticationError,
    RegistryError,
    SelectionError,
)
from core.embeddings.provider import (
    BaseEmbeddingProvider,
    OpenAIEmbeddingProvider,
    OllamaEmbeddingProvider,
)
from core.embeddings.registry import (
    EmbeddingRegistry,
    get_embedding_registry,
    reset_embedding_registry,
)
from core.embeddings.selector import (
    EmbeddingSelector,
)
from core.embeddings.manager import (
    EmbeddingManager,
    get_embedding_manager,
    reset_embedding_manager,
)
from core.embeddings.configuration import (
    EmbeddingConfiguration,
    ProviderConfiguration,
)
from core.embeddings.metrics import (
    EmbeddingMetricsCollector,
    get_embedding_metrics,
    reset_embedding_metrics,
)
from core.embeddings.events import (
    EmbeddingEvent,
    EmbeddingEventBus,
    get_embedding_event_bus,
    reset_embedding_event_bus,
)
from core.embeddings.trace import (
    EmbeddingTracer,
    get_embedding_tracer,
    reset_embedding_tracer,
)

__all__ = [
    # Types
    "EmbeddingProvider",
    "EmbeddingPolicy",
    "Embedding",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "EmbeddingModelInfo",
    "ProviderHealth",
    "EmbeddingMetrics",
    "EmbeddingTrace",
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
]
