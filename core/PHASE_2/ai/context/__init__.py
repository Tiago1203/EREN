"""AI Context Objects - Objetos de contexto del AI Core."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
from typing import Any

from core.PHASE_2.ai.dto import (
    AIContext,
    AIRequest,
    ContextMetadata,
    Message,
    ToolDefinition,
)


@dataclass
class RequestContext:
    """Contexto de una request individual."""
    request_id: str
    tenant_id: str
    user_id: str | None
    session_id: str | None
    created_at: datetime
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Contexto de una conversación."""
    conversation_id: str
    tenant_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: list[Message] = field(default_factory=list)
    system_prompt: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Contexto de una sesión de usuario."""
    session_id: str
    tenant_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    active_conversations: list[str] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class AIContextManager:
    """
    Gestor de contextos del AI Core.
    
    Maneja la creación, almacenamiento y recuperación de contextos
    para requests, conversaciones y sesiones.
    """

    def __init__(self, default_ttl: int = 3600) -> None:
        """
        Inicializa el gestor de contextos.
        
        Args:
            default_ttl: Tiempo de vida por defecto en segundos
        """
        self._default_ttl = default_ttl
        self._request_contexts: dict[str, RequestContext] = {}
        self._conversation_contexts: dict[str, ConversationContext] = {}
        self._session_contexts: dict[str, SessionContext] = {}
        self._lock = RLock()

    def create_request_context(
        self,
        request: AIRequest,
        metadata: ContextMetadata | None = None,
        ttl: int | None = None,
    ) -> str:
        """
        Crea un nuevo contexto de request.
        
        Args:
            request: Request de IA
            metadata: Metadatos adicionales
            ttl: Tiempo de vida en segundos
            
        Returns:
            ID del contexto creado
        """
        request_id = str(uuid.uuid4())
        ttl = ttl or self._default_ttl

        context = RequestContext(
            request_id=request_id,
            tenant_id=metadata.tenant_id or "default",
            user_id=metadata.user_id,
            session_id=metadata.session_id,
            created_at=datetime.now(),
            expires_at=datetime.fromtimestamp(time.time() + ttl),
            metadata={
                "model": request.model,
                "temperature": request.temperature,
                **(metadata.custom if metadata else {}),
            },
        )

        with self._lock:
            self._request_contexts[request_id] = context

        return request_id

    def get_request_context(self, request_id: str) -> RequestContext | None:
        """Obtiene un contexto de request."""
        with self._lock:
            return self._request_contexts.get(request_id)

    def delete_request_context(self, request_id: str) -> bool:
        """Elimina un contexto de request."""
        with self._lock:
            if request_id in self._request_contexts:
                del self._request_contexts[request_id]
                return True
            return False

    def create_conversation_context(
        self,
        user_id: str,
        tenant_id: str,
        system_prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Crea un nuevo contexto de conversación.
        
        Args:
            user_id: ID del usuario
            tenant_id: ID del tenant
            system_prompt: Prompt del sistema
            metadata: Metadatos adicionales
            
        Returns:
            ID de la conversación creada
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now()

        context = ConversationContext(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
            messages=[],
            system_prompt=system_prompt,
            metadata=metadata or {},
        )

        with self._lock:
            self._conversation_contexts[conversation_id] = context

        return conversation_id

    def get_conversation_context(
        self,
        conversation_id: str,
    ) -> ConversationContext | None:
        """Obtiene un contexto de conversación."""
        with self._lock:
            return self._conversation_contexts.get(conversation_id)

    def update_conversation_context(
        self,
        conversation_id: str,
        messages: list[Message] | None = None,
        system_prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Actualiza un contexto de conversación."""
        with self._lock:
            if conversation_id not in self._conversation_contexts:
                return False

            context = self._conversation_contexts[conversation_id]

            if messages is not None:
                context.messages = messages

            if system_prompt is not None:
                context.system_prompt = system_prompt

            if metadata is not None:
                context.metadata.update(metadata)

            context.updated_at = datetime.now()

            return True

    def delete_conversation_context(self, conversation_id: str) -> bool:
        """Elimina un contexto de conversación."""
        with self._lock:
            if conversation_id in self._conversation_contexts:
                del self._conversation_contexts[conversation_id]
                return True
            return False

    def create_session_context(
        self,
        user_id: str,
        tenant_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Crea un nuevo contexto de sesión.
        
        Args:
            user_id: ID del usuario
            tenant_id: ID del tenant
            metadata: Metadatos adicionales
            
        Returns:
            ID de la sesión creada
        """
        session_id = str(uuid.uuid4())
        now = datetime.now()

        context = SessionContext(
            session_id=session_id,
            tenant_id=tenant_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            metadata=metadata or {},
        )

        with self._lock:
            self._session_contexts[session_id] = context

        return session_id

    def get_session_context(self, session_id: str) -> SessionContext | None:
        """Obtiene un contexto de sesión."""
        with self._lock:
            return self._session_contexts.get(session_id)

    def update_session_context(
        self,
        session_id: str,
        last_activity: bool = True,
        preferences: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Actualiza un contexto de sesión."""
        with self._lock:
            if session_id not in self._session_contexts:
                return False

            context = self._session_contexts[session_id]

            if last_activity:
                context.last_activity = datetime.now()

            if preferences is not None:
                context.preferences.update(preferences)

            if metadata is not None:
                context.metadata.update(metadata)

            return True

    def delete_session_context(self, session_id: str) -> bool:
        """Elimina un contexto de sesión."""
        with self._lock:
            if session_id in self._session_contexts:
                del self._session_contexts[session_id]
                return True
            return False

    def cleanup_expired(self) -> int:
        """
        Limpia contextos expirados.
        
        Returns:
            Número de contextos eliminados
        """
        now = datetime.now()
        removed = 0

        with self._lock:
            # Clean expired request contexts
            expired_requests = [
                rid for rid, ctx in self._request_contexts.items()
                if ctx.expires_at and ctx.expires_at < now
            ]
            for rid in expired_requests:
                del self._request_contexts[rid]
                removed += 1

        return removed

    def clear_all(self) -> None:
        """Limpia todos los contextos."""
        with self._lock:
            self._request_contexts.clear()
            self._conversation_contexts.clear()
            self._session_contexts.clear()

    def get_stats(self) -> dict[str, int]:
        """Obtiene estadísticas del gestor de contextos."""
        with self._lock:
            return {
                "request_contexts": len(self._request_contexts),
                "conversation_contexts": len(self._conversation_contexts),
                "session_contexts": len(self._session_contexts),
            }


def create_ai_context(
    request_id: str,
    request: AIRequest,
    metadata: ContextMetadata | None = None,
) -> AIContext:
    """
    Crea un AIContext para una request.
    
    Args:
        request_id: ID único de la request
        request: Request de IA
        metadata: Metadatos de contexto
        
    Returns:
        AIContext configurado
    """
    return AIContext(
        request_id=request_id,
        messages=request.messages,
        model=request.model,
        metadata=metadata or ContextMetadata(),
        system_prompt=None,
        tools=None,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        raw_config={},
    )


def merge_messages(
    conversation: ConversationContext,
    new_messages: list[Message],
) -> list[Message]:
    """
    Combina mensajes de conversación con nuevos mensajes.
    
    Args:
        conversation: Contexto de conversación
        new_messages: Nuevos mensajes a agregar
        
    Returns:
        Lista combinada de mensajes
    """
    return list(conversation.messages) + new_messages
