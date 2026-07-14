"""Agent lifecycle manager for EREN Cognitive Agent Runtime.

Manages agent lifecycle and state transitions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable

from core.agents.types import (
    AgentManifest,
    AgentStatus,
    AgentTask,
    TaskStatus,
)

if TYPE_CHECKING:
    pass


class LifecycleState:
    """Agent lifecycle states."""
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    PAUSING = "pausing"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LifecycleManager:
    """Manages agent lifecycle.

    The Lifecycle Manager does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Manages lifecycle states
    - Handles state transitions
    - Notifies on state changes
    """

    def __init__(self):
        """Initialize lifecycle manager."""
        self._agent_states: dict[str, LifecycleState] = {}
        self._lifecycle_callbacks: dict[str, dict[str, list]] = {}  # agent_id -> state -> callbacks
        self._lifecycle_history: dict[str, list] = {}  # agent_id -> history

    def initialize(
        self,
        agent_id: str,
        manifest: AgentManifest,
    ) -> LifecycleState:
        """Initialize an agent.

        Args:
            agent_id: Agent ID.
            manifest: Agent manifest.

        Returns:
            New state.
        """
        state = LifecycleState.INITIALIZING
        self._set_state(agent_id, state)
        self._record_transition(agent_id, state, "System initialization")

        # Transition to READY
        self.transition(agent_id, LifecycleState.READY)

        return self._agent_states.get(agent_id, state)

    def start(self, agent_id: str) -> LifecycleState:
        """Start an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            New state.
        """
        current = self._agent_states.get(agent_id)
        if current in [LifecycleState.STOPPED, LifecycleState.ERROR]:
            self.transition(agent_id, LifecycleState.STARTING)

        return self.transition(agent_id, LifecycleState.RUNNING)

    def pause(self, agent_id: str) -> LifecycleState:
        """Pause an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            New state.
        """
        return self.transition(agent_id, LifecycleState.PAUSING)

    def resume(self, agent_id: str) -> LifecycleState:
        """Resume a paused agent.

        Args:
            agent_id: Agent ID.

        Returns:
            New state.
        """
        return self.transition(agent_id, LifecycleState.RUNNING)

    def stop(self, agent_id: str) -> LifecycleState:
        """Stop an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            New state.
        """
        return self.transition(agent_id, LifecycleState.STOPPING)

    def set_error(
        self,
        agent_id: str,
        error: str,
    ) -> LifecycleState:
        """Set agent to error state.

        Args:
            agent_id: Agent ID.
            error: Error message.

        Returns:
            New state.
        """
        self._record_transition(agent_id, LifecycleState.ERROR, error)
        return self.transition(agent_id, LifecycleState.ERROR)

    def get_state(self, agent_id: str) -> LifecycleState | None:
        """Get current state.

        Args:
            agent_id: Agent ID.

        Returns:
            Current state or None.
        """
        return self._agent_states.get(agent_id)

    def is_running(self, agent_id: str) -> bool:
        """Check if agent is running.

        Args:
            agent_id: Agent ID.

        Returns:
            True if running.
        """
        return self._agent_states.get(agent_id) == LifecycleState.RUNNING

    def is_ready(self, agent_id: str) -> bool:
        """Check if agent is ready.

        Args:
            agent_id: Agent ID.

        Returns:
            True if ready.
        """
        return self._agent_states.get(agent_id) == LifecycleState.READY

    def transition(
        self,
        agent_id: str,
        new_state: LifecycleState,
        reason: str = "",
    ) -> LifecycleState:
        """Transition to new state.

        Args:
            agent_id: Agent ID.
            new_state: New state.
            reason: Transition reason.

        Returns:
            New state.
        """
        old_state = self._agent_states.get(agent_id)

        self._set_state(agent_id, new_state)
        self._record_transition(agent_id, new_state, reason)
        self._trigger_callbacks(agent_id, old_state, new_state)

        return new_state

    def _set_state(
        self,
        agent_id: str,
        state: LifecycleState,
    ) -> None:
        """Set agent state."""
        self._agent_states[agent_id] = state

    def _record_transition(
        self,
        agent_id: str,
        state: LifecycleState,
        reason: str,
    ) -> None:
        """Record state transition in history."""
        if agent_id not in self._lifecycle_history:
            self._lifecycle_history[agent_id] = []

        state_value = state if isinstance(state, str) else str(state)
        self._lifecycle_history[agent_id].append({
            "state": state_value,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _trigger_callbacks(
        self,
        agent_id: str,
        old_state: LifecycleState | None,
        new_state: LifecycleState,
    ) -> None:
        """Trigger callbacks for state change."""
        if agent_id not in self._lifecycle_callbacks:
            return

        callbacks = self._lifecycle_callbacks[agent_id].get(new_state.value, [])
        callbacks.extend(
            self._lifecycle_callbacks[agent_id].get("any", [])
        )

        for callback in callbacks:
            try:
                callback(agent_id, old_state, new_state)
            except Exception:
                pass

    def register_callback(
        self,
        agent_id: str,
        state: str,  # "any" or specific state
        callback: Callable,
    ) -> None:
        """Register a lifecycle callback.

        Args:
            agent_id: Agent ID.
            state: State to trigger on.
            callback: Callback function.
        """
        if agent_id not in self._lifecycle_callbacks:
            self._lifecycle_callbacks[agent_id] = {}

        if state not in self._lifecycle_callbacks[agent_id]:
            self._lifecycle_callbacks[agent_id][state] = []

        self._lifecycle_callbacks[agent_id][state].append(callback)

    def get_history(
        self,
        agent_id: str,
        limit: int = 50,
    ) -> list:
        """Get lifecycle history.

        Args:
            agent_id: Agent ID.
            limit: Maximum entries.

        Returns:
            List of history entries.
        """
        return self._lifecycle_history.get(agent_id, [])[-limit:]


# Global lifecycle manager
_global_lifecycle_manager: LifecycleManager | None = None
_lifecycle_lock = __import__("threading").Lock()


def get_lifecycle_manager() -> LifecycleManager:
    """Get the global lifecycle manager.

    Returns:
        Global LifecycleManager instance.
    """
    global _global_lifecycle_manager
    with _lifecycle_lock:
        if _global_lifecycle_manager is None:
            _global_lifecycle_manager = LifecycleManager()
        return _global_lifecycle_manager


def reset_lifecycle_manager() -> None:
    """Reset the global lifecycle manager."""
    global _global_lifecycle_manager
    with _lifecycle_lock:
        _global_lifecycle_manager = None
