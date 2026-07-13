"""State machine for the Cognitive Lifecycle Manager."""

from datetime import datetime, timezone
from typing import Optional


class LifecycleStateMachine:
    """State machine for lifecycle management.

    Validates and executes state transitions.
    """

    def __init__(self, initial_state: str = "created"):
        self._current_state = initial_state
        self._history = []
        self._transitions_count = 0

    @property
    def current_state(self) -> str:
        """Get current state."""
        return self._current_state

    @property
    def history(self) -> list:
        """Get transition history."""
        return self._history.copy()

    @property
    def transitions_count(self) -> int:
        """Get transition count."""
        return self._transitions_count

    def can_transition(self, event: str, valid_transitions: dict) -> bool:
        """Check if transition is valid.

        Args:
            event: Event to check.
            valid_transitions: Valid transitions map.

        Returns:
            True if transition is valid.
        """
        state_transitions = valid_transitions.get(self._current_state, {})
        return event in state_transitions

    def transition(
        self,
        event: str,
        valid_transitions: dict,
        reason: str = "",
        metadata: dict = None,
    ) -> tuple[bool, Optional[str], Optional[dict]]:
        """Execute a state transition.

        Args:
            event: Event to process.
            valid_transitions: Valid transitions map.
            reason: Reason for transition.
            metadata: Additional metadata.

        Returns:
            Tuple of (success, new_state, transition_data).
        """
        if self._current_state in {"completed", "archived"}:
            return False, None, {"error": "Terminal state reached"}

        state_transitions = valid_transitions.get(self._current_state, {})

        if event not in state_transitions:
            return False, None, {
                "error": "Invalid transition",
                "current_state": self._current_state,
                "event": event,
                "valid_events": list(state_transitions.keys()),
            }

        old_state = self._current_state
        new_state = state_transitions[event]

        transition_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from_state": old_state,
            "to_state": new_state,
            "event": event,
            "reason": reason,
            "metadata": metadata or {},
        }

        self._history.append(transition_data)
        self._current_state = new_state
        self._transitions_count += 1

        return True, new_state, transition_data

    def get_valid_events(self, valid_transitions: dict) -> list:
        """Get valid events for current state.

        Args:
            valid_transitions: Valid transitions map.

        Returns:
            List of valid events.
        """
        return list(valid_transitions.get(self._current_state, {}).keys())

    def is_terminal(self) -> bool:
        """Check if in terminal state."""
        return self._current_state in {"completed", "archived"}
