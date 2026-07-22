"""Type definitions for the Cognitive Knowledge Engine.

Provides comprehensive type definitions for knowledge operations.

Architecture only -- no AI, no business logic, no implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Knowledge Source Types
# =============================================================================


class KnowledgeSourceType(str, Enum):
    """Types of knowledge sources."""

    CLINICAL_DATABASE = "clinical_database"
    HOSPITAL_PROTOCOLS = "hospital_protocols"
    EQUIPMENT_MANUALS = "equipment_manuals"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    SCIENTIFIC_LITERATURE = "scientific_literature"
    REGULATORY_STANDARDS = "regulatory_standards"
    INTERNAL_MEMORY = "internal_memory"
    EXTERNAL_SERVICES = "external_services"
    KNOWLEDGE_BASE = "knowledge_base"
    PROCEDURES = "procedures"


class KnowledgeSourceCategory(str, Enum):
    """Categories of knowledge sources."""

    CLINICAL = "clinical"
    TECHNICAL = "technical"
    REGULATORY = "regulatory"
    SCIENTIFIC = "scientific"
    OPERATIONAL = "operational"
    HISTORICAL = "historical"


class KnowledgeSourceStatus(str, Enum):
    """Status of a knowledge source."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


# =============================================================================
# Query Types
# =============================================================================


class QueryType(str, Enum):
    """Types of knowledge queries."""

    CLINICAL_PROCEDURE = "clinical_procedure"
    DIAGNOSTIC = "diagnostic"
    TREATMENT = "treatment"
    TECHNICAL_SPECIFICATION = "technical_specification"
    TROUBLESHOOTING = "troubleshooting"
    MAINTENANCE = "maintenance"
    COMPLIANCE = "compliance"
    SAFETY = "safety"
    CERTIFICATION = "certification"
    GENERAL = "general"
    HISTORICAL = "historical"
    POLICY = "policy"
    PROCEDURE = "procedure"


class QueryPriority(str, Enum):
    """Priority of knowledge queries."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResultRelevance(str, Enum):
    """Relevance level of a knowledge result."""

    HIGHLY_RELEVANT = "highly_relevant"
    RELEVANT = "relevant"
    PARTIALLY_RELEVANT = "partially_relevant"
    NOT_RELEVANT = "not_relevant"


class ResultConfidence(str, Enum):
    """Confidence level of knowledge result."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


# =============================================================================
# Protocols (Contracts)
# =============================================================================


class KnowledgeSource(Protocol):
    """Protocol for knowledge source implementations."""

    source_id: str
    source_type: KnowledgeSourceType
    name: str

    async def query(self, query: KnowledgeQuery) -> list[KnowledgeResult]:
        """Query this source for knowledge."""
        ...

    async def health_check(self) -> bool:
        """Check if source is healthy."""
        ...

    def supports_query_type(self, query_type: QueryType) -> bool:
        """Check if source supports a query type."""
        ...


class RetrievalStrategy(Protocol):
    """Protocol for retrieval strategies."""

    async def retrieve(
        self,
        query: KnowledgeQuery,
        sources: list[KnowledgeSource],
    ) -> list[KnowledgeResult]:
        """Retrieve knowledge using specified strategy."""
        ...

    def rank_results(self, results: list[KnowledgeResult]) -> list[KnowledgeResult]:
        """Rank results by relevance."""
        ...


# =============================================================================
# Data Classes
# =============================================================================


@dataclass(frozen=True)
class KnowledgeFilters:
    """Filters for knowledge queries."""

    source_types: tuple[KnowledgeSourceType, ...] | None = None
    categories: tuple[KnowledgeSourceCategory, ...] | None = None
    date_from: str | None = None
    date_to: str | None = None
    language: str = "en"
    max_results: int = 10


