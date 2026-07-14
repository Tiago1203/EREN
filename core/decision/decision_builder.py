"""Decision Builder for EREN Cognitive Decision Engine.

Builds final decision plans from components.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.decision.types import (
    Goal,
    GoalAnalysis,
    DecisionTask,
    DecisionPlan,
    DecisionStatus,
    DecisionStrategy,
    ExecutionPolicy,
    RiskLevel,
    RiskAssessment,
    ExecutionDecision,
    StrategySelection,
)

if TYPE_CHECKING:
    pass


class DecisionBuilder:
    """Builds decision plans.

    The Decision Builder does NOT:
    - Execute tasks
    - Make decisions

    It ONLY:
    - Combines all components
    - Validates plans
    - Finalizes decisions
    """

    def __init__(self):
        """Initialize decision builder."""
        pass

    def build(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
        tasks: list[DecisionTask],
        strategy_selection: StrategySelection,
        risk_assessment: RiskAssessment,
        execution_decision: ExecutionDecision,
    ) -> DecisionPlan:
        """Build final decision plan.

        Args:
            goal: Goal to achieve.
            analysis: Goal analysis.
            tasks: Decomposed tasks.
            strategy_selection: Selected strategy.
            risk_assessment: Risk assessment.
            execution_decision: Execution policy decision.

        Returns:
            Complete decision plan.
        """
        plan_id = str(uuid.uuid4())

        # Calculate estimates
        total_time = sum(t.estimated_time_seconds for t in tasks)
        total_cost = sum(t.estimated_cost for t in tasks)
        total_tokens = sum(t.estimated_tokens for t in tasks)

        # Create plan
        plan = DecisionPlan(
            plan_id=plan_id,
            goal=goal,
            tasks=tasks,
            strategy=strategy_selection.selected_strategy,
            policy=execution_decision.policy,
            status=DecisionStatus.CREATED,
            overall_risk=risk_assessment.overall_risk,
            risk_factors=[f.get("type", "") for f in risk_assessment.risk_factors],
            total_estimated_time_seconds=total_time,
            total_estimated_cost=total_cost,
            total_estimated_tokens=total_tokens,
        )

        # Add metadata
        plan.metadata = {
            "strategy_reasoning": strategy_selection.reasoning,
            "alternatives_considered": [s.value for s in strategy_selection.alternatives],
            "mitigation_strategies": risk_assessment.mitigation_strategies,
            "requires_escalation": risk_assessment.requires_escalation,
            "max_parallel_tasks": execution_decision.max_parallel_tasks,
            "parallelism_allowed": execution_decision.parallelism_allowed,
            "retry_strategy": execution_decision.retry_strategy,
        }

        return plan

    def validate(self, plan: DecisionPlan) -> tuple[bool, list[str]]:
        """Validate decision plan.

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
                    errors.append(f"Task {task.task_id} depends on unknown task {dep_id}")

        # Check estimates
        if plan.total_estimated_time_seconds < 0:
            errors.append("Invalid time estimate")

        if plan.total_estimated_cost < 0:
            errors.append("Invalid cost estimate")

        # Check strategy
        if not plan.strategy:
            errors.append("No strategy selected")

        return len(errors) == 0, errors

    def optimize(self, plan: DecisionPlan) -> DecisionPlan:
        """Optimize decision plan.

        Args:
            plan: Plan to optimize.

        Returns:
            Optimized plan.
        """
        # Mark as evaluated
        plan.status = DecisionStatus.EVALUATED

        # Remove unnecessary dependencies
        self._remove_optional_dependencies(plan)

        return plan

    def approve(self, plan: DecisionPlan) -> DecisionPlan:
        """Approve plan for execution.

        Args:
            plan: Plan to approve.

        Returns:
            Approved plan.
        """
        plan.status = DecisionStatus.APPROVED
        return plan

    def finalize(self, plan: DecisionPlan) -> DecisionPlan:
        """Finalize decision plan.

        Args:
            plan: Plan to finalize.

        Returns:
            Finalized plan.
        """
        plan.status = DecisionStatus.READY
        return plan

    def update_progress(
        self,
        plan: DecisionPlan,
        completed_task_id: str,
        result: any = None,
        error: str = "",
    ) -> DecisionPlan:
        """Update plan progress.

        Args:
            plan: Plan to update.
            completed_task_id: ID of completed task.
            result: Task result.
            error: Task error if failed.

        Returns:
            Updated plan.
        """
        plan.updated_at = datetime.now(timezone.utc)

        for task in plan.tasks:
            if task.task_id == completed_task_id:
                task.completed_at = datetime.now(timezone.utc)
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
        total = plan.completed_tasks + plan.failed_tasks
        if total == len(plan.tasks):
            if plan.failed_tasks == 0:
                plan.status = DecisionStatus.COMPLETED
                plan.completed_at = datetime.now(timezone.utc)
            else:
                plan.status = DecisionStatus.FAILED
                plan.completed_at = datetime.now(timezone.utc)

        return plan

    def get_executable_tasks(
        self,
        plan: DecisionPlan,
    ) -> list[DecisionTask]:
        """Get tasks ready for execution.

        Args:
            plan: Plan to analyze.

        Returns:
            Tasks ready to execute.
        """
        if plan.policy.value == "strict":
            # Strict policy: only first ready task
            for task in plan.tasks:
                if task.status == "pending" and not task.depends_on:
                    return [task]
            return []

        executable = []
        for task in plan.tasks:
            if task.status != "pending":
                continue

            # Check dependencies
            deps_complete = all(
                next((t for t in plan.tasks if t.task_id == dep_id), None)
                for dep_id in task.depends_on
            )

            if deps_complete:
                executable.append(task)

        # Limit by parallelism
        if not plan.metadata.get("parallelism_allowed", True):
            return executable[:1]

        max_parallel = plan.metadata.get("max_parallel_tasks", 10)
        return executable[:max_parallel]

    def _remove_optional_dependencies(self, plan: DecisionPlan) -> None:
        """Remove optional dependencies to simplify plan."""
        for task in plan.tasks:
            # Keep only blocking dependencies
            task.depends_on = [
                dep for dep in task.depends_on
                if any(
                    t.task_id == dep and t.dependency_type.value == "blocks"
                    for t in plan.tasks
                )
            ]
