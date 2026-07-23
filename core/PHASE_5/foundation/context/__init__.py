"""
PHASE 5 - EPIC 0: Agent Context & Session

Gestión de contexto y sesiones de agente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import uuid

from core.PHASE_5.foundation.domain import (
    AgentContext,
    AgentSession,
    SessionStatus,
    AgentTask,
    AgentMessage,
)


# =============================================================================
# CONTEXT MANAGER - Gestor de contexto
# =============================================================================

class ContextManager:
    """Gestor de contextos compartidos entre agentes."""
    
    def __init__(self):
        self._contexts: dict[str, AgentContext] = {}
    
    async def create_context(self, session_id: str) -> AgentContext:
        """Crea un nuevo contexto para una sesión."""
        context = AgentContext(
            context_id=str(uuid.uuid4()),
            session_id=session_id,
        )
        self._contexts[context.context_id] = context
        return context
    
    async def get_context(self, context_id: str) -> Optional[AgentContext]:
        """Obtiene un contexto por ID."""
        return self._contexts.get(context_id)
    
    async def get_context_by_session(self, session_id: str) -> Optional[AgentContext]:
        """Obtiene el contexto de una sesión."""
        for context in self._contexts.values():
            if context.session_id == session_id:
                return context
        return None
    
    async def update_context(
        self,
        context_id: str,
        data: dict,
    ) -> bool:
        """Actualiza datos del contexto."""
        context = self._contexts.get(context_id)
        if not context:
            return False
        
        for key, value in data.items():
            context.set_value(key, value)
        
        context.updated_at = datetime.now(UTC)
        return True
    
    async def add_participant(
        self,
        context_id: str,
        agent_id: str,
    ) -> bool:
        """Agrega un participante al contexto."""
        context = self._contexts.get(context_id)
        if not context:
            return False
        
        context.add_agent(agent_id)
        return True
    
    async def remove_participant(
        self,
        context_id: str,
        agent_id: str,
    ) -> bool:
        """Remueve un participante del contexto."""
        context = self._contexts.get(context_id)
        if not context:
            return False
        
        context.remove_agent(agent_id)
        return True
    
    async def add_message(
        self,
        context_id: str,
        message: AgentMessage,
    ) -> bool:
        """Agrega un mensaje al historial del contexto."""
        context = self._contexts.get(context_id)
        if not context:
            return False
        
        context.message_history.append(message)
        context.updated_at = datetime.now(UTC)
        return True
    
    async def add_task(
        self,
        context_id: str,
        task: AgentTask,
    ) -> bool:
        """Agrega una tarea al historial del contexto."""
        context = self._contexts.get(context_id)
        if not context:
            return False
        
        context.task_history.append(task)
        context.updated_at = datetime.now(UTC)
        return True
    
    async def delete_context(self, context_id: str) -> bool:
        """Elimina un contexto."""
        if context_id in self._contexts:
            del self._contexts[context_id]
            return True
        return False
    
    def list_contexts(self) -> list[AgentContext]:
        """Lista todos los contextos."""
        return list(self._contexts.values())
    
    def list_contexts_by_session(self, session_id: str) -> list[AgentContext]:
        """Lista contextos de una sesión."""
        return [
            c for c in self._contexts.values()
            if c.session_id == session_id
        ]


# =============================================================================
# SESSION MANAGER - Gestor de sesiones
# =============================================================================

class SessionManager:
    """Gestor de sesiones de agente."""
    
    def __init__(self):
        self._sessions: dict[str, AgentSession] = {}
        self._sessions_by_agent: dict[str, str] = {}  # agent_id -> session_id
    
    async def create_session(
        self,
        agent_id: str,
        name: str = "",
        description: str = "",
    ) -> AgentSession:
        """Crea una nueva sesión."""
        session = AgentSession(
            session_id=str(uuid.uuid4()),
            agent_id=agent_id,
            name=name or f"Session-{agent_id}",
            description=description,
        )
        
        self._sessions[session.session_id] = session
        self._sessions_by_agent[agent_id] = session.session_id
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Obtiene una sesión por ID."""
        return self._sessions.get(session_id)
    
    async def get_session_by_agent(
        self,
        agent_id: str,
    ) -> Optional[AgentSession]:
        """Obtiene la sesión activa de un agente."""
        session_id = self._sessions_by_agent.get(agent_id)
        if session_id:
            return self._sessions.get(session_id)
        return None
    
    async def close_session(self, session_id: str) -> bool:
        """Cierra una sesión."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.status = SessionStatus.CLOSED
        session.closed_at = datetime.now(UTC)
        
        # Remover de índice
        self._sessions_by_agent.pop(session.agent_id, None)
        
        return True
    
    async def add_task_to_session(
        self,
        session_id: str,
        task: AgentTask,
    ) -> bool:
        """Agrega una tarea a la sesión."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.add_task(task)
        return True
    
    async def set_active_task(
        self,
        session_id: str,
        task_id: str,
    ) -> bool:
        """Establece la tarea activa de la sesión."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.active_task_id = task_id
        session.last_activity = datetime.now(UTC)
        return True
    
    async def update_activity(self, session_id: str) -> bool:
        """Actualiza última actividad de la sesión."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.last_activity = datetime.now(UTC)
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        self._sessions_by_agent.pop(session.agent_id, None)
        del self._sessions[session_id]
        return True
    
    def list_active_sessions(self) -> list[AgentSession]:
        """Lista sesiones activas."""
        return [
            s for s in self._sessions.values()
            if s.is_active
        ]
    
    def list_sessions_by_agent(self, agent_id: str) -> list[AgentSession]:
        """Lista todas las sesiones de un agente."""
        return [
            s for s in self._sessions.values()
            if s.agent_id == agent_id
        ]
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas de sesiones."""
        active = len([s for s in self._sessions.values() if s.is_active])
        closed = len([s for s in self._sessions.values() if s.status == SessionStatus.CLOSED])
        
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": active,
            "closed_sessions": closed,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ContextManager",
    "SessionManager",
]