@dataclass(frozen=True)
class KnowledgeQuery:
    """A knowledge query."""

    query_id: str
    query_text: str
    query_type: QueryType
    priority: QueryPriority = QueryPriority.MEDIUM
    context: dict = field(default_factory=dict)
    device_info: dict = field(default_factory=dict)
    clinical_context: dict = field(default_factory=dict)
    filters: KnowledgeFilters = field(default_factory=KnowledgeFilters)
    created_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class KnowledgeResult:
    """A knowledge retrieval result."""

    result_id: str
    source_id: str
    source_type: KnowledgeSourceType
    content: str | dict
    relevance: ResultRelevance
    confidence: ResultConfidence
    query_id: str
    title: str = ""
    summary: str = ""
    uri: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class KnowledgeEvidence:
    """Evidence supporting knowledge."""

    evidence_id: str
    content: str | dict
    source_type: KnowledgeSourceType
    source_id: str
    confidence: float = 0.5
    verified: bool = False
    expires_at: str | None = None
    metadata: dict = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class SourceCapability:
    """Capability of a knowledge source."""

    source_id: str
    supported_query_types: tuple[QueryType, ...]
    supported_categories: tuple[KnowledgeSourceCategory, ...]
    max_results: int = 10
    latency_ms: int = 1000


@dataclass(frozen=True)
class SourceMetadata:
    """Metadata for a knowledge source."""

    source_id: str
    source_type: KnowledgeSourceType
    name: str
    description: str
    category: KnowledgeSourceCategory
    status: KnowledgeSourceStatus
    version: str = "1.0.0"
    last_updated: str = ""
    capabilities: tuple[SourceCapability, ...] = field(default_factory=tuple)
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeRoute:
    """A route for knowledge retrieval."""

    route_id: str
    query_type: QueryType
    source_types: tuple[KnowledgeSourceType, ...]
    priority: tuple[int, ...]
    strategy_id: str = "default"
    created_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(UTC).isoformat())


@dataclass
class KnowledgeMetrics:
    """Metrics for knowledge operations."""

    queries_processed: int = 0
    queries_by_type: dict[str, int] = field(default_factory=dict)
    sources_queried: int = 0
    results_retrieved: int = 0
    average_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0


@dataclass(frozen=True)
class KnowledgeSession:
    """A knowledge retrieval session."""

    session_id: str
    query: KnowledgeQuery
    results: tuple[KnowledgeResult, ...] = field(default_factory=tuple)
    sources_consulted: tuple[str, ...] = field(default_factory=tuple)
    routing_decision: dict = field(default_factory=dict)
    status: str = "pending"
    created_at: str = ""
    completed_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(UTC).isoformat())


# =============================================================================
# Source Query Mapping
# =============================================================================


SOURCE_QUERY_MAPPING: dict[KnowledgeSourceType, tuple[QueryType, ...]] = {
    KnowledgeSourceType.CLINICAL_DATABASE: (
        QueryType.CLINICAL_PROCEDURE,
        QueryType.DIAGNOSTIC,
        QueryType.TREATMENT,
    ),
    KnowledgeSourceType.EQUIPMENT_MANUALS: (
        QueryType.TECHNICAL_SPECIFICATION,
        QueryType.TROUBLESHOOTING,
        QueryType.MAINTENANCE,
    ),
    KnowledgeSourceType.HOSPITAL_PROTOCOLS: (
        QueryType.COMPLIANCE,
        QueryType.POLICY,
        QueryType.PROCEDURE,
    ),
    KnowledgeSourceType.TECHNICAL_DOCUMENTATION: (
        QueryType.TECHNICAL_SPECIFICATION,
        QueryType.MAINTENANCE,
    ),
    KnowledgeSourceType.SCIENTIFIC_LITERATURE: (
        QueryType.DIAGNOSTIC,
        QueryType.TREATMENT,
        QueryType.SAFETY,
    ),
    KnowledgeSourceType.REGULATORY_STANDARDS: (
        QueryType.COMPLIANCE,
        QueryType.CERTIFICATION,
        QueryType.SAFETY,
    ),
    KnowledgeSourceType.INTERNAL_MEMORY: (
        QueryType.HISTORICAL,
        QueryType.GENERAL,
    ),
    KnowledgeSourceType.EXTERNAL_SERVICES: (
        QueryType.GENERAL,
        QueryType.DIAGNOSTIC,
    ),
    KnowledgeSourceType.KNOWLEDGE_BASE: (
        QueryType.GENERAL,
        QueryType.TROUBLESHOOTING,
    ),
    KnowledgeSourceType.PROCEDURES: (
        QueryType.CLINICAL_PROCEDURE,
        QueryType.MAINTENANCE,
        QueryType.PROCEDURE,
    ),
}
