"""
PHASE 5 - EPIC 0: Agent Contracts

Contratos (interfaces) para el sistema multiagente:
- IAgent
- IAgentRegistry
- IAgentOrchestrator
- IMessageBroker
- ILifecycleManager
- IAgentFactory
"""

from __future__ import annotations

from typing import Protocol, Optional, Callable
from abc import ABC, abstractmethod

from core.PHASE_5.foundation.types import (
    AgentState,
    AgentType,
    AgentCapability,
    AgentPriority,
    MessageType,
)
from core.PHASE_5.foundation.domain import (
    Agent,
    AgentTask,
    AgentMessage,
    AgentContext,
    AgentSession,
    AgentResult,
)


# =============================================================================
# IAgent - Protocolo para agentes
# =============================================================================

class IAgent(Protocol):
    """Protocolo base para agentes."""
    
    @property
    def agent_id(self) -> str:
        """ID único del agente."""
        ...
    
    @property
    def agent_type(self) -> AgentType:
        """Tipo de agente."""
        ...
    
    @property
    def state(self) -> AgentState:
        """Estado actual del agente."""
        ...
    
    @property
    def capabilities(self) -> list[AgentCapability]:
        """Capabilities del agente."""
        ...
    
    async def initialize(self) -> None:
        """Inicializa el agente."""
        ...
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea."""
        ...
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage | None:
        """Maneja un mensaje entrante."""
        ...
    
    async def shutdown(self) -> None:
        """Detiene el agente."""
        ...


# =============================================================================
# IAgentRegistry - Protocolo para registro de agentes
# =============================================================================

class IAgentRegistry(Protocol):
    """Protocolo para registro de agentes."""
    
    async def register(self, agent: Agent) -> bool:
        """Registra un agente."""
        ...
    
    async def unregister(self, agent_id: str) -> bool:
        """Desregistra un agente."""
        ...
    
    async def get(self, agent_id: str) -> Optional[Agent]:
        """Obtiene un agente por ID."""
        ...
    
    async def get_by_type(self, agent_type: AgentType) -> list[Agent]:
        """Obtiene agentes por tipo."""
        ...
    
    async def get_by_capability(self, capability: AgentCapability) -> list[Agent]:
        """Obtiene agentes con una capability."""
        ...
    
    async def list_all(self) -> list[Agent]:
        """Lista todos los agentes."""
        ...
    
    async def exists(self, agent_id: str) -> bool:
        """Verifica si existe un agente."""
        ...


# =============================================================================
# IMessageBroker - Protocolo para broker de mensajes
# =============================================================================

class IMessageBroker(Protocol):
    """Protocolo para broker de mensajes entre agentes."""
    
    async def send(self, message: AgentMessage) -> bool:
        """Envía un mensaje."""
        ...
    
    async def publish(self, topic: str, message: AgentMessage) -> bool:
        """Publica un mensaje a un topic."""
        ...
    
    async def subscribe(
        self,
        agent_id: str,
        topics: list[str],
    ) -> bool:
        """Suscribe un agente a topics."""
        ...
    
    async def unsubscribe(
        self,
        agent_id: str,
        topics: list[str],
    ) -> bool:
        """Desuscribe un agente de topics."""
        ...
    
    async def receive(
        self,
        agent_id: str,
        timeout: int = 30,
    ) -> Optional[AgentMessage]:
        """Recibe un mensaje para un agente."""
        ...
    
    async def send_and_wait(
        self,
        message: AgentMessage,
        timeout: int = 30,
    ) -> Optional[AgentMessage]:
        """Envía un mensaje y espera respuesta."""
        ...
    
    async def get_queue_size(self, agent_id: str) -> int:
        """Obtiene tamaño de cola de un agente."""
        ...


# =============================================================================
# ILifecycleManager - Protocolo para gestión de ciclo de vida
# =============================================================================

class ILifecycleManager(Protocol):
    """Protocolo para gestión de ciclo de vida de agentes."""
    
    async def create_agent(
        self,
        agent_type: AgentType,
        config: dict,
    ) -> str:
        """Crea un nuevo agente."""
        ...
    
    async def destroy_agent(self, agent_id: str) -> bool:
        """Destruye un agente."""
        ...
    
    async def get_state(self, agent_id: str) -> AgentState:
        """Obtiene estado de un agente."""
        ...
    
    async def transition(
        self,
        agent_id: str,
        new_state: AgentState,
    ) -> bool:
        """Transiciona un agente a un nuevo estado."""
        ...
    
    async def start_agent(self, agent_id: str) -> bool:
        """Inicia un agente."""
        ...
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Detiene un agente."""
        ...


# =============================================================================
# IAgentOrchestrator - Protocolo para orquestador
# =============================================================================

class IAgentOrchestrator(Protocol):
    """Protocolo para orquestador de agentes."""
    
    async def process_request(
        self,
        request: dict,
        context: AgentContext,
    ) -> AgentResult:
        """Procesa un request del usuario."""
        ...
    
    async def select_agents(
        self,
        task: AgentTask,
    ) -> list[str]:
        """Selecciona agentes para una tarea."""
        ...
    
    async def coordinate(
        self,
        task: AgentTask,
        agent_ids: list[str],
    ) -> AgentResult:
        """Coordina ejecución entre agentes."""
        ...
    
    async def synthesize_response(
        self,
        results: list[AgentResult],
    ) -> AgentResult:
        """Sintetiza respuesta final."""
        ...


# =============================================================================
# IAgentFactory - Protocolo para fábrica de agentes
# =============================================================================

class IAgentFactory(Protocol):
    """Protocolo para fábrica de agentes."""
    
    async def create_agent(
        self,
        agent_type: AgentType,
        config: dict,
    ) -> Agent:
        """Crea un agente del tipo especificado."""
        ...
    
    def get_available_types(self) -> list[AgentType]:
        """Obtiene tipos de agente disponibles."""
        ...
    
    def get_default_config(self, agent_type: AgentType) -> dict:
        """Obtiene configuración por defecto para un tipo."""
        ...


# =============================================================================
# IEventBus - Protocolo para bus de eventos
# =============================================================================

class IEventBus(Protocol):
    """Protocolo para bus de eventos."""
    
    async def publish(self, event: AgentEvent) -> bool:
        """Publica un evento."""
        ...
    
    async def subscribe(
        self,
        agent_id: str,
        event_types: list[str],
        handler: Callable,
    ) -> bool:
        """Suscribe a tipos de eventos."""
        ...
    
    async def unsubscribe(
        self,
        agent_id: str,
        event_types: list[str],
    ) -> bool:
        """Desuscribe de tipos de eventos."""
        ...


# =============================================================================
# AgentEvent - Evento del sistema
# =============================================================================

class AgentEvent:
    """Evento del sistema multiagente."""
    
    def __init__(
        self,
        event_type: str,
        agent_id: str,
        payload: dict | None = None,
    ):
        self.event_type = event_type
        self.agent_id = agent_id
        self.payload = payload or {}
        from datetime import UTC, datetime
        self.timestamp = datetime.now(UTC)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocols
    "IAgent",
    "IAgentRegistry",
    "IMessageBroker",
    "ILifecycleManager",
    "IAgentOrchestrator",
    "IAgentFactory",
    "IEventBus",
    # Event
    "AgentEvent",
]
