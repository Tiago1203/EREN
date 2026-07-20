"""Conversation Models - Modelos de conversación."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConversationState(str, Enum):
    """Estados de una conversación."""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ConversationType(str, Enum):
    """Tipos de conversación."""
    SINGLE = "single"
    GROUP = "group"
    THREAD = "thread"


@dataclass
class ConversationMetadata:
    """Metadatos de una conversación."""
    title: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    language: str = "en"
    preferences: dict[str, Any] = field(default_factory=dict)
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """
    Representa una conversación.
    
    Una conversación es el contenedor principal para la interacción
    entre usuarios y el sistema cognitivo.
    """
    id: str
    tenant_id: str
    title: str
    state: ConversationState = ConversationState.ACTIVE
    type: ConversationType = ConversationType.SINGLE
    created_by: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    closed_at: datetime | None = None
    metadata: ConversationMetadata = field(default_factory=ConversationMetadata)
    context: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def is_active(self) -> bool:
        """Verifica si la conversación está activa."""
        return self.state == ConversationState.ACTIVE

    def is_paused(self) -> bool:
        """Verifica si la conversación está pausada."""
        return self.state == ConversationState.PAUSED

    def is_closed(self) -> bool:
        """Verifica si la conversación está cerrada."""
        return self.state == ConversationState.CLOSED

    def can_receive_messages(self) -> bool:
        """Verifica si la conversación puede recibir mensajes."""
        return self.state in (ConversationState.ACTIVE, ConversationState.PAUSED)


@dataclass
class ConversationMessage:
    """Un mensaje dentro de una conversación."""
    id: str
    conversation_id: str
    role: str  # user, assistant, system, function
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    references: list[str] = field(default_factory=list)  # IDs de mensajes referenciados
    edited_at: datetime | None = None
    deleted_at: datetime | None = None


@dataclass
class ConversationParticipant:
    """Participante en una conversación."""
    user_id: str
    conversation_id: str
    role: str = "member"  # owner, admin, member, guest
    joined_at: datetime = field(default_factory=datetime.now)
    left_at: datetime | None = None
    last_read_at: datetime = field(default_factory=datetime.now)
    notifications_enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationSession:
    """
    Sesión dentro de una conversación.
    
    Una sesión representa un periodo de actividad dentro de
    una conversación.
    """
    id: str
    conversation_id: str
    tenant_id: str
    user_id: str
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None
    last_activity_at: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

    def end(self) -> None:
        """Termina la sesión."""
        self.ended_at = datetime.now()
        self.is_active = False

    def update_activity(self) -> None:
        """Actualiza la última actividad."""
        self.last_activity_at = datetime.now()


@dataclass
class ConversationContext:
    """
    Contexto de una conversación.
    
    Almacena información contextual que persiste entre
    mensajes de la conversación.
    """
    conversation_id: str
    session_id: str | None = None
    system_prompt: str | None = None
    user_context: dict[str, Any] = field(default_factory=dict)
    session_context: dict[str, Any] = field(default_factory=dict)
    global_context: dict[str, Any] = field(default_factory=dict)
    tools_enabled: list[str] = field(default_factory=list)
    model_preferences: dict[str, Any] = field(default_factory=dict)
    custom_data: dict[str, Any] = field(default_factory=dict)

    def merge_context(self, new_context: dict[str, Any]) -> None:
        """Fusiona nuevo contexto con el existente."""
        self.custom_data.update(new_context)

    def get_effective_context(self) -> dict[str, Any]:
        """Obtiene el contexto efectivo combinando todos los niveles."""
        return {
            **self.global_context,
            **self.session_context,
            **self.user_context,
            **self.custom_data,
        }
