"""Runtime state management for the Cognitive Operating System.

Defines the state machine and state types for the Cognitive Runtime.
The runtime progresses through well-defined states during its lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class RuntimeState(str, Enum):
    """States of the Cognitive Runtime.

    The runtime transitions through these states during its lifecycle:
    CREATED -> INITIALIZING -> INITIALIZED -> BOOTING -> BOOTED
    -> VALIDATING -> VALIDATED -> RUNNING -> SHUTTING_DOWN -> STOPPED

    Error states:
    INITIALIZATION_FAILED, BOOT_FAILED, VALIDATION_FAILED, RUNNING_FAILED
    """

    # Initialization States
    CREATED = "created"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"

    # Boot States
    BOOTING = "booting"
    BOOTED = "booted"

    # Validation States
    VALIDATING = "validating"
    VALIDATED = "validated"

    # Runtime States
    RUNNING = "running"
    PAUSED = "paused"

    # Shutdown States
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"

    # Error States
    INITIALIZATION_FAILED = "initialization_failed"
    BOOT_FAILED = "boot_failed"
    VALIDATION_FAILED = "validation_failed"
    RUNNING_FAILED = "running_failed"


class SessionState(str, Enum):
    """States of a Cognitive Session within the Runtime."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    PLANNING = "planning"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    MEMORY_RETRIEVAL = "memory_retrieval"
    REASONING = "reasoning"
    DECISION = "decision"
    ACTION = "action"
    CONTEXT_UPDATE = "context_update"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"


class CognitiveCycleState(str, Enum):
    """States of a Cognitive Cycle within a Session."""

    INITIAL = "initial"
    PLANNING = "planning"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    REASONING = "reasoning"
    DECISION = "decision"
    ACTION = "action"
    CONTEXT_UPDATE = "context_update"
    FINAL = "final"


# Valid state transitions
VALID_RUNTIME_TRANSITIONS: dict[RuntimeState, tuple[RuntimeState, ...]] = {
    RuntimeState.CREATED: (RuntimeState.INITIALIZING,),
    RuntimeState.INITIALIZING: (
        RuntimeState.INITIALIZED,
        RuntimeState.INITIALIZATION_FAILED,
    ),
    RuntimeState.INITIALIZED: (RuntimeState.BOOTING,),
    RuntimeState.BOOTING: (RuntimeState.BOOTED, RuntimeState.BOOT_FAILED),
    RuntimeState.BOOTED: (RuntimeState.VALIDATING,),
    RuntimeState.VALIDATING: (
        RuntimeState.VALIDATED,
        RuntimeState.VALIDATION_FAILED,
    ),
    RuntimeState.VALIDATED: (RuntimeState.RUNNING,),
    RuntimeState.RUNNING: (
        RuntimeState.PAUSED,
        RuntimeState.SHUTTING_DOWN,
        RuntimeState.RUNNING_FAILED,
    ),
    RuntimeState.PAUSED: (RuntimeState.RUNNING, RuntimeState.SHUTTING_DOWN),
    RuntimeState.SHUTTING_DOWN: (RuntimeState.STOPPED,),
    # Error states are terminal
    RuntimeState.INITIALIZATION_FAILED: (RuntimeState.SHUTTING_DOWN,),
    RuntimeState.BOOT_FAILED: (RuntimeState.SHUTTING_DOWN,),
    RuntimeState.VALIDATION_FAILED: (RuntimeState.SHUTTING_DOWN,),
    RuntimeState.RUNNING_FAILED: (RuntimeState.SHUTTING_DOWN,),
    # Terminal state
    RuntimeState.STOPPED: (),
}


VALID_SESSION_TRANSITIONS: dict[SessionState, tuple[SessionState, ...]] = {
    SessionState.CREATED: (SessionState.INITIALIZING,),
    SessionState.INITIALIZING: (SessionState.READY, SessionState.FAILED),
    SessionState.READY: (
        SessionState.PLANNING,
        SessionState.FAILED,
    ),
    SessionState.PLANNING: (
        SessionState.KNOWLEDGE_RETRIEVAL,
        SessionState.MEMORY_RETRIEVAL,
        SessionState.FAILED,
    ),
    SessionState.KNOWLEDGE_RETRIEVAL: (
        SessionState.MEMORY_RETRIEVAL,
        SessionState.REASONING,
        SessionState.FAILED,
    ),
    SessionState.MEMORY_RETRIEVAL: (
        SessionState.KNOWLEDGE_RETRIEVAL,
        SessionState.REASONING,
        SessionState.FAILED,
    ),
    SessionState.REASONING: (
        SessionState.DECISION,
        SessionState.FAILED,
    ),
    SessionState.DECISION: (
        SessionState.ACTION,
        SessionState.FAILED,
    ),
    SessionState.ACTION: (
        SessionState.CONTEXT_UPDATE,
        SessionState.FAILED,
    ),
    SessionState.CONTEXT_UPDATE: (
        SessionState.COMPLETING,
        SessionState.FAILED,
    ),
    SessionState.COMPLETING: (SessionState.COMPLETED, SessionState.FAILED),
    SessionState.COMPLETED: (),
    SessionState.FAILED: (),
}


@dataclass
class RuntimeStateInfo:
    """Information about the current runtime state."""

    state: RuntimeState
    previous_state: RuntimeState | None = None
    started_at: str = ""
    duration_ms: int = 0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.started_at:
            self.started_at = datetime.now(UTC).isoformat()


@dataclass
class SessionStateInfo:
    """Information about the current session state."""

    session_id: str
    state: SessionState
    previous_state: SessionState | None = None
    cycle_count: int = 0
    started_at: str = ""
    duration_ms: int = 0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.started_at:
            self.started_at = datetime.now(UTC).isoformat()


