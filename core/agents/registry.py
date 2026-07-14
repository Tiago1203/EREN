"""Agent registry for EREN Cognitive Agent Runtime.

Manages agent registration and discovery.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.agents.types import (
    AgentManifest,
    AgentStatus,
    AgentType,
)

if TYPE_CHECKING:
    pass


class AgentRegistry:
    """Registry for managing agents.

    The Registry does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Registers agents
    - Discovers agents
    - Tracks agent status
    """

    def __init__(self):
        """Initialize agent registry."""
        self._agents: dict[str, AgentManifest] = {}
        self._status: dict[str, AgentStatus] = {}
        self._last_seen: dict[str, datetime] = {}

    def register(
        self,
        manifest: AgentManifest,
    ) -> AgentManifest:
        """Register an agent.

        Args:
            manifest: Agent manifest.

        Returns:
            Registered manifest.
        """
        self._agents[manifest.agent_id] = manifest
        self._status[manifest.agent_id] = AgentStatus.IDLE
        self._last_seen[manifest.agent_id] = datetime.now(timezone.utc)
        return manifest

    def unregister(self, agent_id: str) -> bool:
        """Unregister an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            True if unregistered.
        """
        self._agents.pop(agent_id, None)
        self._status.pop(agent_id, None)
        self._last_seen.pop(agent_id, None)
        return agent_id not in self._agents

    def get(self, agent_id: str) -> AgentManifest | None:
        """Get agent manifest.

        Args:
            agent_id: Agent ID.

        Returns:
            Agent manifest or None.
        """
        return self._agents.get(agent_id)

    def get_all(self) -> list[AgentManifest]:
        """Get all registered agents.

        Returns:
            List of agent manifests.
        """
        return list(self._agents.values())

    def get_by_type(self, agent_type: AgentType) -> list[AgentManifest]:
        """Get agents by type.

        Args:
            agent_type: Agent type.

        Returns:
            List of agents.
        """
        return [
            agent for agent in self._agents.values()
            if agent.agent_type == agent_type
        ]

    def get_by_capability(self, capability: str) -> list[AgentManifest]:
        """Get agents with capability.

        Args:
            capability: Capability name.

        Returns:
            List of agents.
        """
        return [
            agent for agent in self._agents.values()
            if agent.has_capability(capability)
        ]

    def get_available(self) -> list[AgentManifest]:
        """Get available (idle) agents.

        Returns:
            List of available agents.
        """
        return [
            agent for agent in self._agents.values()
            if self._status.get(agent.agent_id) == AgentStatus.IDLE
        ]

    def set_status(
        self,
        agent_id: str,
        status: AgentStatus,
    ) -> None:
        """Set agent status.

        Args:
            agent_id: Agent ID.
            status: New status.
        """
        self._status[agent_id] = status
        self._last_seen[agent_id] = datetime.now(timezone.utc)

    def get_status(self, agent_id: str) -> AgentStatus | None:
        """Get agent status.

        Args:
            agent_id: Agent ID.

        Returns:
            Agent status or None.
        """
        return self._status.get(agent_id)

    def update_last_seen(self, agent_id: str) -> None:
        """Update agent last seen timestamp.

        Args:
            agent_id: Agent ID.
        """
        self._last_seen[agent_id] = datetime.now(timezone.utc)

    def get_last_seen(self, agent_id: str) -> datetime | None:
        """Get agent last seen timestamp.

        Args:
            agent_id: Agent ID.

        Returns:
            Last seen timestamp or None.
        """
        return self._last_seen.get(agent_id)

    def find_best_agent(
        self,
        capability: str,
    ) -> AgentManifest | None:
        """Find best available agent for capability.

        Args:
            capability: Required capability.

        Returns:
            Best agent or None.
        """
        candidates = self.get_by_capability(capability)
        available = [
            agent for agent in candidates
            if self._status.get(agent.agent_id) == AgentStatus.IDLE
        ]

        if not available:
            return None

        # Simple selection: first available
        # Could be enhanced with load balancing, etc.
        return available[0]

    def get_stats(self) -> dict:
        """Get registry statistics.

        Returns:
            Statistics dictionary.
        """
        status_counts = {}
        type_counts = {}

        for agent in self._agents.values():
            status = self._status.get(agent.agent_id, AgentStatus.IDLE)
            status_counts[status.value] = status_counts.get(status.value, 0) + 1

            agent_type = agent.agent_type.value
            type_counts[agent_type] = type_counts.get(agent_type, 0) + 1

        return {
            "total_agents": len(self._agents),
            "by_status": status_counts,
            "by_type": type_counts,
        }


# Global registry
_global_registry: AgentRegistry | None = None
_registry_lock = __import__("threading").Lock()


def get_registry() -> AgentRegistry:
    """Get the global agent registry.

    Returns:
        Global AgentRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = AgentRegistry()
        return _global_registry


def reset_registry() -> None:
    """Reset the global agent registry."""
    global _global_registry
    with _registry_lock:
        _global_registry = None
