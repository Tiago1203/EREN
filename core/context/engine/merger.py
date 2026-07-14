"""Context merger for EREN Cognitive Context Engine.

Merges results from different sources.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.context.engine.types import (
    ContextItem,
    ContextRetrievalResult,
    ContextSource,
)

if TYPE_CHECKING:
    pass


class ContextMerger:
    """Merges context from multiple sources.

    Combines retrieval results into unified context.
    """

    def __init__(self):
        """Initialize merger."""
        pass

    def merge(
        self,
        *results: ContextRetrievalResult,
    ) -> list[ContextItem]:
        """Merge multiple retrieval results.

        Args:
            *results: Results to merge.

        Returns:
            Merged list of context items.
        """
        all_items = []

        for result in results:
            all_items.extend(result.items)

        return all_items

    def merge_by_source(
        self,
        conversation: list[ContextItem] | None = None,
        knowledge: list[ContextItem] | None = None,
        device: list[ContextItem] | None = None,
        clinical: list[ContextItem] | None = None,
    ) -> list[ContextItem]:
        """Merge context items by source.

        Args:
            conversation: Conversation context items.
            knowledge: Knowledge context items.
            device: Device context items.
            clinical: Clinical context items.

        Returns:
            Merged and prioritized list.
        """
        merged = []

        # Add clinical first (highest priority)
        if clinical:
            for item in clinical:
                item.source = ContextSource.CLINICAL
                merged.append(item)

        # Add conversation
        if conversation:
            for item in conversation:
                item.source = ContextSource.CONVERSATION
                merged.append(item)

        # Add knowledge
        if knowledge:
            for item in knowledge:
                item.source = ContextSource.KNOWLEDGE
                merged.append(item)

        # Add device
        if device:
            for item in device:
                item.source = ContextSource.DEVICE
                merged.append(item)

        return merged

    def merge_and_score(
        self,
        items: list[ContextItem],
    ) -> list[ContextItem]:
        """Merge items and calculate combined scores.

        Args:
            items: Items to merge and score.

        Returns:
            Items with updated relevance scores.
        """
        if not items:
            return []

        # Normalize scores
        max_score = max(item.relevance_score for item in items)

        if max_score > 0:
            for item in items:
                item.relevance_score /= max_score

        return items
