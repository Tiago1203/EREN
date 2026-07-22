"""Knowledge metrics collection.

Collects and calculates knowledge operation metrics.

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .knowledge_types import KnowledgeMetrics, QueryType

if TYPE_CHECKING:
    pass


class KnowledgeMetricsCollector:
    """Collects knowledge metrics."""

    def __init__(self) -> None:
        """Initialize the metrics collector."""
        self._queries_processed = 0
        self._queries_by_type: dict[str, int] = {}
        self._sources_queried = 0
        self._results_retrieved = 0
        self._latencies: list[float] = []
        self._cache_hits = 0
        self._cache_misses = 0
        self._errors = 0
        self._start_time: float | None = None

    def record_query(self, query_type: QueryType, results_count: int) -> None:
        """Record a processed query.

        Args:
            query_type: Type of query.
            results_count: Number of results.
        """
        self._queries_processed += 1
        self._queries_by_type[query_type.value] = (
            self._queries_by_type.get(query_type.value, 0) + 1
        )
        self._results_retrieved += results_count

    def record_sources_queried(self, count: int) -> None:
        """Record sources queried.

        Args:
            count: Number of sources.
        """
        self._sources_queried += count

    def record_latency(self, latency_ms: float) -> None:
        """Record query latency.

        Args:
            latency_ms: Latency in milliseconds.
        """
        self._latencies.append(latency_ms)

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self._cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self._cache_misses += 1

    def record_error(self) -> None:
        """Record an error."""
        self._errors += 1

    def calculate(self) -> KnowledgeMetrics:
        """Calculate final metrics.

        Returns:
            Knowledge metrics.
        """
        avg_latency = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0

        return KnowledgeMetrics(
            queries_processed=self._queries_processed,
            queries_by_type=self._queries_by_type.copy(),
            sources_queried=self._sources_queried,
            results_retrieved=self._results_retrieved,
            average_latency_ms=avg_latency,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            errors=self._errors,
        )


@dataclass
class KnowledgeHealthCheck:
    """Health check for knowledge engine."""

    is_healthy: bool = True
    active_sources: int = 0
    total_sources: int = 0
    queries_today: int = 0
    error_rate: float = 0.0
    warnings: tuple[str, ...] = field(default_factory=tuple)
    checked_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp."""
        object.__setattr__(self, 'checked_at', datetime.now(UTC).isoformat())
