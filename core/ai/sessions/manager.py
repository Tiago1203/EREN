"""Session Manager - Gestor de sesiones."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from core.ai.sessions.models import (
    ConversationLimit,
    Message,
    Session,
    SessionContext,
    SessionEventRecord,
    SessionEvent as SessionEventEnum,
    SessionStats,
    SessionStatus,
    TokenBudget,
)


class SessionManager:
    """
    Gestor de sesiones de IA.
    
    Maneja:
    - Creación y cierre de sesiones
    - Gestión de mensajes
    - Token budgets
    - Expiración
    - Resume de sesiones
    """

    def __init__(
        self,
        default_limits: ConversationLimit | None = None,
        default_budget: int = 100000,
    ) -> None:
        self._sessions: dict[str, Session] = {}
        self._user_sessions: dict[str, set[str]] = {}  # user_id -> session_ids
        self._default_limits = default_limits or ConversationLimit()
        self._default_budget = default_budget
    
    # ========== Session Lifecycle ==========
    
    def create_session(
        self,
        user_id: str,
        tenant_id: str | None = None,
        context: SessionContext | None = None,
        budget: int | None = None,
        expires_in_hours: int = 24,
    ) -> Session:
        """
        Crea una nueva sesión.
        
        Args:
            user_id: ID del usuario
            tenant_id: ID del tenant
            context: Contexto de la sesión
            budget: Presupuesto de tokens
            expires_in_hours: Horas hasta expiración
            
        Returns:
            Sesión creada
        """
        # Verificar límites de sesiones por usuario
        if user_id in self._user_sessions:
            user_session_count = len(self._user_sessions[user_id])
            if user_session_count >= self._default_limits.max_sessions_per_user:
                # Cerrar la sesión más antigua
                oldest = min(
                    self._user_sessions[user_id],
                    key=lambda sid: self._sessions[sid].created_at,
                )
                self.close_session(oldest)
        
        # Verificar límite total
        if len(self._sessions) >= self._default_limits.max_sessions_total:
            # Cerrar la sesión más antigua
            oldest = min(
                self._sessions.keys(),
                key=lambda sid: self._sessions[sid].created_at,
            )
            self.close_session(oldest)
        
        session_id = str(uuid.uuid4())
        
        # Crear contexto
        if context is None:
            context = SessionContext(
                session_id=session_id,
                user_id=user_id,
                tenant_id=tenant_id,
            )
        
        # Crear presupuesto
        token_budget = TokenBudget(
            total_limit=budget or self._default_budget,
        )
        
        session = Session(
            id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
            context=context,
            token_budget=token_budget,
            limits=self._default_limits,
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
        )
        
        self._sessions[session_id] = session
        
        if user_id not in self._user_sessions:
            self._user_sessions[user_id] = set()
        self._user_sessions[user_id].add(session_id)
        
        # Registrar evento
        self._add_event(session, SessionEventEnum.CREATED)
        
        return session
    
    def get_session(self, session_id: str) -> Session | None:
        """Obtiene una sesión por ID."""
        session = self._sessions.get(session_id)
        
        if session and session.is_expired:
            session.expire()
        
        return session
    
    def close_session(self, session_id: str) -> bool:
        """Cierra una sesión."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.close()
        self._add_event(session, SessionEventEnum.CLOSED)
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        user_id = session.user_id
        del self._sessions[session_id]
        
        if user_id in self._user_sessions:
            self._user_sessions[user_id].discard(session_id)
        
        return True
    
    # ========== Session State ==========
    
    def pause_session(self, session_id: str) -> bool:
        """Pausa una sesión."""
        session = self.get_session(session_id)
        if not session or not session.is_active:
            return False
        
        session.pause()
        self._add_event(session, SessionEventEnum.PAUSED)
        return True
    
    def resume_session(self, session_id: str) -> bool:
        """Reanuda una sesión."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if not session.can_resume():
            return False
        
        session.resume()
        self._add_event(session, SessionEventEnum.RESUMED)
        return True
    
    # ========== Messages ==========
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> Message | None:
        """Agrega un mensaje a la sesión."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Verificar límites
        can_continue, error = session.check_limits()
        if not can_continue:
            return None
        
        # Verificar presupuesto de tokens
        if tokens > 0 and not session.token_budget.consume(tokens):
            return None
        
        message = Message(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            tokens=tokens,
            metadata=metadata or {},
        )
        
        if session.add_message(message):
            event_type = (
                SessionEventEnum.MESSAGE_SENT if role == "user"
                else SessionEventEnum.MESSAGE_RECEIVED
            )
            self._add_event(session, event_type, message_id=message.id, tokens=tokens)
            return message
        
        return None
    
    def get_messages(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> list[Message]:
        """Obtiene los mensajes de una sesión."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_context_messages(
        self,
        session_id: str,
    ) -> list[Message]:
        """Obtiene los mensajes de contexto."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        return session.get_context_messages()
    
    # ========== Budget ==========
    
    def get_budget(self, session_id: str) -> TokenBudget | None:
        """Obtiene el presupuesto de tokens."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Verificar reset diario
        session.token_budget.check_daily_reset()
        return session.token_budget
    
    def update_budget(
        self,
        session_id: str,
        new_limit: int,
    ) -> bool:
        """Actualiza el límite del presupuesto."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.token_budget.total_limit = new_limit
        return True
    
    def add_budget(
        self,
        session_id: str,
        tokens: int,
    ) -> bool:
        """Agrega tokens al presupuesto."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.token_budget.total_limit += tokens
        return True
    
    # ========== Queries ==========
    
    def list_user_sessions(self, user_id: str) -> list[Session]:
        """Lista las sesiones de un usuario."""
        session_ids = self._user_sessions.get(user_id, set())
        sessions = []
        
        for sid in session_ids:
            session = self.get_session(sid)
            if session and session.is_active:
                sessions.append(session)
        
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)
    
    def list_active_sessions(
        self,
        tenant_id: str | None = None,
    ) -> list[Session]:
        """Lista las sesiones activas."""
        sessions = [
            s for s in self._sessions.values()
            if s.is_active
        ]
        
        if tenant_id:
            sessions = [s for s in sessions if s.tenant_id == tenant_id]
        
        return sorted(sessions, key=lambda s: s.last_activity_at, reverse=True)
    
    def get_session_count(self, user_id: str | None = None) -> int:
        """Cuenta sesiones."""
        if user_id:
            return len(self._user_sessions.get(user_id, set()))
        return len(self._sessions)
    
    # ========== Maintenance ==========
    
    def cleanup_expired_sessions(self) -> int:
        """Limpia las sesiones expiradas."""
        count = 0
        expired_ids = []
        
        for session_id, session in self._sessions.items():
            if session.is_expired:
                session.expire()
                expired_ids.append(session_id)
                count += 1
        
        return count
    
    def cleanup_idle_sessions(self, timeout_minutes: int | None = None) -> int:
        """Limpia sesiones inactivas."""
        timeout = timeout_minutes or self._default_limits.inactivity_timeout_minutes
        cutoff = datetime.now() - timedelta(minutes=timeout)
        
        count = 0
        for session in self._sessions.values():
            if session.status == SessionStatus.IDLE:
                if session.last_activity_at < cutoff:
                    session.expire()
                    count += 1
        
        return count
    
    def get_stats(self, session_id: str) -> SessionStats | None:
        """Obtiene estadísticas de una sesión."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        user_msgs = [m for m in session.messages if m.role == "user"]
        asst_msgs = [m for m in session.messages if m.role == "assistant"]
        
        return SessionStats(
            session_id=session_id,
            total_messages=session.message_count,
            user_messages=len(user_msgs),
            assistant_messages=len(asst_msgs),
            total_tokens=session.total_tokens,
            avg_tokens_per_message=(
                session.total_tokens / session.message_count
                if session.message_count > 0 else 0
            ),
            total_duration_ms=int(
                (session.updated_at - session.created_at).total_seconds() * 1000
            ),
            created_at=session.created_at,
            last_activity_at=session.last_activity_at,
            initial_budget=session.token_budget.total_limit,
            final_budget=session.token_budget.remaining,
            budget_usage_percent=session.token_budget.usage_percent * 100,
        )
    
    # ========== Helpers ==========
    
    def _add_event(
        self,
        session: Session,
        event_type: SessionEvent,
        message_id: str | None = None,
        tokens: int = 0,
        duration_ms: int = 0,
    ) -> None:
        """Agrega un evento a la sesión."""
        event = SessionEventRecord(
            id=str(uuid.uuid4()),
            session_id=session.id,
            event_type=event_type,
            message_id=message_id,
            tokens=tokens,
            duration_ms=duration_ms,
        )
        session.events.append(event)
