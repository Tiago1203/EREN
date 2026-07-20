"""Conversation Controller - Controlador de conversación."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from core.ai.conversation.events import (
    ConversationEvent,
    ConversationEventDispatcher,
    ConversationEventType,
    get_event_dispatcher,
)
from core.ai.conversation.lifecycle import ConversationLifecycle, SessionLifecycle
from core.ai.conversation.models import (
    Conversation,
    ConversationContext,
    ConversationMetadata,
    ConversationMessage,
    ConversationParticipant,
    ConversationSession,
    ConversationState,
    ConversationType,
)
from core.ai.conversation.repository import (
    ConversationRepository,
    InMemoryConversationRepository,
)


class ConversationController:
    """
    Controlador principal de conversaciones.
    
    Orquestra todas las operaciones relacionadas con conversaciones,
    incluyendo creación, gestión de sesiones, mensajes y participantes.
    """

    def __init__(
        self,
        repository: ConversationRepository | None = None,
        event_dispatcher: ConversationEventDispatcher | None = None,
    ) -> None:
        self._repository = repository or InMemoryConversationRepository()
        self._events = event_dispatcher or get_event_dispatcher()
        
        # Initialize lifecycle managers
        self._conversation_lifecycle = ConversationLifecycle(
            repository=self._repository,
            event_dispatcher=self._events,
        )
        self._session_lifecycle = SessionLifecycle(
            repository=self._repository,
            event_dispatcher=self._events,
        )

    @property
    def repository(self) -> ConversationRepository:
        """Obtiene el repositorio."""
        return self._repository

    # ========== Conversation Operations ==========

    def create_conversation(
        self,
        tenant_id: str,
        title: str,
        created_by: str | None = None,
        conversation_type: ConversationType = ConversationType.SINGLE,
        metadata: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
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
        meta = ConversationMetadata(
            title=metadata.get("title") if metadata else None,
            description=metadata.get("description") if metadata else None,
            tags=metadata.get("tags", []) if metadata else [],
            language=metadata.get("language", "en") if metadata else "en",
            preferences=metadata.get("preferences", {}) if metadata else {},
        )

        conversation = self._conversation_lifecycle.create(
            tenant_id=tenant_id,
            title=title,
            created_by=created_by,
            conversation_type=conversation_type,
            metadata=meta,
            context=context,
            tags=tags,
        )

        # Add creator as participant if specified
        if created_by:
            self.add_participant(
                conversation_id=conversation.id,
                user_id=created_by,
                role="owner",
            )

        # Initialize context
        self._initialize_context(conversation.id)

        return conversation

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        """Obtiene una conversación por ID."""
        return self._repository.get(conversation_id)

    def list_conversations(
        self,
        tenant_id: str,
        state: ConversationState | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        """Lista conversaciones de un tenant."""
        return self._repository.list(
            tenant_id=tenant_id,
            state=state,
            limit=limit,
            offset=offset,
        )

    def update_conversation(
        self,
        conversation_id: str,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> Conversation | None:
        """Actualiza una conversación."""
        meta = None
        if metadata:
            meta = ConversationMetadata(
                title=metadata.get("title"),
                description=metadata.get("description"),
                tags=metadata.get("tags", []),
                language=metadata.get("language", "en"),
                preferences=metadata.get("preferences", {}),
            )

        return self._conversation_lifecycle.update(
            conversation_id=conversation_id,
            title=title,
            metadata=meta,
            tags=tags,
        )

    def close_conversation(self, conversation_id: str) -> Conversation | None:
        """Cierra una conversación."""
        return self._conversation_lifecycle.close(conversation_id)

    def pause_conversation(self, conversation_id: str) -> Conversation | None:
        """Pausa una conversación."""
        return self._conversation_lifecycle.pause(conversation_id)

    def resume_conversation(self, conversation_id: str) -> Conversation | None:
        """Reanuda una conversación pausada."""
        return self._conversation_lifecycle.resume(conversation_id)

    def archive_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        """Archiva una conversación cerrada."""
        return self._conversation_lifecycle.archive(conversation_id)

    def delete_conversation(self, conversation_id: str) -> bool:
        """Elimina una conversación."""
        return self._conversation_lifecycle.delete(conversation_id)

    # ========== Session Operations ==========

    def start_session(
        self,
        conversation_id: str,
        tenant_id: str,
        user_id: str,
        context: dict[str, Any] | None = None,
    ) -> ConversationSession | None:
        """
        Inicia una sesión en una conversación.
        
        Args:
            conversation_id: ID de la conversación
            tenant_id: ID del tenant
            user_id: ID del usuario
            context: Contexto de la sesión
            
        Returns:
            Sesión iniciada o None
        """
        return self._session_lifecycle.start_session(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            context=context,
        )

    def end_session(self, session_id: str) -> ConversationSession | None:
        """Termina una sesión."""
        return self._session_lifecycle.end_session(session_id)

    def get_session(self, session_id: str) -> ConversationSession | None:
        """Obtiene una sesión por ID."""
        return self._repository.get_session(session_id)

    def get_active_session(
        self,
        conversation_id: str,
        user_id: str,
    ) -> ConversationSession | None:
        """Obtiene la sesión activa de un usuario."""
        sessions = self._repository.get_active_sessions(
            conversation_id=conversation_id,
            user_id=user_id,
        )
        return sessions[0] if sessions else None

    def update_session_activity(self, session_id: str) -> None:
        """Actualiza la actividad de una sesión."""
        self._session_lifecycle.update_activity(session_id)

    # ========== Message Operations ==========

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
        attachments: list[dict[str, Any]] | None = None,
        references: list[str] | None = None,
    ) -> ConversationMessage | None:
        """
        Agrega un mensaje a una conversación.
        
        Args:
            conversation_id: ID de la conversación
            role: Rol del emisor (user, assistant, system)
            content: Contenido del mensaje
            created_by: Usuario que crea el mensaje
            metadata: Metadatos adicionales
            attachments: Archivos adjuntos
            references: IDs de mensajes referenciados
            
        Returns:
            Mensaje agregado o None
        """
        conversation = self._repository.get(conversation_id)
        if not conversation or not conversation.can_receive_messages():
            return None

        message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_by=created_by,
            metadata=metadata or {},
            attachments=attachments or [],
            references=references or [],
        )

        self._repository.save_message(message)

        # Update conversation
        conversation.updated_at = datetime.now()
        self._repository.save(conversation)

        # Update session activity
        if created_by:
            session = self.get_active_session(conversation_id, created_by)
            if session:
                self.update_session_activity(session.id)

        # Dispatch event
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=ConversationEventType.MESSAGE_ADDED,
            conversation_id=conversation_id,
            tenant_id=conversation.tenant_id,
            user_id=created_by,
            data={
                "message_id": message.id,
                "role": role,
                "content_length": len(content),
            },
        )
        self._events.dispatch(event)

        return message

    def get_message(self, message_id: str) -> ConversationMessage | None:
        """Obtiene un mensaje por ID."""
        return self._repository.get_message(message_id)

    def list_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConversationMessage]:
        """Lista mensajes de una conversación."""
        return self._repository.list_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )

    def edit_message(
        self,
        message_id: str,
        content: str,
    ) -> ConversationMessage | None:
        """Edita un mensaje existente."""
        message = self._repository.get_message(message_id)
        if not message:
            return None

        message.content = content
        message.edited_at = datetime.now()

        self._repository.save_message(message)

        # Dispatch event
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=ConversationEventType.MESSAGE_EDITED,
            conversation_id=message.conversation_id,
            tenant_id=self._repository.get(message.conversation_id).tenant_id if self._repository.get(message.conversation_id) else "",
            user_id=message.created_by,
            data={"message_id": message_id},
        )
        self._events.dispatch(event)

        return message

    def delete_message(self, message_id: str) -> bool:
        """Elimina un mensaje (soft delete)."""
        message = self._repository.get_message(message_id)
        if not message:
            return False

        message.deleted_at = datetime.now()
        self._repository.save_message(message)

        # Dispatch event
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=ConversationEventType.MESSAGE_DELETED,
            conversation_id=message.conversation_id,
            tenant_id=self._repository.get(message.conversation_id).tenant_id if self._repository.get(message.conversation_id) else "",
            user_id=message.created_by,
            data={"message_id": message_id},
        )
        self._events.dispatch(event)

        return True

    # ========== Participant Operations ==========

    def add_participant(
        self,
        conversation_id: str,
        user_id: str,
        role: str = "member",
    ) -> ConversationParticipant | None:
        """Agrega un participante a una conversación."""
        conversation = self._repository.get(conversation_id)
        if not conversation:
            return None

        participant = ConversationParticipant(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
        )

        self._repository.add_participant(participant)

        # Dispatch event
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=ConversationEventType.PARTICIPANT_JOINED,
            conversation_id=conversation_id,
            tenant_id=conversation.tenant_id,
            user_id=user_id,
            data={"role": role},
        )
        self._events.dispatch(event)

        return participant

    def remove_participant(
        self,
        conversation_id: str,
        user_id: str,
    ) -> bool:
        """Elimina un participante de una conversación."""
        removed = self._repository.remove_participant(conversation_id, user_id)
        
        if removed:
            conversation = self._repository.get(conversation_id)
            event = ConversationEvent(
                id=str(uuid.uuid4()),
                type=ConversationEventType.PARTICIPANT_LEFT,
                conversation_id=conversation_id,
                tenant_id=conversation.tenant_id if conversation else "",
                user_id=user_id,
            )
            self._events.dispatch(event)

        return removed

    def list_participants(
        self,
        conversation_id: str,
    ) -> list[ConversationParticipant]:
        """Lista participantes de una conversación."""
        return self._repository.list_participants(conversation_id)

    def update_participant_role(
        self,
        conversation_id: str,
        user_id: str,
        new_role: str,
    ) -> bool:
        """Actualiza el rol de un participante."""
        participants = self._repository.list_participants(conversation_id)
        for participant in participants:
            if participant.user_id == user_id:
                old_role = participant.role
                participant.role = new_role
                self._repository.add_participant(participant)

                # Dispatch event
                conversation = self._repository.get(conversation_id)
                event = ConversationEvent(
                    id=str(uuid.uuid4()),
                    type=ConversationEventType.PARTICIPANT_ROLE_CHANGED,
                    conversation_id=conversation_id,
                    tenant_id=conversation.tenant_id if conversation else "",
                    user_id=user_id,
                    data={"old_role": old_role, "new_role": new_role},
                )
                self._events.dispatch(event)

                return True
        return False

    # ========== Context Operations ==========

    def _initialize_context(
        self,
        conversation_id: str,
    ) -> ConversationContext:
        """Inicializa el contexto de una conversación."""
        context = ConversationContext(
            conversation_id=conversation_id,
        )
        self._repository.save_context(conversation_id, context)
        return context

    def get_context(
        self,
        conversation_id: str,
    ) -> ConversationContext | None:
        """Obtiene el contexto de una conversación."""
        return self._repository.get_context(conversation_id)

    def update_context(
        self,
        conversation_id: str,
        session_id: str | None = None,
        system_prompt: str | None = None,
        user_context: dict[str, Any] | None = None,
        session_context: dict[str, Any] | None = None,
        global_context: dict[str, Any] | None = None,
        tools_enabled: list[str] | None = None,
        model_preferences: dict[str, Any] | None = None,
    ) -> ConversationContext | None:
        """
        Actualiza el contexto de una conversación.
        
        Args:
            conversation_id: ID de la conversación
            session_id: ID de la sesión
            system_prompt: Nuevo prompt del sistema
            user_context: Nuevo contexto de usuario
            session_context: Nuevo contexto de sesión
            global_context: Nuevo contexto global
            tools_enabled: Herramientas habilitadas
            model_preferences: Preferencias del modelo
            
        Returns:
            Contexto actualizado o None
        """
        context = self._repository.get_context(conversation_id)
        if not context:
            return None

        if session_id is not None:
            context.session_id = session_id
        if system_prompt is not None:
            context.system_prompt = system_prompt
        if user_context is not None:
            context.user_context = user_context
        if session_context is not None:
            context.session_context = session_context
        if global_context is not None:
            context.global_context = global_context
        if tools_enabled is not None:
            context.tools_enabled = tools_enabled
        if model_preferences is not None:
            context.model_preferences = model_preferences

        self._repository.save_context(conversation_id, context)

        # Dispatch event
        conversation = self._repository.get(conversation_id)
        event = ConversationEvent(
            id=str(uuid.uuid4()),
            type=ConversationEventType.CONTEXT_UPDATED,
            conversation_id=conversation_id,
            tenant_id=conversation.tenant_id if conversation else "",
            session_id=session_id,
            data={"updated_fields": list(locals().keys())},
        )
        self._events.dispatch(event)

        return context

    # ========== History Operations ==========

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 100,
        include_system: bool = True,
    ) -> list[ConversationMessage]:
        """Obtiene el historial de mensajes de una conversación."""
        messages = self._repository.list_messages(
            conversation_id=conversation_id,
            limit=limit,
        )
        
        if not include_system:
            messages = [m for m in messages if m.role != "system"]
        
        return messages

    def search_conversations(
        self,
        tenant_id: str,
        query: str,
        limit: int = 20,
    ) -> list[Conversation]:
        """Busca conversaciones por título o contenido."""
        all_conversations = self._repository.list(
            tenant_id=tenant_id,
            limit=1000,
        )
        
        results = [
            c for c in all_conversations
            if query.lower() in c.title.lower()
            or any(query.lower() in tag.lower() for tag in c.tags)
        ]
        
        return results[:limit]

    # ========== Multi-user & Multi-tenant ==========

    def get_user_conversations(
        self,
        tenant_id: str,
        user_id: str,
        state: ConversationState | None = None,
    ) -> list[Conversation]:
        """Obtiene todas las conversaciones de un usuario."""
        # Get conversations where user is participant
        all_conversations = self._repository.list(
            tenant_id=tenant_id,
            state=state,
        )
        
        user_conversation_ids = {
            p.conversation_id 
            for p in self._repository.list_participants("")
            if p.user_id == user_id
        }
        
        # Also include conversations created by user
        user_conversation_ids.update(
            c.id for c in all_conversations
            if c.created_by == user_id
        )
        
        return [
            c for c in all_conversations
            if c.id in user_conversation_ids
        ]

    def can_access_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> bool:
        """Verifica si un usuario puede acceder a una conversación."""
        conversation = self._repository.get(conversation_id)
        if not conversation:
            return False

        # Owner can always access
        if conversation.created_by == user_id:
            return True

        # Check participants
        participants = self._repository.list_participants(conversation_id)
        return any(p.user_id == user_id for p in participants)
