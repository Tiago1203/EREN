"""Planning metrics for EREN Cognitive Planning Engine.

Tracks planning performance and statistics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.planning.types import PlanningMetrics

if TYPE_CHECKING:
    pass


class PlanningMetricsCollector:
    """Collects and tracks planning metrics.

    The Metrics Collector does NOT:
    - Execute tasks
    - Query providers

    It ONLY:
    - Collects metrics
    - Tracks statistics
    - Generates reports
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._metrics = PlanningMetrics()
        self._history: list[dict] = []

    def record_plan_creation(
        self,
        plan_id: str,
        goal_type: str,
        task_count: int,
        planning_time_ms: float,
    ) -> None:
        """Record plan creation.

        Args:
            plan_id: ID of created plan.
            goal_type: Type of goal.
            task_count: Number of tasks.
            planning_time_ms: Planning duration in ms.
        """
        self._metrics.plans_created += 1
        self._metrics.total_tasks += task_count
        self._metrics.avg_planning_time_ms = (
            (self._metrics.avg_planning_time_ms * (self._metrics.plans_created - 1) + planning_time_ms)
            / self._metrics.plans_created
        )
        self._metrics.avg_tasks_per_plan = (
            (self._metrics.avg_tasks_per_plan * (self._metrics.plans_created - 1) + task_count)
            / self._metrics.plans_created
        )

        self._history.append({
            "event": "plan_created",
            "plan_id": plan_id,
            "goal_type": goal_type,
            "task_count": task_count,
            "planning_time_ms": planning_time_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        self._metrics.by_goal_type[goal_type] = (
            self._metrics.by_goal_type.get(goal_type, 0) + 1
        )

    def record_plan_completion(
        self,
        plan_id: str,
        success: bool,
        duration_seconds: float,
    ) -> None:
        """Record plan completion.

        Args:
            plan_id: ID of completed plan.
            success: Whether plan succeeded.
            duration_seconds: Execution duration.
        """
        if success:
            self._metrics.plans_completed += 1
        else:
            self._metrics.plans_failed += 1

        if self._metrics.plans_created > 0:
            self._metrics.success_rate = (
                self._metrics.plans_completed / self._metrics.plans_created
            )

        self._history.append({
            "event": "plan_completed" if success else "plan_failed",
            "plan_id": plan_id,
            "success": success,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def record_task_completion(
        self,
        plan_id: str,
        task_id: str,
        duration_seconds: float,
    ) -> None:
        """Record task completion.

        Args:
            plan_id: ID of plan.
            task_id: ID of completed task.
            duration_seconds: Task duration.
        """
        self._history.append({
            "event": "task_completed",
            "plan_id": plan_id,
            "task_id": task_id,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_metrics(self) -> PlanningMetrics:
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
        self._metrics = PlanningMetrics()
        self._history.clear()

    def generate_report(self) -> dict:
        """Generate metrics report.

        Returns:
            Report dictionary.
        """
        return {
            "summary": {
                "total_plans": self._metrics.plans_created,
                "completed": self._metrics.plans_completed,
                "failed": self._metrics.plans_failed,
                "success_rate": f"{self._metrics.success_rate * 100:.1f}%",
            },
            "performance": {
                "avg_planning_time_ms": f"{self._metrics.avg_planning_time_ms:.1f}ms",
                "avg_tasks_per_plan": f"{self._metrics.avg_tasks_per_plan:.1f}",
                "total_tasks": self._metrics.total_tasks,
            },
            "by_goal_type": {
                k: v for k, v in sorted(
                    self._metrics.by_goal_type.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            },
        }
