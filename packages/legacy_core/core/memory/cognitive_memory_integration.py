"""Cognitive Memory Integration (PR-049).

Integration layer between Cognitive Memory and the Cognitive Pipeline.
Provides memory-aware stages and event publishing.

Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from core.memory.memory_engine import CognitiveMemoryEngine


# =============================================================================
# Memory Events
# =============================================================================


class MemoryEventType(str, Enum):
    """Types of memory events."""

    MEMORY_STORED = "memory_stored"
    MEMORY_RETRIEVED = "memory_retrieved"
    MEMORY_UPDATED = "memory_updated"
    MEMORY_DELETED = "memory_deleted"
    MEMORY_SEARCHED = "memory_searched"
    MEMORY_CONSOLIDATED = "memory_consolidated"
    MEMORY_FORGOTTEN = "memory_forgotten"
    MEMORY_ACCESSED = "memory_accessed"


@dataclass
class MemoryEvent:
    """Memory event for the Event Bus."""

    event_type: MemoryEventType
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    memory_id: str = ""
    memory_type: str = ""
    session_id: str = ""
    correlation_id: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Memory Event Publisher
# =============================================================================


class MemoryEventPublisher:
    """Publisher for memory events."""

    def __init__(self):
        """Initialize the publisher."""
        self._subscribers: list[callable] = []
        self._history: list[MemoryEvent] = []

    def subscribe(self, callback: callable) -> None:
        """Subscribe to memory events."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from memory events."""
        self._subscribers.remove(callback)

    def publish(self, event: MemoryEvent) -> None:
        """Publish a memory event."""
        self._history.append(event)
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass  # Best effort

    def get_history(
        self,
        session_id: str | None = None,
        event_type: MemoryEventType | None = None,
        limit: int = 100,
    ) -> list[MemoryEvent]:
        """Get event history."""
        history = self._history

        if session_id:
            history = [e for e in history if e.session_id == session_id]
        if event_type:
            history = [e for e in history if e.event_type == event_type]

        return history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()


# =============================================================================
# Memory Metrics
# =============================================================================


@dataclass
class MemoryMetrics:
    """Metrics for memory operations."""

    total_stores: int = 0
    total_memories: int = 0
    working_memory_count: int = 0
    short_term_count: int = 0
    long_term_count: int = 0
    episodic_count: int = 0
    semantic_count: int = 0
    procedural_count: int = 0
    total_searches: int = 0
    successful_searches: int = 0
    failed_searches: int = 0
    average_search_duration_ms: float = 0.0
    total_storage_duration_ms: float = 0.0
    total_retrieval_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0


# =============================================================================
# Memory Tracer
# =============================================================================


@dataclass
class MemoryTrace:
    """Trace of a memory operation."""

    operation: str
    memory_id: str = ""
    memory_type: str = ""
    start_time: str = ""
    end_time: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class MemoryTracer:
    """Tracer for memory operations."""

    def __init__(self):
        """Initialize the tracer."""
        self._traces: list[MemoryTrace] = []
        self._lock_count: int = 0

    def begin_trace(self, operation: str, **kwargs) -> int:
        """Begin a trace. Returns trace ID."""
        trace_id = len(self._traces)
        self._traces.append(MemoryTrace(
            operation=operation,
            start_time=datetime.now(UTC).isoformat(),
            details=kwargs,
        ))
        self._lock_count += 1
        return trace_id

    def end_trace(self, trace_id: int, success: bool = True, error: str = "") -> None:
        """End a trace."""
        if 0 <= trace_id < len(self._traces):
            trace = self._traces[trace_id]
            trace.end_time = datetime.now(UTC).isoformat()
            trace.success = success
            trace.error = error

            if trace.start_time:
                start = datetime.fromisoformat(trace.start_time)
                end = datetime.fromisoformat(trace.end_time)
                trace.duration_ms = (end - start).total_seconds() * 1000

    def get_traces(self, limit: int = 100) -> list[MemoryTrace]:
        """Get recent traces."""
        return self._traces[-limit:]


# =============================================================================
# Memory Integration Wrapper
# =============================================================================


