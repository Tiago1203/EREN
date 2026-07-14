"""Execution exceptions for EREN OS Cognitive Execution Coordinator.

Defines all exceptions that can be raised during execution operations.
"""

from __future__ import annotations


class ExecutionException(Exception):
    """Base exception for all execution errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ExecutionInitializationError(ExecutionException):
    """Raised when execution fails to initialize."""
    pass


class SessionCreationError(ExecutionException):
    """Raised when session creation fails."""

    def __init__(self, message: str, session_id: str = ""):
        super().__init__(message, {"session_id": session_id})
        self.session_id = session_id


class SessionCompletionError(ExecutionException):
    """Raised when session completion fails."""

    def __init__(self, message: str, session_id: str = ""):
        super().__init__(message, {"session_id": session_id})
        self.session_id = session_id


class SessionNotFoundError(ExecutionException):
    """Raised when session is not found."""

    def __init__(self, session_id: str):
        super().__init__(f"Session not found: {session_id}", {"session_id": session_id})
        self.session_id = session_id


class RoutingError(ExecutionException):
    """Raised when routing fails."""

    def __init__(self, message: str, intent_type: str = ""):
        super().__init__(message, {"intent_type": intent_type})
        self.intent_type = intent_type


class NoPipelineSelectedError(RoutingError):
    """Raised when no pipeline could be selected."""

    def __init__(self, intent_type: str):
        super().__init__(
            f"No pipeline could be selected for intent type: {intent_type}",
            intent_type,
        )


class PipelineExecutionError(ExecutionException):
    """Raised when pipeline execution fails."""

    def __init__(self, message: str, pipeline_name: str = ""):
        super().__init__(message, {"pipeline_name": pipeline_name})
        self.pipeline_name = pipeline_name


class ContextUpdateError(ExecutionException):
    """Raised when context update fails."""

    def __init__(self, message: str, context_key: str = ""):
        super().__init__(message, {"context_key": context_key})
        self.context_key = context_key


class LifecycleError(ExecutionException):
    """Raised when lifecycle operation fails."""

    def __init__(self, message: str, lifecycle_state: str = ""):
        super().__init__(message, {"lifecycle_state": lifecycle_state})
        self.lifecycle_state = lifecycle_state


class SchedulerError(ExecutionException):
    """Raised when scheduler operation fails."""

    def __init__(self, message: str, schedule_id: str = ""):
        super().__init__(message, {"schedule_id": schedule_id})
        self.schedule_id = schedule_id


class StateTransitionError(ExecutionException):
    """Raised when state transition is invalid."""

    def __init__(self, from_state: str, to_state: str, reason: str = ""):
        super().__init__(
            f"Invalid state transition: {from_state} -> {to_state}. Reason: {reason}",
            {"from_state": from_state, "to_state": to_state, "reason": reason},
        )
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason


class PolicyViolationError(ExecutionException):
    """Raised when execution policy is violated."""

    def __init__(self, message: str, policy_name: str = ""):
        super().__init__(message, {"policy_name": policy_name})
        self.policy_name = policy_name


class ValidationError(ExecutionException):
    """Raised when execution validation fails."""

    def __init__(self, message: str, validation_type: str = ""):
        super().__init__(message, {"validation_type": validation_type})
        self.validation_type = validation_type


class ComponentNotAvailableError(ValidationError):
    """Raised when a required component is not available."""

    def __init__(self, component_name: str):
        super().__init__(
            f"Required component not available: {component_name}",
            "component_not_available",
        )
        self.component_name = component_name


class ExecutionCancelledError(ExecutionException):
    """Raised when execution is cancelled."""

    def __init__(self, message: str, execution_id: str = ""):
        super().__init__(message, {"execution_id": execution_id})
        self.execution_id = execution_id


class TimeoutError(ExecutionException):
    """Raised when execution times out."""

    def __init__(self, message: str, timeout_seconds: float):
        super().__init__(message, {"timeout_seconds": timeout_seconds})
        self.timeout_seconds = timeout_seconds


class ExecutionStateError(ExecutionException):
    """Raised when operation is invalid for current state."""

    def __init__(self, message: str, current_state: str = ""):
        super().__init__(message, {"current_state": current_state})
        self.current_state = current_state


class CancellationRequestedError(ExecutionException):
    """Raised when cancellation is requested during execution."""
    pass
