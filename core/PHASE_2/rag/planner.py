"""RAG Retrieval Planner for EREN OS.

Plans retrieval strategy based on query analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.PHASE_2.rag.types import (
    RAGQuery,
    RetrievalStrategy,
)

if TYPE_CHECKING:
    from core.PHASE_2.memory import MemoryCoordinator
    from core.PHASE_2.retrieval import RetrievalEngine


class RetrievalPlanner:
    """Plans retrieval strategy for RAG queries.

    Analyzes query and determines optimal retrieval approach.
    """

    def __init__(self):
        """Initialize retrieval planner."""
        # Keywords for different strategies
        self._semantic_keywords = [
            "explain", "describe", "what is", "how does",
            "concept", "understand", "meaning", "difference",
        ]
        self._keyword_keywords = [
            "list", "find", "search", "show", "get",
            "specific", "exact", "name", "number",
        ]
        self._graph_keywords = [
            "relationship", "related", "connected", "compared",
            "versus", "vs", "compared to", "related to",
        ]

    async def plan_retrieval(
        self,
        query: RAGQuery,
        retrieval_engine: RetrievalEngine | None = None,
        memory_coordinator: MemoryCoordinator | None = None,
    ) -> RetrievalPlan:
        """Plan retrieval strategy.

        Args:
            query: RAG query.
            retrieval_engine: Optional retrieval engine.
            memory_coordinator: Optional memory coordinator.

        Returns:
            Retrieval plan.
        """
        # Analyze query
        strategy = self._analyze_strategy(query.question)
        top_k = self._determine_top_k(query.question)
        filters = self._build_filters(query)

        return RetrievalPlan(
            query=query,
            strategy=strategy,
            top_k=top_k,
            filters=filters,
            use_memory=await self._should_use_memory(query, memory_coordinator),
            use_knowledge=await self._should_use_knowledge(query),
        )

    def _analyze_strategy(self, question: str) -> RetrievalStrategy:
        """Analyze question to determine best strategy."""
        question_lower = question.lower()

        # Check for graph queries
        for keyword in self._graph_keywords:
            if keyword in question_lower:
                return RetrievalStrategy.GRAPH

        # Check for keyword queries
        for keyword in self._keyword_keywords:
            if keyword in question_lower:
                return RetrievalStrategy.KEYWORD

        # Default to semantic
        return RetrievalStrategy.SEMANTIC

    def _determine_top_k(self, question: str) -> int:
        """Determine optimal top_k based on question complexity."""
        question_lower = question.lower()
        words = len(question_lower.split())

        # Simple questions need fewer chunks
        if words < 10:
            return 5

        # Medium complexity
        if words < 30:
            return 10

        # Complex questions need more context
        return 15

    def _build_filters(self, query: RAGQuery) -> dict:
        """Build filters for retrieval."""
        filters = {}

        # Add any context-based filters
        if query.context:
            if "medical_specialty" in query.context:
                filters["medical_specialty"] = query.context["medical_specialty"]
            if "language" in query.context:
                filters["language"] = query.context["language"]
            if "tags" in query.context:
                filters["tags"] = query.context["tags"]

        return filters

    async def _should_use_memory(
        self,
        query: RAGQuery,
        memory_coordinator: MemoryCoordinator | None,
    ) -> bool:
        """Determine if memory should be used."""
        if not memory_coordinator:
            return False

        # Use memory for conversational queries
        conversation_keywords = [
            "previous", "before", "earlier", "mentioned",
            "continued", "following", "also", "additionally",
        ]

        question_lower = query.question.lower()
        for keyword in conversation_keywords:
            if keyword in question_lower:
                return True

        # Use memory if conversation_id provided
        if query.conversation_id:
            return True

        return False

    async def _should_use_knowledge(self, query: RAGQuery) -> bool:
        """Determine if knowledge base should be used."""
        # Always use knowledge base for RAG
        return True


@dataclass
class RetrievalPlan:
    """Plan for retrieval execution."""

    query: RAGQuery
    strategy: RetrievalStrategy
    top_k: int
    filters: dict
    use_memory: bool = False
    use_knowledge: bool = True

    # Optimizations
    deduplicate: bool = True
    rerank: bool = True
    filter_low_relevance: bool = True
    min_relevance_score: float = 0.5
