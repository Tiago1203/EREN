"""Capability resolver for intelligent capability matching.

The resolver provides intelligent capability matching based on queries,
requirements, and context.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .capability import Capability
from .descriptor import CapabilityMatch
from .exceptions import ResolutionError
from .types import (
    CapabilityCategory,
    CapabilityFilter,
    CapabilityPriority,
    CapabilityStatus,
    SearchOptions,
)

if TYPE_CHECKING:
    from .capability_registry import CapabilityRegistry


@dataclass
class ResolutionCriteria:
    """Criteria for capability resolution."""

    # What to find
    capability_id: str | None = None  # Exact match
    category: CapabilityCategory | None = None
    action: str | None = None
    target: str | None = None

    # Requirements
    min_priority: CapabilityPriority | None = None
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    required_events: tuple[str, ...] = field(default_factory=tuple)
    security_level_required: int | None = None

    # Preferences
    prefer_active: bool = True
    prefer_high_priority: bool = True
    prefer_latest_version: bool = True

    # Context
    context: dict = field(default_factory=dict)

    @classmethod
    def from_query(
        cls,
        query: str,
        **kwargs,
    ) -> ResolutionCriteria:
        """Create criteria from a natural language query.

        Args:
            query: Natural language query (e.g., "diagnose monitor")
            **kwargs: Additional criteria

        Returns:
            ResolutionCriteria instance
        """
        parts = query.lower().split()

        # Parse category
        category = None
        for cat in CapabilityCategory:
            if cat.value in parts:
                category = cat
                break

        # Parse action (first word that's not a category)
        action = parts[0] if parts else ""

        return cls(
            category=category,
            action=action,
            capability_id=kwargs.get("capability_id"),
            min_priority=kwargs.get("min_priority"),
            **kwargs,
        )


class CapabilityResolver:
    """Resolves capability queries to matching capabilities.

    The resolver finds the best matching capability for a given query
    or set of criteria. It supports:
    - Exact ID matching
    - Category-based matching
    - Fuzzy matching
    - Multi-criteria matching
    - Fallback chains
    """

    def __init__(self, registry: CapabilityRegistry) -> None:
        """Initialize the resolver.

        Args:
            registry: The capability registry to query.
        """
        self._registry = registry

    def resolve(
        self,
        criteria: ResolutionCriteria,
    ) -> CapabilityMatch:
        """Resolve a query to the best matching capability.

        Args:
            criteria: Resolution criteria.

        Returns:
            CapabilityMatch with the best match.

        Raises:
            ResolutionError: If no matching capability is found.
        """
        # Try exact match first
        if criteria.capability_id:
            try:
                cap = self._registry.get(criteria.capability_id)
                return CapabilityMatch(
                    capability=cap,
                    score=1.0,
                    match_reasons=(f"Exact match for '{criteria.capability_id}'",),
                )
            except Exception:
                pass

        # Build filter
        filter_options = CapabilityFilter()
        if criteria.category:
            filter_options.category = criteria.category
        if criteria.min_priority:
            filter_options.min_priority = criteria.min_priority
        if criteria.prefer_active:
            filter_options.active_only = True

        # Search
        candidates = self._registry.search(
            SearchOptions(
                filter=filter_options,
                sort_by="priority",
                ascending=False,
            )
        )

        # Score candidates
        scored = self._score_candidates(candidates, criteria)

        if not scored:
            raise ResolutionError(
                query=criteria.capability_id or criteria.action or "",
                message="No matching capability found",
            )

        # Return best match
        return scored[0]

    def resolve_all(
        self,
        criteria: ResolutionCriteria,
    ) -> list[CapabilityMatch]:
        """Resolve a query to all matching capabilities.

        Args:
            criteria: Resolution criteria.

        Returns:
            List of capability matches sorted by score.
        """
        if criteria.capability_id:
            try:
                cap = self._registry.get(criteria.capability_id)
                return [
                    CapabilityMatch(
                        capability=cap,
                        score=1.0,
                        match_reasons=(f"Exact match for '{criteria.capability_id}'",),
                    )
                ]
            except Exception:
                pass

        filter_options = CapabilityFilter()
        if criteria.category:
            filter_options.category = criteria.category

        candidates = self._registry.search(
            SearchOptions(filter=filter_options)
        )

        return self._score_candidates(candidates, criteria)

    def resolve_chain(
        self,
        capability_ids: list[str],
    ) -> list[Capability]:
        """Resolve a chain of capabilities in order.

        Args:
            capability_ids: Ordered list of capability IDs.

        Returns:
            List of resolved capabilities.

        Raises:
            ResolutionError: If any capability in the chain cannot be resolved.
        """
        resolved: list[Capability] = []

        for cap_id in capability_ids:
            try:
                cap = self._registry.get(cap_id)
                resolved.append(cap)
            except Exception as e:
                raise ResolutionError(
                    query=cap_id,
                    message=f"Failed to resolve chain: {e}",
                ) from e

        return resolved

    def find_alternatives(
        self,
        capability_id: str,
        max_alternatives: int = 3,
    ) -> list[CapabilityMatch]:
        """Find alternative capabilities to the given one.

        Args:
            capability_id: The capability to find alternatives for.
            max_alternatives: Maximum number of alternatives.

        Returns:
            List of alternative capability matches.
        """
        try:
            original = self._registry.get(capability_id)
        except Exception:
            return []

        # Find capabilities in the same category
        filter_options = CapabilityFilter(
            category=original.category,
        )

        candidates = self._registry.search(
            SearchOptions(filter=filter_options)
        )

        # Exclude the original and score
        alternatives = [c for c in candidates if c.id_string != capability_id]

        scored = self._score_candidates(
            alternatives,
            ResolutionCriteria(
                min_priority=original.priority,
            ),
        )

        return scored[:max_alternatives]

    def _score_candidates(
        self,
        candidates: list[Capability],
        criteria: ResolutionCriteria,
    ) -> list[CapabilityMatch]:
        """Score and rank capability candidates.

        Args:
            candidates: List of candidate capabilities.
            criteria: Resolution criteria.

        Returns:
            Sorted list of CapabilityMatch objects.
        """
        scored: list[CapabilityMatch] = []

        for cap in candidates:
            score = 0.0
            reasons: list[str] = []

            # Exact category match
            if criteria.category and cap.category == criteria.category:
                score += 0.3
                reasons.append(f"Category match: {criteria.category.value}")

            # Priority bonus
            if criteria.prefer_high_priority:
                if criteria.min_priority and cap.priority >= criteria.min_priority:
                    score += 0.2 * (cap.priority.value / criteria.min_priority.value)
                    reasons.append(f"Priority {cap.priority.name}")

            # Active status bonus
            if criteria.prefer_active and cap.is_active():
                score += 0.2
                reasons.append("Active status")

            # Version bonus
            if criteria.prefer_latest_version:
                score += 0.1
                reasons.append("Latest version")

            # Required capabilities match
            if criteria.required_capabilities:
                deps_satisfied = sum(
                    1 for dep in criteria.required_capabilities
                    if cap.requires_capability(dep)
                )
                if deps_satisfied == len(criteria.required_capabilities):
                    score += 0.2
                    reasons.append("All dependencies satisfied")

            # Required events match
            if criteria.required_events:
                events_satisfied = sum(
                    1 for evt in criteria.required_events
                    if cap.consumes_event(evt) or cap.publishes_event(evt)
                )
                if events_satisfied == len(criteria.required_events):
                    score += 0.1
                    reasons.append("All event requirements met")

            # Normalize score
            score = min(score, 1.0)

            if score > 0:
                scored.append(
                    CapabilityMatch(
                        capability=cap,
                        score=score,
                        match_reasons=tuple(reasons),
                    )
                )

        # Sort by score descending
        scored.sort(key=lambda x: x.score, reverse=True)

        return scored


class CapabilityMatcher:
    """Matches capabilities based on various criteria."""

    @staticmethod
    def match_by_category(
        capabilities: list[Capability],
        category: CapabilityCategory,
    ) -> list[Capability]:
        """Filter capabilities by category."""
        return [c for c in capabilities if c.category == category]

    @staticmethod
    def match_by_events(
        capabilities: list[Capability],
        event_type: str,
        direction: str = "both",
    ) -> list[Capability]:
        """Filter capabilities by event."""
        results: list[Capability] = []
        for cap in capabilities:
            if direction == "publishes" and cap.publishes_event(event_type):
                results.append(cap)
            elif direction == "consumes" and cap.consumes_event(event_type):
                results.append(cap)
            elif direction == "both":
                if cap.publishes_event(event_type) or cap.consumes_event(event_type):
                    results.append(cap)
        return results

    @staticmethod
    def match_by_priority(
        capabilities: list[Capability],
        min_priority: CapabilityPriority,
    ) -> list[Capability]:
        """Filter capabilities by minimum priority."""
        return [c for c in capabilities if c.priority >= min_priority]

    @staticmethod
    def match_active(
        capabilities: list[Capability],
    ) -> list[Capability]:
        """Filter to only active capabilities."""
        return [c for c in capabilities if c.is_active()]
