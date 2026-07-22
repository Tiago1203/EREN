"""Runtime context for the Cognitive Operating System.

Provides the execution context for the cognitive runtime, including
access to all components and the current cognitive session state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass
class ComponentReferences:
    """References to all runtime components.

    These are the actual component instances that the runtime
    uses to execute the cognitive cycle.
    """

    # Infrastructure
    container: Any = None
    event_bus: Any = None
    capability_registry: Any = None
    composition_root: Any = None

    # Boot and Lifecycle
    boot_manager: Any = None
    lifecycle_manager: Any = None
    session_manager: Any = None

    # Orchestration
    orchestrator: Any = None
    scheduler: Any = None

    # Cognitive Engines
    planner: Any = None
    knowledge_engine: Any = None
    memory_engine: Any = None
    reasoning_engine: Any = None
    decision_engine: Any = None
    tool_engine: Any = None

    def get_engine(self, engine_name: str) -> Any:
        """Get an engine by name.

        Args:
            engine_name: Name of the engine.

        Returns:
            The engine instance or None.
        """
        engines = {
            "planner": self.planner,
            "knowledge": self.knowledge_engine,
            "knowledge_engine": self.knowledge_engine,
            "memory": self.memory_engine,
            "memory_engine": self.memory_engine,
            "reasoning": self.reasoning_engine,
            "reasoning_engine": self.reasoning_engine,
            "decision": self.decision_engine,
            "decision_engine": self.decision_engine,
            "tools": self.tool_engine,
            "tool_engine": self.tool_engine,
        }
        return engines.get(engine_name)

    def get_all_engines(self) -> dict[str, Any]:
        """Get all engines.

        Returns:
            Dictionary of engine name to instance.
        """
        return {
            "planner": self.planner,
            "knowledge_engine": self.knowledge_engine,
            "memory_engine": self.memory_engine,
            "reasoning_engine": self.reasoning_engine,
            "decision_engine": self.decision_engine,
            "tool_engine": self.tool_engine,
        }


@dataclass
class SessionContext:
    """Context for a cognitive session.

    Maintains all state and data for a single cognitive session,
    including the session ID, correlation ID, and cognitive context.
    """

    session_id: str
    correlation_id: str
    context_id: str = ""
    cycle_id: str = ""
    user_id: str = ""
    hospital_id: str = ""
    session_type: str = "troubleshooting"
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""

    # Current cycle state
    current_stage: str = "initial"
    stages_completed: list[str] = field(default_factory=list)
    engines_executed: list[str] = field(default_factory=list)

    # Data accumulated during cycle
    intent: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, Any] = field(default_factory=dict)
    knowledge_results: list[dict[str, Any]] = field(default_factory=list)
    memory_results: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    decisions: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # Events published during session
    events_published: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize IDs and timestamps."""
        if not self.session_id:
            self.session_id = f"session_{uuid4().hex[:16]}"
        if not self.correlation_id:
            self.correlation_id = f"corr_{uuid4().hex[:16]}"
        if not self.context_id:
            self.context_id = f"ctx_{uuid4().hex[:16]}"
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()

    def start_cycle(self) -> None:
        """Start a new cognitive cycle."""
        self.cycle_id = f"cycle_{uuid4().hex[:16]}"
        self.current_stage = "initial"
        self.started_at = datetime.now(UTC).isoformat()
        self.stages_completed.clear()
        self.engines_executed.clear()
        self.events_published.clear()

    def complete_cycle(self) -> None:
        """Complete the current cognitive cycle."""
        self.cycle_id = ""
        self.current_stage = "completed"

    def set_stage(self, stage: str) -> None:
        """Set the current processing stage.

        Args:
            stage: The new stage name.
        """
        if self.current_stage and self.current_stage != stage:
            self.stages_completed.append(self.current_stage)
        self.current_stage = stage

    def add_engine_executed(self, engine_name: str) -> None:
        """Record an engine execution.

        Args:
            engine_name: Name of the engine.
        """
        if engine_name not in self.engines_executed:
            self.engines_executed.append(engine_name)

    def add_event(self, event_type: str) -> None:
        """Record an event publication.

        Args:
            event_type: Type of event.
        """
        self.events_published.append(event_type)

    def add_error(self, error: str) -> None:
        """Record an error.

        Args:
            error: Error message.
        """
        self.errors.append(error)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Session context as dictionary.
        """
        return {
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "context_id": self.context_id,
            "cycle_id": self.cycle_id,
            "user_id": self.user_id,
            "hospital_id": self.hospital_id,
            "session_type": self.session_type,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "current_stage": self.current_stage,
            "stages_completed": self.stages_completed,
            "engines_executed": self.engines_executed,
            "intent": self.intent,
            "plan": self.plan,
            "knowledge_results_count": len(self.knowledge_results),
            "memory_results_count": len(self.memory_results),
            "evidence_count": len(self.evidence),
            "hypotheses_count": len(self.hypotheses),
            "decisions_count": len(self.decisions),
            "actions_count": len(self.actions),
            "events_published_count": len(self.events_published),
            "errors": self.errors,
        }


@dataclass
class CycleContext:
    """Context for a single cognitive cycle.

    Maintains all data and state for a single execution of the
    cognitive cycle through all engines.
    """

    cycle_id: str
    session_id: str
    correlation_id: str
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0

    # Stage tracking
    current_stage: str = "initial"
    stages: list[dict[str, Any]] = field(default_factory=list)

    # Results
    intent_result: dict[str, Any] = field(default_factory=dict)
    plan_result: dict[str, Any] = field(default_factory=dict)
    knowledge_result: dict[str, Any] = field(default_factory=dict)
    memory_result: dict[str, Any] = field(default_factory=dict)
    reasoning_result: dict[str, Any] = field(default_factory=dict)
    decision_result: dict[str, Any] = field(default_factory=dict)
    action_result: dict[str, Any] = field(default_factory=dict)

    # Status
    success: bool = True
    error: str | None = None

    def __post_init__(self) -> None:
        """Initialize IDs and timestamps."""
        if not self.cycle_id:
            self.cycle_id = f"cycle_{uuid4().hex[:16]}"
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()

    def start(self) -> None:
        """Start the cycle."""
        self.started_at = datetime.now(UTC).isoformat()

    def complete(self, success: bool = True, error: str | None = None) -> None:
        """Complete the cycle.

        Args:
            success: Whether the cycle completed successfully.
            error: Error message if failed.
        """
        self.completed_at = datetime.now(UTC).isoformat()
        if self.started_at:
            started = datetime.fromisoformat(self.started_at)
            completed = datetime.fromisoformat(self.completed_at)
            self.duration_ms = int((completed - started).total_seconds() * 1000)
        self.success = success
        self.error = error

    def add_stage(
        self,
        stage_name: str,
        engine_name: str,
        duration_ms: int,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Add a completed stage.

        Args:
            stage_name: Name of the stage.
            engine_name: Engine that executed the stage.
            duration_ms: Stage duration.
            success: Whether stage succeeded.
            error: Error message if failed.
        """
        self.stages.append({
            "stage_name": stage_name,
            "engine_name": engine_name,
            "duration_ms": duration_ms,
            "success": success,
            "error": error,
            "timestamp": datetime.now(UTC).isoformat(),
        })
        self.current_stage = stage_name

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Cycle context as dictionary.
        """
        return {
            "cycle_id": self.cycle_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "current_stage": self.current_stage,
            "stages_count": len(self.stages),
            "stages": self.stages,
            "intent_result": self.intent_result,
            "plan_result": self.plan_result,
            "knowledge_result": self.knowledge_result,
            "memory_result": self.memory_result,
            "reasoning_result": self.reasoning_result,
            "decision_result": self.decision_result,
            "action_result": self.action_result,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class RuntimeContext:
    """Complete context for the Cognitive Runtime.

    Contains all state and references needed to execute the
    cognitive cycle, including component references and session context.
    """

    runtime_id: str
    configuration: Any = None
    components: ComponentReferences = field(default_factory=ComponentReferences)

    # Current state
    current_session: SessionContext | None = None
    current_cycle: CycleContext | None = None

    # History
    completed_sessions: list[SessionContext] = field(default_factory=list)
    completed_cycles: list[CycleContext] = field(default_factory=list)

    # Timestamps
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""

    def __post_init__(self) -> None:
        """Initialize timestamps."""
        if not self.runtime_id:
            self.runtime_id = f"runtime_{uuid4().hex[:16]}"
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()

    def create_session(
        self,
        user_id: str = "",
        hospital_id: str = "",
        session_type: str = "troubleshooting",
    ) -> SessionContext:
        """Create a new cognitive session.

        Args:
            user_id: User ID.
            hospital_id: Hospital ID.
            session_type: Type of session.

        Returns:
            The new session context.
        """
        correlation_id = f"corr_{uuid4().hex[:16]}"
        session = SessionContext(
            session_id=f"session_{uuid4().hex[:16]}",
            correlation_id=correlation_id,
            user_id=user_id,
            hospital_id=hospital_id,
            session_type=session_type,
        )
        self.current_session = session
        return session

    def create_cycle(self) -> CycleContext:
        """Create a new cognitive cycle.

        Returns:
            The new cycle context.
        """
        if not self.current_session:
            raise ValueError("No active session")

        cycle = CycleContext(
            cycle_id=f"cycle_{uuid4().hex[:16]}",
            session_id=self.current_session.session_id,
            correlation_id=self.current_session.correlation_id,
        )
        self.current_cycle = cycle
        return cycle

    def complete_session(self) -> None:
        """Complete the current session."""
        if self.current_session:
            self.current_session.completed_at = datetime.now(UTC).isoformat()
            self.completed_sessions.append(self.current_session)
            self.current_session = None

    def complete_cycle(self) -> None:
        """Complete the current cycle."""
        if self.current_cycle:
            self.current_cycle.completed_at = datetime.now(UTC).isoformat()
            self.completed_cycles.append(self.current_cycle)
            self.current_cycle = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Runtime context as dictionary.
        """
        return {
            "runtime_id": self.runtime_id,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "has_current_session": self.current_session is not None,
            "has_current_cycle": self.current_cycle is not None,
            "sessions_completed": len(self.completed_sessions),
            "cycles_completed": len(self.completed_cycles),
            "current_session": self.current_session.to_dict() if self.current_session else None,
            "current_cycle": self.current_cycle.to_dict() if self.current_cycle else None,
        }
