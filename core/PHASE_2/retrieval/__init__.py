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

from core.PHASE_2.retrieval.context_builder import (
    CompactContextBuilder,
    ContextBuilder,
    ContextBuilderFactory,
    StructuredContextBuilder,
)
from core.PHASE_2.retrieval.engine import (
    SemanticRetrievalEngine,
    get_retrieval_engine,
    reset_retrieval_engine,
)
from core.PHASE_2.retrieval.events import (
    RetrievalEvent,
    RetrievalEventBus,
    get_retrieval_event_bus,
    reset_retrieval_event_bus,
)
from core.PHASE_2.retrieval.exceptions import (
    ContextOverflowError,
    MemorySourceUnavailableError,
    NoResultsError,
    PolicyNotSupportedError,
    RankingError,
    RegistryError,
    RetrievalError,
    RetrievalExecutionError,
    RetrievalPlanError,
)
from core.PHASE_2.retrieval.metrics import (
    RetrievalMetricsCollector,
    get_retrieval_metrics,
    reset_retrieval_metrics,
)
from core.PHASE_2.retrieval.planner import RetrievalPlanner
from core.PHASE_2.retrieval.policies import RetrievalPolicyHandler
from core.PHASE_2.retrieval.ranker import (
    ContextualRanker,
    RankerFactory,
    ResultRanker,
)
from core.PHASE_2.retrieval.registry import (
    RetrievalRegistry,
    get_retrieval_registry,
    reset_retrieval_registry,
)
from core.PHASE_2.retrieval.strategy import (
    FastestStrategy,
    MergeAllStrategy,
    ParallelStrategy,
    RetrievalStrategy,
    RetrievalStrategyFactory,
    SequentialStrategy,
)
from core.PHASE_2.retrieval.trace import (
    RetrievalTracer,
    get_retrieval_tracer,
    reset_retrieval_tracer,
)
from core.PHASE_2.retrieval.types import (
    MemorySource,
    RetrievalMetrics,
    RetrievalPlan,
    RetrievalPolicy,
    RetrievalQuery,
    RetrievalResponse,
    RetrievalResult,
    RetrievalStep,
    RetrievalTrace,
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
