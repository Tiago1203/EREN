"""Pipeline Selector for EREN OS Cognitive Capability Router.

Selects the best pipeline from candidates using policies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.router.context import RouterContext
from core.router.policy import (
    RoutingPolicyHandler,
    PolicyFactory,
    FirstMatchPolicy,
)
from core.router.types import (
    RoutingPolicy,
    PipelineMetadata,
    CandidatePipeline,
)
from core.router.result import RoutingResult
from core.router.exceptions import SelectorError

if TYPE_CHECKING:
    pass


class PipelineSelector:
    """Selects pipelines from candidates using policies.

    Uses routing policies to determine the best pipeline
    from a list of matched candidates.
    """

    def __init__(
        self,
        policy: RoutingPolicy | RoutingPolicyHandler | None = None,
        fallback_enabled: bool = True,
    ):
        """Initialize the selector.

        Args:
            policy: Routing policy to use.
            fallback_enabled: Whether to use fallback on failure.
        """
        if isinstance(policy, RoutingPolicy):
            self._policy = PolicyFactory.create(policy)
        elif policy is None:
            self._policy = FirstMatchPolicy()
        else:
            self._policy = policy

        self._fallback_enabled = fallback_enabled

    @property
    def policy(self) -> RoutingPolicy:
        """Get current policy."""
        return self._policy.policy

    @property
    def policy_handler(self) -> RoutingPolicyHandler:
        """Get policy handler."""
        return self._policy

    def select(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
        result: RoutingResult,
    ) -> PipelineMetadata | None:
        """Select a pipeline from candidates.

        Args:
            context: Routing context.
            candidates: List of candidate pipelines.
            result: Routing result to update.

        Returns:
            Selected pipeline metadata or None.
        """
        if not candidates:
            result.fail("No candidates provided")
            return None

        # Sort candidates by score
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.score,
            reverse=True,
        )

        # Try primary policy
        result.add_trace_entry("select_start", {
            "policy": self._policy.policy.value,
            "candidate_count": len(candidates),
        })

        if self._policy.can_select(context, sorted_candidates):
            selected = self._policy.select(context, sorted_candidates)
            if selected:
                result.add_trace_entry("select_success", {
                    "pipeline": selected.pipeline_name,
                    "policy": self._policy.policy.value,
                })
                return selected

        # Try fallback policies
        if self._fallback_enabled:
            selected = self._try_fallback(context, sorted_candidates, result)
            if selected:
                return selected

        # No selection possible
        result.fail("No eligible pipeline found")
        result.add_trace_entry("select_failure", {
            "reason": "No policy could select a pipeline",
        })
        return None

    def _try_fallback(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
        result: RoutingResult,
    ) -> PipelineMetadata | None:
        """Try fallback policies.

        Args:
            context: Routing context.
            candidates: List of candidates.
            result: Routing result.

        Returns:
            Selected pipeline or None.
        """
        fallback_policies = [
            RoutingPolicy.HIGHEST_SCORE,
            RoutingPolicy.PRIORITY,
            RoutingPolicy.FIRST_MATCH,
        ]

        for policy_type in fallback_policies:
            if policy_type == self._policy.policy:
                continue

            policy = PolicyFactory.create(policy_type)
            if policy.can_select(context, candidates):
                selected = policy.select(context, candidates)
                if selected:
                    result.add_trace_entry("fallback_used", {
                        "policy": policy_type.value,
                        "pipeline": selected.pipeline_name,
                    })
                    return selected

        return None

    def select_with_reason(
        self,
        context: RouterContext,
        candidates: list[CandidatePipeline],
        result: RoutingResult,
    ) -> tuple[PipelineMetadata | None, str]:
        """Select pipeline with selection reason.

        Args:
            context: Routing context.
            candidates: List of candidates.
            result: Routing result.

        Returns:
            Tuple of (selected pipeline, reason).
        """
        selected = self.select(context, candidates, result)

        if selected is None:
            return None, "No eligible pipeline found"

        # Determine reason based on policy
        reason = self._generate_reason(context, selected, candidates)

        return selected, reason

    def _generate_reason(
        self,
        context: RouterContext,
        selected: PipelineMetadata,
        candidates: list[CandidatePipeline],
    ) -> str:
        """Generate human-readable selection reason.

        Args:
            context: Routing context.
            selected: Selected pipeline.
            candidates: All candidates.

        Returns:
            Reason string.
        """
        reasons = []

        # Policy used
        reasons.append(f"Policy: {self._policy.policy.value}")

        # Match quality
        selected_candidate = next(
            (c for c in candidates if c.metadata.pipeline_name == selected.pipeline_name),
            None,
        )
        if selected_candidate:
            reasons.append(f"Match: {selected_candidate.match_result.value}")
            reasons.append(f"Score: {selected_candidate.score:.1f}")

        # Priority
        if selected.priority > 0:
            reasons.append(f"Priority: {selected.priority}")

        return "; ".join(reasons)
