"""Contract for the agent capability."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from enum import Enum

from core.contracts.base import CognitiveEngine


class AgentStatus(str, Enum):
    """Status of an agent."""
    
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    STOPPED = "stopped"
    ERROR = "error"


class TaskStatus(str, Enum):
    """Status of a task assigned to an agent."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@runtime_checkable
class AgentTask:
    """Task to be executed by an agent."""
    
    task_id: str
    description: str
    input_data: dict
    priority: int = 0


@runtime_checkable
class AgentResult:
    """Result from agent task execution."""
    
    task_id: str
    success: bool
    output_data: dict
    error: str | None = None


@runtime_checkable
class AgentContract(CognitiveEngine, Protocol):
    """Contract for cognitive agents.

    Agents are specialized capabilities that can execute tasks,
    communicate with other agents, and participate in collaborative
    problem-solving.
    """

    @property
    def status(self) -> AgentStatus:
        """Current status of the agent."""
        ...

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Execute a task and return the result."""
        ...

    async def get_status(self) -> AgentStatus:
        """Get current agent status."""
        ...

    async def health_check(self) -> bool:
        """Check if agent is healthy."""
        ...
