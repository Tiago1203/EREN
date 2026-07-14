"""Retrieval policies for EREN Semantic Retrieval Engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.retrieval.types import (
    RetrievalPolicy,
    RetrievalQuery,
    RetrievalPlan,
    RetrievalStep,
    MemorySource,
)

if TYPE_CHECKING:
    pass


class RetrievalPolicyHandler:
    """Handler for retrieval policies.

    Converts policies into execution plans.
    """

    # Priority order for memory sources
    DEFAULT_PRIORITIES = {
        MemorySource.VECTOR: 1,
        MemorySource.SEMANTIC: 2,
        MemorySource.CONVERSATION: 3,
        MemorySource.CLINICAL: 4,
        MemorySource.DEVICE: 5,
        MemorySource.WORKING: 6,
        MemorySource.LONG_TERM: 7,
    }

    # Clinical priority order
    CLINICAL_PRIORITIES = {
        MemorySource.CLINICAL: 1,
        MemorySource.VECTOR: 2,
        MemorySource.SEMANTIC: 3,
        MemorySource.CONVERSATION: 4,
        MemorySource.DEVICE: 5,
        MemorySource.WORKING: 6,
        MemorySource.LONG_TERM: 7,
    }

    # Device priority order
    DEVICE_PRIORITIES = {
        MemorySource.DEVICE: 1,
        MemorySource.VECTOR: 2,
        MemorySource.SEMANTIC: 3,
        MemorySource.CLINICAL: 4,
        MemorySource.CONVERSATION: 5,
        MemorySource.WORKING: 6,
        MemorySource.LONG_TERM: 7,
    }

    @classmethod
    def create_plan(cls, query: RetrievalQuery) -> RetrievalPlan:
        """Create a retrieval plan based on policy.

        Args:
            query: Retrieval query.

        Returns:
            Retrieval plan.
        """
        # Determine sources to use
        sources = query.sources or list(MemorySource)

        # Determine priorities based on policy
        if query.policy == RetrievalPolicy.CLINICAL_PRIORITY:
            priorities = cls.CLINICAL_PRIORITIES
        elif query.policy == RetrievalPolicy.DEVICE_PRIORITY:
            priorities = cls.DEVICE_PRIORITIES
        else:
            priorities = cls.DEFAULT_PRIORITIES

        # Filter sources
        available_sources = [s for s in sources if s in priorities]

        # Create steps
        steps = []
        for i, source in enumerate(available_sources):
            step = RetrievalStep(
                step_id=f"step_{i}",
                action="retrieve",
                source=source,
                priority=priorities.get(source, 99),
            )
            steps.append(step)

        # Sort by priority
        steps.sort(key=lambda s: s.priority)

        # Estimate execution time based on policy
        estimated_time = cls._estimate_time(query.policy, len(steps))

        return RetrievalPlan(
            query=query,
            steps=steps,
            estimated_time_ms=estimated_time,
            estimated_results=query.max_results,
        )

    @classmethod
    def _estimate_time(cls, policy: RetrievalPolicy, num_sources: int) -> int:
        """Estimate execution time.

        Args:
            policy: Retrieval policy.
            num_sources: Number of sources.

        Returns:
            Estimated time in milliseconds.
        """
        base_times = {
            RetrievalPolicy.FASTEST: 50,
            RetrievalPolicy.BEST_MATCH: 200,
            RetrievalPolicy.MERGE_ALL: 300,
            RetrievalPolicy.VECTOR_FIRST: 150,
            RetrievalPolicy.SEMANTIC_FIRST: 150,
            RetrievalPolicy.HYBRID: 250,
            RetrievalPolicy.CLINICAL_PRIORITY: 200,
            RetrievalPolicy.DEVICE_PRIORITY: 200,
        }
        base = base_times.get(policy, 200)
        return base * num_sources

    @classmethod
    def get_policy_description(cls, policy: RetrievalPolicy) -> str:
        """Get policy description.

        Args:
            policy: Policy to describe.

        Returns:
            Description string.
        """
        descriptions = {
            RetrievalPolicy.FASTEST: "Prioritize speed. Query fastest memories first.",
            RetrievalPolicy.BEST_MATCH: "Prioritize relevance. Query all sources and rank by relevance.",
            RetrievalPolicy.MERGE_ALL: "Merge results from all sources.",
            RetrievalPolicy.VECTOR_FIRST: "Query vector memories first for semantic matches.",
            RetrievalPolicy.SEMANTIC_FIRST: "Query semantic memories first for knowledge.",
            RetrievalPolicy.HYBRID: "Combine vector and semantic search.",
            RetrievalPolicy.CLINICAL_PRIORITY: "Prioritize clinical information.",
            RetrievalPolicy.DEVICE_PRIORITY: "Prioritize device information.",
        }
        return descriptions.get(policy, "Default retrieval policy.")

    @classmethod
    def get_recommended_policy(
        cls,
        query_type: str,
        sources: list[MemorySource],
    ) -> RetrievalPolicy:
        """Get recommended policy for query type.

        Args:
            query_type: Type of query (e.g., "medical", "device", "conversation").
            sources: Available memory sources.

        Returns:
            Recommended policy.
        """
        query_lower = query_type.lower()

        if "clinical" in query_lower or "medical" in query_lower:
            if MemorySource.CLINICAL in sources:
                return RetrievalPolicy.CLINICAL_PRIORITY
        elif "device" in query_lower or "sensor" in query_lower:
            if MemorySource.DEVICE in sources:
                return RetrievalPolicy.DEVICE_PRIORITY
        elif "conversation" in query_lower or "chat" in query_lower:
            return RetrievalPolicy.SEMANTIC_FIRST
        elif "what" in query_lower or "who" in query_lower or "how" in query_lower:
            return RetrievalPolicy.BEST_MATCH

        return RetrievalPolicy.FASTEST
