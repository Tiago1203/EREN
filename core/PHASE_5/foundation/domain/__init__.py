"""
PHASE 5 - EPIC 0: Domain Objects

Objetos de dominio para el sistema multiagente:
- Agent
- AgentTask
- AgentMessage
- AgentContext
- AgentSession
- AgentCapability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid

from core.PHASE_5.foundation.types import (
    AgentState,
    AgentType,
    AgentCapability,
    AgentPriority,
    AgentCapabilityVO,
    AgentMetrics,
    MessageType,
    MessageError,
    AgentVersion,
)


# =============================================================================
# AGENT ENTITY - Entidad principal de agente
# =============================================================================

@dataclass
class Agent:
    """Entidad base de agente."""
    agent_id: str = ""  # Auto-generado si no se provee
    agent_type: AgentType = AgentType.ORCHESTRATOR
    name: str = ""
    
    # State
    state: AgentState = AgentState.INITIAL
    current_task_id: str | None = None
    
    # Capabilities
    capabilities: list[AgentCapabilityVO] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    version: AgentVersion = field(default_factory=AgentVersion)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Metrics
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    
    # Configuration
    max_concurrent_tasks: int = 1
    timeout_seconds: int = 300
    
    # Parent
    parent_agent_id: str | None = None
    session_id: str | None = None
    
    def __post_init__(self):
        if not self.agent_id:
            self.agent_id = str(uuid.uuid4())
    
    @property
    def is_available(self) -> bool:
        """Verifica si el agente está disponible para tareas."""
        return self.state == AgentState.IDLE
    
    @property
    def is_running(self) -> bool:
        """Verifica si el agente está ejecutando."""
        return self.state == AgentState.RUNNING
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Verifica si tiene una capability."""
        return any(c.capability == capability for c in self.capabilities)
    
    def get_capability_level(self, capability: AgentCapability) -> float:
        """Obtiene nivel de capability."""
        for cap in self.capabilities:
            if cap.capability == capability:
                return cap.level
        return 0.0
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "name": self.name,
            "state": self.state.value,
            "capabilities": [c.capability.value for c in self.capabilities],
            "version": str(self.version),
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# AGENT TASK - Definición de tarea
# =============================================================================

class TaskStatus(str, Enum):
    """Estado de tarea."""
    PENDING = "pending"         # Esperando ejecución
    QUEUED = "queued"           # En cola
    RUNNING = "running"         # Ejecutando
    COMPLETED = "completed"     # Completada exitosamente
    FAILED = "failed"          # Fallida
    CANCELLED = "cancelled"    # Cancelada
    TIMEOUT = "timeout"         # Timeout


@dataclass
class AgentTask:
    """Tarea asignada a un agente."""
    task_id: str
    agent_id: str
    
    # Task definition
    task_type: str
    description: str = ""
    
    # Input/Output
    input_data: dict = field(default_factory=dict)
    expected_output: dict | None = None
    actual_output: dict | None = None
    
    # Constraints
    priority: AgentPriority = AgentPriority.MEDIUM
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    
    # Dependencies
    depends_on: list[str] = field(default_factory=list)  # task_ids
    required_capabilities: list[AgentCapability] = field(default_factory=list)
    
    # State
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    
    # Error handling
    error: str | None = None
    error_code: MessageError | None = None
    
    # Metadata
    session_id: str | None = None
    correlation_id: str | None = None
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
    
    @property
    def duration_ms(self) -> int | None:
        """Duración en milisegundos."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None
    
    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED
    
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries


# =============================================================================
# AGENT MESSAGE - Mensaje entre agentes
# =============================================================================

@dataclass
class AgentMessage:
    """Mensaje intercambiado entre agentes."""
    message_id: str
    sender: str
    receiver: str  # Puede ser agent_id o "*" para broadcast
    
    # Content
    type: MessageType
    action: str
    payload: dict = field(default_factory=dict)
    
    # Routing
    topic: str | None = None  # Para Pub/Sub
    
    # Correlation
    correlation_id: str | None = None
    parent_id: str | None = None  # Para replies
    
    # QoS
    priority: AgentPriority = AgentPriority.MEDIUM
    ttl: int = 300  # segundos
    retry_count: int = 0
    max_retries: int = 3
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    sent_at: datetime | None = None
    received_at: datetime | None = None
    processed_at: datetime | None = None
    
    # Error handling
    error: str | None = None
    error_code: MessageError | None = None
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
    
    @property
    def is_request(self) -> bool:
        return self.type == MessageType.REQUEST
    
    @property
    def is_response(self) -> bool:
        return self.type == MessageType.RESPONSE
    
    @property
    def is_broadcast(self) -> bool:
        return self.receiver == "*"
    
    def create_reply(self, payload: dict, success: bool = True) -> AgentMessage:
        """Crea mensaje de respuesta."""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender=self.receiver,
            receiver=self.sender,
            type=MessageType.RESPONSE,
            action=f"{self.action}_response",
            payload=payload,
            correlation_id=self.correlation_id or self.message_id,
            parent_id=self.message_id,
            priority=self.priority,
        )
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.type.value,
            "action": self.action,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# AGENT CONTEXT - Contexto compartido
# =============================================================================

@dataclass
class AgentContext:
    """Contexto compartido entre agentes en una sesión."""
    context_id: str
    session_id: str
    
    # Data
    data: dict = field(default_factory=dict)
    
    # Participants
    participating_agents: list[str] = field(default_factory=list)
    
    # State
    state: dict = field(default_factory=dict)
    
    # History
    message_history: list[AgentMessage] = field(default_factory=list)
    task_history: list[AgentTask] = field(default_factory=list)
    
    # Created
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # TTL
    expires_at: datetime | None = None
    
    def __post_init__(self):
        if not self.context_id:
            self.context_id = str(uuid.uuid4())
    
    def add_agent(self, agent_id: str) -> None:
        """Agrega agente participante."""
        if agent_id not in self.participating_agents:
            self.participating_agents.append(agent_id)
    
    def remove_agent(self, agent_id: str) -> None:
        """Remueve agente participante."""
        if agent_id in self.participating_agents:
            self.participating_agents.remove(agent_id)
    
    def set_value(self, key: str, value: Any) -> None:
        """Establece valor en contexto."""
        self.data[key] = value
        self.updated_at = datetime.now(UTC)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Obtiene valor del contexto."""
        return self.data.get(key, default)


