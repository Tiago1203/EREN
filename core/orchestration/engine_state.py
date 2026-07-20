"""Engine state management for orchestration.

Manages state transitions for cognitive engines.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Engine States
# =============================================================================


class EngineState(str, Enum):
    """States of a cognitive engine."""

    # Lifecycle states
    INITIALIZED = "initialized"  # Engine initialized
    REGISTERED = "registered"  # Engine registered

    # Execution states
    IDLE = "idle"  # Not executing
    PREPARING = "preparing"  # In prepare() phase
    EXECUTING = "executing"  # In execute() phase
    CLEANING_UP = "cleaning_up"  # In cleanup() phase

    # Completion states
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed
    CANCELLED = "cancelled"  # Cancelled


# =============================================================================
# State Transition
# =============================================================================


@dataclass(frozen=True)
class StateTransition:
    """A state transition event."""

    transition_id: str
    engine_id: str
    from_state: EngineState
    to_state: EngineState
    reason: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(UTC).isoformat())


# =============================================================================
# Engine State Manager
# =============================================================================


class EngineStateManager:
    """Manages state for cognitive engines.

    Provides a centralized way to track engine states
    and validate transitions.
    """

    # Valid state transitions
    VALID_TRANSITIONS: dict[EngineState, tuple[EngineState, ...]] = {
        EngineState.INITIALIZED: (
            EngineState.REGISTERED,
            EngineState.IDLE,
        ),
        EngineState.REGISTERED: (
            EngineState.IDLE,
        ),
        EngineState.IDLE: (
            EngineState.PREPARING,
            EngineState.FAILED,
        ),
        EngineState.PREPARING: (
            EngineState.EXECUTING,
            EngineState.IDLE,
            EngineState.FAILED,
        ),
        EngineState.EXECUTING: (
            EngineState.CLEANING_UP,
            EngineState.FAILED,
        ),
        EngineState.CLEANING_UP: (
            EngineState.IDLE,
            EngineState.COMPLETED,
            EngineState.FAILED,
        ),
        EngineState.COMPLETED: (
            EngineState.IDLE,
        ),
        EngineState.FAILED: (
            EngineState.IDLE,
        ),
        EngineState.CANCELLED: (
            EngineState.IDLE,
        ),
    }

    def __init__(self) -> None:
        """Initialize the state manager."""
        self._states: dict[str, EngineState] = {}
        self._history: dict[str, list[StateTransition]] = {}

    def initialize(self, engine_id: str) -> None:
        """Initialize engine state.

        Args:
            engine_id: The engine ID.
        """
        self._states[engine_id] = EngineState.INITIALIZED
        self._history[engine_id] = []

    def register(self, engine_id: str) -> bool:
        """Register an engine.

        Args:
            engine_id: The engine ID.

        Returns:
            True if transition is valid.
        """
        return self._transition(engine_id, EngineState.REGISTERED)

    def transition(
        self,
        engine_id: str,
        to_state: EngineState,
        reason: str = "",
    ) -> bool:
        """Transition engine to a new state.

        Args:
            engine_id: The engine ID.
            to_state: Target state.
            reason: Transition reason.

        Returns:
            True if transition is valid.
        """
        return self._transition(engine_id, to_state, reason)

    def _transition(
        self,
        engine_id: str,
        to_state: EngineState,
        reason: str = "",
    ) -> bool:
        """Internal transition method.

        Args:
            engine_id: The engine ID.
            to_state: Target state.
            reason: Transition reason.

        Returns:
            True if transition is valid.
        """
        if engine_id not in self._states:
            self._states[engine_id] = EngineState.INITIALIZED

        from_state = self._states[engine_id]

        # Validate transition
        valid_next = self.VALID_TRANSITIONS.get(from_state, ())
        if to_state not in valid_next:
            return False

        # Record transition
        transition = StateTransition(
            transition_id=f"t_{len(self._history.get(engine_id, []))}",
            engine_id=engine_id,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
        )

        self._history.setdefault(engine_id, []).append(transition)
        self._states[engine_id] = to_state

        return True

    def get_state(self, engine_id: str) -> EngineState:
        """Get current engine state.

        Args:
            engine_id: The engine ID.

        Returns:
            Current engine state.
        """
        return self._states.get(engine_id, EngineState.INITIALIZED)

    def get_history(self, engine_id: str) -> list[StateTransition]:
        """Get state transition history.

        Args:
            engine_id: The engine ID.

        Returns:
            List of state transitions.
        """
        return list(self._history.get(engine_id, []))

    def is_executing(self, engine_id: str) -> bool:
        """Check if engine is currently executing.

        Args:
            engine_id: The engine ID.

        Returns:
            True if engine is executing.
        """
        return self.get_state(engine_id) == EngineState.EXECUTING

    def is_idle(self, engine_id: str) -> bool:
        """Check if engine is idle.

        Args:
            engine_id: The engine ID.

        Returns:
            True if engine is idle.
        """
        return self.get_state(engine_id) == EngineState.IDLE


# =============================================================================
# Global State Manager
# =============================================================================


_global_state_manager: EngineStateManager | None = None


def get_state_manager() -> EngineStateManager:
    """Get the global state manager.

    Returns:
        The global state manager.
    """
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = EngineStateManager()
    return _global_state_manager
