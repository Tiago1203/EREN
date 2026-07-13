"""Runtime trace for the Cognitive Operating System.

Provides comprehensive tracing of all runtime operations, including
state transitions, engine executions, and event publications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class TraceEntry:
    """A single trace entry representing an operation.

    Trace entries record all significant operations during runtime,
    including timing, success/failure, and correlation data.
    """

    entry_id: str
    timestamp: str
    operation: str
    category: str
    component: str
    session_id: str
    correlation_id: str
    cycle_id: str
    duration_ms: int
    success: bool
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Trace entry as dict.
        """
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "category": self.category,
            "component": self.component,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "cycle_id": self.cycle_id,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class TransitionTrace:
    """Records a state transition."""

    transition_id: str
    timestamp: str
    entity_type: str  # "runtime", "session", "cycle"
    entity_id: str
    from_state: str
    to_state: str
    reason: str
    correlation_id: str = ""
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transition_id": self.transition_id,
            "timestamp": self.timestamp,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "reason": reason,
            "correlation_id": self.correlation_id,
            "duration_ms": self.duration_ms,
        }


@dataclass
class EngineExecutionTrace:
    """Records an engine execution."""

    execution_id: str
    timestamp: str
    engine_name: str
    session_id: str
    correlation_id: str
    cycle_id: str
    operation: str
    started_at: str
    completed_at: str = ""
    duration_ms: int = 0
    success: bool = True
    error: str | None = None
    result_summary: str = ""
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "engine_name": self.engine_name,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "cycle_id": self.cycle_id,
            "operation": self.operation,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "result_summary": self.result_summary,
            "input_data": self.input_data,
            "output_data": self.output_data,
        }


@dataclass
class EventPublicationTrace:
    """Records an event publication."""

    publication_id: str
    timestamp: str
    event_type: str
    session_id: str
    correlation_id: str
    runtime_id: str
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "publication_id": self.publication_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "runtime_id": self.runtime_id,
            "success": self.success,
            "error": self.error,
        }


