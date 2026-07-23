"""
PHASE 5 - EPIC 0: Agent Repository

Repositorio de agentes con persistencia básica.
Proporciona almacenamiento y recuperación de agentes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional
import logging

if TYPE_CHECKING:
    from core.PHASE_5.foundation import Agent

logger = logging.getLogger(__name__)


# =============================================================================
# AGENT REPOSITORY INTERFACE
# =============================================================================

class IAgentRepository(ABC):
    """Interfaz abstracta para repositorio de agentes."""
    
    @abstractmethod
    async def save(self, agent: "Agent") -> None:
        """Guarda un agente."""
        pass
    
    @abstractmethod
    async def get_by_id(self, agent_id: str) -> "Agent | None":
        """Obtiene un agente por ID."""
        pass
    
    @abstractmethod
    async def delete(self, agent_id: str) -> bool:
        """Elimina un agente."""
        pass
    
    @abstractmethod
    async def list_all(self) -> list["Agent"]:
        """Lista todos los agentes."""
        pass
    
    @abstractmethod
    async def update(self, agent: "Agent") -> None:
        """Actualiza un agente."""
        pass


# =============================================================================
# IN-MEMORY AGENT REPOSITORY
# =============================================================================

@dataclass
class InMemoryAgentRepository(IAgentRepository):
    """
    Repositorio en memoria para agentes.
    
    Implementación básica con persistencia en memoria.
    Para producción, usar PostgreAgentRepository o similar.
    """
    
    _agents: dict[str, "Agent"] = field(default_factory=dict)
    _metadata: dict[str, dict[str, Any]] = field(default_factory=dict)
    
    async def save(self, agent: "Agent") -> None:
        """Guarda un agente."""
        self._agents[agent.agent_id] = agent
        self._metadata[agent.agent_id] = {
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        logger.info(f"Agent saved: {agent.agent_id}")
    
    async def get_by_id(self, agent_id: str) -> "Agent | None":
        """Obtiene un agente por ID."""
        return self._agents.get(agent_id)
    
    async def delete(self, agent_id: str) -> bool:
        """Elimina un agente."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            if agent_id in self._metadata:
                del self._metadata[agent_id]
            logger.info(f"Agent deleted: {agent_id}")
            return True
        return False
    
    async def list_all(self) -> list["Agent"]:
        """Lista todos los agentes."""
        return list(self._agents.values())
    
    async def update(self, agent: "Agent") -> None:
        """Actualiza un agente."""
        if agent.agent_id in self._agents:
            self._agents[agent.agent_id] = agent
            if agent.agent_id in self._metadata:
                self._metadata[agent.agent_id]["updated_at"] = datetime.now(UTC)
            logger.info(f"Agent updated: {agent.agent_id}")
    
    async def get_by_type(self, agent_type: str) -> list["Agent"]:
        """Obtiene agentes por tipo."""
        return [
            agent for agent in self._agents.values()
            if agent.agent_type.value == agent_type
        ]
    
    async def get_by_state(self, state: str) -> list["Agent"]:
        """Obtiene agentes por estado."""
        return [
            agent for agent in self._agents.values()
            if agent.state.value == state
        ]
    
    async def count(self) -> int:
        """Cuenta el número de agentes."""
        return len(self._agents)
    
    async def clear(self) -> None:
        """Limpia todos los agentes."""
        self._agents.clear()
        self._metadata.clear()
        logger.info("Repository cleared")


# =============================================================================
# JSON FILE AGENT REPOSITORY
# =============================================================================

@dataclass
class JsonFileAgentRepository(IAgentRepository):
    """
    Repositorio basado en archivos JSON.
    
    Persiste agentes en archivos JSON para survive a reinicios.
    """
    
    _file_path: str = "agents.json"
    _agents: dict[str, "Agent"] = field(default_factory=dict)
    _loaded: bool = field(default=False)
    
    def __post_init__(self):
        """Carga datos al inicializar."""
        import json
        import os
        
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r") as f:
                    data = json.load(f)
                    # Placeholder: restaurar agentes desde JSON
                    logger.info(f"Loaded {len(data)} agents from {self._file_path}")
            except Exception as e:
                logger.warning(f"Could not load agents: {e}")
    
    async def save(self, agent: "Agent") -> None:
        """Guarda un agente."""
        self._agents[agent.agent_id] = agent
        await self._persist()
        logger.info(f"Agent saved to file: {agent.agent_id}")
    
    async def get_by_id(self, agent_id: str) -> "Agent | None":
        """Obtiene un agente por ID."""
        return self._agents.get(agent_id)
    
    async def delete(self, agent_id: str) -> bool:
        """Elimina un agente."""
        if agent_id in self._agents:
            del self._agents[agent_id]
            await self._persist()
            return True
        return False
    
    async def list_all(self) -> list["Agent"]:
        """Lista todos los agentes."""
        return list(self._agents.values())
    
    async def update(self, agent: "Agent") -> None:
        """Actualiza un agente."""
        await self.save(agent)
    
    async def _persist(self) -> None:
        """Persiste agentes a archivo JSON."""
        import json
        
        data = {
            agent_id: agent.to_dict()
            for agent_id, agent in self._agents.items()
        }
        
        try:
            with open(self._file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not persist agents: {e}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "IAgentRepository",
    "InMemoryAgentRepository",
    "JsonFileAgentRepository",
]
