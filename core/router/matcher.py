"""Pipeline Matcher for EREN OS Cognitive Capability Router.

Evaluates compatibility between intent and pipelines.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from core.router.context import RouterContext
from core.router.types import (
    PipelineMetadata,
    CandidatePipeline,
    MatchResult,
)
from core.router.exceptions import MatcherError

if TYPE_CHECKING:
    pass


class PipelineMatcher:
    """Matches intents to pipeline candidates.

    Evaluates compatibility based on:
    - Intent type matching
    - Tag matching
    - Capability requirements
    - Priority
    - Custom conditions
    """

    def __init__(self):
        """Initialize the matcher."""
        self._match_weights = {
            MatchResult.EXACT: 100.0,
            MatchResult.PARTIAL: 50.0,
            MatchResult.POTENTIAL: 25.0,
            MatchResult.NO_MATCH: 0.0,
        }

    def match(
        self,
        context: RouterContext,
        metadata: PipelineMetadata,
    ) -> CandidatePipeline:
        """Match context against pipeline metadata.

        Args:
            context: Routing context.
            metadata: Pipeline metadata.

        Returns:
            CandidatePipeline with match information.
        """
        candidate = CandidatePipeline(
            metadata=metadata,
            score=0.0,
            match_result=MatchResult.NO_MATCH,
        )

        # Check excluded types
        if context.intent_type in metadata.excluded_intent_types:
            candidate.is_eligible = False
            candidate.eligibility_reason = "Intent type is excluded"
            candidate.match_result = MatchResult.NO_MATCH
            return candidate

        # Check required capabilities
        if not self._check_capabilities(context, metadata, candidate):
            return candidate

        # Match intent type
        intent_score = self._match_intent_type(context, metadata, candidate)
        candidate.score += intent_score

        # Match tags
        tag_score = self._match_tags(context, metadata, candidate)
        candidate.score += tag_score

        # Check priority
        priority_score = self._evaluate_priority(context, metadata, candidate)
        candidate.score += priority_score

        # Evaluate custom conditions
        condition_score = self._evaluate_conditions(context, metadata, candidate)
        candidate.score += condition_score

        # Normalize score
        candidate.score = min(100.0, max(0.0, candidate.score))

        # Determine match result
        self._determine_match_result(candidate)

        return candidate

    def _check_capabilities(
        self,
        context: RouterContext,
        metadata: PipelineMetadata,
        candidate: CandidatePipeline,
    ) -> bool:
        """Check if required capabilities are available.

        Args:
            context: Routing context.
            metadata: Pipeline metadata.
            candidate: Candidate to update.

        Returns:
            True if all requirements met.
        """
        required = set(metadata.required_capabilities)
        available = set(context.available_capabilities)

        if required and not required.issubset(available):
            missing = required - available
            candidate.is_eligible = False
            candidate.eligibility_reason = f"Missing capabilities: {missing}"
            candidate.match_result = MatchResult.NO_MATCH
            return False

        # Check required context
        for key in metadata.required_context:
            if key not in context.context_data:
                candidate.is_eligible = False
                candidate.eligibility_reason = f"Missing context: {key}"
                return False

        return True

    def _match_intent_type(
        self,
        context: RouterContext,
        metadata: PipelineMetadata,
        candidate: CandidatePipeline,
    ) -> float:
        """Match intent type.

        Args:
            context: Routing context.
            metadata: Pipeline metadata.
            candidate: Candidate to update.

        Returns:
            Score contribution.
        """
        score = 0.0
        intent_type = context.intent_type

        if intent_type in metadata.intent_types:
            score = self._match_weights[MatchResult.EXACT]
            candidate.match_reasons.append(f"Exact intent type match: {intent_type}")
        elif self._is_partial_match(intent_type, metadata.intent_types):
            score = self._match_weights[MatchResult.PARTIAL]
            candidate.match_reasons.append(f"Partial intent type match")
        elif self._has_wildcard_match(intent_type, metadata.intent_types):
            score = self._match_weights[MatchResult.POTENTIAL]
            candidate.match_reasons.append(f"Wildcard intent type match")

        return score

    def _match_tags(
        self,
        context: RouterContext,
        metadata: PipelineMetadata,
        candidate: CandidatePipeline,
    ) -> float:
        """Match tags.

        Args:
            context: Routing context.
            metadata: Pipeline metadata.
            candidate: Candidate to update.

        Returns:
            Score contribution.
        """
        if not metadata.tags:
            return 0.0

        # Check context tags
        context_tags = context.get("tags", [])
        matching_tags = set(metadata.tags) & set(context_tags)
        tag_ratio = len(matching_tags) / len(metadata.tags) if metadata.tags else 0

        score = tag_ratio * 30.0  # Tags contribute up to 30 points

        if matching_tags:
            candidate.match_reasons.append(f"Matching tags: {matching_tags}")

        return score

    def _evaluate_priority(
        self,
        context: RouterContext,
        metadata: PipelineMetadata,
        candidate: CandidatePipeline,
    ) -> float:
        """Evaluate priority.

        Args:
            context: Routing context.
            metadata: Pipeline metadata.
            candidate: Candidate to update.

        Returns:
            Score contribution.
        """
        # Priority contributes up to 20 points
        priority_score = min(metadata.priority, 100) / 5.0

        if context.priority > 0:
            # Boost if context priority matches
            if context.priority >= metadata.priority:
                priority_score *= 1.5

        return priority_score

    def _evaluate_conditions(
        self,
        context: RouterContext,
        metadata: PipelineMetadata,
        candidate: CandidatePipeline,
    ) -> float:
        """Evaluate custom conditions.

        Args:
            context: Routing context.
            metadata: Pipeline metadata.
            candidate: Candidate to update.

        Returns:
            Score contribution.
        """
        conditions = metadata.metadata.get("conditions", {})
        if not conditions:
            return 0.0

        score = 0.0
        for key, expected in conditions.items():
            actual = context.get(key)
            if actual is None:
                continue

            if actual == expected:
                score += 10.0
                candidate.matched_rules.append(f"condition:{key}")
            elif isinstance(expected, str) and "*" in expected:
                # Wildcard match
                pattern = expected.replace("*", ".*")
                if re.match(pattern, str(actual)):
                    score += 5.0
                    candidate.matched_rules.append(f"wildcard:{key}")

        return score

    def _is_partial_match(self, intent_type: str, types: tuple[str, ...]) -> bool:
        """Check for partial match.

        Args:
            intent_type: Intent type.
            types: Available types.

        Returns:
            True if partial match.
        """
        for t in types:
            if t in intent_type or intent_type in t:
                return True
        return False

    def _has_wildcard_match(self, intent_type: str, types: tuple[str, ...]) -> bool:
        """Check for wildcard match.

        Args:
            intent_type: Intent type.
            types: Available types.

        Returns:
            True if wildcard match.
        """
        for t in types:
            if "*" in t:
                pattern = t.replace("*", ".*")
                if re.match(pattern, intent_type):
                    return True
        return False

    def _determine_match_result(self, candidate: CandidatePipeline) -> None:
        """Determine match result from score.

        Args:
            candidate: Candidate to update.
        """
        score = candidate.score

        if score >= 90:
            candidate.match_result = MatchResult.EXACT
        elif score >= 50:
            candidate.match_result = MatchResult.PARTIAL
        elif score > 0:
            candidate.match_result = MatchResult.POTENTIAL
        else:
            candidate.match_result = MatchResult.NO_MATCH
