"""
PHASE 5 - EPIC 0: Agent Types

Tipos fundamentales para el sistema multiagente:
- AgentType
- AgentState
- AgentCapability
- AgentPriority
- MessageType
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional
import uuid


# =============================================================================
# ENUMS - Estados y tipos de agente
# =============================================================================

class AgentState(str, Enum):
    """Estados del ciclo de vida de un agente."""
    INITIAL = "initial"           # Estado inicial
    IDLE = "idle"                 # Esperando tareas
    INITIALIZING = "initializing" # En proceso de inicialización
    RUNNING = "running"           # Ejecutando tarea
    WAITING = "waiting"            # Esperando respuesta externa
    COMPLETED = "completed"        # Tarea completada
    FAILED = "failed"             # Falló ejecución
    STOPPED = "stopped"           # Detenido permanentemente


class AgentType(str, Enum):
    """Tipos de agente especializado."""
    ORCHESTRATOR = "orchestrator"       # Orquestador central
    BIOMEDICAL = "biomedical"           # Agente biomédico
    DIAGNOSTIC = "diagnostic"           # Agente de diagnóstico
    KNOWLEDGE = "knowledge"             # Agente de conocimiento
    RESEARCH = "research"               # Agente de investigación
    PLANNING = "planning"               # Agente de planificación
    COLLABORATION = "collaboration"     # Motor de colaboración
    CONSENSUS = "consensus"             # Motor de consenso
    MEMORY = "memory"                   # Motor de memoria
    LEARNING = "learning"               # Motor de aprendizaje
    GOVERNANCE = "governance"           # Motor de gobernanza


class AgentCapability(str, Enum):
    """Capacidades que puede tener un agente."""
    # Análisis
    DIAGNOSE = "diagnose"                 # Capacidad de diagnóstico
    ANALYZE = "analyze"                   # Análisis general
    RESEARCH = "research"                 # Investigación
    PLAN = "plan"                         # Planificación
    
    # Ejecución
    EXECUTE = "execute"                   # Ejecución de tareas
    COORDINATE = "coordinate"             # Coordinación
    VALIDATE = "validate"                 # Validación
    
    # Colaboración
    COLLABORATE = "collaborate"           # Colaboración
    COMMUNICATE = "communicate"           # Comunicación
    NEGOTIATE = "negotiate"               # Negociación
    
    # Cognición
    REASON = "reason"                     # Razonamiento
    LEARN = "learn"                       # Aprendizaje
    MEMORIZE = "memorize"                 # Memorización
    
    # Gestión
    GOVERN = "govern"                     # Gobernanza
    AUDIT = "audit"                       # Auditoría
    MONITOR = "monitor"                   # Monitoreo


class AgentPriority(str, Enum):
    """Prioridad de tareas y mensajes."""
    CRITICAL = "critical"   # Crítica - respuesta inmediata
    HIGH = "high"           # Alta prioridad
    MEDIUM = "medium"       # Prioridad normal
    LOW = "low"             # Baja prioridad - puede esperar


class MessageType(str, Enum):
    """Tipos de mensaje entre agentes."""
    # Síncrono
    REQUEST = "request"         # Request con Response esperada
    RESPONSE = "response"       # Response a Request
    
    # Asíncrono
    NOTIFICATION = "notification"  # Pub/Sub notificación
    EVENT = "event"              # Evento del sistema
    
    # Control
    ERROR = "error"              # Mensaje de error
    HEARTBEAT = "heartbeat"      # Heartbeat alive
    COMMAND = "command"           # Comando directo


class MessageError(str, Enum):
    """Errores de mensajería."""
    TIMEOUT = "timeout"                    # No response within timeout
    AGENT_NOT_FOUND = "agent_not_found"   # Receiver doesn't exist
    QUEUE_FULL = "queue_full"             # Receiver queue full
    INVALID_MESSAGE = "invalid_message"   # Malformed message
    PROCESSING_FAILED = "processing_failed"  # Processing error


# =============================================================================
# VALUE OBJECTS - Objetos de valor
# =============================================================================

@dataclass(frozen=True)
class AgentCapabilityVO:
    """Value object para capability de agente."""
    capability: AgentCapability
    level: float = 1.0  # 0.0 - 1.0 nivel de competencia
    description: str = ""
    
    def __str__(self) -> str:
        return f"{self.capability.value}:{self.level}"


@dataclass(frozen=True)
class AgentVersion:
    """Versión semántica de un agente."""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __lt__(self, other: AgentVersion) -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch


@dataclass
class AgentMetrics:
    """Métricas de rendimiento de un agente."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_execution_time_ms: float = 0.0
    messages_sent: int = 0
    messages_received: int = 0
    last_execution: datetime | None = None


# =============================================================================
# AGENT CONFIGURATION - Configuración de agente
# =============================================================================

@dataclass
class AgentConfig:
    """Configuración para instanciar un agente."""
    agent_id: str = ""
    agent_type: AgentType = AgentType.BIOMEDICAL
    name: str = ""
    description: str = ""
    
    # Capabilities
    capabilities: list[AgentCapability] = field(default_factory=list)
    capability_levels: dict[AgentCapability, float] = field(default_factory=dict)
    
    # Settings
    max_concurrent_tasks: int = 1
    timeout_seconds: int = 300
    retry_attempts: int = 3
    
    # Priority
    default_priority: AgentPriority = AgentPriority.MEDIUM
    
    # Version
    version: AgentVersion = field(default_factory=AgentVersion)
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    
    def get_capability_level(self, cap: AgentCapability) -> float:
        """Obtiene nivel de capability."""
        return self.capability_levels.get(cap, 1.0)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "AgentState",
    "AgentType",
    "AgentCapability",
    "AgentPriority",
    "MessageType",
    "MessageError",
    # Value Objects
    "AgentCapabilityVO",
    "AgentVersion",
    "AgentMetrics",
    # Config
    "AgentConfig",
]
