"""Retrieval strategy for EREN Semantic Retrieval Engine.

Base strategy and implementations for different retrieval approaches.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from core.retrieval.types import (
    RetrievalQuery,
    RetrievalPlan,
    RetrievalResult,
    RetrievalResponse,
    MemorySource,
)
from core.retrieval.exceptions import RetrievalExecutionError

if TYPE_CHECKING:
    pass


class RetrievalStrategy(ABC):
    """Base class for retrieval strategies."""

    @abstractmethod
    def execute(
        self,
        query: RetrievalQuery,
        plan: RetrievalPlan,
        providers: dict[MemorySource, Callable],
    ) -> RetrievalResponse:
        """Execute the retrieval strategy.

        Args:
            query: Retrieval query.
            plan: Retrieval plan.
            providers: Dictionary of memory providers by source.

        Returns:
            Retrieval response.
        """
        pass


class SequentialStrategy(RetrievalStrategy):
    """Sequential retrieval strategy.

    Retrieves from sources one by one in priority order.
    """

    def execute(
        self,
        query: RetrievalQuery,
        plan: RetrievalPlan,
        providers: dict[MemorySource, Callable],
    ) -> RetrievalResponse:
        """Execute sequential retrieval.

        Args:
            query: Retrieval query.
            plan: Retrieval plan.
            providers: Memory providers.

        Returns:
            Retrieval response.
        """
        all_results: list[RetrievalResult] = []
        sources_queried: list[MemorySource] = []
        errors: list[str] = []

        for step in plan.steps:
            if step.action != "retrieve":
                continue

            source = step.source
            provider = providers.get(source)

            if not provider:
                continue

            try:
                results = provider(query.query, query.max_results)
                for result in results:
                    result.source = source
                all_results.extend(results)
                sources_queried.append(source)
            except Exception as e:
                errors.append(f"{source.value}: {str(e)}")

        return RetrievalResponse(
            results=all_results,
            query=query.query,
            policy_used=query.policy,
            total_results=len(all_results),
            sources_queried=sources_queried,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else None,
        )


class ParallelStrategy(RetrievalStrategy):
    """Parallel retrieval strategy.

    Retrieves from multiple sources concurrently.
    """

    def execute(
        self,
        query: RetrievalQuery,
        plan: RetrievalPlan,
        providers: dict[MemorySource, Callable],
    ) -> RetrievalResponse:
        """Execute parallel retrieval.

        Args:
            query: Retrieval query.
            plan: Retrieval plan.
            providers: Memory providers.

        Returns:
            Retrieval response.
        """
        import concurrent.futures

        all_results: list[RetrievalResult] = []
        sources_queried: list[MemorySource] = []
        errors: list[str] = []

        def retrieve_from_source(source: MemorySource) -> tuple[MemorySource, list[RetrievalResult], str | None]:
            """Retrieve from a single source."""
            provider = providers.get(source)
            if not provider:
                return source, [], f"No provider for {source.value}"

            try:
                results = provider(query.query, query.max_results)
                for result in results:
                    result.source = source
                return source, results, None
            except Exception as e:
                return source, [], str(e)

        # Execute in parallel
        retrieve_steps = [s for s in plan.steps if s.action == "retrieve"]
        sources = [s.source for s in retrieve_steps]

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = {executor.submit(retrieve_from_source, src): src for src in sources}
            for future in concurrent.futures.as_completed(futures):
                source, results, error = future.result()
                if error:
                    errors.append(f"{source.value}: {error}")
                else:
                    all_results.extend(results)
                    sources_queried.append(source)

        return RetrievalResponse(
            results=all_results,
            query=query.query,
            policy_used=query.policy,
            total_results=len(all_results),
            sources_queried=sources_queried,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else None,
        )


class FastestStrategy(RetrievalStrategy):
    """Fastest retrieval strategy.

    Stops after first successful retrieval.
    """

    def execute(
        self,
        query: RetrievalQuery,
        plan: RetrievalPlan,
        providers: dict[MemorySource, Callable],
    ) -> RetrievalResponse:
        """Execute fastest retrieval.

        Args:
            query: Retrieval query.
            plan: Retrieval plan.
            providers: Memory providers.

        Returns:
            Retrieval response.
        """
        retrieve_steps = [s for s in plan.steps if s.action == "retrieve"]
        retrieve_steps.sort(key=lambda s: s.priority)

        for step in retrieve_steps:
            source = step.source
            provider = providers.get(source)

            if not provider:
                continue

            try:
                results = provider(query.query, query.max_results)
                for result in results:
                    result.source = source
                return RetrievalResponse(
                    results=results,
                    query=query.query,
                    policy_used=query.policy,
                    total_results=len(results),
                    sources_queried=[source],
                    success=True,
                )
            except Exception:
                continue

        return RetrievalResponse(
            results=[],
            query=query.query,
            policy_used=query.policy,
            total_results=0,
            sources_queried=[],
            success=False,
            error="No sources available",
        )


class MergeAllStrategy(RetrievalStrategy):
    """Merge all retrieval strategy.

    Retrieves from all sources and merges results.
    """

    def execute(
        self,
        query: RetrievalQuery,
        plan: RetrievalPlan,
        providers: dict[MemorySource, Callable],
    ) -> RetrievalResponse:
        """Execute merge all retrieval.

        Args:
            query: Retrieval query.
            plan: Retrieval plan.
            providers: Memory providers.

        Returns:
            Retrieval response.
        """
        all_results: list[RetrievalResult] = []
        sources_queried: list[MemorySource] = []
        errors: list[str] = []

        for step in plan.steps:
            if step.action != "retrieve":
                continue

            source = step.source
            provider = providers.get(source)

            if not provider:
                continue

            try:
                results = provider(query.query, query.max_results)
                for result in results:
                    result.source = source
                all_results.extend(results)
                sources_queried.append(source)
            except Exception as e:
                errors.append(f"{source.value}: {str(e)}")

        # Deduplicate by content
        seen = set()
        unique_results = []
        for result in all_results:
            content_hash = hash(result.content)
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(result)

        return RetrievalResponse(
            results=unique_results,
            query=query.query,
            policy_used=query.policy,
            total_results=len(unique_results),
            sources_queried=sources_queried,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else None,
        )


# Factory for creating strategies
class RetrievalStrategyFactory:
    """Factory for retrieval strategies."""

    _strategies = {
        "sequential": SequentialStrategy,
        "parallel": ParallelStrategy,
        "fastest": FastestStrategy,
        "merge_all": MergeAllStrategy,
    }

    @classmethod
    def create(cls, name: str) -> RetrievalStrategy:
        """Create a strategy by name.

        Args:
            name: Strategy name.

        Returns:
            Strategy instance.
        """
        strategy_class = cls._strategies.get(name, SequentialStrategy)
        return strategy_class()

    @classmethod
    def register(cls, name: str, strategy_class: type[RetrievalStrategy]) -> None:
        """Register a new strategy.

        Args:
            name: Strategy name.
            strategy_class: Strategy class.
        """
        cls._strategies[name] = strategy_class

    @classmethod
    def list_strategies(cls) -> list[str]:
        """List available strategies.

        Returns:
            List of strategy names.
        """
        return list(cls._strategies.keys())