class CognitiveMemoryIntegration:
    """Integration layer for cognitive memory.

    Provides:
    - Event publishing for all memory operations
    - Metrics collection
    - Tracing
    - Caching layer
    """

    def __init__(self, engine: "CognitiveMemoryEngine"):
        """Initialize the integration layer.

        Args:
            engine: The underlying memory engine.
        """
        self._engine = engine
        self._publisher = MemoryEventPublisher()
        self._metrics = MemoryMetrics()
        self._tracer = MemoryTracer()
        self._cache: dict[str, Any] = {}

    @property
    def engine(self) -> "CognitiveMemoryEngine":
        """Get the underlying engine."""
        return self._engine

    @property
    def publisher(self) -> MemoryEventPublisher:
        """Get the event publisher."""
        return self._publisher

    @property
    def metrics(self) -> MemoryMetrics:
        """Get current metrics."""
        return self._metrics

    def store(
        self,
        content: str | dict,
        memory_type: Any,  # MemoryType enum
        session_id: str = "",
        correlation_id: str = "",
        **kwargs,
    ) -> str:
        """Store a memory with full instrumentation.

        Args:
            content: The content to store
            memory_type: Type of memory
            session_id: Session ID for tracking
            correlation_id: Correlation ID
            **kwargs: Additional arguments

        Returns:
            The memory ID.
        """
        import time

        trace_id = self._tracer.begin_trace(
            "store",
            memory_type=memory_type.value if hasattr(memory_type, "value") else str(memory_type),
            session_id=session_id,
        )

        start = time.perf_counter()

        try:
            memory_id = self._engine.store(content, memory_type, **kwargs)

            # Publish event
            self._publisher.publish(MemoryEvent(
                event_type=MemoryEventType.MEMORY_STORED,
                memory_id=memory_id,
                memory_type=memory_type.value if hasattr(memory_type, "value") else str(memory_type),
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=True,
            ))

            # Update metrics
            self._metrics.total_memories += 1
            self._metrics.total_storage_duration_ms += (time.perf_counter() - start) * 1000

            self._tracer.end_trace(trace_id, success=True)
            return memory_id

        except Exception as e:
            self._publisher.publish(MemoryEvent(
                event_type=MemoryEventType.MEMORY_STORED,
                memory_id="",
                memory_type=memory_type.value if hasattr(memory_type, "value") else str(memory_type),
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=False,
                error=str(e),
            ))

            self._tracer.end_trace(trace_id, success=False, error=str(e))
            raise

    def retrieve(
        self,
        memory_id: str,
        memory_type: Any = None,
        session_id: str = "",
        correlation_id: str = "",
    ) -> Any:
        """Retrieve a memory with full instrumentation.

        Args:
            memory_id: The memory ID
            memory_type: Optional specific type
            session_id: Session ID
            correlation_id: Correlation ID

        Returns:
            The memory entry or None.
        """
        import time

        trace_id = self._tracer.begin_trace(
            "retrieve",
            memory_id=memory_id,
            session_id=session_id,
        )

        start = time.perf_counter()

        try:
            memory = self._engine.retrieve(memory_id, memory_type)

            # Publish event
            self._publisher.publish(MemoryEvent(
                event_type=MemoryEventType.MEMORY_RETRIEVED,
                memory_id=memory_id,
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=memory is not None,
            ))

            # Update metrics
            self._metrics.total_retrieval_duration_ms += (time.perf_counter() - start) * 1000

            self._tracer.end_trace(trace_id, success=memory is not None)
            return memory

        except Exception as e:
            self._publisher.publish(MemoryEvent(
                event_type=MemoryEventType.MEMORY_RETRIEVED,
                memory_id=memory_id,
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=False,
                error=str(e),
            ))

            self._tracer.end_trace(trace_id, success=False, error=str(e))
            raise

    def search(
        self,
        query: Any,  # MemoryQuery
        session_id: str = "",
        correlation_id: str = "",
        **kwargs,
    ) -> list[Any]:
        """Search memories with full instrumentation.

        Args:
            query: The search query
            session_id: Session ID
            correlation_id: Correlation ID
            **kwargs: Additional arguments

        Returns:
            List of matching memories.
        """
        import time

        trace_id = self._tracer.begin_trace(
            "search",
            session_id=session_id,
        )

        start = time.perf_counter()
        self._metrics.total_searches += 1

        try:
            results = self._engine.search(query, **kwargs)

            self._publisher.publish(MemoryEvent(
                event_type=MemoryEventType.MEMORY_SEARCHED,
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=True,
                metadata={"result_count": len(results)},
            ))

            self._metrics.successful_searches += 1
            self._tracer.end_trace(trace_id, success=True)
            return results

        except Exception as e:
            self._publisher.publish(MemoryEvent(
                event_type=MemoryEventType.MEMORY_SEARCHED,
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=False,
                error=str(e),
            ))

            self._metrics.failed_searches += 1
            self._tracer.end_trace(trace_id, success=False, error=str(e))
            raise

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all memory metrics.

        Returns:
            Dictionary of metrics.
        """
        stats = self._engine.get_statistics()

        return {
            "engine": stats,
            "metrics": {
                "total_memories": self._metrics.total_memories,
                "total_searches": self._metrics.total_searches,
                "successful_searches": self._metrics.successful_searches,
                "failed_searches": self._metrics.failed_searches,
                "average_search_duration_ms": (
                    self._metrics.average_search_duration_ms
                ),
                "total_storage_duration_ms": self._metrics.total_storage_duration_ms,
                "total_retrieval_duration_ms": self._metrics.total_retrieval_duration_ms,
                "cache_hits": self._metrics.cache_hits,
                "cache_misses": self._metrics.cache_misses,
            },
            "traces": len(self._tracer._traces),
        }


# =============================================================================
# Factory Function
# =============================================================================


def create_cognitive_memory_integration(
    engine: "CognitiveMemoryEngine" = None,
) -> CognitiveMemoryIntegration:
    """Create a cognitive memory integration.

    Args:
        engine: Optional memory engine (creates new if not provided)

    Returns:
        CognitiveMemoryIntegration instance.
    """
    if engine is None:
        from core.memory.memory_engine import CognitiveMemoryEngine
        engine = CognitiveMemoryEngine()

    return CognitiveMemoryIntegration(engine)
