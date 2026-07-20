"""Embedding metrics for EREN Embedding Provider Layer."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from core.embeddings.types import EmbeddingMetrics

if TYPE_CHECKING:
    pass


class EmbeddingMetricsCollector:
    """Collects and tracks embedding metrics.

    Thread-safe metrics collection.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._lock = threading.RLock()
        self._metrics = EmbeddingMetrics()
        self._latencies: list[int] = []
        self._max_latencies = 1000

    def record_request(
        self,
        success: bool,
        latency_ms: int,
        tokens: int = 0,
        cost: float = 0.0,
        provider: str = "",
        model: str = "",
    ) -> None:
        """Record a request.

        Args:
            success: Whether request succeeded.
            latency_ms: Request latency.
            tokens: Tokens used.
            cost: Cost in USD.
            provider: Provider used.
            model: Model used.
        """
        with self._lock:
            self._metrics.total_requests += 1

            if success:
                self._metrics.successful_requests += 1
            else:
                self._metrics.failed_requests += 1

            self._metrics.total_tokens += tokens
            self._metrics.total_cost_usd += cost

            # Track latencies
            self._latencies.append(latency_ms)
            if len(self._latencies) > self._max_latencies:
                self._latencies = self._latencies[-self._max_latencies:]

            if self._latencies:
                self._metrics.average_latency_ms = sum(self._latencies) / len(self._latencies)

            # Track providers
            if provider:
                self._metrics.providers_used[provider] = (
                    self._metrics.providers_used.get(provider, 0) + 1
                )

            # Track models
            if model:
                self._metrics.models_used[model] = (
                    self._metrics.models_used.get(model, 0) + 1
                )

    def get_metrics(self) -> EmbeddingMetrics:
        """Get current metrics.

        Returns:
            Metrics snapshot.
        """
        with self._lock:
            return EmbeddingMetrics(
                total_requests=self._metrics.total_requests,
                successful_requests=self._metrics.successful_requests,
                failed_requests=self._metrics.failed_requests,
                total_tokens=self._metrics.total_tokens,
                total_cost_usd=self._metrics.total_cost_usd,
                average_latency_ms=self._metrics.average_latency_ms,
                providers_used=dict(self._metrics.providers_used),
                models_used=dict(self._metrics.models_used),
            )

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics = EmbeddingMetrics()
            self._latencies = []

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Metrics as dictionary.
        """
        return self.get_metrics().to_dict()


# Global metrics collector
_global_metrics: EmbeddingMetricsCollector | None = None
_metrics_lock = threading.Lock()


def get_embedding_metrics() -> EmbeddingMetricsCollector:
    """Get the global metrics collector.

    Returns:
        Global EmbeddingMetricsCollector instance.
    """
    global _global_metrics
    with _metrics_lock:
        if _global_metrics is None:
            _global_metrics = EmbeddingMetricsCollector()
        return _global_metrics


def reset_embedding_metrics() -> None:
    """Reset the global metrics collector."""
    global _global_metrics
    with _metrics_lock:
        if _global_metrics is not None:
            _global_metrics.reset()
        _global_metrics = None
