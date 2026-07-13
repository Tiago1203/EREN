"""Cognitive cycle definition for EREN.

Defines the complete cognitive processing cycle.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Cycle States
# =============================================================================


class CycleState(str, Enum):
    """States in the cognitive cycle."""

    # Lifecycle states
    CREATED = "created"  # Cycle created
    READY = "ready"  # Ready to start

    # Execution states
    PLANNING = "planning"  # Planner engine active
    KNOWLEDGE = "knowledge"  # Knowledge engine active
    MEMORY = "memory"  # Memory engine active
    REASONING = "reasoning"  # Reasoning engine active
    DECISION = "decision"  # Decision engine active
    ACTION = "action"  # Action/execution active

    # Completion states
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed
    CANCELLED = "cancelled"  # Cancelled


# =============================================================================
# Cycle Phases
# =============================================================================


class CyclePhase(str, Enum):
    """Phases in the cognitive cycle."""

    # Intake phase
    INTAKE = "intake"  # Receive and validate input

    # Planning phase
    PLANNING = "planning"  # Plan next steps

    # Processing phases
    KNOWLEDGE = "knowledge"  # Query knowledge base
    MEMORY = "memory"  # Query memory
    REASONING = "reasoning"  # Reason about context
    DECISION = "decision"  # Make decisions

    # Execution phase
    ACTION = "action"  # Execute decisions

    # Output phase
    OUTPUT = "output"  # Generate response


# =============================================================================
# Cycle Data
# =============================================================================


@dataclass(frozen=True)
class CycleMetadata:
    """Metadata for a cognitive cycle."""

    cycle_id: str
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0
    triggered_by: str = ""  # What triggered the cycle
    user_id: str = ""
    session_id: str = ""

    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class PhaseTransition:
    """A transition between phases."""

    transition_id: str
    from_phase: CyclePhase
    to_phase: CyclePhase
    engine_executed: str
    success: bool
    duration_ms: int = 0
    error: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class PhaseResult:
    """Result from a phase execution."""

    phase: CyclePhase
    success: bool
    data: dict = field(default_factory=dict)
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    execution_time_ms: int = 0


# =============================================================================
# Cognitive Cycle
# =============================================================================


@dataclass
class CognitiveCycle:
    """A complete cognitive processing cycle.

    Represents the full lifecycle of processing a request
    through all cognitive engines.
    """

    metadata: CycleMetadata
    current_state: CycleState = CycleState.CREATED
    current_phase: CyclePhase = CyclePhase.INTAKE
    phase_history: tuple[PhaseResult, ...] = field(default_factory=tuple)
    transitions: tuple[PhaseTransition, ...] = field(default_factory=tuple)
    engine_results: dict[str, Any] = field(default_factory=dict)
    context_updates: dict[str, Any] = field(default_factory=dict)
    events_published: tuple[str, ...] = field(default_factory=tuple)

    def transition_to(self, state: CycleState, phase: CyclePhase) -> None:
        """Transition to a new state and phase.

        Args:
            state: New cycle state.
            phase: New cycle phase.
        """
        self.current_state = state
        self.current_phase = phase

    def add_phase_result(self, result: PhaseResult) -> None:
        """Add a phase result.

        Args:
            result: The phase result.
        """
        self.phase_history = self.phase_history + (result,)

    def add_engine_result(self, engine_id: str, result: Any) -> None:
        """Add an engine result.

        Args:
            engine_id: The engine ID.
            result: The engine result.
        """
        self.engine_results[engine_id] = result

    def add_transition(self, transition: PhaseTransition) -> None:
        """Add a phase transition.

        Args:
            transition: The transition.
        """
        self.transitions = self.transitions + (transition,)


# =============================================================================
# Cycle Configuration
# =============================================================================


@dataclass(frozen=True)
class CycleConfiguration:
    """Configuration for cognitive cycle execution."""

    # Phase settings
    phases_enabled: tuple[CyclePhase, ...] = (
        CyclePhase.INTAKE,
        CyclePhase.PLANNING,
        CyclePhase.KNOWLEDGE,
        CyclePhase.MEMORY,
        CyclePhase.REASONING,
        CyclePhase.DECISION,
        CyclePhase.ACTION,
        CyclePhase.OUTPUT,
    )
    phases_required: tuple[CyclePhase, ...] = (
        CyclePhase.INTAKE,
        CyclePhase.REASONING,
        CyclePhase.DECISION,
    )

    # Timeout settings (ms)
    phase_timeout_ms: int = 30000
    cycle_timeout_ms: int = 300000  # 5 minutes

    # Retry settings
    max_retries: int = 3
    retry_delay_ms: int = 1000

    # Feature flags
    enable_knowledge: bool = True
    enable_memory: bool = True
    enable_parallel: bool = False


# =============================================================================
# Default Cycle Configuration
# =============================================================================


DEFAULT_CYCLE_CONFIG = CycleConfiguration()


# =============================================================================
# Phase Dependencies
# =============================================================================


PHASE_DEPENDENCIES: dict[CyclePhase, tuple[CyclePhase, ...]] = {
    CyclePhase.PLANNING: (CyclePhase.INTAKE,),
    CyclePhase.KNOWLEDGE: (CyclePhase.PLANNING,),
    CyclePhase.MEMORY: (CyclePhase.PLANNING,),
    CyclePhase.REASONING: (CyclePhase.KNOWLEDGE, CyclePhase.MEMORY),
    CyclePhase.DECISION: (CyclePhase.REASONING,),
    CyclePhase.ACTION: (CyclePhase.DECISION,),
    CyclePhase.OUTPUT: (CyclePhase.ACTION,),
}


# =============================================================================
# Phase to Engine Mapping
# =============================================================================


PHASE_ENGINE_MAP: dict[CyclePhase, str] = {
    CyclePhase.INTAKE: "orchestrator",
    CyclePhase.PLANNING: "planner",
    CyclePhase.KNOWLEDGE: "knowledge",
    CyclePhase.MEMORY: "memory",
    CyclePhase.REASONING: "reasoning",
    CyclePhase.DECISION: "decision",
    CyclePhase.ACTION: "tool",
    CyclePhase.OUTPUT: "voice",
}
