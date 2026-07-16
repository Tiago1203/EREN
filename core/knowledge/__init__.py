"""Cognitive Knowledge Engine (CKE).

The knowledge component of EREN. Manages knowledge retrieval
and storage through a unified interface.

EREN NO uses AI. EREN NO generates embeddings. EREN NO does real search.
EREN only organizes knowledge infrastructure.

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

from core.knowledge.exceptions import (
    KnowledgeError,
    KnowledgeNotFoundError,
    NoSourcesAvailableError,
    QueryFailedError,
    RoutingError,
    SourceNotAvailableError,
    SourceNotFoundError,
    SourceRegistrationError,
    TimeoutError,
    ValidationError,
)
from core.knowledge.knowledge_engine import (
    CognitiveKnowledgeEngine,
    KnowledgeCapabilityRegistrar,
    KnowledgeEventPublisher,
    KnowledgeSessionData,
)
from core.knowledge.knowledge_metrics import KnowledgeHealthCheck, KnowledgeMetricsCollector
from core.knowledge.knowledge_registry import KnowledgeRegistry
from core.knowledge.knowledge_router import (
    ExhaustiveRouting,
    KnowledgeRouter,
    MinimumRouting,
    PriorityRouting,
    RoutingDecision,
    RoutingStrategy,
)
from core.knowledge.knowledge_types import (
    SOURCE_QUERY_MAPPING,
    KnowledgeEvidence,
    KnowledgeFilters,
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeRoute,
    KnowledgeSession,
    KnowledgeSource,
    KnowledgeSourceCategory,
    KnowledgeSourceStatus,
    KnowledgeSourceType,
    QueryPriority,
    QueryType,
    ResultConfidence,
    ResultRelevance,
    RetrievalStrategy,
    SourceCapability,
    SourceMetadata,
)

# Knowledge Article Domain (Sprint 6)
from core.knowledge.domain import (
    ArticleContent,
    KnowledgeArticle,
    KnowledgeCategory,
    KnowledgeReference,
    KnowledgeRepository,
    KnowledgeService,
    KnowledgeStatus,
    ReviewInfo,
    UsageStatistics,
)

__all__ = [
    # Core Engine
    "CognitiveKnowledgeEngine",
    "KnowledgeCapabilityRegistrar",
    "KnowledgeEventPublisher",
    "KnowledgeSessionData",
    # Registry
    "KnowledgeRegistry",
    # Router
    "KnowledgeRouter",
    "RoutingStrategy",
    "RoutingDecision",
    "ExhaustiveRouting",
    "PriorityRouting",
    "MinimumRouting",
    # Types
    "KnowledgeQuery",
    "KnowledgeResult",
    "KnowledgeEvidence",
    "KnowledgeSession",
    "KnowledgeRoute",
    "KnowledgeSource",
    "KnowledgeFilters",
    # Enums
    "KnowledgeSourceType",
    "KnowledgeSourceCategory",
    "KnowledgeSourceStatus",
    "QueryType",
    "QueryPriority",
    "ResultRelevance",
    "ResultConfidence",
    # Metadata
    "SourceCapability",
    "SourceMetadata",
    # Metrics
    "KnowledgeMetricsCollector",
    "KnowledgeHealthCheck",
    # Constants
    "RetrievalStrategy",
    "SOURCE_QUERY_MAPPING",
    # Exceptions
    "KnowledgeError",
    "SourceNotFoundError",
    "SourceNotAvailableError",
    "QueryFailedError",
    "SourceRegistrationError",
    "NoSourcesAvailableError",
    "RoutingError",
    "KnowledgeNotFoundError",
    "ValidationError",
    "TimeoutError",
    # Knowledge Article Domain (Sprint 6)
    "KnowledgeArticle",
    "KnowledgeStatus",
    "KnowledgeCategory",
    "ArticleContent",
    "KnowledgeReference",
    "ReviewInfo",
    "UsageStatistics",
    "KnowledgeService",
    "KnowledgeRepository",
]
