"""Knowledge Router for the Cognitive Knowledge Engine.

Routes knowledge queries to appropriate sources based on query type.

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .knowledge_registry import KnowledgeRegistry
from .knowledge_types import (
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeRoute,
    KnowledgeSource,
    QueryType,
    ResultConfidence,
    ResultRelevance,
    SOURCE_QUERY_MAPPING,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Routing Strategy
# =============================================================================


class RoutingStrategy:
    """Base routing strategy."""

    def select_sources(
        self,
        query: KnowledgeQuery,
        available_sources: list[KnowledgeSource],
    ) -> list[KnowledgeSource]:
        """Select sources based on strategy.
        
        Args:
            query: The query to route.
            available_sources: Sources available.
            
        Returns:
            Selected sources in priority order.
        """
        raise NotImplementedError


class ExhaustiveRouting(RoutingStrategy):
    """Route to all relevant sources."""

    def select_sources(
        self,
        query: KnowledgeQuery,
        available_sources: list[KnowledgeSource],
    ) -> list[KnowledgeSource]:
        """Select all sources that support this query type."""
        selected = []
        for source in available_sources:
            if source.supports_query_type(query.query_type):
                selected.append(source)
        return selected


class PriorityRouting(RoutingStrategy):
    """Route to highest priority sources first."""

    def select_sources(
        self,
        query: KnowledgeQuery,
        available_sources: list[KnowledgeSource],
    ) -> list[KnowledgeSource]:
        """Select sources by priority (clinical > technical > operational)."""
        priority_order = {
            QueryType.DIAGNOSTIC: 0,
            QueryType.CLINICAL_PROCEDURE: 0,
            QueryType.SAFETY: 1,
            QueryType.TROUBLESHOOTING: 2,
            QueryType.MAINTENANCE: 3,
            QueryType.TECHNICAL_SPECIFICATION: 4,
            QueryType.COMPLIANCE: 5,
            QueryType.GENERAL: 6,
        }

        def source_priority(source: KnowledgeSource) -> tuple[int, int]:
            # First by query type priority
            q_type_priority = priority_order.get(query.query_type, 99)
            # Then by registration order
            return (q_type_priority, 0)

        supported = [s for s in available_sources if s.supports_query_type(query.query_type)]
        return sorted(supported, key=source_priority)


class MinimumRouting(RoutingStrategy):
    """Route to minimum number of sources needed."""

    def select_sources(
        self,
        query: KnowledgeQuery,
        available_sources: list[KnowledgeSource],
    ) -> list[KnowledgeSource]:
        """Select only essential sources (max 3)."""
        selected = []
        for source in available_sources:
            if source.supports_query_type(query.query_type):
                if len(selected) < 3:
                    selected.append(source)
        return selected


# =============================================================================
# Routing Decision
# =============================================================================


@dataclass(frozen=True)
class RoutingDecision:
    """Record of a routing decision."""

    decision_id: str
    query_id: str
    query_type: str
    selected_sources: tuple[str, ...]
    rejected_sources: tuple[str, ...]
    reason: str
    strategy: str
    timestamp: str


# =============================================================================
# Knowledge Router
# =============================================================================


class KnowledgeRouter:
    """Routes knowledge queries to appropriate sources.

    The router does NOT know about concrete source implementations.
    It only knows about source capabilities through contracts.
    """

    def __init__(
        self,
        registry: KnowledgeRegistry | None = None,
        strategy: RoutingStrategy | None = None,
    ) -> None:
        """Initialize the router.

        Args:
            registry: Knowledge registry.
            strategy: Routing strategy.
        """
        self._registry = registry or KnowledgeRegistry()
        self._strategy = strategy or PriorityRouting()
        self._routing_history: list[RoutingDecision] = []

    def set_strategy(self, strategy: RoutingStrategy) -> None:
        """Set the routing strategy.

        Args:
            strategy: New routing strategy.
        """
        self._strategy = strategy

    def get_sources_for_query(self, query: KnowledgeQuery) -> list[KnowledgeSource]:
        """Get sources suitable for a query.

        Args:
            query: The knowledge query.

        Returns:
            List of suitable sources.
        """
        all_sources = self._registry.get_all_sources()
        return self._strategy.select_sources(query, all_sources)

    async def route_query(
        self,
        query: KnowledgeQuery,
        sources: list[KnowledgeSource],
    ) -> list[KnowledgeResult]:
        """Route query to sources and collect results.

        Args:
            query: The query to route.
            sources: Sources to query.

        Returns:
            Combined results from all sources.
        """
        all_results: list[KnowledgeResult] = []
        all_source_ids = [s.source_id for s in self._registry.get_all_sources()]

        for source in sources:
            try:
                results = await source.query(query)
                all_results.extend(results)
            except Exception:
                # Log error but continue
                pass

        # Rank results
        ranked = self._rank_results(all_results)

        # Record routing decision
        self._record_decision(
            query_id=query.query_id,
            query_type=query.query_type.value,
            selected=[s.source_id for s in sources],
            rejected=[sid for sid in all_source_ids if sid not in [s.source_id for s in sources]],
            strategy=self._strategy.__class__.__name__,
        )

        return ranked

    def _rank_results(self, results: list[KnowledgeResult]) -> list[KnowledgeResult]:
        """Rank results by relevance and confidence.

        Args:
            results: Results to rank.

        Returns:
            Ranked results.
        """
        # Relevance priority
        relevance_priority = {
            ResultRelevance.HIGHLY_RELEVANT: 0,
            ResultRelevance.RELEVANT: 1,
            ResultRelevance.PARTIALLY_RELEVANT: 2,
            ResultRelevance.NOT_RELEVANT: 3,
        }

        # Confidence priority
        confidence_priority = {
            ResultConfidence.HIGH: 0,
            ResultConfidence.MEDIUM: 1,
            ResultConfidence.LOW: 2,
            ResultConfidence.UNKNOWN: 3,
        }

        def result_score(r: KnowledgeResult) -> tuple[int, int]:
            return (
                relevance_priority.get(r.relevance, 99),
                confidence_priority.get(r.confidence, 99),
            )

        return sorted(results, key=result_score)

    def _record_decision(
        self,
        query_id: str,
        query_type: str,
        selected: list[str],
        rejected: list[str],
        strategy: str,
    ) -> None:
        """Record a routing decision.

        Args:
            query_id: Query ID.
            query_type: Type of query.
            selected: Selected source IDs.
            rejected: Rejected source IDs.
            strategy: Strategy used.
        """
        decision = RoutingDecision(
            decision_id=f"rd_{uuid.uuid4().hex[:16]}",
            query_id=query_id,
            query_type=query_type,
            selected_sources=tuple(selected),
            rejected_sources=tuple(rejected),
            reason=self._explain_decision(query_type, selected, strategy),
            strategy=strategy,
            timestamp="",  # Will be set by dataclass
        )
        self._routing_history.append(decision)

    def _explain_decision(
        self,
        query_type: str,
        selected: list[str],
        strategy: str,
    ) -> str:
        """Explain routing decision.

        Args:
            query_type: Query type.
            selected: Selected sources.
            strategy: Strategy used.

        Returns:
            Human-readable explanation.
        """
        return f"Query type '{query_type}' routed using {strategy} strategy to {len(selected)} sources"

    def get_routing_decision(self, query: KnowledgeQuery) -> dict[str, Any]:
        """Get routing decision for a query.

        Args:
            query: The query.

        Returns:
            Routing decision details.
        """
        sources = self.get_sources_for_query(query)
        return {
            "query_type": query.query_type.value,
            "sources_selected": [s.source_id for s in sources],
            "strategy": self._strategy.__class__.__name__,
            "source_count": len(sources),
        }

    def get_routing_history(self) -> list[RoutingDecision]:
        """Get routing decision history."""
        return list(self._routing_history)

    def clear_history(self) -> None:
        """Clear routing history."""
        self._routing_history.clear()
