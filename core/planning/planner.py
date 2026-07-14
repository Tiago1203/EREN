"""Cognitive Planning Engine (CPE) for EREN OS.

Main planning engine that transforms user intent into execution plans.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from core.planning.dependency_resolver import DependencyResolver
from core.planning.goal_analyzer import GoalAnalyzer
from core.planning.plan_builder import PlanBuilder
from core.planning.task_decomposer import TaskDecomposer
from core.planning.types import (
    ExecutionPlan,
    PlanningMetrics,
    PlanStatus,
    Task,
)

if TYPE_CHECKING:
    pass


class CognitivePlanningEngine:
    """Cognitive Planning Engine.

    The Planning Engine does NOT:
    - Execute tasks
    - Query providers
    - Use OpenAI directly
    - Consult memory
    - Consult retrieval

    It ONLY:
    - Analyzes goals
    - Decomposes into tasks
    - Resolves dependencies
    - Builds execution plans

    Philosophy:
        LLM responds.
        Planning Engine decides what to do.
        Never executes tasks.
        Never queries providers.
        Never uses OpenAI directly.
        Only generates plans.
    """

    def __init__(self):
        """Initialize planning engine."""
        # Components
        self._goal_analyzer = GoalAnalyzer()
        self._task_decomposer = TaskDecomposer()
        self._dependency_resolver = DependencyResolver()
        self._plan_builder = PlanBuilder()

        # Metrics
        self._metrics = PlanningMetrics()

    def plan(
        self,
        user_intent: str,
        context: dict | None = None,
    ) -> ExecutionPlan:
        """Create execution plan from user intent.

        This is the main entry point for planning.

        Args:
            user_intent: User's intent or question.
            context: Additional context.

        Returns:
            ExecutionPlan ready for execution.
        """
        start_time = time.time()

        # Step 1: Analyze goal
        analysis = self._goal_analyzer.analyze(user_intent, context)
        goal = analysis.goal

        # Step 2: Decompose into tasks
        tasks = self._task_decomposer.decompose(goal, analysis)

        # Step 3: Resolve dependencies
        ordered_tasks = self._dependency_resolver.resolve(tasks)

        # Step 4: Build plan
        plan = self._plan_builder.build(goal, analysis, ordered_tasks)

        # Step 5: Validate
        is_valid, errors = self._plan_builder.validate(plan)
        if not is_valid:
            # Try to fix common issues
            plan = self._fix_plan(plan, errors)

        # Step 6: Optimize
        plan = self._plan_builder.optimize(plan)

        # Step 7: Finalize
        plan = self._plan_builder.finalize(plan)

        # Update metrics
        planning_time = (time.time() - start_time) * 1000
        self._update_metrics(plan, planning_time)

        return plan

    def _fix_plan(self, plan: ExecutionPlan, errors: list[str]) -> ExecutionPlan:
        """Attempt to fix plan errors.

        Args:
            plan: Plan with errors.
            errors: Error messages.

        Returns:
            Fixed plan.
        """
        # Remove invalid dependencies
        task_ids = {t.task_id for t in plan.tasks}
        for task in plan.tasks:
            task.depends_on = [
                dep_id for dep_id in task.depends_on
                if dep_id in task_ids and dep_id != task.task_id
            ]

        # Re-resolve dependencies
        plan.tasks = self._dependency_resolver.resolve(plan.tasks)

        return plan

    def _update_metrics(self, plan: ExecutionPlan, planning_time_ms: float) -> None:
        """Update planning metrics.

        Args:
            plan: Created plan.
            planning_time_ms: Planning duration in ms.
        """
        self._metrics.plans_created += 1
        self._metrics.total_tasks += len(plan.tasks)

        if plan.status == PlanStatus.COMPLETED:
            self._metrics.plans_completed += 1
        elif plan.status == PlanStatus.FAILED:
            self._metrics.plans_failed += 1

        # Update averages
        total_plans = self._metrics.plans_created
        self._metrics.avg_planning_time_ms = (
            (self._metrics.avg_planning_time_ms * (total_plans - 1) + planning_time_ms)
            / total_plans
        )
        self._metrics.avg_tasks_per_plan = (
            (self._metrics.avg_tasks_per_plan * (total_plans - 1) + len(plan.tasks))
            / total_plans
        )

        # Success rate
        if self._metrics.plans_created > 0:
            self._metrics.success_rate = (
                self._metrics.plans_completed / self._metrics.plans_created
            )

        # By goal type
        goal_type = plan.goal.goal_type.value
        self._metrics.by_goal_type[goal_type] = (
            self._metrics.by_goal_type.get(goal_type, 0) + 1
        )

    def get_metrics(self) -> PlanningMetrics:
        """Get planning metrics.

        Returns:
            Current metrics.
        """
        return self._metrics

    def validate_plan(self, plan: ExecutionPlan) -> tuple[bool, list[str]]:
        """Validate an execution plan.

        Args:
            plan: Plan to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        return self._plan_builder.validate(plan)

    def get_executable_tasks(self, plan: ExecutionPlan) -> list[Task]:
        """Get tasks ready for execution.

        Args:
            plan: Plan to analyze.

        Returns:
            Tasks ready to execute.
        """
        return self._plan_builder.get_executable_tasks(plan)

    def update_plan_progress(
        self,
        plan: ExecutionPlan,
        completed_task_id: str,
        result: any = None,
        error: str = "",
    ) -> ExecutionPlan:
        """Update plan progress after task completion.

        Args:
            plan: Plan to update.
            completed_task_id: ID of completed task.
            result: Task result.
            error: Task error if failed.

        Returns:
            Updated plan.
        """
        return self._plan_builder.update_progress(
            plan, completed_task_id, result, error
        )


# Global planner instance
_global_planner: CognitivePlanningEngine | None = None
_planner_lock = __import__("threading").Lock()


def get_planning_engine() -> CognitivePlanningEngine:
    """Get the global planning engine.

    Returns:
        Global CognitivePlanningEngine instance.
    """
    global _global_planner
    with _planner_lock:
        if _global_planner is None:
            _global_planner = CognitivePlanningEngine()
        return _global_planner


def reset_planning_engine() -> None:
    """Reset the global planning engine."""
    global _global_planner
    with _planner_lock:
        _global_planner = None
