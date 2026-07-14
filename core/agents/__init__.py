"""EREN Cognitive Agent Runtime (CAR).

The official runtime for cognitive agents in EREN.
Allows multiple specialized agents to collaborate.

Philosophy:
    Decision Engine decides.
    Agents execute.
    Runtime coordinates.

Architecture:
    Execution Coordinator
            │
            ▼
    Decision Engine
            │
            ▼
    Agent Runtime
            │
            ├── Agent Registry
            ├── Agent Scheduler
            ├── Agent Communicator
            ├── Lifecycle Manager
            ├── Health Manager
            ├── Context Manager
            ├── Capability Registry
            ├── Event Bus
            └── Metrics Collector

Responsibilities:
- Register agents
- Discover agents
- Activate agents
- Assign tasks
- Coordinate communication
- Share context
- Resolve conflicts
- Control lifecycle
- Monitor execution
- Recover from failures
"""

from __future__ import annotations

# Types
from core.agents.types import (
    # Enums
    AgentType,
    AgentStatus,
    AgentHealthStatus,
    TaskStatus,
    # Classes
    AgentCapability,
    AgentManifest,
    AgentHealth,
    AgentTask,
    AgentContext,
    AgentMessage,
    RuntimeState,
    AgentMetrics,
)

# Components
from core.agents.capabilities import (
    CapabilityRegistry,
    get_capability_registry,
    reset_capability_registry,
)
from core.agents.health import (
    AgentHealthManager,
    get_health_manager,
    reset_health_manager,
)
from core.agents.context import (
    ContextManager,
    get_context_manager,
    reset_context_manager,
)
from core.agents.registry import (
    AgentRegistry,
    get_registry,
    reset_registry,
)
from core.agents.communicator import (
    AgentCommunicator,
    get_communicator,
    reset_communicator,
)
from core.agents.lifecycle import (
    LifecycleManager,
    LifecycleState,
    get_lifecycle_manager,
    reset_lifecycle_manager,
)
from core.agents.scheduler import (
    AgentScheduler,
    get_scheduler,
    reset_scheduler,
)
from core.agents.events import (
    AgentEventType,
    AgentEvent,
    AgentEventBus,
    get_event_bus,
    reset_event_bus,
)
from core.agents.metrics import (
    AgentMetricsCollector,
    get_metrics_collector,
    reset_metrics_collector,
)

# Main runtime
from core.agents.runtime import (
    CognitiveAgentRuntime,
    get_agent_runtime,
    reset_agent_runtime,
)

__all__ = [
    # Types
    "AgentType",
    "AgentStatus",
    "AgentHealthStatus",
    "TaskStatus",
    "AgentCapability",
    "AgentManifest",
    "AgentHealth",
    "AgentTask",
    "AgentContext",
    "AgentMessage",
    "RuntimeState",
    "AgentMetrics",
    # Components
    "CapabilityRegistry",
    "get_capability_registry",
    "reset_capability_registry",
    "AgentHealthManager",
    "get_health_manager",
    "reset_health_manager",
    "ContextManager",
    "get_context_manager",
    "reset_context_manager",
    "AgentRegistry",
    "get_registry",
    "reset_registry",
    "AgentCommunicator",
    "get_communicator",
    "reset_communicator",
    "LifecycleManager",
    "LifecycleState",
    "get_lifecycle_manager",
    "reset_lifecycle_manager",
    "AgentScheduler",
    "get_scheduler",
    "reset_scheduler",
    "AgentEventType",
    "AgentEvent",
    "AgentEventBus",
    "get_event_bus",
    "reset_event_bus",
    "AgentMetricsCollector",
    "get_metrics_collector",
    "reset_metrics_collector",
    # Main runtime
    "CognitiveAgentRuntime",
    "get_agent_runtime",
    "reset_agent_runtime",
]