# =============================================================================
# AGENT SESSION - Sesión de agente
# =============================================================================

class SessionStatus(str, Enum):
    """Estado de sesión."""
    ACTIVE = "active"
    IDLE = "idle"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    EXPIRED = "expired"


@dataclass
class AgentSession:
    """Sesión de trabajo de un agente."""
    session_id: str
    agent_id: str
    
    # Session info
    name: str = ""
    description: str = ""
    
    # State
    status: SessionStatus = SessionStatus.ACTIVE
    
    # Tasks
    tasks: list[AgentTask] = field(default_factory=list)
    active_task_id: str | None = None
    
    # Messages
    messages_sent: int = 0
    messages_received: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = field(default_factory=lambda: datetime.now(UTC))
    closed_at: datetime | None = None
    
    # TTL
    ttl_seconds: int = 3600  # 1 hora por defecto
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    @property
    def is_active(self) -> bool:
        return self.status == SessionStatus.ACTIVE
    
    def add_task(self, task: AgentTask) -> None:
        """Agrega tarea a la sesión."""
        task.session_id = self.session_id
        self.tasks.append(task)
        self.last_activity = datetime.now(UTC)
    
    def get_active_task(self) -> AgentTask | None:
        """Obtiene tarea activa."""
        if self.active_task_id:
            for task in self.tasks:
                if task.task_id == self.active_task_id:
                    return task
        return None


# =============================================================================
# AGENT RESULT - Resultado de ejecución
# =============================================================================

class ConfidenceLevel(str, Enum):
    """Nivel de confianza."""
    HIGH = "high"       # >= 0.8
    MEDIUM = "medium"   # >= 0.5
    LOW = "low"         # >= 0.3
    UNKNOWN = "unknown" # < 0.3


@dataclass
class AgentResult:
    """Resultado de ejecución de un agente."""
    task_id: str
    agent_id: str
    
    # Result
    success: bool
    output: dict = field(default_factory=dict)
    
    # Metrics
    execution_time_ms: int = 0
    tokens_used: int = 0
    
    # Confidence
    confidence: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    
    # Evidence
    citations: list[str] = field(default_factory=list)
    reasoning: str = ""
    
    # Errors
    error: str | None = None
    error_code: str | None = None
    
    # Timestamps
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "output": self.output,
            "confidence": self.confidence,
            "execution_time_ms": self.execution_time_ms,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Agent
    "Agent",
    # Task
    "AgentTask",
    "TaskStatus",
    # Message
    "AgentMessage",
    # Context
    "AgentContext",
    # Session
    "AgentSession",
    "SessionStatus",
    # Result
    "AgentResult",
    "ConfidenceLevel",
]
