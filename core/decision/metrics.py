"""Decision metrics for EREN Cognitive Decision Engine.

Tracks decision performance and statistics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.decision.types import DecisionMetrics

if TYPE_CHECKING:
    pass


class DecisionMetricsCollector:
    """Collects and tracks decision metrics.

    The Metrics Collector does NOT:
    - Execute tasks
    - Make decisions

    It ONLY:
    - Collects metrics
    - Tracks statistics
    - Generates reports
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._metrics = DecisionMetrics()
        self._history: list[dict] = []

    def record_decision(
        self,
        plan_id: str,
        goal_type: str,
        strategy: str,
        task_count: int,
        decision_time_ms: float,
    ) -> None:
        """Record decision creation.

        Args:
            plan_id: ID of decision.
            goal_type: Type of goal.
            strategy: Selected strategy.
            task_count: Number of tasks.
            decision_time_ms: Decision duration in ms.
        """
        self._metrics.decisions_made += 1
        self._metrics.total_tasks += task_count

        total = self._metrics.decisions_made
        self._metrics.avg_decision_time_ms = (
            (self._metrics.avg_decision_time_ms * (total - 1) + decision_time_ms)
            / total
        )
        self._metrics.avg_tasks_per_decision = (
            (self._metrics.avg_tasks_per_decision * (total - 1) + task_count)
            / total
        )

        self._history.append({
            "event": "decision_made",
            "plan_id": plan_id,
            "goal_type": goal_type,
            "strategy": strategy,
            "task_count": task_count,
            "decision_time_ms": decision_time_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        self._metrics.by_goal_type[goal_type] = (
            self._metrics.by_goal_type.get(goal_type, 0) + 1
        )
        self._metrics.by_strategy[strategy] = (
            self._metrics.by_strategy.get(strategy, 0) + 1
        )

    def record_completion(
        self,
        plan_id: str,
        success: bool,
        duration_seconds: float,
    ) -> None:
        """Record decision completion.

        Args:
            plan_id: ID of completed decision.
            success: Whether decision succeeded.
            duration_seconds: Execution duration.
        """
        if success:
            self._metrics.decisions_completed += 1
        else:
            self._metrics.decisions_failed += 1

        if self._metrics.decisions_made > 0:
            self._metrics.success_rate = (
                self._metrics.decisions_completed / self._metrics.decisions_made
            )

        self._history.append({
            "event": "decision_completed" if success else "decision_failed",
            "plan_id": plan_id,
            "success": success,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_replan(
        self,
        original_plan_id: str,
        new_plan_id: str,
        reason: str,
    ) -> None:
        """Record replanning.

        Args:
            original_plan_id: Original plan ID.
            new_plan_id: New plan ID.
            reason: Replanning reason.
        """
        self._metrics.replans_triggered += 1

        if self._metrics.decisions_made > 0:
            self._metrics.replan_rate = (
                self._metrics.replans_triggered / self._metrics.decisions_made
            )

        self._history.append({
            "event": "replan",
            "original_plan_id": original_plan_id,
            "new_plan_id": new_plan_id,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_metrics(self) -> DecisionMetrics:
        """Get current metrics.

        Returns:
            Current metrics snapshot.
        """
        return self._metrics

    def get_history(
        self,
        limit: int = 100,
    ) -> list[dict]:
        """Get event history.

        Args:
            limit: Maximum events to return.

        Returns:
            List of events.
        """
        return self._history[-limit:]

    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics = DecisionMetrics()
        self._history.clear()

    def generate_report(self) -> dict:
        """Generate metrics report.

        Returns:
            Report dictionary.
        """
        return {
            "summary": {
                "total_decisions": self._metrics.decisions_made,
                "completed": self._metrics.decisions_completed,
                "failed": self._metrics.decisions_failed,
                "success_rate": f"{self._metrics.success_rate * 100:.1f}%",
                "replans": self._metrics.replans_triggered,
                "replan_rate": f"{self._metrics.replan_rate * 100:.1f}%",
            },
            "performance": {
                "avg_decision_time_ms": f"{self._metrics.avg_decision_time_ms:.1f}ms",
                "avg_tasks_per_decision": f"{self._metrics.avg_tasks_per_decision:.1f}",
                "total_tasks": self._metrics.total_tasks,
            },
            "by_strategy": {
                k: v for k, v in sorted(
                    self._metrics.by_strategy.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            },
            "by_goal_type": {
                k: v for k, v in sorted(
                    self._metrics.by_goal_type.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            },
        }
