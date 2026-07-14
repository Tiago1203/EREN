"""Retrieval planner for EREN Semantic Retrieval Engine.

Plans retrieval operations based on queries and policies.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.retrieval.exceptions import RetrievalPlanError
from core.retrieval.policies import RetrievalPolicyHandler
from core.retrieval.types import (
    MemorySource,
    RetrievalPlan,
    RetrievalPolicy,
    RetrievalQuery,
    RetrievalStep,
)

if TYPE_CHECKING:
    pass


class RetrievalPlanner:
    """Planner for retrieval operations.

    Responsibilities:
    - Analyze queries
    - Select relevant memories
    - Create execution plans
    - Handle policy application
    """

    def __init__(self):
        """Initialize planner."""
        self._policy_handler = RetrievalPolicyHandler()

    def plan(self, query: RetrievalQuery) -> RetrievalPlan:
        """Create a retrieval plan.

        Args:
            query: Retrieval query.

        Returns:
            Retrieval plan.

        Raises:
            RetrievalPlanError: If planning fails.
        """
        try:
            # Validate query
            self._validate_query(query)

            # Create plan based on policy
            plan = self._policy_handler.create_plan(query)

            # Add query-specific optimizations
            plan = self._optimize_plan(plan)

            return plan

        except Exception as e:
            raise RetrievalPlanError(query.query, str(e))

    def _validate_query(self, query: RetrievalQuery) -> None:
        """Validate a query.

        Args:
            query: Query to validate.

        Raises:
            RetrievalPlanError: If validation fails.
        """
        if not query.query or not query.query.strip():
            raise RetrievalPlanError(query.query, "Query cannot be empty")

        if query.max_results <= 0:
            raise RetrievalPlanError(query.query, "max_results must be positive")

        if query.max_context_tokens <= 0:
            raise RetrievalPlanError(query.query, "max_context_tokens must be positive")

    def _optimize_plan(self, plan: RetrievalPlan) -> RetrievalPlan:
        """Optimize a retrieval plan.

        Args:
            plan: Plan to optimize.

        Returns:
            Optimized plan.
        """
        query = plan.query

        # Add filter steps if filters are present
        if query.filters:
            filter_step = RetrievalStep(
                step_id=f"step_{len(plan.steps)}",
                action="filter",
                source=MemorySource.CONVERSATION,
                priority=0,
            )
            plan.steps.append(filter_step)

        # Add ranking step
        rank_step = RetrievalStep(
            step_id=f"step_{len(plan.steps) + 1}",
            action="rank",
            source=MemorySource.CONVERSATION,
            priority=999,
        )
        plan.steps.append(rank_step)

        # Add context building step
        context_step = RetrievalStep(
            step_id=f"step_{len(plan.steps) + 1}",
            action="build_context",
            source=MemorySource.CONVERSATION,
            priority=1000,
        )
        plan.steps.append(context_step)

        return plan

    def create_trace_id(self) -> str:
        """Create a unique trace ID.

        Returns:
            Trace ID.
        """
        return str(uuid.uuid4())

    def suggest_policy(self, query: str, sources: list[MemorySource]) -> RetrievalPolicy:
        """Suggest a policy for a query.

        Args:
            query: Query string.
            sources: Available sources.

        Returns:
            Suggested policy.
        """
        return self._policy_handler.get_recommended_policy(query, sources)
