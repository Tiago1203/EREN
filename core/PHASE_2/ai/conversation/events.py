"""Conversation Events - Eventos de conversación."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConversationEventType(str, Enum):
    """Tipos de eventos de conversación."""
    # Lifecycle events
    CREATED = "conversation.created"
    UPDATED = "conversation.updated"
    CLOSED = "conversation.closed"
    ARCHIVED = "conversation.archived"
    DELETED = "conversation.deleted"
    
    # State events
    STATE_CHANGED = "conversation.state_changed"
    PAUSED = "conversation.paused"
    RESUMED = "conversation.resumed"
    
    # Session events
    SESSION_STARTED = "conversation.session_started"
    SESSION_ENDED = "conversation.session_ended"
    SESSION_JOINED = "conversation.session_joined"
    SESSION_LEFT = "conversation.session_left"
    
    # Message events
    MESSAGE_ADDED = "conversation.message_added"
    MESSAGE_EDITED = "conversation.message_edited"
    MESSAGE_DELETED = "conversation.message_deleted"
    
    # Participant events
    PARTICIPANT_JOINED = "conversation.participant_joined"
    PARTICIPANT_LEFT = "conversation.participant_left"
    PARTICIPANT_ROLE_CHANGED = "conversation.participant_role_changed"
    
    # Context events
    CONTEXT_UPDATED = "conversation.context_updated"


@dataclass
class ConversationEvent:
    """Evento de conversación."""
    id: str
    type: ConversationEventType
    conversation_id: str
    tenant_id: str
    user_id: str | None
    session_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convierte el evento a diccionario."""
        return {
            "id": self.id,
            "type": self.type.value,
            "conversation_id": self.conversation_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
        }


class ConversationEventDispatcher:
    """
    Despachador de eventos de conversación.
    
    Maneja la publicación y suscripción a eventos.
    """

    def __init__(self) -> None:
        self._handlers: dict[ConversationEventType, list[callable]] = {}
        self._global_handlers: list[callable] = []

    def subscribe(
        self,
        event_type: ConversationEventType,
        handler: callable,
    ) -> None:
        """Suscribe un handler a un tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: callable) -> None:
        """Suscribe un handler a todos los eventos."""
        self._global_handlers.append(handler)

    def unsubscribe(
        self,
        event_type: ConversationEventType,
        handler: callable,
    ) -> bool:
        """Desuscribe un handler de un tipo de evento."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False

    def unsubscribe_all(self, handler: callable) -> bool:
        """Desuscribe un handler de todos los eventos."""
        removed = False
        for event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                removed = True
            except ValueError:
                pass
        try:
            self._global_handlers.remove(handler)
            removed = True
        except ValueError:
            pass
        return removed

    def dispatch(self, event: ConversationEvent) -> None:
        """Despacha un evento a todos los handlers suscritos."""
        # Call type-specific handlers
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                try:
                    handler(event)
                except Exception:
                    pass  # Log error in production

        # Call global handlers
        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception:
                pass  # Log error in production

    def clear(self) -> None:
        """Limpia todos los handlers."""
        self._handlers.clear()
        self._global_handlers.clear()


# Global event dispatcher instance
_event_dispatcher: ConversationEventDispatcher | None = None


def get_event_dispatcher() -> ConversationEventDispatcher:
    """Obtiene el despachador de eventos global."""
    global _event_dispatcher
    if _event_dispatcher is None:
        _event_dispatcher = ConversationEventDispatcher()
    return _event_dispatcher


def reset_event_dispatcher() -> None:
    """Resetea el despachador de eventos global."""
    global _event_dispatcher
    if _event_dispatcher is not None:
        _event_dispatcher.clear()
    _event_dispatcher = None
