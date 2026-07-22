"""Exceptions for the Cognitive Reasoning Engine.

Architecture only — no business logic.
"""

from __future__ import annotations


class ReasoningError(Exception):
    """Base class for reasoning errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class SessionNotFoundError(ReasoningError):
    """Raised when a reasoning session is not found."""

    def __init__(self, session_id: str = "") -> None:
        super().__init__(f"Reasoning session '{session_id}' not found")
        self.session_id = session_id


class SessionAlreadyActiveError(ReasoningError):
    """Raised when trying to start a session while one is active."""

    def __init__(self, session_id: str = "") -> None:
        super().__init__(f"Session '{session_id}' is already active")
        self.session_id = session_id


class HypothesisNotFoundError(ReasoningError):
    """Raised when a hypothesis is not found."""

    def __init__(self, hypothesis_id: str = "") -> None:
        super().__init__(f"Hypothesis '{hypothesis_id}' not found")
        self.hypothesis_id = hypothesis_id


class EvidenceNotFoundError(ReasoningError):
    """Raised when evidence is not found."""

    def __init__(self, evidence_id: str = "") -> None:
        super().__init__(f"Evidence '{evidence_id}' not found")
        self.evidence_id = evidence_id


class DecisionNotFoundError(ReasoningError):
    """Raised when a decision is not found."""

    def __init__(self, decision_id: str = "") -> None:
        super().__init__(f"Decision '{decision_id}' not found")
        self.decision_id = decision_id


class ChainNotFoundError(ReasoningError):
    """Raised when a reasoning chain is not found."""

    def __init__(self, chain_id: str = "") -> None:
        super().__init__(f"Reasoning chain '{chain_id}' not found")
        self.chain_id = chain_id


class InvalidConfidenceError(ReasoningError):
    """Raised when a confidence value is invalid."""

    def __init__(self, value: float = 0.0) -> None:
        super().__init__(f"Invalid confidence value: {value}. Must be between 0.0 and 1.0")
        self.value = value


class HypothesisLimitExceededError(ReasoningError):
    """Raised when hypothesis limit is exceeded."""

    def __init__(self, limit: int = 0) -> None:
        super().__init__(f"Hypothesis limit exceeded: {limit}")
        self.limit = limit


class ChainValidationError(ReasoningError):
    """Raised when a reasoning chain is invalid."""

    def __init__(
        self,
        chain_id: str = "",
        errors: list[str] | None = None,
    ) -> None:
        errors_str = "; ".join(errors or [])
        super().__init__(f"Chain '{chain_id}' validation failed: {errors_str}")
        self.chain_id = chain_id
        self.errors = errors or []


class StrategyNotSupportedError(ReasoningError):
    """Raised when a reasoning strategy is not supported."""

    def __init__(self, strategy: str = "") -> None:
        super().__init__(f"Reasoning strategy not supported: {strategy}")
        self.strategy = strategy


class InsufficientEvidenceError(ReasoningError):
    """Raised when there is insufficient evidence."""

    def __init__(self, required: int = 0, available: int = 0) -> None:
        super().__init__(
            f"Insufficient evidence: required {required}, available {available}"
        )
        self.required = required
        self.available = available


class ReasoningStageError(ReasoningError):
    """Raised when an operation is invalid for the current stage."""

    def __init__(
        self,
        current_stage: str = "",
        required_stage: str = "",
    ) -> None:
        super().__init__(
            f"Invalid stage: current is '{current_stage}', required is '{required_stage}'"
        )
        self.current_stage = current_stage
        self.required_stage = required_stage