class RuntimeTraceCollector:
    """Collects and manages all runtime traces.

    Provides a comprehensive trace of all operations during
    runtime execution, including:
    - State transitions
    - Engine executions
    - Event publications
    - Errors and failures
    """

    def __init__(self, runtime_id: str):
        """Initialize the trace collector.

        Args:
            runtime_id: The runtime instance ID.
        """
        self._runtime_id = runtime_id
        self._entries: list[TraceEntry] = []
        self._transitions: list[TransitionTrace] = []
        self._engine_executions: list[EngineExecutionTrace] = []
        self._event_publications: list[EventPublicationTrace] = []
        self._enabled = True

    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id

    def enable(self) -> None:
        """Enable trace collection."""
        self._enabled = True

    def disable(self) -> None:
        """Disable trace collection."""
        self._enabled = False

    # -------------------------------------------------------------------------
    # Trace Entries
    # -------------------------------------------------------------------------

    def add_entry(
        self,
        operation: str,
        category: str,
        component: str,
        session_id: str = "",
        correlation_id: str = "",
        cycle_id: str = "",
        duration_ms: int = 0,
        success: bool = True,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a trace entry.

        Args:
            operation: The operation being traced.
            category: Category of the operation.
            component: Component performing the operation.
            session_id: Session ID (if applicable).
            correlation_id: Correlation ID for tracking.
            cycle_id: Cycle ID (if applicable).
            duration_ms: Operation duration.
            success: Whether operation succeeded.
            error: Error message if failed.
            metadata: Additional metadata.
        """
        if not self._enabled:
            return

        entry = TraceEntry(
            entry_id=f"trace_{uuid4().hex[:16]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
            category=category,
            component=component,
            session_id=session_id,
            correlation_id=correlation_id,
            cycle_id=cycle_id,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata or {},
        )
        self._entries.append(entry)

    # -------------------------------------------------------------------------
    # State Transitions
    # -------------------------------------------------------------------------

    def record_transition(
        self,
        entity_type: str,
        entity_id: str,
        from_state: str,
        to_state: str,
        reason: str,
        correlation_id: str = "",
        duration_ms: int = 0,
    ) -> None:
        """Record a state transition.

        Args:
            entity_type: Type of entity (runtime, session, cycle).
            entity_id: ID of the entity.
            from_state: Previous state.
            to_state: New state.
            reason: Reason for transition.
            correlation_id: Correlation ID.
            duration_ms: Transition duration.
        """
        if not self._enabled:
            return

        transition = TransitionTrace(
            transition_id=f"trans_{uuid4().hex[:16]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            entity_type=entity_type,
            entity_id=entity_id,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
        )
        self._transitions.append(transition)

    # -------------------------------------------------------------------------
    # Engine Executions
    # -------------------------------------------------------------------------

    def start_engine_execution(
        self,
        engine_name: str,
        operation: str,
        session_id: str = "",
        correlation_id: str = "",
        cycle_id: str = "",
        input_data: dict[str, Any] | None = None,
    ) -> EngineExecutionTrace:
        """Start tracking an engine execution.

        Args:
            engine_name: Name of the engine.
            operation: Operation being performed.
            session_id: Session ID.
            correlation_id: Correlation ID.
            cycle_id: Cycle ID.
            input_data: Input data for the operation.

        Returns:
            The execution trace object.
        """
        if not self._enabled:
            return None

        trace = EngineExecutionTrace(
            execution_id=f"exec_{uuid4().hex[:16]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            engine_name=engine_name,
            session_id=session_id,
            correlation_id=correlation_id,
            cycle_id=cycle_id,
            operation=operation,
            started_at=datetime.now(timezone.utc).isoformat(),
            input_data=input_data or {},
        )
        self._engine_executions.append(trace)
        return trace

    def complete_engine_execution(
        self,
        execution_id: str,
        success: bool = True,
        error: str | None = None,
        result_summary: str = "",
        output_data: dict[str, Any] | None = None,
    ) -> None:
        """Complete tracking an engine execution.

        Args:
            execution_id: Execution trace ID.
            success: Whether execution succeeded.
            error: Error message if failed.
            result_summary: Summary of results.
            output_data: Output data from the operation.
        """
        if not self._enabled:
            return

        for trace in self._engine_executions:
            if trace.execution_id == execution_id:
                trace.completed_at = datetime.now(timezone.utc).isoformat()
                if trace.started_at:
                    started = datetime.fromisoformat(trace.started_at)
                    completed = datetime.now(timezone.utc)
                    trace.duration_ms = int((completed - started).total_seconds() * 1000)
                trace.success = success
                trace.error = error
                trace.result_summary = result_summary
                trace.output_data = output_data or {}
                break

    # -------------------------------------------------------------------------
    # Event Publications
    # -------------------------------------------------------------------------

    def record_event_publication(
        self,
        event_type: str,
        session_id: str = "",
        correlation_id: str = "",
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record an event publication.

        Args:
            event_type: Type of event.
            session_id: Session ID.
            correlation_id: Correlation ID.
            success: Whether publication succeeded.
            error: Error message if failed.
        """
        if not self._enabled:
            return

        publication = EventPublicationTrace(
            publication_id=f"pub_{uuid4().hex[:16]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            session_id=session_id,
            correlation_id=correlation_id,
            runtime_id=self._runtime_id,
            success=success,
            error=error,
        )
        self._event_publications.append(publication)

    # -------------------------------------------------------------------------
    # Query Methods
    # -------------------------------------------------------------------------

    def get_all_entries(self) -> list[TraceEntry]:
        """Get all trace entries.

        Returns:
            List of all trace entries.
        """
        return self._entries.copy()

    def get_transitions(
        self,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> list[TransitionTrace]:
        """Get transitions filtered by criteria.

        Args:
            entity_type: Filter by entity type.
            entity_id: Filter by entity ID.

        Returns:
            List of matching transitions.
        """
        transitions = self._transitions
        if entity_type:
            transitions = [t for t in transitions if t.entity_type == entity_type]
        if entity_id:
            transitions = [t for t in transitions if t.entity_id == entity_id]
        return transitions

    def get_engine_executions(
        self,
        engine_name: str | None = None,
        session_id: str | None = None,
        cycle_id: str | None = None,
    ) -> list[EngineExecutionTrace]:
        """Get engine executions filtered by criteria.

        Args:
            engine_name: Filter by engine name.
            session_id: Filter by session ID.
            cycle_id: Filter by cycle ID.

        Returns:
            List of matching executions.
        """
        executions = self._engine_executions
        if engine_name:
            executions = [e for e in executions if e.engine_name == engine_name]
        if session_id:
            executions = [e for e in executions if e.session_id == session_id]
        if cycle_id:
            executions = [e for e in executions if e.cycle_id == cycle_id]
        return executions

    def get_event_publications(
        self,
        event_type: str | None = None,
        session_id: str | None = None,
    ) -> list[EventPublicationTrace]:
        """Get event publications filtered by criteria.

        Args:
            event_type: Filter by event type.
            session_id: Filter by session ID.

        Returns:
            List of matching publications.
        """
        publications = self._event_publications
        if event_type:
            publications = [p for p in publications if p.event_type == event_type]
        if session_id:
            publications = [p for p in publications if p.session_id == session_id]
        return publications

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the trace.

        Returns:
            Trace summary.
        """
        return {
            "runtime_id": self._runtime_id,
            "total_entries": len(self._entries),
            "total_transitions": len(self._transitions),
            "total_engine_executions": len(self._engine_executions),
            "total_event_publications": len(self._event_publications),
            "successful_executions": sum(
                1 for e in self._engine_executions if e.success
            ),
            "failed_executions": sum(
                1 for e in self._engine_executions if not e.success
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary.

        Returns:
            Full trace as dictionary.
        """
        return {
            "runtime_id": self._runtime_id,
            "entries": [e.to_dict() for e in self._entries],
            "transitions": [t.to_dict() for t in self._transitions],
            "engine_executions": [e.to_dict() for e in self._engine_executions],
            "event_publications": [p.to_dict() for p in self._event_publications],
        }

    def clear(self) -> None:
        """Clear all trace data."""
        self._entries.clear()
        self._transitions.clear()
        self._engine_executions.clear()
        self._event_publications.clear()
