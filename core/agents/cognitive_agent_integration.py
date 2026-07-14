"""Cognitive Multi-Agent Collaboration (PR-053).

Provides multi-agent collaboration capabilities for EREN OS.
Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable


# =============================================================================
# Agent Events
# =============================================================================


class AgentEventType(str, Enum):
    """Types of agent events."""
    AGENT_REGISTERED = "agent_registered"
    AGENT_UNREGISTERED = "agent_unregistered"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    COLLABORATION_STARTED = "collaboration_started"
    COLLABORATION_ENDED = "collaboration_ended"


@dataclass
class AgentEvent:
    """Agent event."""
    event_type: AgentEventType
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    agent_id: str = ""
    task_id: str = ""
    session_id: str = ""
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Agent Types
# =============================================================================


class AgentType(str, Enum):
    """Types of agents."""
    ORCHESTRATOR = "orchestrator"
    PLANNER = "planner"
    EXECUTOR = "executor"
    MONITOR = "monitor"
    SPECIALIST = "specialist"


@dataclass
class Agent:
    """An agent in the system."""
    id: str
    name: str
    agent_type: AgentType = AgentType.SPECIALIST
    handler: Callable | None = None
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """A task assigned to an agent."""
    id: str
    description: str
    assigned_to: str = ""
    status: str = "pending"
    result: Any = None
    error: str = ""


# =============================================================================
# Agent Registry
# =============================================================================


class AgentRegistry:
    """Registry for agents."""

    def __init__(self):
        self._agents: dict[str, Agent] = {}
        self._subscribers: list[Callable] = []

    def register(self, agent: Agent) -> None:
        """Register an agent."""
        self._agents[agent.id] = agent
        self._publish(AgentEvent(
            event_type=AgentEventType.AGENT_REGISTERED,
            agent_id=agent.id,
        ))

    def unregister(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            self._publish(AgentEvent(
                event_type=AgentEventType.AGENT_UNREGISTERED,
                agent_id=agent_id,
            ))
            return True
        return False

    def get(self, agent_id: str) -> Agent | None:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def find_by_type(self, agent_type: AgentType) -> list[Agent]:
        """Find agents by type."""
        return [a for a in self._agents.values() if a.agent_type == agent_type]

    def find_by_capability(self, capability: str) -> list[Agent]:
        """Find agents by capability."""
        return [a for a in self._agents.values() if capability in a.capabilities]

    def list_all(self) -> list[Agent]:
        """List all agents."""
        return list(self._agents.values())

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to agent events."""
        self._subscribers.append(callback)

    def _publish(self, event: AgentEvent) -> None:
        """Publish an event."""
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass


# =============================================================================
# Task Manager
# =============================================================================


class TaskManager:
    """Manages tasks across agents."""

    def __init__(self, registry: AgentRegistry):
        self._registry = registry
        self._tasks: dict[str, Task] = {}

    def create_task(self, description: str, agent_id: str) -> Task:
        """Create and assign a task."""
        import uuid
        task = Task(
            id=f"task_{uuid.uuid4().hex[:8]}",
            description=description,
            assigned_to=agent_id,
        )
        self._tasks[task.id] = task
        self._registry._publish(AgentEvent(
            event_type=AgentEventType.TASK_ASSIGNED,
            agent_id=agent_id,
            task_id=task.id,
        ))
        return task

    def execute_task(self, task_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a task."""
        task = self._tasks.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}

        agent = self._registry.get(task.assigned_to)
        if not agent or not agent.handler:
            return {"success": False, "error": "Agent not found or no handler"}

        try:
            result = agent.handler(context or {})
            task.status = "completed"
            task.result = result
            self._registry._publish(AgentEvent(
                event_type=AgentEventType.TASK_COMPLETED,
                agent_id=agent.id,
                task_id=task.id,
            ))
            return {"success": True, "result": result}
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self._registry._publish(AgentEvent(
                event_type=AgentEventType.TASK_FAILED,
                agent_id=agent.id,
                task_id=task.id,
                error=str(e),
            ))
            return {"success": False, "error": str(e)}

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)
