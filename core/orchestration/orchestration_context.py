"""Orchestration context for cognitive engines.

Provides shared context for all engines during a cycle.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Context Keys
# =============================================================================


class ContextKey(str):
    """Well-known context keys."""

    # User/Session
    USER_ID = "user_id"
    SESSION_ID = "session_id"
    REQUEST_ID = "request_id"

    # Input
    USER_INPUT = "user_input"
    INTENT = "intent"
    DEVICE_INFO = "device_info"

    # Cognitive data
    HYPOTHESES = "hypotheses"
    EVIDENCE = "evidence"
    DECISIONS = "decisions"
    KNOWLEDGE_RESULTS = "knowledge_results"
    MEMORY_RESULTS = "memory_results"

    # Actions
    PLANNED_ACTIONS = "planned_actions"
    SELECTED_ACTION = "selected_action"
    ACTION_RESULTS = "action_results"

    # Output
    RESPONSE = "response"
    RESPONSE_TYPE = "response_type"

    # Meta
    CYCLE_ID = "cycle_id"
    ENGINE_RESULTS = "engine_results"


# =============================================================================
# Orchestration Context
# =============================================================================


@dataclass
class OrchestrationContext:
    """Shared context for orchestration.

    All engines read from and write to this context
    during a cognitive cycle.
    """

    # Session info
    user_id: str = ""
    session_id: str = ""
    request_id: str = ""

    # User input
    user_input: str = ""
    intent: str = ""

    # Device information
    device_type: str = ""
    device_model: str = ""
    device_manufacturer: str = ""

    # Cognitive data
    hypotheses: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    decisions: list = field(default_factory=list)
    knowledge_results: list = field(default_factory=list)
    memory_results: list = field(default_factory=list)

    # Actions
    planned_actions: list = field(default_factory=list)
    selected_action: dict = field(default_factory=dict)
    action_results: list = field(default_factory=list)

    # Response
    response: str = ""
    response_type: str = "text"

    # Meta
    cycle_id: str = ""
    metadata: dict = field(default_factory=dict)

    # Engine results
    _engine_results: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set IDs if not provided."""
        if not self.request_id:
            import uuid
            self.request_id = f"req_{uuid.uuid4().hex[:16]}"
        if not self.cycle_id:
            import uuid
            self.cycle_id = f"cycle_{uuid.uuid4().hex[:16]}"

    # =========================================================================
    # Get Methods
    # =========================================================================

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: The context key.
            default: Default value.

        Returns:
            The value or default.
        """
        return getattr(self, key, default)

    def get_hypotheses(self) -> list:
        """Get current hypotheses."""
        return list(self.hypotheses)

    def get_evidence(self) -> list:
        """Get current evidence."""
        return list(self.evidence)

    def get_decisions(self) -> list:
        """Get current decisions."""
        return list(self.decisions)

    def get_engine_result(self, engine_id: str) -> Any:
        """Get result from a specific engine.

        Args:
            engine_id: The engine ID.

        Returns:
            The engine result or None.
        """
        return self._engine_results.get(engine_id)

    # =========================================================================
    # Set Methods
    # =========================================================================

    def set(self, key: str, value: Any) -> None:
        """Set a context value.

        Args:
            key: The context key.
            value: The value.
        """
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.metadata[key] = value

    def add_hypothesis(self, hypothesis: Any) -> None:
        """Add a hypothesis.

        Args:
            hypothesis: The hypothesis to add.
        """
        self.hypotheses.append(hypothesis)

    def add_evidence(self, evidence: Any) -> None:
        """Add evidence.

        Args:
            evidence: The evidence to add.
        """
        self.evidence.append(evidence)

    def add_decision(self, decision: Any) -> None:
        """Add a decision.

        Args:
            decision: The decision to add.
        """
        self.decisions.append(decision)

    def add_knowledge_result(self, result: Any) -> None:
        """Add a knowledge result.

        Args:
            result: The knowledge result.
        """
        self.knowledge_results.append(result)

    def add_memory_result(self, result: Any) -> None:
        """Add a memory result.

        Args:
            result: The memory result.
        """
        self.memory_results.append(result)

    def set_engine_result(self, engine_id: str, result: Any) -> None:
        """Set result from an engine.

        Args:
            engine_id: The engine ID.
            result: The engine result.
        """
        self._engine_results[engine_id] = result

    def set_response(self, response: str, response_type: str = "text") -> None:
        """Set the response.

        Args:
            response: The response text.
            response_type: The response type.
        """
        self.response = response
        self.response_type = response_type

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_dict(self) -> dict:
        """Convert context to dictionary.

        Returns:
            Context as dictionary.
        """
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "user_input": self.user_input,
            "intent": self.intent,
            "device_type": self.device_type,
            "device_model": self.device_model,
            "device_manufacturer": self.device_manufacturer,
            "hypotheses": self.hypotheses,
            "evidence": self.evidence,
            "decisions": self.decisions,
            "knowledge_results": self.knowledge_results,
            "memory_results": self.memory_results,
            "planned_actions": self.planned_actions,
            "selected_action": self.selected_action,
            "action_results": self.action_results,
            "response": self.response,
            "response_type": self.response_type,
            "cycle_id": self.cycle_id,
            "metadata": self.metadata,
        }

    def copy(self) -> OrchestrationContext:
        """Create a copy of the context.

        Returns:
            Copy of the context.
        """
        ctx = OrchestrationContext(
            user_id=self.user_id,
            session_id=self.session_id,
            request_id=self.request_id,
            user_input=self.user_input,
            intent=self.intent,
            device_type=self.device_type,
            device_model=self.device_model,
            device_manufacturer=self.device_manufacturer,
            hypotheses=list(self.hypotheses),
            evidence=list(self.evidence),
            decisions=list(self.decisions),
            knowledge_results=list(self.knowledge_results),
            memory_results=list(self.memory_results),
            planned_actions=list(self.planned_actions),
            selected_action=dict(self.selected_action),
            action_results=list(self.action_results),
            response=self.response,
            response_type=self.response_type,
            cycle_id=self.cycle_id,
            metadata=dict(self.metadata),
        )
        ctx._engine_results = dict(self._engine_results)
        return ctx


# =============================================================================
# Context Factory
# =============================================================================


class ContextFactory:
    """Factory for creating orchestration contexts."""

    @staticmethod
    def create_from_user_input(
        user_input: str,
        user_id: str = "",
        session_id: str = "",
    ) -> OrchestrationContext:
        """Create context from user input.

        Args:
            user_input: The user's input.
            user_id: User ID.
            session_id: Session ID.

        Returns:
            New orchestration context.
        """
        return OrchestrationContext(
            user_input=user_input,
            user_id=user_id,
            session_id=session_id,
        )

    @staticmethod
    def create_for_device(
        device_type: str,
        device_model: str,
        device_manufacturer: str = "",
    ) -> OrchestrationContext:
        """Create context for device operation.

        Args:
            device_type: Type of device.
            device_model: Device model.
            device_manufacturer: Device manufacturer.

        Returns:
            New orchestration context.
        """
        return OrchestrationContext(
            device_type=device_type,
            device_model=device_model,
            device_manufacturer=device_manufacturer,
        )
