"""Retrieval types for EREN Semantic Retrieval Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Retrieval Policies
# =============================================================================


class RetrievalPolicy(str, Enum):
    """Retrieval policies for different use cases."""

    FASTEST = "fastest"
    BEST_MATCH = "best_match"
    MERGE_ALL = "merge_all"
    VECTOR_FIRST = "vector_first"
    SEMANTIC_FIRST = "semantic_first"
    HYBRID = "hybrid"
    CLINICAL_PRIORITY = "clinical_priority"
    DEVICE_PRIORITY = "device_priority"


# =============================================================================
# Memory Sources
# =============================================================================


class MemorySource(str, Enum):
    """Available memory sources for retrieval."""

    CONVERSATION = "conversation"
    SEMANTIC = "semantic"
    CLINICAL = "clinical"
    DEVICE = "device"
    VECTOR = "vector"
    WORKING = "working"
    LONG_TERM = "long_term"


# =============================================================================
# Retrieval Query
# =============================================================================


@dataclass
class RetrievalQuery:
    """Query for retrieval operations."""

    query: str
    sources: list[MemorySource] | None = None
    policy: RetrievalPolicy = RetrievalPolicy.BEST_MATCH
    max_results: int = 10
    max_context_tokens: int = 4000
    min_relevance_score: float = 0.0
    filters: dict = field(default_factory=dict)
    user_id: str | None = None
    session_id: str | None = None
    conversation_id: str | None = None
    include_metadata: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "sources": [s.value for s in self.sources] if self.sources else None,
            "policy": self.policy.value,
            "max_results": self.max_results,
            "max_context_tokens": self.max_context_tokens,
            "min_relevance_score": self.min_relevance_score,
            "filters": self.filters,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "include_metadata": self.include_metadata,
        }


# =============================================================================
# Retrieval Result
# =============================================================================


@dataclass
class RetrievalResult:
    """Result from a retrieval operation."""

    content: str
    source: MemorySource
    memory_id: str
    relevance_score: float = 0.0
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    cached: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "source": self.source.value,
            "memory_id": self.memory_id,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "cached": self.cached,
        }


# =============================================================================
# Retrieval Response
# =============================================================================


@dataclass
class RetrievalResponse:
    """Response from retrieval engine."""

    results: list[RetrievalResult] = field(default_factory=list)
    query: str = ""
    policy_used: RetrievalPolicy = RetrievalPolicy.BEST_MATCH
    total_results: int = 0
    execution_time_ms: int = 0
    success: bool = True
    error: str | None = None
    sources_queried: list[MemorySource] = field(default_factory=list)

    @property
    def content(self) -> str:
        """Get combined content."""
        return "\n\n".join(r.content for r in self.results)

    @property
    def is_empty(self) -> bool:
        """Check if response is empty."""
        return len(self.results) == 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "results": [r.to_dict() for r in self.results],
            "query": self.query,
            "policy_used": self.policy_used.value,
            "total_results": self.total_results,
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "error": self.error,
            "sources_queried": [s.value for s in self.sources_queried],
        }


# =============================================================================
# Retrieval Plan
# =============================================================================


@dataclass
class RetrievalPlan:
    """Plan for retrieval execution."""

    query: RetrievalQuery
    steps: list[RetrievalStep] = field(default_factory=list)
    estimated_time_ms: int = 0
    estimated_results: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query.to_dict(),
            "steps": [s.to_dict() for s in self.steps],
            "estimated_time_ms": self.estimated_time_ms,
            "estimated_results": self.estimated_results,
        }


@dataclass
class RetrievalStep:
    """Single step in retrieval plan."""

    step_id: str
    action: str
    source: MemorySource
    priority: int = 0
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "action": self.action,
            "source": self.source.value,
            "priority": self.priority,
            "dependencies": self.dependencies,
        }


# =============================================================================
# Retrieval Metrics
# =============================================================================


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval operations."""

    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_results: int = 0
    average_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    sources_used: dict[str, int] = field(default_factory=dict)
    policies_used: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_queries": self.total_queries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "total_results": self.total_results,
            "average_latency_ms": self.average_latency_ms,
            "cache_hit_rate": self.cache_hit_rate,
            "sources_used": self.sources_used,
            "policies_used": self.policies_used,
        }


# =============================================================================
# Retrieval Trace
# =============================================================================


@dataclass
class RetrievalTrace:
    """Trace for retrieval operations."""

    trace_id: str
    query: str
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None
    steps: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_step(self, step: dict) -> None:
        """Add a step to the trace."""
        self.steps.append(step)

    def add_error(self, error: str) -> None:
        """Add an error to the trace."""
        self.errors.append(error)

    def finish(self) -> None:
        """Mark trace as finished."""
        self.end_time = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "steps": self.steps,
            "errors": self.errors,
        }
