"""Scoring Engine for EREN OS Multi-Provider Layer.

Scores and ranks providers based on multiple criteria.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.PHASE_2.providers.health_monitor import HealthMetrics
    from core.PHASE_2.providers.provider import BaseProvider
    from core.PHASE_2.providers.types import ProviderCapabilities, SelectionCriteria


@dataclass
class ProviderScore:
    """Score for a provider."""

    provider_id: str
    total_score: float
    breakdown: dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "total_score": self.total_score,
            "breakdown": self.breakdown,
            "timestamp": self.timestamp.isoformat(),
            "reasons": self.reasons,
        }


@dataclass
class ScoringWeights:
    """Weights for scoring components."""

    latency: float = 0.25  # Lower latency = higher score
    reliability: float = 0.25  # Success rate
    cost: float = 0.15  # Lower cost = higher score
    capabilities: float = 0.20  # Capability match
    availability: float = 0.15  # Current availability

    # Optional weights
    privacy: float = 0.0  # Privacy compliance bonus
    regional: float = 0.0  # Regional proximity bonus


class ScoringEngine:
    """Scores and ranks providers based on multiple criteria.

    Scoring factors:
    - Latency (weighted inverse)
    - Reliability/success rate
    - Cost efficiency
    - Capability match
    - Current availability/health
    - Privacy compliance
    - Regional proximity
    """

    def __init__(self, weights: ScoringWeights | None = None):
        """Initialize scoring engine.

        Args:
            weights: Scoring weights.
        """
        self._weights = weights or ScoringWeights()
        self._lock = threading.Lock()

        # Score cache
        self._cache: dict[str, ProviderScore] = {}
        self._cache_ttl_seconds = 30

    @property
    def weights(self) -> ScoringWeights:
        """Get scoring weights."""
        return self._weights

    @weights.setter
    def weights(self, value: ScoringWeights) -> None:
        """Set scoring weights."""
        with self._lock:
            self._weights = value
            self._cache.clear()

    def score(
        self,
        provider: BaseProvider,
        criteria: SelectionCriteria,
        health_metrics: HealthMetrics | None = None,
    ) -> ProviderScore:
        """Score a provider based on criteria.

        Args:
            provider: Provider to score.
            criteria: Selection criteria.
            health_metrics: Optional health metrics.

        Returns:
            Provider score with breakdown.
        """
        with self._lock:
            breakdown: dict[str, float] = {}
            reasons: list[str] = []

            # Latency score (inverse - lower is better)
            latency_score = self._score_latency(health_metrics)
            breakdown["latency"] = latency_score * self._weights.latency

            # Reliability score
            reliability_score = self._score_reliability(health_metrics)
            breakdown["reliability"] = reliability_score * self._weights.reliability

            # Cost score (inverse - lower is better)
            cost_score = self._score_cost(provider)
            breakdown["cost"] = cost_score * self._weights.cost

            # Capability score
            capability_score = self._score_capabilities(provider, criteria)
            breakdown["capabilities"] = capability_score * self._weights.capabilities

            # Availability score
            availability_score = self._score_availability(health_metrics, provider)
            breakdown["availability"] = availability_score * self._weights.availability

            # Privacy score
            if self._weights.privacy > 0:
                privacy_score = self._score_privacy(provider, criteria)
                breakdown["privacy"] = privacy_score * self._weights.privacy

            # Regional score
            if self._weights.regional > 0:
                regional_score = self._score_regional(provider, criteria)
                breakdown["regional"] = regional_score * self._weights.regional

            # Calculate total
            total = sum(breakdown.values())

            # Add reasons
            if latency_score > 0.8:
                reasons.append("Excellent latency")
            elif latency_score < 0.3:
                reasons.append("High latency")

            if reliability_score > 0.9:
                reasons.append("High reliability")
            elif reliability_score < 0.5:
                reasons.append("Low reliability")

            if capability_score == 1.0:
                reasons.append("Full capability match")
            elif capability_score < 0.5:
                reasons.append("Limited capabilities")

            return ProviderScore(
                provider_id=provider.provider_id,
                total_score=total,
                breakdown=breakdown,
                reasons=reasons,
            )

    def _score_latency(self, health_metrics: HealthMetrics | None) -> float:
        """Score based on latency.

        Args:
            health_metrics: Health metrics with latency info.

        Returns:
            Score between 0 and 1.
        """
        if not health_metrics or health_metrics.total_checks == 0:
            return 0.5  # Neutral

        avg_latency = health_metrics.average_latency_ms

        # Score curve: 0ms = 1.0, 1000ms = 0.5, 5000ms+ = 0.0
        if avg_latency <= 0:
            return 1.0
        elif avg_latency >= 5000:
            return 0.0
        else:
            return 1.0 - (avg_latency / 5000) * 0.5

    def _score_reliability(self, health_metrics: HealthMetrics | None) -> float:
        """Score based on reliability.

        Args:
            health_metrics: Health metrics with reliability info.

        Returns:
            Score between 0 and 1.
        """
        if not health_metrics:
            return 0.5  # Neutral

        success_rate = health_metrics.success_rate

        if success_rate >= 99:
            return 1.0
        elif success_rate >= 95:
            return 0.9
        elif success_rate >= 90:
            return 0.8
        elif success_rate >= 80:
            return 0.6
        elif success_rate >= 70:
            return 0.4
        elif success_rate >= 50:
            return 0.2
        else:
            return 0.0

    def _score_cost(self, provider: BaseProvider) -> float:
        """Score based on cost.

        Args:
            provider: Provider to score.

        Returns:
            Score between 0 and 1.
        """
        # Get cost info from config or metadata
        config = provider.config
        if not config:
            return 0.5  # Neutral

        # Assume pricing tier from metadata
        pricing_tier = config.metadata.get("pricing_tier", "standard")

        if pricing_tier == "budget":
            return 1.0
        elif pricing_tier == "standard":
            return 0.7
        elif pricing_tier == "premium":
            return 0.4
        else:
            return 0.5

    def _score_capabilities(
        self,
        provider: BaseProvider,
        criteria: SelectionCriteria,
    ) -> float:
        """Score based on capability match.

        Args:
            provider: Provider to score.
            criteria: Selection criteria.

        Returns:
            Score between 0 and 1.
        """
        if not criteria.required_capabilities:
            return 0.7  # No specific requirements

        matched = 0
        total = len(criteria.required_capabilities)

        for cap in criteria.required_capabilities:
            if cap == "streaming" and provider.supports_streaming():
                matched += 1
            elif cap == "embeddings" and provider.supports_embeddings():
                matched += 1
            elif cap == "vision" and provider.supports_streaming():  # Vision via streaming
                matched += 1

        if total == 0:
            return 0.7

        return matched / total

    def _score_availability(
        self,
        health_metrics: HealthMetrics | None,
        provider: BaseProvider,
    ) -> float:
        """Score based on current availability.

        Args:
            health_metrics: Health metrics.
            provider: Provider to score.

        Returns:
            Score between 0 and 1.
        """
        from core.PHASE_2.providers.types import ProviderState

        if not health_metrics:
            # Check provider state
            state = provider.state
            if state == ProviderState.HEALTHY:
                return 0.8
            elif state == ProviderState.DEGRADED:
                return 0.5
            else:
                return 0.2

        # Score based on consecutive successes
        consecutive = health_metrics.consecutive_successes
        if consecutive >= 10:
            return 1.0
        elif consecutive >= 5:
            return 0.8
        elif consecutive >= 2:
            return 0.6
        elif consecutive >= 1:
            return 0.4
        else:
            return 0.2

    def _score_privacy(
        self,
        provider: BaseProvider,
        criteria: SelectionCriteria,
    ) -> float:
        """Score based on privacy compliance.

        Args:
            provider: Provider to score.
            criteria: Selection criteria.

        Returns:
            Score between 0 and 1.
        """
        config = provider.config
        if not config:
            return 0.5

        is_compliant = config.metadata.get("privacy_compliant", True)

        if not criteria.privacy_required:
            return 0.7  # Neutral if not required

        return 1.0 if is_compliant else 0.0

    def _score_regional(
        self,
        provider: BaseProvider,
        criteria: SelectionCriteria,
    ) -> float:
        """Score based on regional proximity.

        Args:
            provider: Provider to score.
            criteria: Selection criteria.

        Returns:
            Score between 0 and 1.
        """
        if not criteria.preferred_regions:
            return 0.7  # Neutral

        config = provider.config
        if not config:
            return 0.5

        provider_region = config.metadata.get("region", "")

        if provider_region in criteria.preferred_regions:
            return 1.0
        elif provider_region:
            return 0.3
        else:
            return 0.5

    def rank_providers(
        self,
        providers: list[BaseProvider],
        criteria: SelectionCriteria,
        health_metrics: dict[str, HealthMetrics] | None = None,
    ) -> list[ProviderScore]:
        """Rank providers by score.

        Args:
            providers: List of providers.
            criteria: Selection criteria.
            health_metrics: Optional health metrics per provider.

        Returns:
            Sorted list of provider scores (highest first).
        """
        scores = []

        for provider in providers:
            metrics = health_metrics.get(provider.provider_id) if health_metrics else None
            score = self.score(provider, criteria, metrics)
            scores.append(score)

        # Sort by total score descending
        scores.sort(key=lambda s: s.total_score, reverse=True)

        return scores

    def get_best_provider(
        self,
        providers: list[BaseProvider],
        criteria: SelectionCriteria,
        health_metrics: dict[str, HealthMetrics] | None = None,
    ) -> ProviderScore | None:
        """Get the best provider based on criteria.

        Args:
            providers: List of providers.
            criteria: Selection criteria.
            health_metrics: Optional health metrics per provider.

        Returns:
            Best provider score or None.
        """
        ranked = self.rank_providers(providers, criteria, health_metrics)
        return ranked[0] if ranked else None

    def clear_cache(self) -> None:
        """Clear score cache."""
        with self._lock:
            self._cache.clear()
