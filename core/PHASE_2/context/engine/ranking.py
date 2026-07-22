"""Context ranking for EREN Cognitive Context Engine.

Ranks and prioritizes context items.
"""

from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING

from core.PHASE_2.context.engine.types import (
    ContextItem,
    ContextPriority,
    ContextSource,
)

if TYPE_CHECKING:
    pass


class ContextRanker:
    """Ranks and prioritizes context items.

    Ensures best context items are included.
    """

    def __init__(self):
        """Initialize ranker."""
        self._priority_weights = {
            ContextPriority.CRITICAL: 1.0,
            ContextPriority.HIGH: 0.8,
            ContextPriority.MEDIUM: 0.5,
            ContextPriority.LOW: 0.2,
        }

    def rank(
        self,
        items: list[ContextItem],
        prioritize_clinical: bool = True,
        prioritize_recent: bool = True,
    ) -> list[ContextItem]:
        """Rank context items.

        Args:
            items: Items to rank.
            prioritize_clinical: Prioritize clinical context.
            prioritize_recent: Prioritize recent items.

        Returns:
            Ranked items.
        """
        if not items:
            return []

        # Calculate composite score
        scored_items = []
        for item in items:
            score = self._calculate_score(
                item,
                prioritize_clinical,
                prioritize_recent,
            )
            scored_items.append((score, item))

        # Sort by score descending
        scored_items.sort(key=lambda x: x[0], reverse=True)

        return [item for _, item in scored_items]

    def _calculate_score(
        self,
        item: ContextItem,
        prioritize_clinical: bool,
        prioritize_recent: bool,
    ) -> float:
        """Calculate composite score for item."""
        score = item.relevance_score

        # Priority weight
        priority_weight = self._priority_weights.get(item.priority, 0.5)
        score *= priority_weight

        # Clinical bonus
        if prioritize_clinical and item.source == ContextSource.CLINICAL:
            score *= 1.5

        # Recency bonus
        if prioritize_recent:
            recency_score = self._calculate_recency(item.timestamp)
            score *= (0.5 + recency_score * 0.5)

        return score

    def _calculate_recency(self, timestamp) -> float:
        """Calculate recency score (0-1)."""
        from datetime import datetime

        now = datetime.now(UTC)
        age = (now - timestamp).total_seconds()

        # Decay over 24 hours
        if age < 0:
            return 1.0

        recency = max(0.0, 1.0 - (age / 86400))
        return recency

    def prioritize(
        self,
        items: list[ContextItem],
    ) -> list[ContextItem]:
        """Prioritize items by importance.

        Args:
            items: Items to prioritize.

        Returns:
            Prioritized items.
        """
        return self.rank(items, prioritize_clinical=True, prioritize_recent=True)
