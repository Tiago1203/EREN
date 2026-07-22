"""Semantic Retrieval Engine for EREN OS.

The main engine for retrieving relevant knowledge from memory systems.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.PHASE_2.retrieval.context_builder import ContextBuilder
from core.PHASE_2.retrieval.events import RetrievalEvent, get_retrieval_event_bus
from core.PHASE_2.retrieval.metrics import get_retrieval_metrics
from core.PHASE_2.retrieval.planner import RetrievalPlanner
from core.PHASE_2.retrieval.ranker import ResultRanker
from core.PHASE_2.retrieval.registry import RetrievalRegistry, get_retrieval_registry
from core.PHASE_2.retrieval.strategy import (
    FastestStrategy,
    ParallelStrategy,
    SequentialStrategy,
)
from core.PHASE_2.retrieval.trace import RetrievalTracer, get_retrieval_tracer
from core.PHASE_2.retrieval.types import (
    MemorySource,
    RetrievalPlan,
    RetrievalPolicy,
    RetrievalQuery,
    RetrievalResponse,
)

if TYPE_CHECKING:
    pass


class SemanticRetrievalEngine:
    """Semantic Retrieval Engine for EREN.

    Responsibilities:
    - Plan searches
    - Select relevant memories
    - Execute parallel searches
    - Combine results
    - Remove duplicates
    - Rank results
    - Build context for LLM

    The engine NEVER knows:
    - PostgreSQL
    - SQLite
    - Chroma
    - Qdrant
    - Pinecone
    - FAISS
    - Milvus
    - Redis

    It only knows contracts.
    """

    def __init__(
        self,
        registry: RetrievalRegistry | None = None,
        planner: RetrievalPlanner | None = None,
        ranker: ResultRanker | None = None,
        context_builder: ContextBuilder | None = None,
    ):
        """Initialize retrieval engine.

        Args:
            registry: Retrieval registry.
            planner: Retrieval planner.
            ranker: Result ranker.
            context_builder: Context builder.
        """
        self._registry = registry or get_retrieval_registry()
        self._planner = planner or RetrievalPlanner()
        self._ranker = ranker or ResultRanker()
        self._context_builder = context_builder or ContextBuilder()

        self._metrics = get_retrieval_metrics()
        self._events = get_retrieval_event_bus()
        self._tracer = get_retrieval_tracer()

    def retrieve(self, query: RetrievalQuery) -> RetrievalResponse:
        """Retrieve relevant information.

        Args:
            query: Retrieval query.

        Returns:
            Retrieval response.

        Raises:
            RetrievalError: If retrieval fails.
        """
        start_time = time.time()
        trace = self._tracer.create_trace(query.query)

        try:
            # Emit query received event
            self._events.publish(RetrievalEvent.QUERY_RECEIVED, {"query": query.query})

            # Create plan
            self._events.publish(RetrievalEvent.PLANNING_STARTED, {"query": query.query})
            plan = self._planner.plan(query)
            trace.add_step({"action": "planning", "duration_ms": 0})
            self._events.publish(RetrievalEvent.PLANNING_COMPLETED, {"plan": plan.to_dict()})

            # Execute retrieval
            self._events.publish(RetrievalEvent.RETRIEVAL_STARTED, {"plan": plan.to_dict()})
            response = self._execute_plan(plan, trace)
            self._events.publish(RetrievalEvent.RETRIEVAL_COMPLETED, {"results": len(response.results)})

            # Rank results
            if response.results:
                self._events.publish(RetrievalEvent.RANKING_STARTED, {"count": len(response.results)})
                ranked = self._ranker.rank(response.results, query)
                response.results = ranked
                self._events.publish(RetrievalEvent.RANKING_COMPLETED, {"ranked": len(ranked)})

            # Calculate execution time
            response.execution_time_ms = int((time.time() - start_time) * 1000)
            trace.finish()

            # Record metrics
            self._metrics.record_query(
                success=response.success,
                latency_ms=response.execution_time_ms,
                num_results=response.total_results,
                policy=query.policy,
            )

            # Emit completion event
            self._events.publish(RetrievalEvent.QUERY_COMPLETED, {"response": response.to_dict()})

            return response

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            trace.add_error(str(e))
            trace.finish()

            self._events.publish(RetrievalEvent.QUERY_FAILED, {"error": str(e)})

            return RetrievalResponse(
                results=[],
                query=query.query,
                policy_used=query.policy,
                execution_time_ms=execution_time_ms,
                success=False,
                error=str(e),
            )

    def _execute_plan(
        self,
        plan: RetrievalPlan,
        trace: RetrievalTracer,
    ) -> RetrievalResponse:
        """Execute a retrieval plan.

        Args:
            plan: Retrieval plan.
            trace: Trace for logging.

        Returns:
            Retrieval response.
        """
        # Get strategy based on policy
        strategy = self._get_strategy(plan.query.policy)

        # Get providers
        providers = self._get_providers(plan)

        # Execute
        response = strategy.execute(plan.query, plan, providers)

        trace.add_step({
            "action": "execution",
            "sources": [s.value for s in response.sources_queried],
            "results": len(response.results),
        })

        return response

    def _get_strategy(self, policy: RetrievalPolicy):
        """Get strategy for policy.

        Args:
            policy: Retrieval policy.

        Returns:
            Retrieval strategy.
        """
        strategy_map = {
            RetrievalPolicy.FASTEST: FastestStrategy(),
            RetrievalPolicy.SEQUENTIAL: SequentialStrategy(),
            RetrievalPolicy.PARALLEL: ParallelStrategy(),
            RetrievalPolicy.MERGE_ALL: SequentialStrategy(),  # Use sequential for merge
        }

        return strategy_map.get(policy, ParallelStrategy())

    def _get_providers(
        self,
        plan: RetrievalPlan,
    ) -> dict[MemorySource, Callable]:
        """Get memory providers.

        Args:
            plan: Retrieval plan.

        Returns:
            Dictionary of providers by source.
        """
        providers = {}
        for step in plan.steps:
            if step.action == "retrieve":
                provider = self._registry.get_memory_provider(step.source)
                if provider:
                    providers[step.source] = provider

        return providers

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def retrieve_text(
        self,
        query: str,
        sources: list[MemorySource] | None = None,
        max_results: int = 10,
    ) -> str:
        """Retrieve as text.

        Args:
            query: Query string.
            sources: Memory sources.
            max_results: Maximum results.

        Returns:
            Context string.
        """
        retrieval_query = RetrievalQuery(
            query=query,
            sources=sources,
            max_results=max_results,
        )
        response = self.retrieve(retrieval_query)
        return response.content

    def retrieve_with_context(
        self,
        query: str,
        sources: list[MemorySource] | None = None,
        max_context_tokens: int = 4000,
    ) -> tuple[str, RetrievalResponse]:
        """Retrieve with full response.

        Args:
            query: Query string.
            sources: Memory sources.
            max_context_tokens: Max context tokens.

        Returns:
            Tuple of (context, response).
        """
        retrieval_query = RetrievalQuery(
            query=query,
            sources=sources,
            max_context_tokens=max_context_tokens,
        )
        response = self.retrieve(retrieval_query)
        context = self._context_builder.build(response.results, retrieval_query)
        return context, response

    # =========================================================================
    # Registry Management
    # =========================================================================

    def register_memory_provider(
        self,
        source: MemorySource,
        provider: Callable,
    ) -> None:
        """Register a memory provider.

        Args:
            source: Memory source.
            provider: Provider callable.
        """
        self._registry.register_memory_provider(source, provider)

    def get_metrics(self) -> dict:
        """Get metrics.

        Returns:
            Metrics dictionary.
        """
        return self._metrics.to_dict()

    def get_status(self) -> dict:
        """Get engine status.

        Returns:
            Status dictionary.
        """
        return {
            "registered_sources": [s.value for s in self._registry.list_memory_sources()],
            "metrics": self._metrics.to_dict(),
        }


# Global engine instance
_global_engine: SemanticRetrievalEngine | None = None
_engine_lock = threading.Lock()


def get_retrieval_engine() -> SemanticRetrievalEngine:
    """Get the global retrieval engine.

    Returns:
        Global SemanticRetrievalEngine instance.
    """
    global _global_engine
    with _engine_lock:
        if _global_engine is None:
            _global_engine = SemanticRetrievalEngine()
        return _global_engine


def reset_retrieval_engine() -> None:
    """Reset the global engine."""
    global _global_engine
    with _engine_lock:
        _global_engine = None
