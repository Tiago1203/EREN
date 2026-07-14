"""Cognitive Events for EREN OS Cognitive Runtime.

Events emitted during cognitive pipeline execution.
Each stage emits its specific event for observability.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class CognitiveEventType(str, Enum):
    """Event types for cognitive pipeline execution.
    
    Each event represents a stage completion or milestone
    in the cognitive processing pipeline.
    """
    
    # Pipeline lifecycle
    PIPELINE_INITIALIZED = "pipeline_initialized"
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    
    # Cognitive stages
    INPUT_RECEIVED = "input_received"
    INTENT_DETECTED = "intent_detected"
    CONTEXT_BUILT = "context_built"
    MEMORY_RETRIEVED = "memory_retrieved"
    KNOWLEDGE_RETRIEVED = "knowledge_retrieved"
    REASONING_COMPLETED = "reasoning_completed"
    PLAN_CREATED = "plan_created"
    DECISION_MADE = "decision_made"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    LEARNING_COMPLETED = "learning_completed"
    RESPONSE_GENERATED = "response_generated"
    
    # Telemetry events
    METRICS_RECORDED = "metrics_recorded"
    TRACE_RECORDED = "trace_recorded"


@dataclass
class CognitiveEvent:
    """Base class for all cognitive events.
    
    All cognitive events contain common metadata plus
    stage-specific data.
    """
    
    event_type: CognitiveEventType | str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str = ""
    session_id: str = ""
    pipeline_id: str = ""
    stage_name: str = ""
    success: bool = True
    error: str = ""
    
    # Telemetry
    duration_ms: float = 0.0
    tokens_used: int = 0
    provider: str = ""
    estimated_cost: float = 0.0
    
    # Stage-specific data
    data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        event_type_str = (
            self.event_type.value 
            if isinstance(self.event_type, Enum) 
            else self.event_type
        )
        return {
            "event_type": event_type_str,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "pipeline_id": self.pipeline_id,
            "stage_name": self.stage_name,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "provider": self.provider,
            "estimated_cost": self.estimated_cost,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass
class IntentDetectedEvent(CognitiveEvent):
    """Event emitted when intent is detected from user input."""
    
    intent: str = ""
    confidence: float = 0.0
    entities: dict = field(default_factory=dict)
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.INTENT_DETECTED


@dataclass
class ContextBuiltEvent(CognitiveEvent):
    """Event emitted when context is built."""
    
    context_items: int = 0
    context_sources: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.CONTEXT_BUILT


@dataclass
class MemoryRetrievedEvent(CognitiveEvent):
    """Event emitted when memory is retrieved."""
    
    memories_found: int = 0
    memory_types: list[str] = field(default_factory=list)
    relevance_scores: list[float] = field(default_factory=list)
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.MEMORY_RETRIEVED


@dataclass
class KnowledgeRetrievedEvent(CognitiveEvent):
    """Event emitted when knowledge is retrieved."""
    
    knowledge_found: int = 0
    knowledge_sources: list[str] = field(default_factory=list)
    relevance: float = 0.0
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.KNOWLEDGE_RETRIEVED


@dataclass
class ReasoningCompletedEvent(CognitiveEvent):
    """Event emitted when reasoning is completed."""
    
    reasoning_type: str = ""
    confidence: float = 0.0
    evidence_count: int = 0
    conclusions: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.REASONING_COMPLETED


@dataclass
class PlanCreatedEvent(CognitiveEvent):
    """Event emitted when a plan is created."""
    
    plan_id: str = ""
    task_count: int = 0
    estimated_duration_ms: float = 0.0
    risk_level: str = "low"
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.PLAN_CREATED


@dataclass
class DecisionMadeEvent(CognitiveEvent):
    """Event emitted when a decision is made."""
    
    decision: str = ""
    confidence: float = 0.0
    alternatives_considered: int = 0
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.DECISION_MADE


@dataclass
class ExecutionCompletedEvent(CognitiveEvent):
    """Event emitted when execution is completed."""
    
    actions_executed: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.EXECUTION_COMPLETED


@dataclass
class LearningCompletedEvent(CognitiveEvent):
    """Event emitted when learning is completed."""
    
    lessons_learned: int = 0
    memory_updates: int = 0
    confidence_delta: float = 0.0
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.LEARNING_COMPLETED


@dataclass
class ResponseGeneratedEvent(CognitiveEvent):
    """Event emitted when response is generated."""
    
    response_text: str = ""
    response_type: str = ""
    includes_citations: bool = False
    
    def __post_init__(self):
        self.event_type = CognitiveEventType.RESPONSE_GENERATED


class CognitiveEventPublisher:
    """Publisher for cognitive events.
    
    Integrates with EREN's Event Bus and provides
    convenience methods for publishing cognitive events.
    """
    
    def __init__(self, event_bus=None):
        """Initialize the event publisher.
        
        Args:
            event_bus: Optional Event Bus instance.
        """
        self._event_bus = event_bus
        self._event_history: list[CognitiveEvent] = []
        self._lock = threading.RLock()
        self._subscribers: list[callable] = []
    
    def set_event_bus(self, event_bus) -> None:
        """Set the Event Bus instance.
        
        Args:
            event_bus: Event Bus to use.
        """
        self._event_bus = event_bus
    
    def subscribe(self, callback: callable) -> None:
        """Subscribe to cognitive events.
        
        Args:
            callback: Function to call with events.
        """
        with self._lock:
            self._subscribers.append(callback)
    
    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from cognitive events.
        
        Args:
            callback: Function to remove.
        """
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
    
    def publish(self, event: CognitiveEvent) -> None:
        """Publish a cognitive event.
        
        Args:
            event: The event to publish.
        """
        with self._lock:
            # Store in history
            self._event_history.append(event)
            
            # Notify subscribers
            for callback in self._subscribers:
                try:
                    callback(event)
                except Exception:
                    pass  # Don't let subscriber errors break publishing
            
            # Publish to event bus if available
            if self._event_bus:
                self._event_bus.publish(
                    topic=event.event_type,
                    payload=event.to_dict()
                )
    
    def get_history(
        self, 
        session_id: str | None = None,
        event_type: CognitiveEventType | None = None,
        limit: int = 100
    ) -> list[CognitiveEvent]:
        """Get event history with optional filtering.
        
        Args:
            session_id: Filter by session ID.
            event_type: Filter by event type.
            limit: Maximum number of events to return.
            
        Returns:
            List of matching events.
        """
        with self._lock:
            events = self._event_history
            
            if session_id:
                events = [e for e in events if e.session_id == session_id]
            
            if event_type:
                event_type_str = (
                    event_type.value 
                    if isinstance(event_type, Enum) 
                    else event_type
                )
                events = [
                    e for e in events 
                    if e.event_type == event_type_str
                ]
            
            return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._event_history.clear()
