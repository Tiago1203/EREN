"""Pipeline exceptions for EREN OS Cognitive Capability Pipeline.

Defines all exceptions that can be raised during pipeline operations.
Following EREN's philosophy: explicit, typed, and comprehensive.
"""

from __future__ import annotations


class PipelineException(Exception):
    """Base exception for all pipeline errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PipelineInitializationError(PipelineException):
    """Raised when pipeline fails to initialize."""
    pass


class PipelineConfigurationError(PipelineException):
    """Raised when pipeline configuration is invalid."""

    def __init__(self, message: str, config_key: str = ""):
        super().__init__(message, {"config_key": config_key})
        self.config_key = config_key


class PipelineValidationError(PipelineException):
    """Raised when pipeline validation fails."""

    def __init__(self, message: str, validation_type: str = ""):
        super().__init__(message, {"validation_type": validation_type})
        self.validation_type = validation_type


class DuplicateStageError(PipelineValidationError):
    """Raised when duplicate stages are detected."""

    def __init__(self, stage_name: str):
        super().__init__(
            f"Duplicate stage detected: {stage_name}",
            "duplicate_stage",
        )
        self.stage_name = stage_name


class InvalidStageOrderError(PipelineValidationError):
    """Raised when stage order is invalid."""

    def __init__(self, message: str, stage_name: str = ""):
        super().__init__(message, "invalid_order")
        self.stage_name = stage_name


class MissingDependencyError(PipelineValidationError):
    """Raised when a required dependency is missing."""

    def __init__(self, stage_name: str, missing_dependency: str):
        super().__init__(
            f"Stage '{stage_name}' is missing required dependency: {missing_dependency}",
            "missing_dependency",
        )
        self.stage_name = stage_name
        self.missing_dependency = missing_dependency


class EmptyPipelineError(PipelineValidationError):
    """Raised when pipeline has no stages."""

    def __init__(self):
        super().__init__("Pipeline has no stages", "empty_pipeline")


class ContractNotFoundError(PipelineValidationError):
    """Raised when a required contract is not registered."""

    def __init__(self, contract_name: str):
        super().__init__(
            f"Required contract not found: {contract_name}",
            "contract_not_found",
        )
        self.contract_name = contract_name


class StageException(PipelineException):
    """Base exception for stage-related errors."""

    def __init__(self, message: str, stage_name: str = ""):
        super().__init__(message, {"stage_name": stage_name})
        self.stage_name = stage_name


class StageExecutionError(StageException):
    """Raised when a stage fails to execute."""

    def __init__(self, stage_name: str, original_error: Exception | None = None):
        super().__init__(
            f"Stage '{stage_name}' failed to execute",
            stage_name,
        )
        self.original_error = original_error


class StageTimeoutError(StageException):
    """Raised when a stage execution times out."""

    def __init__(self, stage_name: str, timeout_seconds: float):
        super().__init__(
            f"Stage '{stage_name}' timed out after {timeout_seconds}s",
            stage_name,
        )
        self.timeout_seconds = timeout_seconds


class StageSkippedError(StageException):
    """Raised when a stage is skipped."""

    def __init__(self, stage_name: str, reason: str = ""):
        super().__init__(
            f"Stage '{stage_name}' was skipped: {reason}",
            stage_name,
        )
        self.reason = reason


class StageCancelledError(StageException):
    """Raised when a stage is cancelled."""

    def __init__(self, stage_name: str):
        super().__init__(
            f"Stage '{stage_name}' was cancelled",
            stage_name,
        )


class PipelineExecutionError(PipelineException):
    """Raised when pipeline execution fails."""

    def __init__(self, message: str, failed_stage: str = ""):
        super().__init__(message, {"failed_stage": failed_stage})
        self.failed_stage = failed_stage


class PolicyViolationError(PipelineException):
    """Raised when a pipeline policy is violated."""

    def __init__(self, message: str, policy_name: str = ""):
        super().__init__(message, {"policy_name": policy_name})
        self.policy_name = policy_name


class PolicyStopOnFailureError(PolicyViolationError):
    """Raised when StopOnFailure policy stops execution."""

    def __init__(self, stage_name: str):
        super().__init__(
            f"Pipeline stopped due to StopOnFailure policy at stage '{stage_name}'",
            "StopOnFailure",
        )
        self.stage_name = stage_name


class RetryExhaustedError(StageException):
    """Raised when stage retries are exhausted."""

    def __init__(self, stage_name: str, max_retries: int):
        super().__init__(
            f"Stage '{stage_name}' exhausted {max_retries} retries",
            stage_name,
        )
        self.max_retries = max_retries


class PipelineStateError(PipelineException):
    """Raised when an operation is invalid for current state."""

    def __init__(self, message: str, current_state: str = "", operation: str = ""):
        super().__init__(message, {
            "current_state": current_state,
            "operation": operation,
        })
        self.current_state = current_state
        self.operation = operation


class InvalidTransitionError(PipelineStateError):
    """Raised when state transition is invalid."""

    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            f"Invalid state transition: {from_state} -> {to_state}",
            from_state,
            "transition",
        )
        self.from_state = from_state
        self.to_state = to_state


class PipelineNotRunningError(PipelineStateError):
    """Raised when pipeline is not in RUNNING state."""

    def __init__(self, operation: str, current_state: str):
        super().__init__(
            f"Cannot '{operation}' - pipeline is not running (current state: {current_state})",
            current_state,
            operation,
        )


class PipelineAlreadyRunningError(PipelineStateError):
    """Raised when attempting to start an already running pipeline."""

    def __init__(self, pipeline_id: str):
        super().__init__(
            f"Pipeline '{pipeline_id}' is already running",
            "RUNNING",
            "start",
        )
        self.pipeline_id = pipeline_id


class CancellationRequestedError(PipelineException):
    """Raised when pipeline cancellation is requested."""
    pass


class PauseNotSupportedError(PipelineStateError):
    """Raised when pause is not supported."""

    def __init__(self, stage_name: str):
        super().__init__(
            f"Stage '{stage_name}' does not support pause",
            "",
            "pause",
        )
        self.stage_name = stage_name


class ContextError(PipelineException):
    """Raised when there's an error with pipeline context."""

    def __init__(self, message: str, context_key: str = ""):
        super().__init__(message, {"context_key": context_key})
        self.context_key = context_key


class RegistryError(PipelineException):
    """Raised when there's an error with pipeline registry."""

    def __init__(self, message: str, pipeline_name: str = ""):
        super().__init__(message, {"pipeline_name": pipeline_name})
        self.pipeline_name = pipeline_name


class PipelineNotFoundError(RegistryError):
    """Raised when a pipeline is not found in registry."""

    def __init__(self, pipeline_name: str):
        super().__init__(
            f"Pipeline '{pipeline_name}' not found in registry",
            pipeline_name,
        )


class PipelineAlreadyRegisteredError(RegistryError):
    """Raised when a pipeline is already registered."""

    def __init__(self, pipeline_name: str):
        super().__init__(
            f"Pipeline '{pipeline_name}' is already registered",
            pipeline_name,
        )
