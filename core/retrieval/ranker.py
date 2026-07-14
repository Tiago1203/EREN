"""Result ranker for EREN Semantic Retrieval Engine.

Ranks retrieval results by relevance and quality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.retrieval.types import (
    RetrievalQuery,
    RetrievalResult,
    RetrievalResponse,
    MemorySource,
)
from core.retrieval.exceptions import RankingError

if TYPE_CHECKING:
    pass


class ResultRanker:
    """Ranks retrieval results.

    Responsibilities:
    - Score results by relevance
    - Apply filters
    - Remove duplicates
    - Order results
    """

    # Source priority weights
    SOURCE_WEIGHTS = {
        MemorySource.CLINICAL: 1.5,
        MemorySource.VECTOR: 1.3,
        MemorySource.SEMANTIC: 1.2,
        MemorySource.CONVERSATION: 1.1,
        MemorySource.DEVICE: 1.0,
        MemorySource.WORKING: 1.0,
        MemorySource.LONG_TERM: 0.9,
    }

    def rank(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Rank results.

        Args:
            results: Results to rank.
            query: Original query.

        Returns:
            Ranked results.
        """
        if not results:
            return []

        try:
            # Apply source weights
            weighted = self._apply_source_weights(results)

            # Filter by minimum relevance
            filtered = self._filter_by_relevance(weighted, query.min_relevance_score)

            # Remove duplicates
            deduplicated = self._deduplicate(filtered)

            # Sort by score
            sorted_results = self._sort_by_score(deduplicated)

            # Apply limit
            return sorted_results[:query.max_results]

        except Exception as e:
            raise RankingError(str(e))

    def _apply_source_weights(
        self,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """Apply source priority weights.

        Args:
            results: Results to weight.

        Returns:
            Weighted results.
        """
        for result in results:
            weight = self.SOURCE_WEIGHTS.get(result.source, 1.0)
            result.relevance_score *= weight
        return results

    def _filter_by_relevance(
        self,
        results: list[RetrievalResult],
        min_score: float,
    ) -> list[RetrievalResult]:
        """Filter by minimum relevance score.

        Args:
            results: Results to filter.
            min_score: Minimum score.

        Returns:
            Filtered results.
        """
        if min_score <= 0:
            return results
        return [r for r in results if r.relevance_score >= min_score]

    def _deduplicate(
        self,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """Remove duplicate results.

        Args:
            results: Results to deduplicate.

        Returns:
            Deduplicated results.
        """
        seen = set()
        unique = []

        for result in results:
            # Use content hash for deduplication
            content_hash = hash(result.content.lower().strip())
            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(result)

        return unique

    def _sort_by_score(
        self,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:
        """Sort results by relevance score.

        Args:
            results: Results to sort.

        Returns:
            Sorted results.
        """
        return sorted(results, key=lambda r: r.relevance_score, reverse=True)


class ContextualRanker(ResultRanker):
    """Enhanced ranker with contextual scoring.

    Considers:
    - Recency
    - Context relevance
    - Query type
    """

    def rank(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Rank with contextual scoring.

        Args:
            results: Results to rank.
            query: Original query.

        Returns:
            Ranked results.
        """
        if not results:
            return []

        # Apply basic ranking
        ranked = super().rank(results, query)

        # Apply contextual boosts
        ranked = self._apply_contextual_boosts(ranked, query)

        # Re-sort after boosts
        return sorted(ranked, key=lambda r: r.relevance_score, reverse=True)

    def _apply_contextual_boosts(
        self,
        results: list[RetrievalResult],
        query: RetrievalQuery,
    ) -> list[RetrievalResult]:
        """Apply contextual score boosts.

        Args:
            results: Results to boost.
            query: Query context.

        Returns:
            Boosted results.
        """
        for result in results:
            # Boost if query matches result metadata
            if query.conversation_id and result.metadata.get("conversation_id") == query.conversation_id:
                result.relevance_score *= 1.2

            # Boost if from current session
            if query.session_id and result.metadata.get("session_id") == query.session_id:
                result.relevance_score *= 1.1

            # Boost recent results
            from datetime import datetime, timezone, timedelta
            age = datetime.now(timezone.utc) - result.timestamp
            if age < timedelta(hours=1):
                result.relevance_score *= 1.1
            elif age < timedelta(hours=24):
                result.relevance_score *= 1.05

        return results


# Factory for creating rankers
class RankerFactory:
    """Factory for result rankers."""

    _rankers = {
        "default": ResultRanker,
        "contextual": ContextualRanker,
    }

    @classmethod
    def create(cls, name: str = "default") -> ResultRanker:
        """Create a ranker by name.

        Args:
            name: Ranker name.

        Returns:
            Ranker instance.
        """
        ranker_class = cls._rankers.get(name, ResultRanker)
        return ranker_class()

    @classmethod
    def register(cls, name: str, ranker_class: type[ResultRanker]) -> None:
        """Register a new ranker.

        Args:
            name: Ranker name.
            ranker_class: Ranker class.
        """
        cls._rankers[name] = ranker_class

    @classmethod
    def list_rankers(cls) -> list[str]:
        """List available rankers.

        Returns:
            List of ranker names.
        """
        return list(cls._rankers.keys())
