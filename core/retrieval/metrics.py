"""Retrieval metrics for EREN Semantic Retrieval Engine."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from core.retrieval.types import RetrievalMetrics, MemorySource, RetrievalPolicy


class RetrievalMetricsCollector:
    """Collects and tracks retrieval metrics.

    Thread-safe metrics collection.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._lock = threading.RLock()
        self._metrics = RetrievalMetrics()
        self._latencies: list[int] = []
        self._max_latencies = 1000  # Keep last 1000 latencies

    def record_query(
        self,
        success: bool,
        latency_ms: int,
        num_results: int,
        source: MemorySource | None = None,
        policy: RetrievalPolicy | None = None,
    ) -> None:
        """Record a query.

        Args:
            success: Whether query succeeded.
            latency_ms: Query latency.
            num_results: Number of results.
            source: Memory source used.
            policy: Policy used.
        """
        with self._lock:
            self._metrics.total_queries += 1
            if success:
                self._metrics.successful_queries += 1
            else:
                self._metrics.failed_queries += 1

            self._metrics.total_results += num_results

            # Track latencies
            self._latencies.append(latency_ms)
            if len(self._latencies) > self._max_latencies:
                self._latencies = self._latencies[-self._max_latencies:]

            # Calculate average
            if self._latencies:
                self._metrics.average_latency_ms = sum(self._latencies) / len(self._latencies)

            # Track sources
            if source:
                source_key = source.value
                self._metrics.sources_used[source_key] = (
                    self._metrics.sources_used.get(source_key, 0) + 1
                )

            # Track policies
            if policy:
                policy_key = policy.value
                self._metrics.policies_used[policy_key] = (
                    self._metrics.policies_used.get(policy_key, 0) + 1
                )

            # Calculate cache hit rate (placeholder)
            # In real implementation, track cache hits
            self._metrics.cache_hit_rate = 0.0

    def get_metrics(self) -> RetrievalMetrics:
        """Get current metrics.

        Returns:
            Metrics snapshot.
        """
        with self._lock:
            return RetrievalMetrics(
                total_queries=self._metrics.total_queries,
                successful_queries=self._metrics.successful_queries,
                failed_queries=self._metrics.failed_queries,
                total_results=self._metrics.total_results,
                average_latency_ms=self._metrics.average_latency_ms,
                cache_hit_rate=self._metrics.cache_hit_rate,
                sources_used=dict(self._metrics.sources_used),
                policies_used=dict(self._metrics.policies_used),
            )

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics = RetrievalMetrics()
            self._latencies = []

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Metrics as dictionary.
        """
        return self.get_metrics().to_dict()


# Global metrics collector
_global_metrics: RetrievalMetricsCollector | None = None
_metrics_lock = threading.Lock()


def get_retrieval_metrics() -> RetrievalMetricsCollector:
    """Get the global metrics collector.

    Returns:
        Global RetrievalMetricsCollector instance.
    """
    global _global_metrics
    with _metrics_lock:
        if _global_metrics is None:
            _global_metrics = RetrievalMetricsCollector()
        return _global_metrics


def reset_retrieval_metrics() -> None:
    """Reset the global metrics collector."""
    global _global_metrics
    with _metrics_lock:
        if _global_metrics is not None:
            _global_metrics.reset()
        _global_metrics = None
