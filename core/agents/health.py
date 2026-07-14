"""Agent health management for EREN Cognitive Agent Runtime.

Manages agent health and heartbeat.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.agents.types import (
    AgentHealth,
    AgentHealthStatus,
    AgentStatus,
)

if TYPE_CHECKING:
    pass


class AgentHealthManager:
    """Manages agent health.

    The Health Manager does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Tracks health status
    - Performs health checks
    - Calculates metrics
    """

    def __init__(self):
        """Initialize health manager."""
        self._health: dict[str, AgentHealth] = {}

    def register_agent(
        self,
        agent_id: str,
        initial_status: AgentHealthStatus = AgentHealthStatus.HEALTHY,
    ) -> AgentHealth:
        """Register an agent for health monitoring.

        Args:
            agent_id: Agent ID.
            initial_status: Initial health status.

        Returns:
            Agent health.
        """
        health = AgentHealth(
            agent_id=agent_id,
            status=initial_status,
            last_heartbeat=datetime.now(timezone.utc),
        )
        self._health[agent_id] = health
        return health

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent.

        Args:
            agent_id: Agent ID.
        """
        self._health.pop(agent_id, None)

    def get_health(self, agent_id: str) -> AgentHealth | None:
        """Get agent health.

        Args:
            agent_id: Agent ID.

        Returns:
            Agent health or None.
        """
        return self._health.get(agent_id)

    def get_all_health(self) -> list[AgentHealth]:
        """Get health for all agents.

        Returns:
            List of agent health.
        """
        return list(self._health.values())

    def update_heartbeat(self, agent_id: str) -> None:
        """Update agent heartbeat.

        Args:
            agent_id: Agent ID.
        """
        if agent_id in self._health:
            self._health[agent_id].last_heartbeat = datetime.now(timezone.utc)

    def record_task_start(self, agent_id: str) -> None:
        """Record task start for agent.

        Args:
            agent_id: Agent ID.
        """
        if agent_id in self._health:
            self._health[agent_id].total_tasks += 1

    def record_task_success(
        self,
        agent_id: str,
        duration_ms: float,
    ) -> None:
        """Record successful task completion.

        Args:
            agent_id: Agent ID.
            duration_ms: Task duration in ms.
        """
        if agent_id in self._health:
            health = self._health[agent_id]
            health.success_count += 1
            health.failure_count = 0  # Reset failure count

            # Update avg response time
            if health.avg_response_time_ms == 0:
                health.avg_response_time_ms = duration_ms
            else:
                health.avg_response_time_ms = (
                    (health.avg_response_time_ms * 0.7) + (duration_ms * 0.3)
                )

            # Update error rate
            total = health.success_count + health.failure_count
            health.error_rate = health.failure_count / total if total > 0 else 0

            # Update status
            self._update_status(agent_id)

    def record_task_failure(
        self,
        agent_id: str,
        duration_ms: float,
    ) -> None:
        """Record task failure.

        Args:
            agent_id: Agent ID.
            duration_ms: Task duration in ms.
        """
        if agent_id in self._health:
            health = self._health[agent_id]
            health.failure_count += 1

            # Update avg response time
            if health.avg_response_time_ms == 0:
                health.avg_response_time_ms = duration_ms
            else:
                health.avg_response_time_ms = (
                    (health.avg_response_time_ms * 0.7) + (duration_ms * 0.3)
                )

            # Update error rate
            total = health.success_count + health.failure_count
            health.error_rate = health.failure_count / total if total > 0 else 0

            # Update status
            self._update_status(agent_id)

    def _update_status(self, agent_id: str) -> None:
        """Update agent status based on health metrics."""
        health = self._health.get(agent_id)
        if not health:
            return

        if health.error_rate >= 0.5 or health.failure_count >= 3:
            health.status = AgentHealthStatus.UNHEALTHY
        elif health.error_rate >= 0.2 or health.failure_count >= 1:
            health.status = AgentHealthStatus.DEGRADED
        else:
            health.status = AgentHealthStatus.HEALTHY

    def check_stale_agents(
        self,
        timeout_seconds: float = 60.0,
    ) -> list[str]:
        """Check for stale agents (no heartbeat).

        Args:
            timeout_seconds: Timeout in seconds.

        Returns:
            List of stale agent IDs.
        """
        stale = []
        now = datetime.now(timezone.utc)

        for agent_id, health in self._health.items():
            age = (now - health.last_heartbeat).total_seconds()
            if age > timeout_seconds:
                stale.append(agent_id)
                health.status = AgentHealthStatus.UNHEALTHY

        return stale

    def get_aggregate_health(self) -> dict[str, int]:
        """Get aggregate health statistics.

        Returns:
            Dictionary with counts by status.
        """
        counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "failed": 0,
        }

        for health in self._health.values():
            if health.status == AgentHealthStatus.HEALTHY:
                counts["healthy"] += 1
            elif health.status == AgentHealthStatus.DEGRADED:
                counts["degraded"] += 1
            elif health.status == AgentHealthStatus.UNHEALTHY:
                counts["unhealthy"] += 1
            elif health.status == AgentHealthStatus.FAILED:
                counts["failed"] += 1

        return counts


# Global health manager
_global_health_manager: AgentHealthManager | None = None
_health_lock = __import__("threading").Lock()


def get_health_manager() -> AgentHealthManager:
    """Get the global health manager.

    Returns:
        Global AgentHealthManager instance.
    """
    global _global_health_manager
    with _health_lock:
        if _global_health_manager is None:
            _global_health_manager = AgentHealthManager()
        return _global_health_manager


def reset_health_manager() -> None:
    """Reset the global health manager."""
    global _global_health_manager
    with _health_lock:
        _global_health_manager = None
