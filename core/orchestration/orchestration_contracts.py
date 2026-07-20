"""Orchestration contracts for EREN's cognitive engines.

Defines the common interface all cognitive engines must implement.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .engine_result import EngineResult
    from .orchestration_context import OrchestrationContext


# =============================================================================
# Engine Contracts
# =============================================================================


class CognitiveEngine(Protocol):
    """Protocol for all cognitive engines.

    All engines in EREN must implement this contract.
    This ensures all engines can be orchestrated uniformly.
    """

    engine_id: str
    engine_type: str
    engine_version: str

    async def prepare(self, context: OrchestrationContext) -> None:
        """Prepare the engine for execution.

        Called once before execution to set up resources.

        Args:
            context: The orchestration context.
        """
        ...

    async def execute(self, context: OrchestrationContext) -> EngineResult:
        """Execute the engine's cognitive operation.

        Args:
            context: The orchestration context.

        Returns:
            The engine's result.
        """
        ...

    def publish_events(self) -> list[Any]:
        """Publish any pending events.

        Returns:
            List of events to publish.
        """
        ...

    async def cleanup(self) -> None:
        """Clean up resources after execution.

        Called after execution completes (success or failure).
        """
        ...


class Plannable(Protocol):
    """Protocol for engines that can be planned."""

    def plan(self, context: OrchestrationContext) -> list[str]:
        """Generate execution plan.

        Args:
            context: The orchestration context.

        Returns:
            List of planned actions.
        """
        ...


class Stateful(Protocol):
    """Protocol for engines with state."""

    def get_state(self) -> dict[str, Any]:
        """Get current engine state.

        Returns:
            Engine state as dictionary.
        """
        ...

    def set_state(self, state: dict[str, Any]) -> None:
        """Restore engine state.

        Args:
            state: State to restore.
        """
        ...


# =============================================================================
# Engine Types
# =============================================================================


class EngineType(str):
    """Types of cognitive engines."""

    PLANNER = "planner"
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    REASONING = "reasoning"
    DECISION = "decision"
    TOOL = "tool"
    WORKFLOW = "workflow"
    VOICE = "voice"
    CONTEXT = "context"
    ORCHESTRATOR = "orchestrator"


# =============================================================================
# Contract Violation Exception
# =============================================================================


class ContractViolationError(Exception):
    """Raised when an engine violates its contract."""

    def __init__(self, engine_id: str, method: str, reason: str) -> None:
        super().__init__(
            f"Engine '{engine_id}' violated contract in method '{method}': {reason}"
        )
        self.engine_id = engine_id
        self.method = method
        self.reason = reason


# =============================================================================
# Engine Registration Contract
# =============================================================================


class EngineRegistry(Protocol):
    """Protocol for engine registration."""

    def register(self, engine: CognitiveEngine) -> None:
        """Register an engine.

        Args:
            engine: The engine to register.
        """
        ...

    def unregister(self, engine_id: str) -> bool:
        """Unregister an engine.

        Args:
            engine_id: The engine ID to unregister.

        Returns:
            True if unregistered.
        """
        ...

    def get(self, engine_id: str) -> CognitiveEngine | None:
        """Get an engine by ID.

        Args:
            engine_id: The engine ID.

        Returns:
            The engine or None.
        """
        ...

    def list_by_type(self, engine_type: str) -> list[CognitiveEngine]:
        """List engines by type.

        Args:
            engine_type: The engine type.

        Returns:
            List of engines.
        """
        ...
