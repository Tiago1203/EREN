"""Cognitive Decision Engine (CDE) for EREN OS.

Main decision engine that transforms user intent into decisions.
Refactored from Planning Engine to be a complete decision-making system.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from core.decision.decision_builder import DecisionBuilder
from core.decision.dependency_resolver import DependencyResolver
from core.decision.execution_policy import ExecutionPolicyManager
from core.decision.goal_analyzer import GoalAnalyzer
from core.decision.replanner import Replanner
from core.decision.risk_evaluator import RiskEvaluator
from core.decision.strategy_selector import StrategySelector
from core.decision.task_decomposer import TaskDecomposer
from core.decision.types import (
    DecisionMetrics,
    DecisionPlan,
    DecisionStatus,
    DecisionTask,
)

if TYPE_CHECKING:
    pass


class CognitiveDecisionEngine:
    """Cognitive Decision Engine.

    The Decision Engine does NOT:
    - Execute tasks
    - Query providers
    - Use OpenAI directly
    - Consult memory
    - Consult retrieval

    It ONLY:
    - Analyzes goals
    - Selects strategies
    - Evaluates risks
    - Builds decision plans
    - Manages replanning

    Philosophy:
        Planning is only part of decision-making.
        The Decision Engine decides the best strategy to achieve a cognitive goal.

        LLM responds.
        Decision Engine decides what to do.
        Never executes tasks.
        Only takes decisions.
    """

    def __init__(self):
        """Initialize decision engine."""
        # Core components (from Planning)
        self._goal_analyzer = GoalAnalyzer()
        self._task_decomposer = TaskDecomposer()
        self._dependency_resolver = DependencyResolver()

        # Decision-specific components
        self._strategy_selector = StrategySelector()
        self._risk_evaluator = RiskEvaluator()
        self._policy_manager = ExecutionPolicyManager()
        self._replanner = Replanner()
        self._decision_builder = DecisionBuilder()

        # Metrics
        self._metrics = DecisionMetrics()

    def decide(
        self,
        user_intent: str,
        context: dict | None = None,
    ) -> DecisionPlan:
        """Create decision plan from user intent.

        This is the main entry point for decision-making.

        Args:
            user_intent: User's intent or question.
            context: Additional context.

        Returns:
            DecisionPlan ready for execution.
        """
        start_time = time.time()

        # Step 1: Analyze goal
        analysis = self._goal_analyzer.analyze(user_intent, context)
        goal = analysis.goal

        # Step 2: Decompose into tasks
        tasks = self._task_decomposer.decompose(goal, analysis)

        # Step 3: Resolve dependencies
        ordered_tasks = self._dependency_resolver.resolve(tasks)

        # Step 4: Select strategy
        strategy_selection = self._strategy_selector.select(goal, analysis, ordered_tasks)

        # Step 5: Evaluate risk
        risk_assessment = self._risk_evaluator.evaluate_plan(
            plan=DecisionPlan(plan_id="", goal=goal, tasks=ordered_tasks),
            tasks=ordered_tasks,
        )

        # Step 6: Select execution policy
        execution_decision = self._policy_manager.select_policy(
            strategy=strategy_selection.selected_strategy,
            risk_level=risk_assessment.overall_risk,
            task_count=len(ordered_tasks),
        )

        # Step 7: Build decision plan
        plan = self._decision_builder.build(
            goal=goal,
            analysis=analysis,
            tasks=ordered_tasks,
            strategy_selection=strategy_selection,
            risk_assessment=risk_assessment,
            execution_decision=execution_decision,
        )

        # Step 8: Validate
        is_valid, errors = self._decision_builder.validate(plan)
        if not is_valid:
            plan = self._fix_plan(plan, errors)

        # Step 9: Optimize
        plan = self._decision_builder.optimize(plan)

        # Step 10: Check approval
        if self._policy_manager.should_approve(plan, risk_assessment.overall_risk):
            plan = self._decision_builder.approve(plan)

        # Step 11: Finalize
        plan = self._decision_builder.finalize(plan)

        # Update metrics
        decision_time = (time.time() - start_time) * 1000
        self._update_metrics(plan, decision_time)

        return plan

    def replan(
        self,
        plan: DecisionPlan,
        reason: str,
        affected_tasks: list[str] | None = None,
    ) -> DecisionPlan:
        """Replan a failed or problematic decision.

        Args:
            plan: Original plan.
            reason: Reason for replanning.
            affected_tasks: Tasks to replan.

        Returns:
            New decision plan.
        """
        # Check if replanning is allowed
        should_replan, replan_reason = self._policy_manager.should_replan(
            plan,
            affected_tasks[0] if affected_tasks else None,
        )

        if not should_replan:
            return plan

        # Replan
        new_plan = self._replanner.replan(
            plan,
            reason or replan_reason,
            affected_tasks,
        )

        self._metrics.replans_triggered += 1

        return new_plan

    def cancel(self, plan: DecisionPlan, reason: str) -> DecisionPlan:
        """Cancel a decision plan.

        Args:
            plan: Plan to cancel.
            reason: Cancellation reason.

        Returns:
            Cancelled plan.
        """
        return self._replanner.cancel_plan(plan, reason)

    def pause(self, plan: DecisionPlan) -> DecisionPlan:
        """Pause a decision plan.

        Args:
            plan: Plan to pause.

        Returns:
            Paused plan.
        """
        return self._replanner.pause_plan(plan)

    def resume(self, plan: DecisionPlan) -> DecisionPlan:
        """Resume a paused plan.

        Args:
            plan: Plan to resume.

        Returns:
            Resumed plan.
        """
        return self._replanner.resume_plan(plan)

    def _fix_plan(self, plan: DecisionPlan, errors: list[str]) -> DecisionPlan:
        """Attempt to fix plan errors."""
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

    def _update_metrics(self, plan: DecisionPlan, decision_time_ms: float) -> None:
        """Update decision metrics."""
        self._metrics.decisions_made += 1
        self._metrics.total_tasks += len(plan.tasks)

        if plan.status == DecisionStatus.COMPLETED:
            self._metrics.decisions_completed += 1
        elif plan.status == DecisionStatus.FAILED:
            self._metrics.decisions_failed += 1

        # Update averages
        total = self._metrics.decisions_made
        self._metrics.avg_decision_time_ms = (
            (self._metrics.avg_decision_time_ms * (total - 1) + decision_time_ms)
            / total
        )
        self._metrics.avg_tasks_per_decision = (
            (self._metrics.avg_tasks_per_decision * (total - 1) + len(plan.tasks))
            / total
        )

        # Success rate
        if self._metrics.decisions_made > 0:
            self._metrics.success_rate = (
                self._metrics.decisions_completed / self._metrics.decisions_made
            )

        # Replan rate
        if self._metrics.decisions_made > 0:
            self._metrics.replan_rate = (
                self._metrics.replans_triggered / self._metrics.decisions_made
            )

        # By strategy
        strategy = plan.strategy.value
        self._metrics.by_strategy[strategy] = (
            self._metrics.by_strategy.get(strategy, 0) + 1
        )

        # By goal type
        goal_type = plan.goal.goal_type.value
        self._metrics.by_goal_type[goal_type] = (
            self._metrics.by_goal_type.get(goal_type, 0) + 1
        )

    def get_metrics(self) -> DecisionMetrics:
        """Get decision metrics.

        Returns:
            Current metrics.
        """
        return self._metrics

    def validate_plan(self, plan: DecisionPlan) -> tuple[bool, list[str]]:
        """Validate a decision plan.

        Args:
            plan: Plan to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        return self._decision_builder.validate(plan)

    def get_executable_tasks(self, plan: DecisionPlan) -> list[DecisionTask]:
        """Get tasks ready for execution.

        Args:
            plan: Plan to analyze.

        Returns:
            Tasks ready to execute.
        """
        return self._decision_builder.get_executable_tasks(plan)

    def update_plan_progress(
        self,
        plan: DecisionPlan,
        completed_task_id: str,
        result: any = None,
        error: str = "",
    ) -> DecisionPlan:
        """Update plan progress after task completion.

        Args:
            plan: Plan to update.
            completed_task_id: ID of completed task.
            result: Task result.
            error: Task error if failed.

        Returns:
            Updated plan.
        """
        return self._decision_builder.update_progress(
            plan, completed_task_id, result, error
        )

    def should_escalate(self, plan: DecisionPlan) -> tuple[bool, str]:
        """Check if decision should escalate to human.

        Args:
            plan: Decision plan.

        Returns:
            Tuple of (should_escalate, reason).
        """
        risk_assessment = self._risk_evaluator.evaluate_plan(
            plan=plan,
            tasks=plan.tasks,
        )

        escalation = self._risk_evaluator.should_escalate(plan, risk_assessment)
        return escalation, risk_assessment.escalation_reason


# Global engine instance
_global_engine: CognitiveDecisionEngine | None = None
_engine_lock = __import__("threading").Lock()


def get_decision_engine() -> CognitiveDecisionEngine:
    """Get the global decision engine.

    Returns:
        Global CognitiveDecisionEngine instance.
    """
    global _global_engine
    with _engine_lock:
        if _global_engine is None:
            _global_engine = CognitiveDecisionEngine()
        return _global_engine


def reset_decision_engine() -> None:
    """Reset the global decision engine."""
    global _global_engine
    with _engine_lock:
        _global_engine = None
