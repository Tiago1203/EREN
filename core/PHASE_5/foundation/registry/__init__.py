"""
PHASE 5 - EPIC 0: Agent Registry

Registro centralizado de agentes.
"""

from __future__ import annotations

from typing import Optional
import threading

from core.PHASE_5.foundation.types import (
    AgentType,
    AgentCapability,
)
from core.PHASE_5.foundation.domain import Agent


# =============================================================================
# AGENT REGISTRY - Registro de agentes
# =============================================================================

class AgentRegistry:
    """Registro centralizado de agentes."""
    
    def __init__(self):
        # Agentes por ID
        self._agents: dict[str, Agent] = {}
        
        # Índices secundarios
        self._by_type: dict[AgentType, set[str]] = {}
        self._by_capability: dict[AgentCapability, set[str]] = {}
        
        # Lock para thread safety
        self._lock = threading.RLock()
    
    async def register(self, agent: Agent) -> bool:
        """Registra un agente."""
        with self._lock:
            if agent.agent_id in self._agents:
                return False
            
            # Registrar agente
            self._agents[agent.agent_id] = agent
            
            # Indexar por tipo
            if agent.agent_type not in self._by_type:
                self._by_type[agent.agent_type] = set()
            self._by_type[agent.agent_type].add(agent.agent_id)
            
            # Indexar por capabilities
            for cap in agent.capabilities:
                if cap.capability not in self._by_capability:
                    self._by_capability[cap.capability] = set()
                self._by_capability[cap.capability].add(agent.agent_id)
            
            return True
    
    async def unregister(self, agent_id: str) -> bool:
        """Desregistra un agente."""
        with self._lock:
            if agent_id not in self._agents:
                return False
            
            agent = self._agents[agent_id]
            
            # Remover de índices
            self._by_type.get(agent.agent_type, set()).discard(agent_id)
            for cap in agent.capabilities:
                self._by_capability.get(cap.capability, set()).discard(agent_id)
            
            # Remover agente
            del self._agents[agent_id]
            
            return True
    
    async def get(self, agent_id: str) -> Optional[Agent]:
        """Obtiene un agente por ID."""
        with self._lock:
            return self._agents.get(agent_id)
    
    async def get_by_type(self, agent_type: AgentType) -> list[Agent]:
        """Obtiene agentes por tipo."""
        with self._lock:
            agent_ids = self._by_type.get(agent_type, set())
            return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    async def get_by_capability(
        self,
        capability: AgentCapability,
    ) -> list[Agent]:
        """Obtiene agentes con una capability específica."""
        with self._lock:
            agent_ids = self._by_capability.get(capability, set())
            return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    async def get_by_capabilities(
        self,
        capabilities: list[AgentCapability],
        match_all: bool = False,
    ) -> list[Agent]:
        """Obtiene agentes con capabilities específicas.
        
        Args:
            capabilities: Lista de capabilities requeridas
            match_all: Si True, el agente debe tener todas las capabilities
        """
        with self._lock:
            if match_all:
                # Agentes que tienen TODAS las capabilities
                result = []
                for agent in self._agents.values():
                    agent_caps = {c.capability for c in agent.capabilities}
                    if all(cap in agent_caps for cap in capabilities):
                        result.append(agent)
                return result
            else:
                # Agentes que tienen AL MENOS UNA capability
                agent_ids = set()
                for cap in capabilities:
                    agent_ids.update(self._by_capability.get(cap, set()))
                return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    async def list_all(self) -> list[Agent]:
        """Lista todos los agentes registrados."""
        with self._lock:
            return list(self._agents.values())
    
    async def exists(self, agent_id: str) -> bool:
        """Verifica si existe un agente."""
        with self._lock:
            return agent_id in self._agents
    
    async def count(self) -> int:
        """Cuenta agentes registrados."""
        with self._lock:
            return len(self._agents)
    
    async def count_by_type(self, agent_type: AgentType) -> int:
        """Cuenta agentes por tipo."""
        with self._lock:
            return len(self._by_type.get(agent_type, set()))
    
    async def count_by_capability(self, capability: AgentCapability) -> int:
        """Cuenta agentes por capability."""
        with self._lock:
            return len(self._by_capability.get(capability, set()))
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del registro."""
        with self._lock:
            return {
                "total_agents": len(self._agents),
                "by_type": {
                    atype.value: len(agents)
                    for atype, agents in self._by_type.items()
                },
                "by_capability": {
                    cap.value: len(agents)
                    for cap, agents in self._by_capability.items()
                },
            }


# =============================================================================
# AGENT LOOKUP - Helper para lookup rápido
# =============================================================================

class AgentLookup:
    """Helper para lookup rápido de agentes."""
    
    def __init__(self, registry: AgentRegistry):
        self._registry = registry
    
    async def find_best_for_task(
        self,
        required_capabilities: list[AgentCapability],
    ) -> Optional[Agent]:
        """Encuentra el mejor agente para una tarea.
        
        Estrategia:
        1. Filtrar agentes con las capabilities requeridas
        2. Ordenar por nivel de skill
        3. Seleccionar el primero disponible
        """
        agents = await self._registry.get_by_capabilities(
            required_capabilities,
            match_all=True,
        )
        
        if not agents:
            return None
        
        # Filtrar disponibles
        available = [a for a in agents if a.is_available]
        
        if not available:
            return None
        
        # Ordenar por nivel promedio de capabilities
        def avg_capability_level(agent: Agent) -> float:
            if not agent.capabilities:
                return 0.0
            return sum(c.level for c in agent.capabilities) / len(agent.capabilities)
        
        available.sort(key=avg_capability_level, reverse=True)
        
        return available[0]
    
    async def find_available_by_type(
        self,
        agent_type: AgentType,
    ) -> Optional[Agent]:
        """Encuentra un agente disponible de un tipo específico."""
        agents = await self._registry.get_by_type(agent_type)
        
        available = [a for a in agents if a.is_available]
        
        if not available:
            return None
        
        return available[0]
    
    async def find_any_available(
        self,
        agent_types: list[AgentType],
    ) -> Optional[Agent]:
        """Encuentra cualquier agente disponible de los tipos especificados."""
        for agent_type in agent_types:
            agent = await self.find_available_by_type(agent_type)
            if agent:
                return agent
        return None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AgentRegistry",
    "AgentLookup",
]
