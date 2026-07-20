"""Conversation Lifecycle - Ciclo de vida de conversación."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from core.ai.conversation.events import (
    ConversationEvent,
    ConversationEventDispatcher,
    ConversationEventType,
    get_event_dispatcher,
)
from core.ai.conversation.models import (
    Conversation,
    ConversationMetadata,
    ConversationSession,
    ConversationState,
    ConversationType,
)

if TYPE_CHECKING:
    from core.ai.conversation.repository import ConversationRepository


class ConversationLifecycle:
    """
    Gestor del ciclo de vida de conversaciones.
    
    Maneja la creación, actualización, cierre y archivado
    de conversaciones.
    """

    def __init__(
        self,
        repository: ConversationRepository | None = None,
        event_dispatcher: ConversationEventDispatcher | None = None,
    ) -> None:
        self._repository = repository
        self._events = event_dispatcher or get_event_dispatcher()

    def set_repository(self, repository: ConversationRepository) -> None:
        """Establece el repositorio de conversaciones."""
        self._repository = repository

    def create(
        self,
        tenant_id: str,
        title: str,
        created_by: str | None = None,
        conversation_type: ConversationType = ConversationType.SINGLE,
        metadata: ConversationMetadata | None = None,
        context: dict | None = None,
        tags: list[str] | None = None,
    ) -> Conversation:
        """
        Crea una nueva conversación.
        
        Args:
            tenant_id: ID del tenant
            title: Título de la conversación
            created_by: Usuario que crea la conversación
            conversation_type: Tipo de conversación
            metadata: Metadatos adicionales
            context: Contexto inicial
            tags: Etiquetas
            
        Returns:
            Conversación creada
        """
        conversation = Conversation(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            title=title,
            state=ConversationState.ACTIVE,
            type=conversation_type,
            created_by=created_by,
            metadata=metadata or ConversationMetadata(),
            context=context or {},
            tags=tags or [],
        )

        # Save to repository
        if self._repository:
            self._repository.save(conversation)

        # Dispatch event
        self._dispatch_event(
            ConversationEventType.CREATED,
            conversation,
            {"created_by": created_by},
        )

        return conversation

    def update(
        self,
        conversation_id: str,
        title: str | None = None,
        metadata: ConversationMetadata | None = None,
        tags: list[str] | None = None,
        context: dict | None = None,
    ) -> Conversation | None:
        """
        Actualiza una conversación.
        
        Args:
            conversation_id: ID de la conversación
            title: Nuevo título
            metadata: Nuevos metadatos
            tags: Nuevas etiquetas
            context: Nuevo contexto
            
        Returns:
            Conversación actualizada o None si no existe
        """
        if not self._repository:
            return None

        conversation = self._repository.get(conversation_id)
        if not conversation:
            return None

        if title is not None:
            conversation.title = title
        if metadata is not None:
            conversation.metadata = metadata
        if tags is not None:
            conversation.tags = tags
        if context is not None:
            conversation.context = context

        conversation.updated_at = datetime.now()

        self._repository.save(conversation)

        self._dispatch_event(
            ConversationEventType.UPDATED,
            conversation,
            {"updated_by": conversation.created_by},
        )

        return conversation

    def close(self, conversation_id: str) -> Conversation | None:
        """
        Cierra una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Conversación cerrada o None si no existe
        """
        if not self._repository:
            return None

        conversation = self._repository.get(conversation_id)
        if not conversation:
            return None

        conversation.state = ConversationState.CLOSED
        conversation.closed_at = datetime.now()
        conversation.updated_at = datetime.now()

        self._repository.save(conversation)

        self._dispatch_event(
            ConversationEventType.CLOSED,
            conversation,
            {},
        )

        return conversation

    def pause(self, conversation_id: str) -> Conversation | None:
        """
        Pausa una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Conversación pausada o None
        """
        if not self._repository:
            return None

        conversation = self._repository.get(conversation_id)
        if not conversation or not conversation.is_active():
            return None

        old_state = conversation.state
        conversation.state = ConversationState.PAUSED
        conversation.updated_at = datetime.now()

        self._repository.save(conversation)

        self._dispatch_event(
            ConversationEventType.PAUSED,
            conversation,
            {"old_state": old_state.value},
        )

        return conversation

    def resume(self, conversation_id: str) -> Conversation | None:
        """
        Reanuda una conversación pausada.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Conversación reanudada o None
        """
        if not self._repository:
            return None

        conversation = self._repository.get(conversation_id)
        if not conversation or not conversation.is_paused():
            return None

        old_state = conversation.state
        conversation.state = ConversationState.ACTIVE
        conversation.updated_at = datetime.now()

        self._repository.save(conversation)

        self._dispatch_event(
            ConversationEventType.RESUMED,
            conversation,
            {"old_state": old_state.value},
        )

        return conversation

    def archive(self, conversation_id: str) -> Conversation | None:
        """
        Archiva una conversación cerrada.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Conversación archivada o None
        """
        if not self._repository:
            return None

        conversation = self._repository.get(conversation_id)
        if not conversation or not conversation.is_closed():
            return None

        conversation.state = ConversationState.ARCHIVED
        conversation.updated_at = datetime.now()

        self._repository.save(conversation)

        self._dispatch_event(
            ConversationEventType.ARCHIVED,
            conversation,
            {},
        )

        return conversation

    def delete(self, conversation_id: str) -> bool:
        """
        Elimina una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            True si se eliminó, False si no existe
        """
        if not self._repository:
            return False

        conversation = self._repository.get(conversation_id)
        if not conversation:
            return False

        self._repository.delete(conversation_id)

        self._dispatch_event(
            ConversationEventType.DELETED,
            conversation,
            {"deleted_by": conversation.created_by},
        )

        return True

    def _dispatch_event(
        self,
        event_type: ConversationEventType,
        conversation: Conversation,
        data: dict,
    ) -> None:
        """Despacha un evento."""
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=event_type,
            conversation_id=conversation.id,
            tenant_id=conversation.tenant_id,
            user_id=conversation.created_by,
            data=data,
        )
        self._events.dispatch(event)


class SessionLifecycle:
    """
    Gestor del ciclo de vida de sesiones.
    
    Maneja la creación, actualización y cierre de sesiones
    dentro de conversaciones.
    """

    def __init__(
        self,
        repository: ConversationRepository | None = None,
        event_dispatcher: ConversationEventDispatcher | None = None,
    ) -> None:
        self._repository = repository
        self._events = event_dispatcher or get_event_dispatcher()

    def set_repository(self, repository: ConversationRepository) -> None:
        """Establece el repositorio."""
        self._repository = repository

    def start_session(
        self,
        conversation_id: str,
        tenant_id: str,
        user_id: str,
        context: dict | None = None,
        metadata: dict | None = None,
    ) -> ConversationSession | None:
        """
        Inicia una nueva sesión en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            tenant_id: ID del tenant
            user_id: ID del usuario
            context: Contexto inicial de la sesión
            metadata: Metadatos adicionales
            
        Returns:
            Sesión creada o None si la conversación no existe
        """
        if not self._repository:
            return None

        conversation = self._repository.get(conversation_id)
        if not conversation or not conversation.can_receive_messages():
            return None

        # End any active session for this user in this conversation
        self._end_active_sessions(conversation_id, user_id)

        session = ConversationSession(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            context=context or {},
            metadata=metadata or {},
        )

        # Save session
        self._repository.save_session(session)

        # Dispatch event
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=ConversationEventType.SESSION_STARTED,
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session.id,
            data={"session_id": session.id},
        )
        self._events.dispatch(event)

        return session

    def end_session(
        self,
        session_id: str,
    ) -> ConversationSession | None:
        """
        Termina una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Sesión terminada o None
        """
        if not self._repository:
            return None

        session = self._repository.get_session(session_id)
        if not session:
            return None

        session.end()
        self._repository.save_session(session)

        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=ConversationEventType.SESSION_ENDED,
            conversation_id=session.conversation_id,
            tenant_id=session.tenant_id,
            user_id=session.user_id,
            session_id=session.id,
            data={"duration": (session.ended_at - session.started_at).seconds if session.ended_at else None},
        )
        self._events.dispatch(event)

        return session

    def update_activity(
        self,
        session_id: str,
    ) -> ConversationSession | None:
        """
        Actualiza la actividad de una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Sesión actualizada o None
        """
        if not self._repository:
            return None

        session = self._repository.get_session(session_id)
        if not session:
            return None

        session.update_activity()
        session.message_count += 1
        self._repository.save_session(session)

        return session

    def _end_active_sessions(
        self,
        conversation_id: str,
        user_id: str,
    ) -> None:
        """Termina todas las sesiones activas de un usuario."""
        if not self._repository:
            return

        sessions = self._repository.get_active_sessions(
            conversation_id=conversation_id,
            user_id=user_id,
        )
        for session in sessions:
            session.end()
            self._repository.save_session(session)
