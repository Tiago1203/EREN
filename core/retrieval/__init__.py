"""EREN Semantic Retrieval Engine (SRE).

The engine responsible for retrieving relevant knowledge from multiple memory systems.
This is the beginning of EREN's RAG system.

Philosophy:
    The Retrieval Engine never knows:
    - PostgreSQL
    - SQLite
    - Chroma
    - Qdrant
    - Pinecone
    - FAISS
    - Milvus
    - Redis

    It only knows contracts.

Responsibilities:
    - Plan searches
    - Select relevant memories
    - Execute parallel searches
    - Combine results
    - Remove duplicates
    - Rank results
    - Build context for LLM
"""

from __future__ import annotations

from core.retrieval.types import (
    RetrievalPolicy,
    MemorySource,
    RetrievalQuery,
    RetrievalResult,
    RetrievalResponse,
    RetrievalPlan,
    RetrievalStep,
    RetrievalMetrics,
    RetrievalTrace,
)
from core.retrieval.exceptions import (
    RetrievalError,
    RetrievalPlanError,
    RetrievalExecutionError,
    NoResultsError,
    MemorySourceUnavailableError,
    PolicyNotSupportedError,
    ContextOverflowError,
    RankingError,
    RegistryError,
)
from core.retrieval.registry import (
    RetrievalRegistry,
    get_retrieval_registry,
    reset_retrieval_registry,
)
from core.retrieval.planner import RetrievalPlanner
from core.retrieval.strategy import (
    RetrievalStrategy,
    SequentialStrategy,
    ParallelStrategy,
    FastestStrategy,
    MergeAllStrategy,
    RetrievalStrategyFactory,
)
from core.retrieval.ranker import (
    ResultRanker,
    ContextualRanker,
    RankerFactory,
)
from core.retrieval.context_builder import (
    ContextBuilder,
    StructuredContextBuilder,
    CompactContextBuilder,
    ContextBuilderFactory,
)
from core.retrieval.policies import RetrievalPolicyHandler
from core.retrieval.metrics import (
    RetrievalMetricsCollector,
    get_retrieval_metrics,
    reset_retrieval_metrics,
)
from core.retrieval.events import (
    RetrievalEvent,
    RetrievalEventBus,
    get_retrieval_event_bus,
    reset_retrieval_event_bus,
)
from core.retrieval.trace import (
    RetrievalTracer,
    get_retrieval_tracer,
    reset_retrieval_tracer,
)
from core.retrieval.engine import (
    SemanticRetrievalEngine,
    get_retrieval_engine,
    reset_retrieval_engine,
)

__all__ = [
    # Engine
    "SemanticRetrievalEngine",
    "get_retrieval_engine",
    "reset_retrieval_engine",
    # Types
    "RetrievalPolicy",
    "MemorySource",
    "RetrievalQuery",
    "RetrievalResult",
    "RetrievalResponse",
    "RetrievalPlan",
    "RetrievalStep",
    "RetrievalMetrics",
    "RetrievalTrace",
    # Exceptions
    "RetrievalError",
    "RetrievalPlanError",
    "RetrievalExecutionError",
    "NoResultsError",
    "MemorySourceUnavailableError",
    "PolicyNotSupportedError",
    "ContextOverflowError",
    "RankingError",
    "RegistryError",
    # Registry
    "RetrievalRegistry",
    "get_retrieval_registry",
    "reset_retrieval_registry",
    # Planner
    "RetrievalPlanner",
    # Strategy
    "RetrievalStrategy",
    "SequentialStrategy",
    "ParallelStrategy",
    "FastestStrategy",
    "MergeAllStrategy",
    "RetrievalStrategyFactory",
    # Ranker
    "ResultRanker",
    "ContextualRanker",
    "RankerFactory",
    # Context Builder
    "ContextBuilder",
    "StructuredContextBuilder",
    "CompactContextBuilder",
    "ContextBuilderFactory",
    # Policies
    "RetrievalPolicyHandler",
    # Metrics
    "RetrievalMetricsCollector",
    "get_retrieval_metrics",
    "reset_retrieval_metrics",
    # Events
    "RetrievalEvent",
    "RetrievalEventBus",
    "get_retrieval_event_bus",
    "reset_retrieval_event_bus",
    # Trace
    "RetrievalTracer",
    "get_retrieval_tracer",
    "reset_retrieval_tracer",
]
