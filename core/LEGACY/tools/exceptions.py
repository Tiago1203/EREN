"""Exception types for the Cognitive Tool Engine.

Provides a typed exception hierarchy for tool operations.

Architecture only — no business logic.
"""

from __future__ import annotations


class ToolsError(Exception):
    """Base class for all tools-related errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class ToolNotFoundError(ToolsError):
    """Raised when a tool is not found in the registry.

    Attributes:
        tool_id: The ID of the tool that was not found.
    """

    def __init__(self, tool_id: str = "") -> None:
        super().__init__(f"Tool '{tool_id}' not found in registry")
        self.tool_id = tool_id


class ToolAlreadyRegisteredError(ToolsError):
    """Raised when registering a duplicate tool.

    Attributes:
        tool_id: The ID of the tool that is already registered.
    """

    def __init__(self, tool_id: str = "") -> None:
        super().__init__(f"Tool '{tool_id}' already registered")
        self.tool_id = tool_id


class ToolInvocationError(ToolsError):
    """Raised when an external tool fails during invocation."""


class ToolExecutionError(ToolsError):
    """Raised when tool execution fails.

    Attributes:
        tool_id: The tool that failed.
        execution_id: The execution ID.
        error: The error message.
    """

    def __init__(
        self,
        tool_id: str = "",
        execution_id: str = "",
        error: str = "",
    ) -> None:
        super().__init__(
            f"Tool '{tool_id}' execution failed: {error}"
        )
        self.tool_id = tool_id
        self.execution_id = execution_id
        self.error = error


class ToolTimeoutError(ToolsError):
    """Raised when tool execution times out.

    Attributes:
        tool_id: The tool that timed out.
        timeout_seconds: The timeout threshold.
    """

    def __init__(
        self,
        tool_id: str = "",
        timeout_seconds: float = 0.0,
    ) -> None:
        super().__init__(
            f"Tool '{tool_id}' execution timed out after {timeout_seconds}s"
        )
        self.tool_id = tool_id
        self.timeout_seconds = timeout_seconds


class ToolValidationError(ToolsError):
    """Raised when tool parameters are invalid.

    Attributes:
        tool_id: The tool with invalid parameters.
        violations: List of validation violations.
    """

    def __init__(
        self,
        tool_id: str = "",
        violations: list[str] | None = None,
    ) -> None:
        violations_str = "; ".join(violations or [])
        super().__init__(
            f"Validation failed for tool '{tool_id}': {violations_str}"
        )
        self.tool_id = tool_id
        self.violations = violations or []


class ToolUnavailableError(ToolsError):
    """Raised when a tool is not available.

    Attributes:
        tool_id: The unavailable tool.
        reason: Why the tool is unavailable.
    """

    def __init__(
        self,
        tool_id: str = "",
        reason: str = "",
    ) -> None:
        super().__init__(
            f"Tool '{tool_id}' is unavailable: {reason}"
        )
        self.tool_id = tool_id
        self.reason = reason


class ToolPermissionError(ToolsError):
    """Raised when user lacks permission to use a tool.

    Attributes:
        tool_id: The tool requiring permissions.
        missing_permissions: List of missing permissions.
    """

    def __init__(
        self,
        tool_id: str = "",
        missing_permissions: list[str] | None = None,
    ) -> None:
        perms = ", ".join(missing_permissions or [])
        super().__init__(
            f"Permission denied for tool '{tool_id}'. Missing: [{perms}]"
        )
        self.tool_id = tool_id
        self.missing_permissions = missing_permissions or []


class CircuitBreakerOpenError(ToolsError):
    """Raised when circuit breaker is open.

    Attributes:
        tool_id: The tool with open circuit breaker.
    """

    def __init__(self, tool_id: str = "") -> None:
        super().__init__(
            f"Circuit breaker is open for tool '{tool_id}'"
        )
        self.tool_id = tool_id


class RateLimitExceededError(ToolsError):
    """Raised when rate limit is exceeded.

    Attributes:
        tool_id: The tool with exceeded rate limit.
        retry_after: Seconds until rate limit resets.
    """

    def __init__(
        self,
        tool_id: str = "",
        retry_after: float = 0.0,
    ) -> None:
        super().__init__(
            f"Rate limit exceeded for tool '{tool_id}'. Retry after {retry_after}s"
        )
        self.tool_id = tool_id
        self.retry_after = retry_after


class PipelineExecutionError(ToolsError):
    """Raised when pipeline execution fails.

    Attributes:
        pipeline_id: The pipeline that failed.
        reason: Why the pipeline failed.
    """

    def __init__(
        self,
        pipeline_id: str = "",
        reason: str = "",
    ) -> None:
        super().__init__(
            f"Pipeline '{pipeline_id}' execution failed: {reason}"
        )
        self.pipeline_id = pipeline_id
        self.reason = reason


class PipelineStepError(ToolsError):
    """Raised when a pipeline step fails.

    Attributes:
        pipeline_id: The pipeline ID.
        step_id: The failed step ID.
        error: The error message.
    """

    def __init__(
        self,
        pipeline_id: str = "",
        step_id: str = "",
        error: str = "",
    ) -> None:
        super().__init__(
            f"Pipeline '{pipeline_id}' step '{step_id}' failed: {error}"
        )
        self.pipeline_id = pipeline_id
        self.step_id = step_id
        self.error = error


class ToolHealthError(ToolsError):
    """Raised when a tool health check fails.

    Attributes:
        tool_id: The unhealthy tool.
        message: Health check message.
    """

    def __init__(
        self,
        tool_id: str = "",
        message: str = "",
    ) -> None:
        super().__init__(
            f"Tool '{tool_id}' health check failed: {message}"
        )
        self.tool_id = tool_id
        self.message = message
