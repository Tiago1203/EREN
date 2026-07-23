"""
PHASE 5 - EPIC 0: Agent Lifecycle

Gestión del ciclo de vida de agentes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional
import uuid

from core.PHASE_5.foundation.types import (
    AgentState,
    AgentType,
    AgentCapability,
    AgentCapabilityVO,
    AgentVersion,
)
from core.PHASE_5.foundation.domain import Agent
from core.PHASE_5.foundation.events import EventBus, EventFactory, AgentEventType


# =============================================================================
# VALID TRANSITIONS - Transiciones válidas de estado
# =============================================================================

VALID_TRANSITIONS: dict[AgentState, list[AgentState]] = {
    AgentState.INITIAL: [AgentState.IDLE, AgentState.INITIALIZING],
    AgentState.INITIALIZING: [AgentState.IDLE, AgentState.FAILED],
    AgentState.IDLE: [
        AgentState.RUNNING,
        AgentState.STOPPED,
        AgentState.INITIALIZING,
    ],
    AgentState.RUNNING: [
        AgentState.COMPLETED,
        AgentState.WAITING,
        AgentState.FAILED,
        AgentState.IDLE,
    ],
    AgentState.WAITING: [
        AgentState.RUNNING,
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.IDLE,
    ],
    AgentState.COMPLETED: [AgentState.IDLE, AgentState.STOPPED],
    AgentState.FAILED: [AgentState.IDLE, AgentState.STOPPED],
    AgentState.STOPPED: [AgentState.INITIALIZING],
}


# =============================================================================
# LIFECYCLE MANAGER - Gestor de ciclo de vida
# =============================================================================

class AgentLifecycleManager:
    """Gestor de ciclo de vida de agentes."""
    
    def __init__(self, event_bus: EventBus | None = None):
        self._agents: dict[str, Agent] = {}
        self._event_bus = event_bus or EventBus()
        self._state_history: dict[str, list[tuple[AgentState, datetime]]] = {}
    
    async def register_agent(self, agent: Agent) -> bool:
        """Registra un agente."""
        if agent.agent_id in self._agents:
            return False
        
        self._agents[agent.agent_id] = agent
        self._state_history[agent.agent_id] = [
            (agent.state, datetime.now(UTC))
        ]
        
        # Publicar evento
        await self._event_bus.publish(
            EventFactory.agent_registered(agent.agent_id)
        )
        
        return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Desregistra un agente."""
        if agent_id not in self._agents:
            return False
        
        agent = self._agents[agent_id]
        
        # Forzar estado a STOPPED
        await self.transition(agent_id, AgentState.STOPPED)
        
        del self._agents[agent_id]
        del self._state_history[agent_id]
        
        return True
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Obtiene un agente."""
        return self._agents.get(agent_id)
    
    async def get_state(self, agent_id: str) -> AgentState:
        """Obtiene estado de un agente."""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        return agent.state
    
    async def transition(
        self,
        agent_id: str,
        new_state: AgentState,
    ) -> bool:
        """Transiciona un agente a un nuevo estado."""
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        current_state = agent.state
        
        # Validar transición
        if new_state not in VALID_TRANSITIONS.get(current_state, []):
            return False
        
        # Actualizar estado
        old_state = agent.state
        agent.state = new_state
        agent.updated_at = datetime.now(UTC)
        
        # Registrar en historial
        self._state_history[agent_id].append((new_state, datetime.now(UTC)))
        
        # Publicar eventos según transición
        if new_state == AgentState.RUNNING:
            await self._event_bus.publish(
                EventFactory.agent_started(agent_id)
            )
        elif new_state == AgentState.FAILED:
            await self._event_bus.publish(
                EventFactory.agent_failed(agent_id, "State transition to FAILED")
            )
        elif new_state == AgentState.COMPLETED:
            await self._event_bus.publish(
                EventFactory.agent_completed(agent_id, agent.current_task_id or "")
            )
        
        return True
    
    async def initialize_agent(self, agent_id: str) -> bool:
        """Inicializa un agente."""
        await self.transition(agent_id, AgentState.INITIALIZING)
        await self.transition(agent_id, AgentState.IDLE)
        return True
    
    async def start_task(
        self,
        agent_id: str,
        task_id: str,
    ) -> bool:
        """Marca que un agente inicia una tarea."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        
        agent.current_task_id = task_id
        return await self.transition(agent_id, AgentState.RUNNING)
    
    async def complete_task(
        self,
        agent_id: str,
        task_id: str,
    ) -> bool:
        """Marca que un agente completa una tarea."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        
        agent.current_task_id = None
        agent.metrics.tasks_completed += 1
        
        return await self.transition(agent_id, AgentState.COMPLETED)
    
    async def fail_task(
        self,
        agent_id: str,
        task_id: str,
        error: str,
    ) -> bool:
        """Marca que un agente falla una tarea."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        
        agent.current_task_id = None
        agent.metrics.tasks_failed += 1
        
        await self._event_bus.publish(
            EventFactory.agent_failed(agent_id, error)
        )
        
        return await self.transition(agent_id, AgentState.FAILED)
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Detiene un agente."""
        return await self.transition(agent_id, AgentState.STOPPED)
    
    def get_state_history(
        self,
        agent_id: str,
    ) -> list[tuple[AgentState, datetime]]:
        """Obtiene historial de estados de un agente."""
        return self._state_history.get(agent_id, [])
    
    def get_all_agents(self) -> list[Agent]:
        """Obtiene todos los agentes registrados."""
        return list(self._agents.values())
    
    def get_agents_by_state(
        self,
        state: AgentState,
    ) -> list[Agent]:
        """Obtiene agentes por estado."""
        return [
            a for a in self._agents.values()
            if a.state == state
        ]


# =============================================================================
# STATE VALIDATOR - Validador de estado
# =============================================================================

class StateValidator:
    """Validador de transiciones de estado."""
    
    @staticmethod
    def can_transition(
        current_state: AgentState,
        new_state: AgentState,
    ) -> bool:
        """Verifica si una transición es válida."""
        return new_state in VALID_TRANSITIONS.get(current_state, [])
    
    @staticmethod
    def get_valid_transitions(
        current_state: AgentState,
    ) -> list[AgentState]:
        """Obtiene transiciones válidas desde un estado."""
        return VALID_TRANSITIONS.get(current_state, [])
    
    @staticmethod
    def is_terminal_state(state: AgentState) -> bool:
        """Verifica si un estado es terminal."""
        return state in [AgentState.STOPPED]
    
    @staticmethod
    def is_active_state(state: AgentState) -> bool:
        """Verifica si un estado es activo."""
        return state in [
            AgentState.INITIALIZING,
            AgentState.RUNNING,
            AgentState.WAITING,
        ]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AgentLifecycleManager",
    "StateValidator",
    "VALID_TRANSITIONS",
]
