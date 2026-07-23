"""
PHASE 5 - EPIC 0: Agent Events

Sistema de eventos para comunicación asíncrona entre componentes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Callable, Any, Optional
import uuid


# =============================================================================
# EVENT TYPES - Tipos de evento
# =============================================================================

class AgentEventType(str, Enum):
    """Tipos de evento del sistema multiagente."""
    # Agent Lifecycle
    AGENT_REGISTERED = "agent.registered"
    AGENT_UNREGISTERED = "agent.unregistered"
    AGENT_INITIALIZED = "agent.initialized"
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    
    # Task Events
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    
    # Message Events
    MESSAGE_SENT = "message.sent"
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_PROCESSED = "message.processed"
    MESSAGE_FAILED = "message.failed"
    
    # System Events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"
    
    # Collaboration Events
    COLLABORATION_STARTED = "collaboration.started"
    COLLABORATION_ENDED = "collaboration.ended"
    CONSENSUS_REACHED = "consensus.reached"


class EventSeverity(str, Enum):
    """Severidad del evento."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# =============================================================================
# AGENT EVENT - Evento del sistema
# =============================================================================

@dataclass
class AgentEvent:
    """Evento del sistema multiagente."""
    event_id: str
    event_type: AgentEventType
    agent_id: str
    
    # Content
    message: str = ""
    data: dict = field(default_factory=dict)
    
    # Severity
    severity: EventSeverity = EventSeverity.INFO
    
    # Context
    session_id: str | None = None
    task_id: str | None = None
    correlation_id: str | None = None
    
    # Source
    source_agent_id: str | None = None
    source_module: str = "foundation"
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "message": self.message,
            "severity": self.severity.value,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# EVENT SUBSCRIBER - Suscriptor de eventos
# =============================================================================

@dataclass
class EventSubscriber:
    """Suscriptor de eventos."""
    subscriber_id: str
    agent_id: str
    
    # Handler (required, no default)
    handler: Callable[[AgentEvent], None]
    
    # Topics
    event_types: list[AgentEventType] = field(default_factory=list)
    
    # Filters
    agent_filter: str | None = None
    severity_filter: list[EventSeverity] | None = None
    
    # Status
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# EVENT BUS - Bus de eventos
# =============================================================================

class EventBus:
    """Bus de eventos para el sistema multiagente."""
    
    def __init__(self):
        # Suscribers por tipo de evento
        self._subscribers: dict[AgentEventType, list[EventSubscriber]] = {}
        
        # Historial de eventos
        self._event_history: list[AgentEvent] = []
        self._max_history: int = 1000
        
        # Handlers síncronos
        self._handlers: dict[AgentEventType, list[Callable]] = {}
    
    async def publish(self, event: AgentEvent) -> bool:
        """Publica un evento."""
        # Agregar a historial
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notificar subscriptors
        subscribers = self._subscribers.get(event.event_type, [])
        for subscriber in subscribers:
            if subscriber.active:
                try:
                    subscriber.handler(event)
                except Exception:
                    pass  # Log error
        
        # Notificar handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                pass  # Log error
        
        return True
    
    async def subscribe(
        self,
        subscriber: EventSubscriber,
    ) -> bool:
        """Suscribe a eventos."""
        for event_type in subscriber.event_types:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(subscriber)
        return True
    
    async def unsubscribe(
        self,
        subscriber_id: str,
    ) -> bool:
        """Desuscribe de eventos."""
        for event_type, subscribers in self._subscribers.items():
            self._subscribers[event_type] = [
                s for s in subscribers
                if s.subscriber_id != subscriber_id
            ]
        return True
    
    def add_handler(
        self,
        event_type: AgentEventType,
        handler: Callable[[AgentEvent], None],
    ) -> None:
        """Agrega un handler para un tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def get_history(
        self,
        event_type: AgentEventType | None = None,
        agent_id: str | None = None,
        limit: int = 100,
    ) -> list[AgentEvent]:
        """Obtiene historial de eventos."""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if agent_id:
            events = [e for e in events if e.agent_id == agent_id]
        
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Limpia historial de eventos."""
        self._event_history.clear()


# =============================================================================
# EVENT FACTORY - Fábrica de eventos
# =============================================================================

class EventFactory:
    """Fábrica para crear eventos comunes."""
    
    @staticmethod
    def agent_registered(agent_id: str) -> AgentEvent:
        """Crea evento de agente registrado."""
        return AgentEvent(
            event_id=str(uuid.uuid4()),
            event_type=AgentEventType.AGENT_REGISTERED,
            agent_id=agent_id,
            message=f"Agent {agent_id} registered",
        )
    
    @staticmethod
    def agent_started(agent_id: str) -> AgentEvent:
        """Crea evento de agente iniciado."""
        return AgentEvent(
            event_id=str(uuid.uuid4()),
            event_type=AgentEventType.AGENT_STARTED,
            agent_id=agent_id,
            message=f"Agent {agent_id} started",
        )
    
    @staticmethod
    def agent_completed(agent_id: str, task_id: str) -> AgentEvent:
        """Crea evento de agente completado."""
        return AgentEvent(
            event_id=str(uuid.uuid4()),
            event_type=AgentEventType.AGENT_COMPLETED,
            agent_id=agent_id,
            message=f"Agent {agent_id} completed task {task_id}",
            data={"task_id": task_id},
        )
    
    @staticmethod
    def agent_failed(agent_id: str, error: str) -> AgentEvent:
        """Crea evento de agente fallido."""
        return AgentEvent(
            event_id=str(uuid.uuid4()),
            event_type=AgentEventType.AGENT_FAILED,
            agent_id=agent_id,
            message=f"Agent {agent_id} failed: {error}",
            severity=EventSeverity.ERROR,
            data={"error": error},
        )
    
    @staticmethod
    def task_created(task_id: str, agent_id: str) -> AgentEvent:
        """Crea evento de tarea creada."""
        return AgentEvent(
            event_id=str(uuid.uuid4()),
            event_type=AgentEventType.TASK_CREATED,
            agent_id=agent_id,
            message=f"Task {task_id} created",
            data={"task_id": task_id},
        )
    
    @staticmethod
    def task_completed(task_id: str, agent_id: str) -> AgentEvent:
        """Crea evento de tarea completada."""
        return AgentEvent(
            event_id=str(uuid.uuid4()),
            event_type=AgentEventType.TASK_COMPLETED,
            agent_id=agent_id,
            message=f"Task {task_id} completed",
            data={"task_id": task_id},
        )
    
    @staticmethod
    def message_sent(sender: str, receiver: str, message_id: str) -> AgentEvent:
        """Crea evento de mensaje enviado."""
        return AgentEvent(
            event_id=str(uuid.uuid4()),
            event_type=AgentEventType.MESSAGE_SENT,
            agent_id=sender,
            message=f"Message {message_id} sent from {sender} to {receiver}",
            data={
                "message_id": message_id,
                "sender": sender,
                "receiver": receiver,
            },
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Event Types
    "AgentEventType",
    "EventSeverity",
    # Event
    "AgentEvent",
    # Subscriber
    "EventSubscriber",
    # Bus
    "EventBus",
    # Factory
    "EventFactory",
]
