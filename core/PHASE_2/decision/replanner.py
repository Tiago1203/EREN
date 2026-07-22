"""Replanner for EREN Cognitive Decision Engine.

Handles plan modification and replanning.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_2.decision.types import (
    DecisionPlan,
    DecisionStatus,
    DecisionTask,
    ReplanningReason,
    TaskStatus,
)

if TYPE_CHECKING:
    pass


class Replanner:
    """Handles plan replanning.

    The Replanner does NOT:
    - Execute tasks
    - Make decisions

    It ONLY:
    - Modifies plans
    - Cancels plans
    - Recreates plans
    - Tracks replanning history
    """

    def __init__(self):
        """Initialize replanner."""
        self._replan_history: list[ReplanningReason] = []

    def replan(
        self,
        plan: DecisionPlan,
        reason: str,
        affected_tasks: list[str] | None = None,
    ) -> DecisionPlan:
        """Replan a failed or problematic plan.

        Args:
            plan: Original plan.
            reason: Reason for replanning.
            affected_tasks: Tasks affected.

        Returns:
            New plan.
        """
        affected_tasks = affected_tasks or []

        # Record replanning reason
        replan_reason = ReplanningReason(
            reason=reason,
            affected_tasks=affected_tasks,
            original_plan_id=plan.plan_id,
        )
        self._replan_history.append(replan_reason)

        # Create new plan based on original
        new_plan = DecisionPlan(
            plan_id=str(uuid.uuid4()),
            goal=plan.goal,
            tasks=self._modify_tasks(plan.tasks, affected_tasks),
            strategy=plan.strategy,
            policy=plan.policy,
            status=DecisionStatus.CREATED,
            overall_risk=plan.overall_risk,
            risk_factors=plan.risk_factors,
            total_estimated_time_seconds=plan.total_estimated_time_seconds,
            total_estimated_cost=plan.total_estimated_cost,
            total_estimated_tokens=plan.total_estimated_tokens,
            original_plan_id=plan.plan_id,
            replan_count=plan.replan_count + 1,
        )

        return new_plan

    def cancel_plan(
        self,
        plan: DecisionPlan,
        reason: str,
    ) -> DecisionPlan:
        """Cancel a plan.

        Args:
            plan: Plan to cancel.
            reason: Cancellation reason.

        Returns:
            Cancelled plan.
        """
        plan.status = DecisionStatus.CANCELLED
        plan.completed_at = datetime.now(UTC)
        plan.metadata["cancellation_reason"] = reason
        plan.metadata["cancelled_at"] = datetime.now(UTC).isoformat()

        return plan

    def pause_plan(self, plan: DecisionPlan) -> DecisionPlan:
        """Pause a plan.

        Args:
            plan: Plan to pause.

        Returns:
            Paused plan.
        """
        # Mark pending tasks as skipped
        for task in plan.tasks:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.SKIPPED

        plan.metadata["paused_at"] = datetime.now(UTC).isoformat()
        return plan

    def resume_plan(self, plan: DecisionPlan) -> DecisionPlan:
        """Resume a paused plan.

        Args:
            plan: Plan to resume.

        Returns:
            Resumed plan.
        """
        # Restore skipped tasks to pending
        for task in plan.tasks:
            if task.status == TaskStatus.SKIPPED:
                task.status = TaskStatus.PENDING

        plan.metadata["resumed_at"] = datetime.now(UTC).isoformat()
        return plan

    def modify_task(
        self,
        plan: DecisionPlan,
        task_id: str,
        modifications: dict,
    ) -> DecisionPlan:
        """Modify a task in the plan.

        Args:
            plan: Plan containing task.
            task_id: Task to modify.
            modifications: Changes to apply.

        Returns:
            Modified plan.
        """
        task = plan.get_task(task_id)
        if task:
            for key, value in modifications.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now(UTC)

        plan.updated_at = datetime.now(UTC)
        return plan

    def add_task(
        self,
        plan: DecisionPlan,
        task: DecisionTask,
        after_task_id: str | None = None,
    ) -> DecisionPlan:
        """Add a task to the plan.

        Args:
            plan: Plan to add to.
            task: Task to add.
            after_task_id: Add after this task.

        Returns:
            Modified plan.
        """
        if after_task_id:
            # Find index and insert
            for i, t in enumerate(plan.tasks):
                if t.task_id == after_task_id:
                    plan.tasks.insert(i + 1, task)
                    break
            else:
                plan.tasks.append(task)
        else:
            plan.tasks.append(task)

        plan.updated_at = datetime.now(UTC)
        return plan

    def remove_task(
        self,
        plan: DecisionPlan,
        task_id: str,
    ) -> DecisionPlan:
        """Remove a task from the plan.

        Args:
            plan: Plan to modify.
            task_id: Task to remove.

        Returns:
            Modified plan.
        """
        # Remove task
        plan.tasks = [t for t in plan.tasks if t.task_id != task_id]

        # Remove from dependencies
        for task in plan.tasks:
            if task_id in task.depends_on:
                task.depends_on.remove(task_id)

        plan.updated_at = datetime.now(UTC)
        return plan

    def skip_task(
        self,
        plan: DecisionPlan,
        task_id: str,
        reason: str,
    ) -> DecisionPlan:
        """Skip a task.

        Args:
            plan: Plan containing task.
            task_id: Task to skip.
            reason: Skip reason.

        Returns:
            Modified plan.
        """
        task = plan.get_task(task_id)
        if task:
            task.status = TaskStatus.SKIPPED
            task.error = reason
            task.completed_at = datetime.now(UTC)
            task.metadata["skipped_reason"] = reason

        plan.updated_at = datetime.now(UTC)
        return plan

    def retry_task(
        self,
        plan: DecisionPlan,
        task_id: str,
    ) -> DecisionPlan:
        """Retry a failed task.

        Args:
            plan: Plan containing task.
            task_id: Task to retry.

        Returns:
            Modified plan.
        """
        task = plan.get_task(task_id)
        if task:
            task.status = TaskStatus.PENDING
            task.retries += 1
            task.error = ""
            task.started_at = None
            task.completed_at = None
            task.result = None

        plan.updated_at = datetime.now(UTC)
        return plan

    def _modify_tasks(
        self,
        tasks: list[DecisionTask],
        affected_task_ids: list[str],
    ) -> list[DecisionTask]:
        """Modify tasks for replanning."""
        modified = []

        for task in tasks:
            # Create new task
            new_task = DecisionTask(
                task_id=str(uuid.uuid4()) if task.task_id in affected_task_ids else task.task_id,
                name=task.name,
                description=task.description,
                task_type=task.task_type,
                capability=task.capability,
                status=TaskStatus.PENDING if task.task_id in affected_task_ids else task.status,
                priority=task.priority,
                depends_on=[],  # Reset dependencies for affected tasks
                dependency_type=task.dependency_type,
                input_schema=task.input_schema,
                output_schema=task.output_schema,
                estimated_time_seconds=task.estimated_time_seconds,
                estimated_cost=task.estimated_cost,
                estimated_tokens=task.estimated_tokens,
                risk_level=task.risk_level,
                retries=0,  # Reset retries
            )

            modified.append(new_task)

        return modified

    def get_replan_history(
        self,
        plan_id: str | None = None,
    ) -> list[ReplanningReason]:
        """Get replanning history.

        Args:
            plan_id: Filter by original plan ID.

        Returns:
            List of replanning reasons.
        """
        if plan_id:
            return [r for r in self._replan_history if r.original_plan_id == plan_id]
        return self._replan_history
