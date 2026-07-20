"""Exceptions for the Cognitive Orchestrator."""

from __future__ import annotations


class OrchestrationError(Exception):
    """Base exception for orchestration errors."""

    def __init__(self, message: str = "", **kwargs) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class SessionNotFoundError(OrchestrationError):
    """Raised when a session is not found."""

    def __init__(self, session_id: str = "") -> None:
        super().__init__(f"Session '{session_id}' not found")
        self.session_id = session_id


class InvalidStateTransitionError(OrchestrationError):
    """Raised when a state transition is invalid."""

    def __init__(
        self,
        from_state: str = "",
        to_state: str = "",
    ) -> None:
        super().__init__(
            f"Invalid state transition from '{from_state}' to '{to_state}'"
        )
        self.from_state = from_state
        self.to_state = to_state


class SessionTimeoutError(OrchestrationError):
    """Raised when a session times out."""

    def __init__(self, session_id: str = "", duration_ms: int = 0) -> None:
        super().__init__(
            f"Session '{session_id}' timed out after {duration_ms}ms"
        )
        self.session_id = session_id
        self.duration_ms = duration_ms


class SessionCancelledError(OrchestrationError):
    """Raised when a session is cancelled."""

    def __init__(self, session_id: str = "", reason: str = "") -> None:
        super().__init__(
            f"Session '{session_id}' cancelled: {reason}"
        )
        self.session_id = session_id
        self.reason = reason


class PolicyViolationError(OrchestrationError):
    """Raised when an orchestration policy is violated."""

    def __init__(self, policy_name: str = "", reason: str = "") -> None:
        super().__init__(
            f"Policy '{policy_name}' violated: {reason}"
        )
        self.policy_name = policy_name
        self.reason = reason


class TraceError(OrchestrationError):
    """Raised when trace operations fail."""

    def __init__(self, reason: str = "") -> None:
        super().__init__(f"Trace error: {reason}")
        self.reason = reason
