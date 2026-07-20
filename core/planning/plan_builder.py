"""Plan Builder for EREN Cognitive Planning Engine.

Builds execution plans from tasks.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.planning.types import (
    ExecutionPlan,
    Goal,
    GoalAnalysis,
    PlanStatus,
    Task,
)

if TYPE_CHECKING:
    pass


class PlanBuilder:
    """Builds execution plans from tasks.

    The Plan Builder does NOT:
    - Execute tasks
    - Query providers
    - Use OpenAI directly

    It ONLY:
    - Combines tasks into plan
    - Calculates estimates
    - Validates plan
    """

    def __init__(self):
        """Initialize plan builder."""
        pass

    def build(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
        tasks: list[Task],
    ) -> ExecutionPlan:
        """Build execution plan.

        Args:
            goal: Goal to achieve.
            analysis: Goal analysis results.
            tasks: Decomposed tasks.

        Returns:
            Execution plan.
        """
        plan_id = str(uuid.uuid4())

        # Calculate estimates
        total_time = sum(t.estimated_time_seconds for t in tasks)
        total_cost = sum(t.estimated_cost for t in tasks)
        total_tokens = sum(t.estimated_tokens for t in tasks)

        # Create plan
        plan = ExecutionPlan(
            plan_id=plan_id,
            goal=goal,
            tasks=tasks,
            status=PlanStatus.CREATED,
            total_estimated_time_seconds=total_time,
            total_estimated_cost=total_cost,
            total_estimated_tokens=total_tokens,
        )

        return plan

    def validate(self, plan: ExecutionPlan) -> tuple[bool, list[str]]:
        """Validate execution plan.

        Args:
            plan: Plan to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        # Check for empty plan
        if not plan.tasks:
            errors.append("Plan has no tasks")

        # Check task IDs are unique
        task_ids = [t.task_id for t in plan.tasks]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Duplicate task IDs detected")

        # Check for self-dependencies
        for task in plan.tasks:
            if task.task_id in task.depends_on:
                errors.append(f"Task {task.task_id} has self-dependency")

        # Check dependency validity
        for task in plan.tasks:
            for dep_id in task.depends_on:
                if dep_id not in task_ids:
                    errors.append(
                        f"Task {task.task_id} depends on unknown task {dep_id}"
                    )

        # Check estimates
        if plan.total_estimated_time_seconds < 0:
            errors.append("Invalid time estimate")

        if plan.total_estimated_cost < 0:
            errors.append("Invalid cost estimate")

        return len(errors) == 0, errors

    def optimize(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize execution plan.

        Args:
            plan: Plan to optimize.

        Returns:
            Optimized plan.
        """
        # Mark plan as validated
        plan.status = PlanStatus.VALIDATED

        return plan

    def finalize(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Finalize execution plan.

        Args:
            plan: Plan to finalize.

        Returns:
            Finalized plan.
        """
        # Mark plan as ready
        plan.status = PlanStatus.READY

        return plan

    def update_progress(
        self,
        plan: ExecutionPlan,
        completed_task_id: str,
        result: any = None,
        error: str = "",
    ) -> ExecutionPlan:
        """Update plan progress.

        Args:
            plan: Plan to update.
            completed_task_id: ID of completed task.
            result: Task result.
            error: Task error if failed.

        Returns:
            Updated plan.
        """
        plan.updated_at = datetime.now(UTC)

        for task in plan.tasks:
            if task.task_id == completed_task_id:
                task.completed_at = datetime.now(UTC)
                task.result = result

                if error:
                    task.status = "failed"
                    task.error = error
                    plan.failed_tasks += 1
                else:
                    task.status = "completed"
                    plan.completed_tasks += 1

                break

        # Check if plan is complete
        if plan.completed_tasks + plan.failed_tasks == len(plan.tasks):
            if plan.failed_tasks == 0:
                plan.status = PlanStatus.COMPLETED
                plan.completed_at = datetime.now(UTC)
            else:
                plan.status = PlanStatus.FAILED

        return plan

    def get_executable_tasks(
        self,
        plan: ExecutionPlan,
    ) -> list[Task]:
        """Get tasks ready for execution.

        Args:
            plan: Plan to analyze.

        Returns:
            List of tasks ready to execute.
        """
        executable = []

        for task in plan.tasks:
            if task.status != "pending":
                continue

            # Check dependencies
            deps_complete = all(
                next(
                    (t for t in plan.tasks if t.task_id == dep_id),
                    None,
                )
                for dep_id in task.depends_on
            )

            if deps_complete:
                executable.append(task)

        return executable
