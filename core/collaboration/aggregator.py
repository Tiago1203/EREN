"""Result aggregator for EREN Multi-Agent Collaboration Engine.

Aggregates results from multiple agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class ResultAggregator:
    """Aggregates results from multiple agents.

    The Result Aggregator does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Collects results
    - Merges results
    - Prioritizes results
    """

    def __init__(self):
        """Initialize result aggregator."""
        self._results: dict[str, dict[str, Any]] = {}  # session_id -> {agent_id -> result}

    def add_result(
        self,
        session_id: str,
        agent_id: str,
        result: Any,
        priority: int = 5,
    ) -> None:
        """Add a result from an agent.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.
            result: Result value.
            priority: Agent priority (1-10, higher = more important).
        """
        if session_id not in self._results:
            self._results[session_id] = {}

        self._results[session_id][agent_id] = {
            "result": result,
            "priority": priority,
            "agent_id": agent_id,
        }

    def get_results(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get all results for a session.

        Args:
            session_id: Session ID.

        Returns:
            Dictionary of results by agent.
        """
        return self._results.get(session_id, {}).copy()

    def get_result_count(
        self,
        session_id: str,
    ) -> int:
        """Get number of results.

        Args:
            session_id: Session ID.

        Returns:
            Result count.
        """
        return len(self._results.get(session_id, {}))

    def aggregate(
        self,
        session_id: str,
        strategy: str = "priority",
    ) -> Any:
        """Aggregate results.

        Args:
            session_id: Session ID.
            strategy: Aggregation strategy.

        Returns:
            Aggregated result.
        """
        results = self._results.get(session_id, {})
        if not results:
            return None

        if strategy == "priority":
            return self._aggregate_by_priority(results)
        elif strategy == "all":
            return self._aggregate_all(results)
        elif strategy == "best":
            return self._aggregate_best(results)
        elif strategy == "combine":
            return self._aggregate_combine(results)
        elif strategy == "vote":
            return self._aggregate_by_vote(results)

        return None

    def _aggregate_by_priority(
        self,
        results: dict[str, Any],
    ) -> Any:
        """Aggregate by agent priority."""
        if not results:
            return None

        # Sort by priority (higher = more important)
        sorted_results = sorted(
            results.values(),
            key=lambda x: x.get("priority", 5),
            reverse=True,
        )

        return sorted_results[0]["result"]

    def _aggregate_all(
        self,
        results: dict[str, Any],
    ) -> list[Any]:
        """Aggregate all results as a list."""
        return [r["result"] for r in results.values()]

    def _aggregate_best(
        self,
        results: dict[str, Any],
    ) -> Any:
        """Aggregate by selecting the best result."""
        best = None
        best_score = -1

        for r in results.values():
            result = r["result"]
            score = self._score_result(result)

            if score > best_score:
                best_score = score
                best = result

        return best

    def _aggregate_combine(
        self,
        results: dict[str, Any],
    ) -> dict:
        """Combine results into a single dict."""
        combined = {}

        for r in results.values():
            result = r["result"]
            if isinstance(result, dict):
                combined.update(result)
            elif isinstance(result, list):
                if "items" not in combined:
                    combined["items"] = []
                combined["items"].extend(result)

        return combined

    def _aggregate_by_vote(
        self,
        results: dict[str, Any],
    ) -> Any:
        """Aggregate by voting/duplicates."""
        from collections import Counter

        values = []
        for r in results.values():
            result = r["result"]
            if isinstance(result, list):
                values.extend(result)
            else:
                values.append(result)

        # Find most common
        if values:
            counter = Counter(values)
            return counter.most_common(1)[0][0]

        return None

    def _score_result(
        self,
        result: Any,
    ) -> float:
        """Score a result for quality."""
        score = 0.0

        if result is None:
            return 0.0

        if isinstance(result, dict):
            score += len(result) * 0.5
            if "confidence" in result:
                score += result["confidence"] * 10
            if "evidence" in result:
                score += len(result["evidence"]) * 2

        if isinstance(result, list):
            score += len(result) * 0.3

        if isinstance(result, str):
            score += len(result) * 0.1

        return score

    def merge(
        self,
        session_id: str,
        source_session_id: str,
    ) -> None:
        """Merge results from another session.

        Args:
            session_id: Target session ID.
            source_session_id: Source session ID.
        """
        source = self._results.get(source_session_id, {})
        if session_id not in self._results:
            self._results[session_id] = {}

        self._results[session_id].update(source)

    def clear(self, session_id: str) -> int:
        """Clear results for a session.

        Args:
            session_id: Session ID.

        Returns:
            Number of results cleared.
        """
        count = len(self._results.get(session_id, {}))
        self._results.pop(session_id, None)
        return count

    def rank_results(
        self,
        session_id: str,
    ) -> list[tuple[str, Any, float]]:
        """Rank results by quality.

        Args:
            session_id: Session ID.

        Returns:
            List of (agent_id, result, score) tuples.
        """
        results = self._results.get(session_id, {})
        ranked = []

        for agent_id, data in results.items():
            result = data["result"]
            score = self._score_result(result)
            priority = data.get("priority", 5)
            # Combined score
            final_score = score + (priority * 0.1)
            ranked.append((agent_id, result, final_score))

        ranked.sort(key=lambda x: x[2], reverse=True)
        return ranked


# Global result aggregator
_global_result_aggregator: ResultAggregator | None = None
_aggregator_lock = __import__("threading").Lock()


def get_result_aggregator() -> ResultAggregator:
    """Get the global result aggregator.

    Returns:
        Global ResultAggregator instance.
    """
    global _global_result_aggregator
    with _aggregator_lock:
        if _global_result_aggregator is None:
            _global_result_aggregator = ResultAggregator()
        return _global_result_aggregator


def reset_result_aggregator() -> None:
    """Reset the global result aggregator."""
    global _global_result_aggregator
    with _aggregator_lock:
        _global_result_aggregator = None
