"""Routing Policies for EREN OS Cognitive Capability Router.

Defines policies for pipeline selection.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.router.context import RouterContext
from core.router.types import (
    CandidatePipeline,
    PipelineMetadata,
    RoutingPolicy,
)

if TYPE_CHECKING:
    pass


class RoutingPolicyHandler(ABC):
    """Abstract base class for routing policies."""

    @property
    @abstractmethod
    def policy(self) -> RoutingPolicy:
        """Get the policy type."""
        ...

    @abstractmethod
    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> PipelineMetadata | None:
        """Select a pipeline from candidates.

        Args:
            context: Routing context.
            candidates: List of candidate pipelines.

        Returns:
            Selected pipeline metadata or None.
        """
        ...

    @abstractmethod
    def can_select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> bool:
        """Check if policy can select from candidates.

        Args:
            context: Routing context.
            candidates: List of candidate pipelines.

        Returns:
            True if selection is possible.
        """
        ...


class FirstMatchPolicy(RoutingPolicyHandler):
    """Select the first matching pipeline."""

    @property
    def policy(self) -> RoutingPolicy:
        return RoutingPolicy.FIRST_MATCH

    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> PipelineMetadata | None:
        """Select first eligible candidate with score > 0."""
        eligible = [c for c in candidates if c.is_eligible and c.score > 0]
        if not eligible:
            return None
        return eligible[0].metadata

    def can_select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> bool:
        """Check if any eligible candidate exists."""
        return any(c.is_eligible and c.score > 0 for c in candidates)


class HighestScorePolicy(RoutingPolicyHandler):
    """Select the pipeline with the highest score."""

    @property
    def policy(self) -> RoutingPolicy:
        return RoutingPolicy.HIGHEST_SCORE

    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> PipelineMetadata | None:
        """Select highest scoring eligible candidate."""
        eligible = [c for c in candidates if c.is_eligible]
        if not eligible:
            return None
        return max(eligible, key=lambda c: c.score).metadata

    def can_select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> bool:
        """Check if any eligible candidate exists."""
        return any(c.is_eligible for c in candidates)


class PriorityPolicy(RoutingPolicyHandler):
    """Select the pipeline with highest priority."""

    @property
    def policy(self) -> RoutingPolicy:
        return RoutingPolicy.PRIORITY

    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> PipelineMetadata | None:
        """Select highest priority eligible candidate."""
        eligible = [c for c in candidates if c.is_eligible]
        if not eligible:
            return None
        return max(eligible, key=lambda c: c.metadata.priority).metadata

    def can_select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> bool:
        """Check if any eligible candidate exists."""
        return any(c.is_eligible for c in candidates)


class StrictPolicy(RoutingPolicyHandler):
    """Require exact match, fail if none found."""

    @property
    def policy(self) -> RoutingPolicy:
        return RoutingPolicy.STRICT

    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> PipelineMetadata | None:
        """Select only exact match candidates."""
        from core.router.types import MatchResult
        exact = [c for c in candidates if c.is_eligible and c.match_result == MatchResult.EXACT]
        if not exact:
            return None
        return max(exact, key=lambda c: c.score).metadata

    def can_select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> bool:
        """Check if exact match exists."""
        from core.router.types import MatchResult
        return any(c.is_eligible and c.match_result == MatchResult.EXACT for c in candidates)


class WeightedPolicy(RoutingPolicyHandler):
    """Select based on weighted combination of score and priority."""

    @property
    def policy(self) -> RoutingPolicy:
        return RoutingPolicy.WEIGHTED

    def __init__(self, score_weight: float = 0.7, priority_weight: float = 0.3):
        """Initialize weighted policy.

        Args:
            score_weight: Weight for match score.
            priority_weight: Weight for priority.
        """
        self.score_weight = score_weight
        self.priority_weight = priority_weight

    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> PipelineMetadata | None:
        """Select based on weighted score."""
        eligible = [c for c in candidates if c.is_eligible]
        if not eligible:
            return None

        for candidate in eligible:
            # Calculate weighted score
            priority_normalized = min(candidate.metadata.priority, 100) / 100.0
            weighted_score = (
                self.score_weight * candidate.score +
                self.priority_weight * priority_normalized * 100
            )
            candidate.score = weighted_score

        return max(eligible, key=lambda c: c.score).metadata

    def can_select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> bool:
        """Check if any eligible candidate exists."""
        return any(c.is_eligible for c in candidates)


class FallbackPolicy(RoutingPolicyHandler):
    """Try policies in order until one succeeds."""

    def __init__(
        self,
        policies: list[RoutingPolicyHandler] | None = None,
        default_policy: RoutingPolicyHandler | None = None,
    ):
        """Initialize fallback policy.

        Args:
            policies: List of policies to try.
            default_policy: Default policy if all fail.
        """
        self.policies = policies or [
            HighestScorePolicy(),
            PriorityPolicy(),
            FirstMatchPolicy(),
        ]
        self.default_policy = default_policy or FirstMatchPolicy()

    @property
    def policy(self) -> RoutingPolicy:
        return RoutingPolicy.FALLBACK

    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> PipelineMetadata | None:
        """Try policies in order."""
        for policy in self.policies:
            if policy.can_select(context, candidates):
                selected = policy.select(context, candidates)
                if selected:
                    return selected

        # Try default policy
        if self.default_policy.can_select(context, candidates):
            return self.default_policy.select(context, candidates)

        return None

    def can_select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
    ) -> bool:
        """Check if any policy can select."""
        return any(p.can_select(context, candidates) for p in self.policies) or \
               self.default_policy.can_select(context, candidates)


class PolicyFactory:
    """Factory for creating policy handlers."""

    _policies: dict[RoutingPolicy, type[RoutingPolicyHandler]] = {
        RoutingPolicy.FIRST_MATCH: FirstMatchPolicy,
        RoutingPolicy.HIGHEST_SCORE: HighestScorePolicy,
        RoutingPolicy.PRIORITY: PriorityPolicy,
        RoutingPolicy.STRICT: StrictPolicy,
        RoutingPolicy.WEIGHTED: WeightedPolicy,
    }

    @classmethod
    def create(cls, policy: RoutingPolicy, **kwargs) -> RoutingPolicyHandler:
        """Create a policy handler.

        Args:
            policy: Policy type.
            **kwargs: Additional arguments.

        Returns:
            Policy handler instance.
        """
        policy_class = cls._policies.get(policy)
        if policy_class is None:
            return FirstMatchPolicy()
        return policy_class(**kwargs)

    @classmethod
    def create_fallback(
        cls,
        policies: list[RoutingPolicy] | None = None,
    ) -> FallbackPolicy:
        """Create a fallback policy.

        Args:
            policies: List of policy types.

        Returns:
            FallbackPolicy instance.
        """
        handlers = [cls.create(p) for p in (policies or [])]
        return FallbackPolicy(policies=handlers)

    @classmethod
    def register(cls, policy: RoutingPolicy, handler_class: type[RoutingPolicyHandler]) -> None:
        """Register a new policy.

        Args:
            policy: Policy type.
            handler_class: Policy handler class.
        """
        cls._policies[policy] = handler_class

    @classmethod
    def list_policies(cls) -> list[RoutingPolicy]:
        """List all registered policies.

        Returns:
            List of policy types.
        """
        return list(cls._policies.keys())
