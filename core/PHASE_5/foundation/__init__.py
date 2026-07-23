"""
PHASE 5 - EPIC 0: Multi-Agent Architecture Foundation

Shared Kernel de la FASE 5.
Proporciona contratos, interfaces, tipos comunes y componentes base.

Este módulo es el fundamento sobre el cual se construyen todos los demás EPICs.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
VERSION = __version__


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Types
from core.PHASE_5.foundation.types import (
    AgentState,
    AgentType,
    AgentCapability,
    AgentPriority,
    MessageType,
    MessageError,
    AgentCapabilityVO,
    AgentVersion,
    AgentMetrics,
    AgentConfig,
)

# Domain
from core.PHASE_5.foundation.domain import (
    Agent,
    AgentTask,
    TaskStatus,
    AgentMessage,
    AgentContext,
    AgentSession,
    SessionStatus,
    AgentResult,
    ConfidenceLevel,
)

# Contracts
from core.PHASE_5.foundation.contracts import (
    IAgent,
    IAgentRegistry,
    IMessageBroker,
    ILifecycleManager,
    IAgentOrchestrator,
    IAgentFactory,
    IEventBus,
    AgentEvent,
)

# Events
from core.PHASE_5.foundation.events import (
    AgentEventType,
    EventSeverity,
    EventSubscriber,
    EventBus,
    EventFactory,
)

# Messaging
from core.PHASE_5.foundation.messaging import (
    MessageBroker,
    MessageBuilder,
)

# Lifecycle
from core.PHASE_5.foundation.lifecycle import (
    AgentLifecycleManager,
    StateValidator,
    VALID_TRANSITIONS,
)

# Registry
from core.PHASE_5.foundation.registry import (
    AgentRegistry,
    AgentLookup,
)

# Context
from core.PHASE_5.foundation.context import (
    ContextManager,
    SessionManager,
)

# Gateways
from core.PHASE_5.foundation.gateways import (
    PHASE1Gateway,
    PHASE2Gateway,
    PHASE3Gateway,
    PHASE4Gateway,
    MultiPhaseGateway,
)


# =============================================================================
# BASE AGENT - Clase base abstracta para agentes
# =============================================================================

class BaseAgent:
    """Clase base abstracta para todos los agentes."""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        name: str = "",
        description: str = "",
        capabilities: list[AgentCapabilityVO] | None = None,
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name or f"{agent_type.value}_agent"
        self.description = description
        
        # State
        self.state = AgentState.INITIAL
        self.current_task_id: str | None = None
        
        # Capabilities
        self.capabilities = capabilities or []
        
        # Lifecycle manager (inyectado)
        self._lifecycle: AgentLifecycleManager | None = None
        
        # Message broker (inyectado)
        self._broker: MessageBroker | None = None
    
    @property
    def agent_id(self) -> str:
        return self._agent_id
    
    @agent_id.setter
    def agent_id(self, value: str):
        self._agent_id = value
    
    @property
    def state(self) -> AgentState:
        return self._state
    
    @state.setter
    def state(self, value: AgentState):
        self._state = value
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type.value}, state={self.state.value})>"
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Verifica si tiene una capability."""
        return any(c.capability == capability for c in self.capabilities)
    
    async def initialize(self) -> None:
        """Inicializa el agente. Override en subclases."""
        self._state = AgentState.IDLE
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea. Override en subclases."""
        from datetime import UTC, datetime
        
        result = AgentResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            success=True,
            output={},
        )
        
        return result
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage | None:
        """Maneja un mensaje. Override en subclases."""
        return None
    
    async def shutdown(self) -> None:
        """Detiene el agente. Override en subclases."""
        self._state = AgentState.STOPPED
    
    def set_lifecycle(self, lifecycle: AgentLifecycleManager) -> None:
        """Inyecta lifecycle manager."""
        self._lifecycle = lifecycle
    
    def set_broker(self, broker: MessageBroker) -> None:
        """Inyecta message broker."""
        self._broker = broker


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "VERSION",
    # Enums - Types
    "AgentState",
    "AgentType",
    "AgentCapability",
    "AgentPriority",
    "MessageType",
    "MessageError",
    # Value Objects
    "AgentCapabilityVO",
    "AgentVersion",
    "AgentMetrics",
    "AgentConfig",
    # Domain
    "Agent",
    "AgentTask",
    "TaskStatus",
    "AgentMessage",
    "AgentContext",
    "AgentSession",
    "SessionStatus",
    "AgentResult",
    "ConfidenceLevel",
    # Contracts
    "IAgent",
    "IAgentRegistry",
    "IMessageBroker",
    "ILifecycleManager",
    "IAgentOrchestrator",
    "IAgentFactory",
    "IEventBus",
    "AgentEvent",
    # Events
    "AgentEventType",
    "EventSeverity",
    "EventSubscriber",
    "EventBus",
    "EventFactory",
    # Messaging
    "MessageBroker",
    "MessageBuilder",
    # Lifecycle
    "AgentLifecycleManager",
    "StateValidator",
    "VALID_TRANSITIONS",
    # Registry
    "AgentRegistry",
    "AgentLookup",
    # Context
    "ContextManager",
    "SessionManager",
    # Base
    "BaseAgent",
    # Gateways
    "PHASE1Gateway",
    "PHASE2Gateway",
    "PHASE3Gateway",
    "PHASE4Gateway",
    "MultiPhaseGateway",
]
