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

# Components
from core.PHASE_2.agents.capabilities import (
    CapabilityRegistry,
    get_capability_registry,
    reset_capability_registry,
)
from core.PHASE_2.agents.communicator import (
    AgentCommunicator,
    get_communicator,
    reset_communicator,
)
from core.PHASE_2.agents.context import (
    ContextManager,
    get_context_manager,
    reset_context_manager,
)
from core.PHASE_2.agents.events import (
    AgentEvent,
    AgentEventBus,
    AgentEventType,
    get_event_bus,
    reset_event_bus,
)
from core.PHASE_2.agents.health import (
    AgentHealthManager,
    get_health_manager,
    reset_health_manager,
)
from core.PHASE_2.agents.lifecycle import (
    LifecycleManager,
    LifecycleState,
    get_lifecycle_manager,
    reset_lifecycle_manager,
)
from core.PHASE_2.agents.metrics import (
    AgentMetricsCollector,
    get_metrics_collector,
    reset_metrics_collector,
)
from core.PHASE_2.agents.registry import (
    AgentRegistry,
    get_registry,
    reset_registry,
)

# Main runtime
from core.PHASE_2.agents.runtime import (
    CognitiveAgentRuntime,
    get_agent_runtime,
    reset_agent_runtime,
)
from core.PHASE_2.agents.scheduler import (
    AgentScheduler,
    get_scheduler,
    reset_scheduler,
)

# Types
from core.PHASE_2.agents.types import (
    # Classes
    AgentCapability,
    AgentContext,
    AgentHealth,
    AgentHealthStatus,
    AgentManifest,
    AgentMessage,
    AgentMetrics,
    AgentStatus,
    AgentTask,
    # Enums
    AgentType,
    RuntimeState,
    TaskStatus,
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
