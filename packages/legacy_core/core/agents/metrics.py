"""Agent metrics for EREN Cognitive Agent Runtime.

Tracks agent performance and statistics.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.agents.types import AgentMetrics

if TYPE_CHECKING:
    pass


class AgentMetricsCollector:
    """Collects and tracks agent metrics.

    The Metrics Collector does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Collects metrics
    - Tracks statistics
    - Generates reports
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._metrics = AgentMetrics()
        self._history: list[dict] = []

    def record_task_submitted(
        self,
        task_id: str,
        agent_id: str,
        capability: str,
    ) -> None:
        """Record task submission.

        Args:
            task_id: Task ID.
            agent_id: Agent ID.
            capability: Capability used.
        """
        self._metrics.tasks_submitted += 1

        self._history.append({
            "event": "task_submitted",
            "task_id": task_id,
            "agent_id": agent_id,
            "capability": capability,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Update per-agent metrics
        if agent_id not in self._metrics.by_agent:
            self._metrics.by_agent[agent_id] = {
                "submitted": 0,
                "completed": 0,
                "failed": 0,
                "avg_duration_ms": 0,
            }
        self._metrics.by_agent[agent_id]["submitted"] += 1

        # Update per-capability metrics
        self._metrics.by_capability[capability] = (
            self._metrics.by_capability.get(capability, 0) + 1
        )

    def record_task_completed(
        self,
        task_id: str,
        agent_id: str,
        duration_ms: float,
    ) -> None:
        """Record task completion.

        Args:
            task_id: Task ID.
            agent_id: Agent ID.
            duration_ms: Task duration in ms.
        """
        self._metrics.tasks_completed += 1

        self._history.append({
            "event": "task_completed",
            "task_id": task_id,
            "agent_id": agent_id,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Update averages
        total = self._metrics.tasks_completed + self._metrics.tasks_failed
        if total > 0:
            self._metrics.success_rate = self._metrics.tasks_completed / total
            self._metrics.error_rate = self._metrics.tasks_failed / total

        # Update avg duration
        if self._metrics.avg_task_duration_ms == 0:
            self._metrics.avg_task_duration_ms = duration_ms
        else:
            self._metrics.avg_task_duration_ms = (
                (self._metrics.avg_task_duration_ms * 0.7) + (duration_ms * 0.3)
            )

        # Update per-agent metrics
        if agent_id in self._metrics.by_agent:
            agent_metrics = self._metrics.by_agent[agent_id]
            agent_metrics["completed"] += 1

            if agent_metrics["avg_duration_ms"] == 0:
                agent_metrics["avg_duration_ms"] = duration_ms
            else:
                agent_metrics["avg_duration_ms"] = (
                    (agent_metrics["avg_duration_ms"] * 0.7) + (duration_ms * 0.3)
                )

    def record_task_failed(
        self,
        task_id: str,
        agent_id: str,
        duration_ms: float,
        error: str,
    ) -> None:
        """Record task failure.

        Args:
            task_id: Task ID.
            agent_id: Agent ID.
            duration_ms: Task duration in ms.
            error: Error message.
        """
        self._metrics.tasks_failed += 1

        self._history.append({
            "event": "task_failed",
            "task_id": task_id,
            "agent_id": agent_id,
            "duration_ms": duration_ms,
            "error": error,
            "timestamp": datetime.now(UTC).isoformat(),
        })

        # Update rates
        total = self._metrics.tasks_completed + self._metrics.tasks_failed
        if total > 0:
            self._metrics.success_rate = self._metrics.tasks_completed / total
            self._metrics.error_rate = self._metrics.tasks_failed / total

        # Update per-agent metrics
        if agent_id in self._metrics.by_agent:
            self._metrics.by_agent[agent_id]["failed"] += 1

    def record_message_sent(
        self,
        sender_id: str,
        receiver_id: str,
    ) -> None:
        """Record message sent.

        Args:
            sender_id: Sender agent ID.
            receiver_id: Receiver agent ID.
        """
        self._metrics.messages_sent += 1

        self._history.append({
            "event": "message_sent",
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def get_metrics(self) -> AgentMetrics:
        """Get current metrics.

        Returns:
            Current metrics snapshot.
        """
        return self._metrics

    def get_agent_metrics(self, agent_id: str) -> dict | None:
        """Get metrics for specific agent.

        Args:
            agent_id: Agent ID.

        Returns:
            Agent metrics or None.
        """
        return self._metrics.by_agent.get(agent_id)

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
        self._metrics = AgentMetrics()
        self._history.clear()

    def generate_report(self) -> dict:
        """Generate metrics report.

        Returns:
            Report dictionary.
        """
        return {
            "summary": {
                "total_tasks": self._metrics.tasks_submitted,
                "completed": self._metrics.tasks_completed,
                "failed": self._metrics.tasks_failed,
                "messages": self._metrics.messages_sent,
            },
            "rates": {
                "success_rate": f"{self._metrics.success_rate * 100:.1f}%",
                "error_rate": f"{self._metrics.error_rate * 100:.1f}%",
            },
            "performance": {
                "avg_task_duration_ms": f"{self._metrics.avg_task_duration_ms:.1f}ms",
            },
            "by_capability": {
                k: v for k, v in sorted(
                    self._metrics.by_capability.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            },
        }


# Global metrics collector
_global_metrics_collector: AgentMetricsCollector | None = None
_metrics_lock = __import__("threading").Lock()


def get_metrics_collector() -> AgentMetricsCollector:
    """Get the global metrics collector.

    Returns:
        Global AgentMetricsCollector instance.
    """
    global _global_metrics_collector
    with _metrics_lock:
        if _global_metrics_collector is None:
            _global_metrics_collector = AgentMetricsCollector()
        return _global_metrics_collector


def reset_metrics_collector() -> None:
    """Reset the global metrics collector."""
    global _global_metrics_collector
    with _metrics_lock:
        _global_metrics_collector = None