@dataclass
class CycleStateInfo:
    """Information about the current cognitive cycle state."""

    cycle_id: str
    state: CognitiveCycleState
    previous_state: CognitiveCycleState | None = None
    stage_started_at: str = ""
    duration_ms: int = 0
    engines_executed: tuple[str, ...] = field(default_factory=tuple)
    events_published: int = 0

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.stage_started_at:
            self.stage_started_at = datetime.now(UTC).isoformat()


class RuntimeStateMachine:
    """State machine for managing runtime state transitions.

    Ensures that state transitions are valid and records transition history.
    """

    def __init__(self, initial_state: RuntimeState = RuntimeState.CREATED):
        """Initialize the state machine.

        Args:
            initial_state: The initial runtime state.
        """
        self._current_state = initial_state
        self._state_info = RuntimeStateInfo(state=initial_state)
        self._transition_history: list[dict[str, Any]] = []

    @property
    def current_state(self) -> RuntimeState:
        """Get the current state."""
        return self._current_state

    @property
    def state_info(self) -> RuntimeStateInfo:
        """Get the current state information."""
        return self._state_info

    @property
    def transition_history(self) -> list[dict[str, Any]]:
        """Get the transition history."""
        return self._transition_history.copy()

    def can_transition(self, target_state: RuntimeState) -> bool:
        """Check if a transition to the target state is valid.

        Args:
            target_state: The target state.

        Returns:
            True if the transition is valid.
        """
        valid_targets = VALID_RUNTIME_TRANSITIONS.get(self._current_state, ())
        return target_state in valid_targets

    def transition(
        self,
        target_state: RuntimeState,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Attempt to transition to a new state.

        Args:
            target_state: The target state.
            error: Optional error message (for error states).
            metadata: Optional metadata for the transition.

        Returns:
            True if the transition was successful.

        Raises:
            ValueError: If the transition is not valid.
        """
        if not self.can_transition(target_state):
            raise ValueError(
                f"Invalid state transition from {self._current_state.value} "
                f"to {target_state.value}"
            )

        now = datetime.now(UTC)
        duration_ms = 0
        if self._state_info.started_at:
            started = datetime.fromisoformat(self._state_info.started_at)
            duration_ms = int((now - started).total_seconds() * 1000)

        # Record transition
        transition = {
            "from_state": self._current_state.value,
            "to_state": target_state.value,
            "timestamp": now.isoformat(),
            "duration_ms": duration_ms,
            "error": error,
            "metadata": metadata or {},
        }
        self._transition_history.append(transition)

        # Update state
        self._current_state = target_state
        self._state_info = RuntimeStateInfo(
            state=target_state,
            previous_state=self._state_info.state,
            started_at=now.isoformat(),
            duration_ms=duration_ms,
            error=error,
            metadata=metadata or {},
        )

        return True

    def is_terminal(self) -> bool:
        """Check if the current state is terminal.

        Returns:
            True if the state is terminal.
        """
        valid_targets = VALID_RUNTIME_TRANSITIONS.get(self._current_state, ())
        return len(valid_targets) == 0


class SessionStateMachine:
    """State machine for managing session state transitions.

    Tracks the state of a cognitive session as it progresses through
    the cognitive cycle.
    """

    def __init__(self, session_id: str):
        """Initialize the session state machine.

        Args:
            session_id: The session identifier.
        """
        self._session_id = session_id
        self._current_state = SessionState.CREATED
        self._state_info = SessionStateInfo(
            session_id=session_id,
            state=SessionState.CREATED,
        )
        self._transition_history: list[dict[str, Any]] = []

    @property
    def session_id(self) -> str:
        """Get the session ID."""
        return self._session_id

    @property
    def current_state(self) -> SessionState:
        """Get the current state."""
        return self._current_state

    @property
    def state_info(self) -> SessionStateInfo:
        """Get the current state information."""
        return self._state_info

    @property
    def transition_history(self) -> list[dict[str, Any]]:
        """Get the transition history."""
        return self._transition_history.copy()

    def can_transition(self, target_state: SessionState) -> bool:
        """Check if a transition is valid.

        Args:
            target_state: The target state.

        Returns:
            True if the transition is valid.
        """
        valid_targets = VALID_SESSION_TRANSITIONS.get(self._current_state, ())
        return target_state in valid_targets

    def transition(
        self,
        target_state: SessionState,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Attempt to transition to a new state.

        Args:
            target_state: The target state.
            error: Optional error message.
            metadata: Optional metadata.

        Returns:
            True if successful.

        Raises:
            ValueError: If transition is not valid.
        """
        if not self.can_transition(target_state):
            raise ValueError(
                f"Invalid session state transition from {self._current_state.value} "
                f"to {target_state.value}"
            )

        now = datetime.now(UTC)
        duration_ms = 0
        if self._state_info.started_at:
            started = datetime.fromisoformat(self._state_info.started_at)
            duration_ms = int((now - started).total_seconds() * 1000)

        transition = {
            "from_state": self._current_state.value,
            "to_state": target_state.value,
            "timestamp": now.isoformat(),
            "duration_ms": duration_ms,
            "error": error,
            "metadata": metadata or {},
        }
        self._transition_history.append(transition)

        self._current_state = target_state
        self._state_info = SessionStateInfo(
            session_id=self._session_id,
            state=target_state,
            previous_state=self._state_info.state,
            started_at=now.isoformat(),
            duration_ms=duration_ms,
            error=error,
            metadata=metadata or {},
        )

        return True

    def increment_cycle(self) -> None:
        """Increment the cycle count."""
        self._state_info.cycle_count += 1
