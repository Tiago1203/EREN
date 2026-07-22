"""Conversation Repository - Repositorio de conversaciones."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.PHASE_2.ai.conversation.models import (
    Conversation,
    ConversationMessage,
    ConversationParticipant,
    ConversationSession,
    ConversationState,
)

if TYPE_CHECKING:
    from core.PHASE_2.ai.conversation.models import ConversationContext


class ConversationRepository(ABC):
    """
    Repositorio abstracto para conversaciones.
    
    Define la interfaz para persistencia de conversaciones.
    """

    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        """Guarda una conversación."""
        ...

    @abstractmethod
    def get(self, conversation_id: str) -> Conversation | None:
        """Obtiene una conversación por ID."""
        ...

    @abstractmethod
    def delete(self, conversation_id: str) -> bool:
        """Elimina una conversación."""
        ...

    @abstractmethod
    def list(
        self,
        tenant_id: str,
        state: ConversationState | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        """Lista conversaciones de un tenant."""
        ...

    @abstractmethod
    def count(
        self,
        tenant_id: str,
        state: ConversationState | None = None,
    ) -> int:
        """Cuenta conversaciones de un tenant."""
        ...

    # Session methods
    @abstractmethod
    def save_session(self, session: ConversationSession) -> None:
        """Guarda una sesión."""
        ...

    @abstractmethod
    def get_session(self, session_id: str) -> ConversationSession | None:
        """Obtiene una sesión por ID."""
        ...

    @abstractmethod
    def get_active_sessions(
        self,
        conversation_id: str | None = None,
        user_id: str | None = None,
    ) -> list[ConversationSession]:
        """Obtiene sesiones activas."""
        ...

    # Message methods
    @abstractmethod
    def save_message(self, message: ConversationMessage) -> None:
        """Guarda un mensaje."""
        ...

    @abstractmethod
    def get_message(self, message_id: str) -> ConversationMessage | None:
        """Obtiene un mensaje por ID."""
        ...

    @abstractmethod
    def list_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConversationMessage]:
        """Lista mensajes de una conversación."""
        ...

    # Participant methods
    @abstractmethod
    def add_participant(
        self,
        participant: ConversationParticipant,
    ) -> None:
        """Agrega un participante."""
        ...

    @abstractmethod
    def remove_participant(
        self,
        conversation_id: str,
        user_id: str,
    ) -> bool:
        """Elimina un participante."""
        ...

    @abstractmethod
    def list_participants(
        self,
        conversation_id: str,
    ) -> list[ConversationParticipant]:
        """Lista participantes de una conversación."""
        ...

    # Context methods
    @abstractmethod
    def save_context(
        self,
        conversation_id: str,
        context: ConversationContext,
    ) -> None:
        """Guarda el contexto de una conversación."""
        ...

    @abstractmethod
    def get_context(
        self,
        conversation_id: str,
    ) -> ConversationContext | None:
        """Obtiene el contexto de una conversación."""
        ...


class InMemoryConversationRepository(ConversationRepository):
    """
    Repositorio en memoria para conversaciones.
    
    Útil para testing y desarrollo.
    """

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._sessions: dict[str, ConversationSession] = {}
        self._messages: dict[str, ConversationMessage] = {}
        self._conversation_messages: dict[str, list[str]] = {}
        self._participants: dict[str, list[ConversationParticipant]] = {}
        self._contexts: dict[str, ConversationContext] = {}

    def save(self, conversation: Conversation) -> None:
        """Guarda una conversación."""
        self._conversations[conversation.id] = conversation

    def get(self, conversation_id: str) -> Conversation | None:
        """Obtiene una conversación por ID."""
        return self._conversations.get(conversation_id)

    def delete(self, conversation_id: str) -> bool:
        """Elimina una conversación."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            # Clean up related data
            if conversation_id in self._messages:
                del self._conversation_messages[conversation_id]
            if conversation_id in self._participants:
                del self._participants[conversation_id]
            if conversation_id in self._contexts:
                del self._contexts[conversation_id]
            return True
        return False

    def list(
        self,
        tenant_id: str,
        state: ConversationState | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        """Lista conversaciones de un tenant."""
        results = [
            c for c in self._conversations.values()
            if c.tenant_id == tenant_id
            and (state is None or c.state == state)
        ]
        results.sort(key=lambda c: c.updated_at, reverse=True)
        return results[offset:offset + limit]

    def count(
        self,
        tenant_id: str,
        state: ConversationState | None = None,
    ) -> int:
        """Cuenta conversaciones de un tenant."""
        return len([
            c for c in self._conversations.values()
            if c.tenant_id == tenant_id
            and (state is None or c.state == state)
        ])

    # Session methods
    def save_session(self, session: ConversationSession) -> None:
        """Guarda una sesión."""
        self._sessions[session.id] = session

    def get_session(self, session_id: str) -> ConversationSession | None:
        """Obtiene una sesión por ID."""
        return self._sessions.get(session_id)

    def get_active_sessions(
        self,
        conversation_id: str | None = None,
        user_id: str | None = None,
    ) -> list[ConversationSession]:
        """Obtiene sesiones activas."""
        results = [s for s in self._sessions.values() if s.is_active]
        if conversation_id:
            results = [s for s in results if s.conversation_id == conversation_id]
        if user_id:
            results = [s for s in results if s.user_id == user_id]
        return results

    # Message methods
    def save_message(self, message: ConversationMessage) -> None:
        """Guarda un mensaje."""
        self._messages[message.id] = message
        if message.conversation_id not in self._conversation_messages:
            self._conversation_messages[message.conversation_id] = []
        self._conversation_messages[message.conversation_id].append(message.id)

    def get_message(self, message_id: str) -> ConversationMessage | None:
        """Obtiene un mensaje por ID."""
        return self._messages.get(message_id)

    def list_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConversationMessage]:
        """Lista mensajes de una conversación."""
        message_ids = self._conversation_messages.get(conversation_id, [])
        messages = [self._messages[mid] for mid in message_ids if mid in self._messages]
        messages.sort(key=lambda m: m.created_at)
        return messages[offset:offset + limit]

    # Participant methods
    def add_participant(
        self,
        participant: ConversationParticipant,
    ) -> None:
        """Agrega un participante."""
        if participant.conversation_id not in self._participants:
            self._participants[participant.conversation_id] = []
        # Remove existing participant if any
        self._participants[participant.conversation_id] = [
            p for p in self._participants[participant.conversation_id]
            if p.user_id != participant.user_id
        ]
        self._participants[participant.conversation_id].append(participant)

    def remove_participant(
        self,
        conversation_id: str,
        user_id: str,
    ) -> bool:
        """Elimina un participante."""
        if conversation_id in self._participants:
            original_count = len(self._participants[conversation_id])
            self._participants[conversation_id] = [
                p for p in self._participants[conversation_id]
                if p.user_id != user_id
            ]
            return len(self._participants[conversation_id]) < original_count
        return False

    def list_participants(
        self,
        conversation_id: str,
    ) -> list[ConversationParticipant]:
        """Lista participantes de una conversación."""
        return self._participants.get(conversation_id, [])

    # Context methods
    def save_context(
        self,
        conversation_id: str,
        context: ConversationContext,
    ) -> None:
        """Guarda el contexto de una conversación."""
        self._contexts[conversation_id] = context

    def get_context(
        self,
        conversation_id: str,
    ) -> ConversationContext | None:
        """Obtiene el contexto de una conversación."""
        return self._contexts.get(conversation_id)

    def clear(self) -> None:
        """Limpia todos los datos."""
        self._conversations.clear()
        self._sessions.clear()
        self._messages.clear()
        self._conversation_messages.clear()
        self._participants.clear()
        self._contexts.clear()
