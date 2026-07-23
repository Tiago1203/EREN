"""
PHASE 5 - EPIC 9: Memory Domain Objects

Domain objects especializados para memoria:
- MemoryRecord
- ConversationContext
- AgentExperience
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

class MemoryType(str, Enum):
    """Tipos de memoria."""
    EPISODIC = "episodic"           # Episódica - eventos específicos
    SEMANTIC = "semantic"           # Semántica - conocimiento general
    PROCEDURAL = "procedural"       # Procedimental - habilidades
    WORKING = "working"             # De trabajo - corto plazo
    SHARED = "shared"              # Compartida - entre agentes


class MemoryImportance(str, Enum):
    """Importancia de memoria."""
    CRITICAL = "critical"           # Crítica - no olvidar
    HIGH = "high"                  # Alta
    MEDIUM = "medium"              # Media
    LOW = "low"                   # Baja


class ExperienceOutcome(str, Enum):
    """Resultado de experiencia."""
    SUCCESS = "success"           # Exitoso
    FAILURE = "failure"         # Fallido
    PARTIAL = "partial"         # Parcial
    UNKNOWN = "unknown"         # Desconocido


# =============================================================================
# MEMORY RECORD - Registro de memoria
# =============================================================================

@dataclass
class MemoryRecord:
    """Registro de memoria."""
    record_id: str = ""
    agent_id: str = ""
    
    # Tipo y contenido
    memory_type: MemoryType = MemoryType.EPISODIC
    importance: MemoryImportance = MemoryImportance.MEDIUM
    
    # Contenido
    content: str = ""
    metadata: dict = field(default_factory=dict)
    
    # Contexto
    session_id: str = ""
    task_id: str = ""
    
    # Tiempo
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Uso
    access_count: int = 0
    
    def __post_init__(self):
        if not self.record_id:
            self.record_id = str(uuid.uuid4())
    
    def access(self) -> None:
        """Registra acceso a la memoria."""
        self.access_count += 1
        self.last_accessed = datetime.now(UTC)
    
    def is_expired(self) -> bool:
        """Verifica si la memoria ha expirado."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at


# =============================================================================
# MESSAGE - Mensaje
# =============================================================================

@dataclass
class Message:
    """Mensaje en conversación."""
    message_id: str = ""
    sender_id: str = ""
    content: str = ""
    message_type: str = "text"
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())


# =============================================================================
# CONVERSATION CONTEXT - Contexto de conversación
# =============================================================================

@dataclass
class ConversationContext:
    """Contexto de conversación."""
    context_id: str = ""
    session_id: str = ""
    
    # Participantes
    participants: list[str] = field(default_factory=list)
    
    # Mensajes
    messages: list[Message] = field(default_factory=list)
    
    # Resumen
    summary: str = ""
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.context_id:
            self.context_id = str(uuid.uuid4())
    
    def add_message(self, message: Message) -> None:
        """Agrega un mensaje."""
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)
    
    def get_messages_for(self, agent_id: str) -> list[Message]:
        """Obtiene mensajes para un agente."""
        return [m for m in self.messages if m.sender_id == agent_id]
    
    def get_recent_messages(self, count: int = 10) -> list[Message]:
        """Obtiene mensajes recientes."""
        return sorted(self.messages, key=lambda m: m.created_at, reverse=True)[:count]


# =============================================================================
# AGENT EXPERIENCE - Experiencia de agente
# =============================================================================

@dataclass
class AgentExperience:
    """Experiencia de un agente."""
    experience_id: str = ""
    agent_id: str = ""
    
    # Descripción
    description: str = ""
    context: str = ""
    
    # Resultado
    outcome: ExperienceOutcome = ExperienceOutcome.UNKNOWN
    
    # Lecciones aprendidas
    lessons_learned: list[str] = field(default_factory=list)
    
    # Métricas
    success_score: float = 0.5  # 0.0 - 1.0
    confidence_score: float = 0.5
    
    # Aplicabilidad
    applicable_scenarios: list[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    validated: bool = False
    
    def __post_init__(self):
        if not self.experience_id:
            self.experience_id = str(uuid.uuid4())
    
    def is_applicable(self, scenario: str) -> bool:
        """Verifica si la experiencia es aplicable a un escenario."""
        return scenario in self.applicable_scenarios
    
    def validate(self) -> None:
        """Valida la experiencia."""
        self.validated = True
    
    def add_lesson(self, lesson: str) -> None:
        """Agrega una lección aprendida."""
        if lesson not in self.lessons_learned:
            self.lessons_learned.append(lesson)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "MemoryType",
    "MemoryImportance",
    "ExperienceOutcome",
    # Domain Objects
    "MemoryRecord",
    "Message",
    "ConversationContext",
    "AgentExperience",
]
