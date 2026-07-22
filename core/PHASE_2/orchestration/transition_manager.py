"""Transition manager for cognitive cycle orchestration.

Manages phase transitions and validates them.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cognitive_cycle import PhaseTransition


# =============================================================================
# Transition Handler
# =============================================================================


@dataclass
class TransitionHandler:
    """Handler for phase transitions."""

    from_phase: str
    to_phase: str
    callback: Callable
    condition: Callable | None = None
    timeout_ms: int = 30000

    def can_execute(self, context: Any) -> bool:
        """Check if handler should execute.

        Args:
            context: The orchestration context.

        Returns:
            True if handler should execute.
        """
        if self.condition is None:
            return True
        return self.condition(context)


# =============================================================================
# Transition Manager
# =============================================================================


class TransitionManager:
    """Manages phase transitions in a cognitive cycle.

    Validates transitions and executes handlers.
    """

    def __init__(self) -> None:
        """Initialize the transition manager."""
        self._handlers: dict[str, list[TransitionHandler]] = {}
        self._transition_history: list[PhaseTransition] = []

    def register_handler(
        self,
        from_phase: str,
        to_phase: str,
        handler: Callable,
        condition: Callable | None = None,
        timeout_ms: int = 30000,
    ) -> None:
        """Register a transition handler.

        Args:
            from_phase: Source phase.
            to_phase: Target phase.
            handler: Handler callback.
            condition: Optional condition.
            timeout_ms: Handler timeout.
        """
        key = f"{from_phase}->{to_phase}"
        transition_handler = TransitionHandler(
            from_phase=from_phase,
            to_phase=to_phase,
            callback=handler,
            condition=condition,
            timeout_ms=timeout_ms,
        )
        self._handlers.setdefault(key, []).append(transition_handler)

    def execute_transition(
        self,
        from_phase: str,
        to_phase: str,
        context: Any,
    ) -> tuple[bool, list[Any]]:
        """Execute a phase transition.

        Args:
            from_phase: Source phase.
            to_phase: Target phase.
            context: The orchestration context.

        Returns:
            Tuple of (success, handler results).
        """
        key = f"{from_phase}->{to_phase}"
        handlers = self._handlers.get(key, [])

        results = []
        all_success = True

        for handler in handlers:
            if handler.can_execute(context):
                try:
                    result = handler.callback(context)
                    results.append(result)
                except Exception as e:
                    results.append(e)
                    all_success = False

        # Record transition
        self._transition_history.append(PhaseTransition(
            transition_id=f"tr_{len(self._transition_history)}",
            from_phase=from_phase,
            to_phase=to_phase,
            engine_executed="transition_manager",
            success=all_success,
            error=str(results) if not all_success else "",
        ))

        return all_success, results

    def get_handlers(
        self,
        from_phase: str,
        to_phase: str,
    ) -> list[TransitionHandler]:
        """Get handlers for a transition.

        Args:
            from_phase: Source phase.
            to_phase: Target phase.

        Returns:
            List of handlers.
        """
        key = f"{from_phase}->{to_phase}"
        return list(self._handlers.get(key, []))

    def get_transition_history(self) -> list:
        """Get transition history.

        Returns:
            List of transitions.
        """
        return list(self._transition_history)


# =============================================================================
# Global Transition Manager
# =============================================================================


_global_transition_manager: TransitionManager | None = None


def get_transition_manager() -> TransitionManager:
    """Get the global transition manager.

    Returns:
        The global transition manager.
    """
    global _global_transition_manager
    if _global_transition_manager is None:
        _global_transition_manager = TransitionManager()
    return _global_transition_manager
