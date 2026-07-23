"""
PHASE 5 - EPIC 7: Collaboration Domain Objects

Domain objects especializados para colaboración:
- SharedContext
- CollaborationSession
- AgentConversation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class ContextType(str, Enum):
    """Tipos de contexto compartido."""
    TASK = "task"                     # Contexto de tarea
    RESULT = "result"               # Contexto de resultado
    STATE = "state"                 # Estado del agente
    KNOWLEDGE = "knowledge"         # Conocimiento
    PLAN = "plan"                   # Plan
    DECISION = "decision"           # Decisión


class SessionStatus(str, Enum):
    """Estado de sesión de colaboración."""
    PENDING = "pending"           # Pendiente
    ACTIVE = "active"             # Activa
    PAUSED = "paused"            # Pausada
    COMPLETED = "completed"       # Completada
    FAILED = "failed"            # Fallida


class MessageType(str, Enum):
    """Tipos de mensaje."""
    REQUEST = "request"           # Solicitud
    RESPONSE = "response"         # Respuesta
    NOTIFICATION = "notification" # Notificación
    QUERY = "query"              # Consulta
    COMMAND = "command"           # Comando
    EVENT = "event"              # Evento


# =============================================================================
# CONTEXT ENTRY - Entrada de contexto
# =============================================================================

@dataclass
class ContextEntry:
    """Entrada individual de contexto."""
    entry_id: str = ""
    
    # Tipo y contenido
    context_type: ContextType = ContextType.TASK
    key: str = ""
    value: Any = None
    
    # Proveniencia
    source_agent_id: str = ""
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    ttl_seconds: int = 3600  # 1 hour default
    
    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = str(uuid.uuid4())
        if self.expires_at is None:
            from datetime import timedelta
            self.expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return datetime.now(UTC) > self.expires_at


# =============================================================================
# SHARED CONTEXT - Contexto compartido
# =============================================================================

@dataclass
class SharedContext:
    """Contexto compartido entre agentes."""
    context_id: str = ""
    session_id: str = ""
    
    # Entradas
    entries: list[ContextEntry] = field(default_factory=list)
    
    # Stats
    entries_count: int = 0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.context_id:
            self.context_id = str(uuid.uuid4())
        self.entries_count = len(self.entries)
    
    def add_entry(self, entry: ContextEntry) -> None:
        """Agrega una entrada al contexto."""
        self.entries.append(entry)
        self.entries_count = len(self.entries)
        self.updated_at = datetime.now(UTC)
    
    def get_entry(self, key: str) -> ContextEntry | None:
        """Obtiene una entrada por clave."""
        for entry in self.entries:
            if entry.key == key and not entry.is_expired():
                return entry
        return None
    
    def get_entries_by_type(self, context_type: ContextType) -> list[ContextEntry]:
        """Obtiene entradas por tipo."""
        return [e for e in self.entries if e.context_type == context_type and not e.is_expired()]
    
    def cleanup_expired(self) -> None:
        """Limpia entradas expiradas."""
        self.entries = [e for e in self.entries if not e.is_expired()]
        self.entries_count = len(self.entries)


# =============================================================================
# PARTICIPANT - Participante
# =============================================================================

@dataclass
class Participant:
    """Participante en una sesión."""
    participant_id: str = ""
    agent_id: str = ""
    role: str = ""  # organizer, contributor, observer
    
    # Estado
    joined_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    
    def __post_init__(self):
        if not self.participant_id:
            self.participant_id = str(uuid.uuid4())


# =============================================================================
# COLLABORATION SESSION - Sesión de colaboración
# =============================================================================

@dataclass
class CollaborationSession:
    """Sesión de colaboración entre agentes."""
    session_id: str = ""
    session_type: str = ""  # parallel, sequential, expert_review
    
    # Participantes
    participants: list[Participant] = field(default_factory=list)
    
    # Contexto compartido
    shared_context: SharedContext | None = None
    
    # Estado
    status: SessionStatus = SessionStatus.PENDING
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    def add_participant(self, agent_id: str, role: str = "contributor") -> Participant:
        """Agrega un participante."""
        participant = Participant(
            agent_id=agent_id,
            role=role,
        )
        self.participants.append(participant)
        return participant
    
    def remove_participant(self, agent_id: str) -> bool:
        """Remueve un participante."""
        for p in self.participants:
            if p.agent_id == agent_id:
                p.is_active = False
                return True
        return False
    
    def start(self) -> None:
        """Inicia la sesión."""
        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.now(UTC)
    
    def complete(self) -> None:
        """Completa la sesión."""
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
    
    def get_active_participants(self) -> list[Participant]:
        """Obtiene participantes activos."""
        return [p for p in self.participants if p.is_active]


# =============================================================================
# MESSAGE - Mensaje
# =============================================================================

@dataclass
class Message:
    """Mensaje entre agentes."""
    message_id: str = ""
    
    # Remitente y destinatario
    sender_id: str = ""
    recipient_id: str = ""
    
    # Tipo y contenido
    message_type: MessageType = MessageType.REQUEST
    content: str = ""
    payload: dict = field(default_factory=dict)
    
    # Conversación
    conversation_id: str = ""
    in_reply_to: str = ""
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    read: bool = False
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
    
    def mark_read(self) -> None:
        """Marca el mensaje como leído."""
        self.read = True


# =============================================================================
# AGENT CONVERSATION - Conversación entre agentes
# =============================================================================

@dataclass
class AgentConversation:
    """Conversación entre agentes."""
    conversation_id: str = ""
    participants: list[str] = field(default_factory=list)  # agent_ids
    
    # Mensajes
    messages: list[Message] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_message_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.conversation_id:
            self.conversation_id = str(uuid.uuid4())
    
    def add_message(self, message: Message) -> None:
        """Agrega un mensaje a la conversación."""
        message.conversation_id = self.conversation_id
        self.messages.append(message)
        self.last_message_at = datetime.now(UTC)
    
    def get_messages_for(self, agent_id: str, unread_only: bool = False) -> list[Message]:
        """Obtiene mensajes para un agente."""
        messages = [m for m in self.messages if m.recipient_id == agent_id]
        if unread_only:
            messages = [m for m in messages if not m.read]
        return messages
    
    def get_unread_count(self, agent_id: str) -> int:
        """Obtiene el conteo de mensajes no leídos."""
        return len(self.get_messages_for(agent_id, unread_only=True))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ContextType",
    "SessionStatus",
    "MessageType",
    # Domain Objects
    "ContextEntry",
    "SharedContext",
    "Participant",
    "CollaborationSession",
    "Message",
    "AgentConversation",
]
