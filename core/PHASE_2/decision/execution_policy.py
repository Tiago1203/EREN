"""Execution Policy for EREN Cognitive Decision Engine.

Defines policies for executing decisions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.decision.types import (
    DecisionPlan,
    DecisionStrategy,
    ExecutionDecision,
    ExecutionPolicy,
    RiskLevel,
)

if TYPE_CHECKING:
    pass


class ExecutionPolicyManager:
    """Manages execution policies.

    The Policy Manager does NOT:
    - Execute tasks
    - Make decisions

    It ONLY:
    - Selects execution policies
    - Defines execution rules
    - Configures retry strategies
    """

    def __init__(self):
        """Initialize policy manager."""
        self._policies = self._load_policies()

    def select_policy(
        self,
        strategy: DecisionStrategy,
        risk_level: RiskLevel,
        task_count: int,
    ) -> ExecutionDecision:
        """Select execution policy.

        Args:
            strategy: Selected strategy.
            risk_level: Overall risk level.
            task_count: Number of tasks.

        Returns:
            Execution decision.
        """
        # Map strategy to base policy
        if strategy == DecisionStrategy.CONSERVATIVE:
            base_policy = ExecutionPolicy.CONSERVATIVE
        elif strategy == DecisionStrategy.AGGRESSIVE:
            base_policy = ExecutionPolicy.AGGRESSIVE
        elif risk_level == RiskLevel.CRITICAL:
            base_policy = ExecutionPolicy.FAILFAST
        elif risk_level == RiskLevel.HIGH:
            base_policy = ExecutionPolicy.STRICT
        else:
            base_policy = ExecutionPolicy.ADAPTIVE

        # Determine parallelism
        parallelism_allowed = strategy in [
            DecisionStrategy.PARALLEL,
            DecisionStrategy.HYBRID,
        ]

        max_parallel = self._calculate_max_parallel(
            strategy=strategy,
            risk_level=risk_level,
            task_count=task_count,
        )

        # Determine replanning
        allow_replanning = base_policy in [
            ExecutionPolicy.ADAPTIVE,
            ExecutionPolicy.GRACEFUL,
        ]

        # Determine failfast
        failfast_enabled = base_policy == ExecutionPolicy.FAILFAST

        # Determine retry strategy
        retry_strategy = self._select_retry_strategy(
            policy=base_policy,
            risk_level=risk_level,
        )

        # Calculate timeout
        timeout_seconds = self._calculate_timeout(
            strategy=strategy,
            task_count=task_count,
        )

        return ExecutionDecision(
            policy=base_policy,
            parallelism_allowed=parallelism_allowed,
            max_parallel_tasks=max_parallel,
            allow_replanning=allow_replanning,
            failfast_enabled=failfast_enabled,
            retry_strategy=retry_strategy,
            timeout_seconds=timeout_seconds,
        )

    def should_approve(
        self,
        plan: DecisionPlan,
        risk_level: RiskLevel,
    ) -> bool:
        """Determine if plan should be approved.

        Args:
            plan: Decision plan.
            risk_level: Risk level.

        Returns:
            True if approved.
        """
        # Critical risk always requires approval
        if risk_level == RiskLevel.CRITICAL:
            return False  # Needs human approval

        # High risk requires approval
        if risk_level == RiskLevel.HIGH:
            return False

        # Check policy
        if plan.policy == ExecutionPolicy.STRICT:
            return False

        # Default to approved
        return True

    def should_replan(
        self,
        plan: DecisionPlan,
        failed_task_id: str | None = None,
    ) -> tuple[bool, str]:
        """Determine if replanning is needed.

        Args:
            plan: Current plan.
            failed_task_id: ID of failed task.

        Returns:
            Tuple of (should_replan, reason).
        """
        # Check if replanning allowed
        if plan.replan_count >= 3:
            return False, "Maximum replans reached"

        # Check failure rate
        if len(plan.tasks) > 0:
            failure_rate = plan.failed_tasks / len(plan.tasks)

            if failure_rate > 0.5:
                return True, "High failure rate"
            elif failure_rate > 0.2 and plan.replan_count < 1:
                return True, "Moderate failure rate - attempt replan"

        # Check for critical task failure
        if failed_task_id:
            task = plan.get_task(failed_task_id)
            if task and task.priority.value == "critical":
                return False, "Critical task failed - escalate"

        # Check time
        if plan.total_duration_seconds > plan.total_estimated_time_seconds * 2:
            return True, "Execution time exceeded estimates"

        return False, ""

    def _calculate_max_parallel(
        self,
        strategy: DecisionStrategy,
        risk_level: RiskLevel,
        task_count: int,
    ) -> int:
        """Calculate maximum parallel tasks."""
        if strategy == DecisionStrategy.PARALLEL:
            base = min(task_count, 5)
        elif strategy == DecisionStrategy.HYBRID:
            base = min(task_count // 2, 3)
        else:
            return 1

        # Reduce for high risk
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            base = min(base, 2)

        return max(base, 1)

    def _select_retry_strategy(
        self,
        policy: ExecutionPolicy,
        risk_level: RiskLevel,
    ) -> str:
        """Select retry strategy."""
        if policy == ExecutionPolicy.FAILFAST:
            return "no_retry"
        elif policy == ExecutionPolicy.CONSERVATIVE:
            return "exponential_backoff"
        elif risk_level == RiskLevel.CRITICAL:
            return "no_retry"
        elif risk_level == RiskLevel.HIGH:
            return "limited_retry"
        else:
            return "standard_retry"

    def _calculate_timeout(
        self,
        strategy: DecisionStrategy,
        task_count: int,
    ) -> float:
        """Calculate timeout in seconds."""
        base_timeout = task_count * 30.0  # 30 seconds per task

        if strategy == DecisionStrategy.PARALLEL:
            base_timeout = base_timeout * 0.5  # Faster
        elif strategy == DecisionStrategy.SEQUENTIAL:
            base_timeout = base_timeout * 1.5  # More time

        return max(base_timeout, 60.0)  # Minimum 1 minute

    def _load_policies(self) -> dict:
        """Load policy configurations."""
        return {
            ExecutionPolicy.STRICT: {
                "allow_replan": False,
                "failfast": True,
                "max_retries": 0,
            },
            ExecutionPolicy.ADAPTIVE: {
                "allow_replan": True,
                "failfast": False,
                "max_retries": 2,
            },
            ExecutionPolicy.CONSERVATIVE: {
                "allow_replan": True,
                "failfast": False,
                "max_retries": 3,
            },
            ExecutionPolicy.AGGRESSIVE: {
                "allow_replan": True,
                "failfast": False,
                "max_retries": 1,
            },
            ExecutionPolicy.FAILFAST: {
                "allow_replan": False,
                "failfast": True,
                "max_retries": 0,
            },
            ExecutionPolicy.GRACEFUL: {
                "allow_replan": True,
                "failfast": False,
                "max_retries": 5,
            },
        }
