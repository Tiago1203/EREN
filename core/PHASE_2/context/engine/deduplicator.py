"""Context deduplicator for EREN Cognitive Context Engine.

Removes duplicate context items.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.context.engine.types import ContextItem, ContextRetrievalResult

if TYPE_CHECKING:
    pass


class ContextDeduplicator:
    """Deduplicates context items.

    Ensures unique content in context package.
    """

    def __init__(self, similarity_threshold: float = 0.9):
        """Initialize deduplicator.

        Args:
            similarity_threshold: Threshold for considering duplicates.
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(
        self,
        items: list[ContextItem],
    ) -> tuple[list[ContextItem], int]:
        """Remove duplicate items.

        Args:
            items: Items to deduplicate.

        Returns:
            Tuple of (unique_items, duplicates_removed).
        """
        if not items:
            return [], 0

        unique_items = []
        seen_content = set()
        duplicates = 0

        for item in items:
            normalized = self._normalize(item.content)

            if normalized not in seen_content:
                seen_content.add(normalized)
                unique_items.append(item)
            else:
                duplicates += 1

        return unique_items, duplicates

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        return " ".join(text.lower().split())

    def deduplicate_result(
        self,
        result: ContextRetrievalResult,
    ) -> ContextRetrievalResult:
        """Deduplicate a retrieval result.

        Args:
            result: Retrieval result to deduplicate.

        Returns:
            Deduplicated result.
        """
        unique_items, duplicates = self.deduplicate(result.items)

        return ContextRetrievalResult(
            query_id=result.query_id,
            items=unique_items,
            total_retrieved=len(unique_items),
            retrieval_time_ms=result.retrieval_time_ms,
            unique_items=len(unique_items),
            duplicates_removed=duplicates,
            avg_relevance=result.avg_relevance,
        )
