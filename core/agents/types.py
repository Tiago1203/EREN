"""Agent types for EREN Cognitive Agent Runtime.

Types for the multi-agent system.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Agent Types
# =============================================================================


class AgentType(str, Enum):
    """Types of agents."""

    ENGINEERING = "engineering"
    MEDICAL = "medical"
    RESEARCH = "research"
    DEVICE = "device"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    VISION = "vision"
    SPEECH = "speech"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    """Agent status."""

    IDLE = "idle"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class AgentHealthStatus(str, Enum):
    """Agent health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"


class TaskStatus(str, Enum):
    """Status of agent task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Agent Capability
# =============================================================================


@dataclass
class AgentCapability:
    """A capability that an agent can perform."""

    name: str
    description: str
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    estimated_time_seconds: float = 1.0
    risk_level: str = "low"  # low, medium, high, critical


# =============================================================================
# Agent Manifest
# =============================================================================


@dataclass
class AgentManifest:
    """Manifest describing an agent."""

    agent_id: str
    name: str
    agent_type: AgentType
    description: str
    version: str = "1.0.0"

    # Capabilities
    capabilities: list[AgentCapability] = field(default_factory=list)

    # Configuration
    max_concurrent_tasks: int = 1
    timeout_seconds: float = 60.0
    retry_limit: int = 3

    # Health
    health_check_interval: float = 30.0
    max_failure_count: int = 3

    # Metadata
    metadata: dict = field(default_factory=dict)

    def has_capability(self, name: str) -> bool:
        """Check if agent has capability."""
        return any(cap.name == name for cap in self.capabilities)

    def get_capability(self, name: str) -> AgentCapability | None:
        """Get capability by name."""
        for cap in self.capabilities:
            if cap.name == name:
                return cap
        return None


# =============================================================================
# Agent Health
# =============================================================================


@dataclass
class AgentHealth:
    """Agent health information."""

    agent_id: str
    status: AgentHealthStatus
    last_heartbeat: datetime
    failure_count: int = 0
    success_count: int = 0
    total_tasks: int = 0

    # Metrics
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0

    # Details
    details: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    @property
    def uptime_seconds(self) -> float:
        """Calculate uptime in seconds."""
        return (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds()


# =============================================================================
# Agent Task
# =============================================================================


@dataclass
class AgentTask:
    """A task assigned to an agent."""

    task_id: str
    agent_id: str
    capability: str
    description: str

    # Input
    input_data: dict = field(default_factory=dict)

    # Status
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5  # 1-10, lower is higher priority

    # Execution
    assigned_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Result
    output_data: Any = None
    error: str = ""

    # Retries
    retries: int = 0
    max_retries: int = 3

    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    blocked_by: list[str] = field(default_factory=list)

    # Metadata
    correlation_id: str = ""
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def duration_seconds(self) -> float:
        """Calculate task duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now(timezone.utc) - self.started_at).total_seconds()
        return 0.0

    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked."""
        return len(self.blocked_by) > 0 and self.status == TaskStatus.PENDING


# =============================================================================
# Agent Context
# =============================================================================


@dataclass
class AgentContext:
    """Context shared between agents."""

    session_id: str
    correlation_id: str = ""

    # Shared data
    shared_data: dict = field(default_factory=dict)

    # Execution state
    task_results: dict[str, Any] = field(default_factory=dict)
    agent_states: dict[str, dict] = field(default_factory=dict)

    # Messages
    messages: list[dict] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def put_result(self, task_id: str, result: Any) -> None:
        """Store task result."""
        self.task_results[task_id] = result
        self.updated_at = datetime.now(timezone.utc)

    def get_result(self, task_id: str) -> Any | None:
        """Get task result."""
        return self.task_results.get(task_id)

    def put_shared(self, key: str, value: Any) -> None:
        """Store shared data."""
        self.shared_data[key] = value
        self.updated_at = datetime.now(timezone.utc)

    def get_shared(self, key: str) -> Any | None:
        """Get shared data."""
        return self.shared_data.get(key)

    def add_message(self, sender: str, message: str, type: str = "info") -> None:
        """Add a message to the context."""
        self.messages.append({
            "sender": sender,
            "message": message,
            "type": type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.updated_at = datetime.now(timezone.utc)


# =============================================================================
# Agent Message
# =============================================================================


@dataclass
class AgentMessage:
    """Message between agents."""

    message_id: str
    sender_id: str
    receiver_id: str
    content: Any
    type: str = "request"  # request, response, event, error

    # Routing
    correlation_id: str = ""
    reply_to: str = ""

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Runtime State
# =============================================================================


@dataclass
class RuntimeState:
    """State of the agent runtime."""

    # Status
    is_running: bool = False
    started_at: datetime | None = None

    # Agents
    active_agents: int = 0
    total_agents: int = 0

    # Tasks
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0

    # Metrics
    total_messages: int = 0
    avg_task_duration_ms: float = 0.0

    # Timestamps
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Metrics
# =============================================================================


@dataclass
class AgentMetrics:
    """Metrics for agent operations."""

    # Counts
    tasks_submitted: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    messages_sent: int = 0

    # Timing
    avg_task_duration_ms: float = 0.0
    avg_agent_response_ms: float = 0.0

    # Rates
    success_rate: float = 0.0
    error_rate: float = 0.0

    # By agent
    by_agent: dict[str, dict] = field(default_factory=dict)

    # By capability
    by_capability: dict[str, int] = field(default_factory=dict)
