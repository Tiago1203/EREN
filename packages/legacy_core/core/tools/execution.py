"""Tool Execution Runtime for EREN OS Universal Tool Calling Engine.

Orchestrates tool execution with validation, security, and observability.
"""

from __future__ import annotations

import asyncio
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from core.tools.catalog.base import ExternalTool, ToolCategory
from core.tools.discovery import ToolDiscovery, DiscoveryConfig, tool as tool_decorator
from core.tools.exceptions import ToolExecutionError, ToolTimeoutError
from core.tools.sandbox import (
    SandboxConfig,
    SandboxManager,
    SandboxType,
    ToolSandbox,
)
from core.tools.tool_types import (
    ExecutionContext,
    ExecutionMode,
    ExecutionStatus,
    RetryPolicy,
    RetryStrategy,
    ToolResult,
    ToolSelectorCriteria,
)
from core.tools.tool_registry import ToolRegistry
from core.tools.validation import (
    ToolValidator,
    ValidationConfig,
    ValidationResult,
)


# =============================================================================
# Execution Types
# =============================================================================


class ExecutionEngineState(str, Enum):
    """State of the execution engine."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ExecutionConfig:
    """Configuration for tool execution."""

    enable_sandbox: bool = True
    enable_validation: bool = True
    enable_retry: bool = True
    enable_circuit_breaker: bool = True
    default_timeout_seconds: float = 30.0
    max_concurrent_executions: int = 100
    retry_policy: RetryPolicy = field(default_factory=lambda: RetryPolicy())


@dataclass
class ExecutionMetrics:
    """Metrics for tool execution."""

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    timed_out_executions: int = 0
    total_execution_time_ms: float = 0.0
    average_execution_time_ms: float = 0.0
    active_executions: int = 0


# =============================================================================
# Execution Runtime
# =============================================================================


class ToolExecutionRuntime:
    """Runtime for executing tools with full lifecycle management.

    Features:
    - Synchronous and asynchronous execution
    - Automatic parameter validation
    - Sandbox isolation
    - Retry with backoff
    - Circuit breaker
    - Metrics and observability
    - Result validation
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        config: ExecutionConfig | None = None,
    ):
        """Initialize tool execution runtime.

        Args:
            registry: Tool registry.
            config: Execution configuration.
        """
        self._registry = registry or ToolRegistry()
        self._config = config or ExecutionConfig()
        self._state = ExecutionEngineState.IDLE

        # Components
        self._sandbox_manager = SandboxManager()
        self._validator = ToolValidator()
        self._discovery = ToolDiscovery()

        # Metrics
        self._metrics = ExecutionMetrics()
        self._metrics_lock = threading.Lock()

        # Active executions
        self._active_executions: dict[str, asyncio.Task] = {}
        self._executions_lock = threading.RLock()

        # Callbacks
        self._on_execution_start: list[Callable] = []
        self._on_execution_end: list[Callable] = []

    @property
    def state(self) -> ExecutionEngineState:
        """Get execution engine state."""
        return self._state

    @property
    def metrics(self) -> ExecutionMetrics:
        """Get execution metrics."""
        return self._metrics

    # =========================================================================
    # Execution
    # =========================================================================

    async def execute(
        self,
        tool_name: str,
        parameters: dict,
        context: ExecutionContext | None = None,
        mode: ExecutionMode = ExecutionMode.SYNCHRONOUS,
    ) -> ToolResult:
        """Execute a tool.

        Args:
            tool_name: Name of tool to execute.
            parameters: Tool parameters.
            context: Execution context.
            mode: Execution mode.

        Returns:
            Tool execution result.
        """
        execution_id = str(uuid.uuid4())
        context = context or ExecutionContext()
        start_time = time.time()

        # Get tool from registry
        tool = self._registry.get(tool_name)

        # Create execution context
        execution_context = ExecutionContext(
            correlation_id=context.correlation_id or execution_id,
            session_id=context.session_id,
            user_id=context.user_id,
            hospital_id=context.hospital_id,
            request_id=execution_id,
            priority=context.priority,
            mode=mode,
            timeout_seconds=tool.timeout,
        )

        # Emit start event
        await self._emit_execution_start(execution_id, tool_name, parameters)

        try:
            # Update state
            self._state = ExecutionEngineState.RUNNING
            self._increment_active_executions()

            # Validate parameters
            if self._config.enable_validation:
                validation_result = await self._validate_parameters(tool, parameters)
                if not validation_result.valid:
                    return self._create_error_result(
                        execution_id=execution_id,
                        tool_name=tool_name,
                        error=f"Validation failed: {validation_result.errors}",
                        start_time=start_time,
                    )

            # Execute with retry
            if self._config.enable_retry and tool.retry_policy:
                result = await self._execute_with_retry(
                    tool, parameters, execution_context
                )
            else:
                result = await self._execute_tool(
                    tool, parameters, execution_context
                )

            # Validate result
            if self._config.enable_validation and result.is_success():
                result_validation = await self._validate_result(tool, result)
                if not result_validation.valid:
                    result.error = f"Result validation failed: {result_validation.errors}"

            return result

        except TimeoutError as e:
            self._update_metrics(success=False, timeout=True)
            return self._create_error_result(
                execution_id=execution_id,
                tool_name=tool_name,
                error=f"Timeout: {e}",
                start_time=start_time,
            )

        except Exception as e:
            self._update_metrics(success=False)
            return self._create_error_result(
                execution_id=execution_id,
                tool_name=tool_name,
                error=str(e),
                start_time=start_time,
            )

        finally:
            self._decrement_active_executions()
            await self._emit_execution_end(execution_id, tool_name)
            self._state = ExecutionEngineState.IDLE

    async def _execute_with_retry(
        self,
        tool: ExternalTool,
        parameters: dict,
        context: ExecutionContext,
    ) -> ToolResult:
        """Execute tool with retry logic.

        Args:
            tool: Tool to execute.
            parameters: Parameters.
            context: Execution context.

        Returns:
            Tool result.
        """
        retry_policy = tool.retry_policy or RetryPolicy()
        attempt = 0
        last_error = None

        while attempt < retry_policy.max_attempts:
            try:
                return await self._execute_tool(tool, parameters, context)

            except Exception as e:
                last_error = e
                attempt += 1

                if attempt >= retry_policy.max_attempts:
                    break

                # Calculate delay
                delay = self._calculate_retry_delay(attempt, retry_policy)
                await asyncio.sleep(delay)

        # All retries failed
        raise last_error or Exception("Unknown retry error")

    async def _execute_tool(
        self,
        tool: ExternalTool,
        parameters: dict,
        context: ExecutionContext,
    ) -> ToolResult:
        """Execute tool implementation.

        Args:
            tool: Tool to execute.
            parameters: Parameters.
            context: Execution context.

        Returns:
            Tool result.
        """
        execution_id = context.request_id
        start_time = time.time()

        try:
            # Get or create sandbox
            sandbox_id = f"sandbox_{tool.name}"
            sandbox = self._sandbox_manager.get_sandbox(
                sandbox_id,
                SandboxType.PROCESS if self._config.enable_sandbox else SandboxType.THREAD,
                SandboxConfig(timeout_seconds=tool.timeout),
            )

            # Execute in sandbox
            if self._config.enable_sandbox:
                result_data = await sandbox.execute(
                    tool.execute,
                    parameters,
                )
            else:
                result_data = await asyncio.wait_for(
                    asyncio.to_thread(tool.execute, parameters),
                    timeout=context.timeout_seconds,
                )

            execution_time = (time.time() - start_time) * 1000
            self._update_metrics(success=True, execution_time=execution_time)

            return ToolResult(
                tool_id=tool.name,
                execution_id=execution_id,
                status=ExecutionStatus.SUCCESS,
                output=result_data,
                execution_time_ms=execution_time,
                timestamp=datetime.now(UTC).isoformat(),
            )

        except asyncio.TimeoutError:
            return ToolResult(
                tool_id=tool.name,
                execution_id=execution_id,
                status=ExecutionStatus.TIMEOUT,
                error=f"Execution timed out after {tool.timeout}s",
                execution_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(UTC).isoformat(),
            )

        except Exception as e:
            return ToolResult(
                tool_id=tool.name,
                execution_id=execution_id,
                status=ExecutionStatus.FAILED,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now(UTC).isoformat(),
            )

    def _calculate_retry_delay(
        self,
        attempt: int,
        policy: RetryPolicy,
    ) -> float:
        """Calculate retry delay.

        Args:
            attempt: Current attempt number.
            policy: Retry policy.

        Returns:
            Delay in seconds.
        """
        if policy.strategy == RetryStrategy.EXPONENTIAL:
            delay = policy.base_delay_seconds * (2 ** (attempt - 1))
        elif policy.strategy == RetryStrategy.LINEAR:
            delay = policy.base_delay_seconds * attempt
        elif policy.strategy == RetryStrategy.FIBONACCI:
            # Simplified fibonacci
            a, b = 1, 1
            for _ in range(attempt - 1):
                a, b = b, a + b
            delay = policy.base_delay_seconds * a
        else:
            delay = policy.base_delay_seconds

        # Apply jitter
        if policy.jitter:
            import random
            delay *= 0.5 + random.random()

        return min(delay, policy.max_delay_seconds)

    # =========================================================================
    # Validation
    # =========================================================================

    async def _validate_parameters(
        self,
        tool: ExternalTool,
        parameters: dict,
    ) -> ValidationResult:
        """Validate tool parameters.

        Args:
            tool: Tool to validate.
            parameters: Parameters to validate.

        Returns:
            Validation result.
        """
        if not tool.input_schema:
            return ValidationResult(valid=True)

        return self._validator.validate_parameters(parameters, tool.input_schema)

    async def _validate_result(
        self,
        tool: ExternalTool,
        result: ToolResult,
    ) -> ValidationResult:
        """Validate tool result.

        Args:
            tool: Tool that was executed.
            result: Result to validate.

        Returns:
            Validation result.
        """
        if not tool.output_schema:
            return ValidationResult(valid=True)

        return self._validator.validate_result(result.output, tool.output_schema)

    # =========================================================================
    # Metrics
    # =========================================================================

    def _update_metrics(
        self,
        success: bool,
        execution_time: float = 0,
        timeout: bool = False,
    ) -> None:
        """Update execution metrics.

        Args:
            success: Whether execution succeeded.
            execution_time: Execution time in ms.
            timeout: Whether execution timed out.
        """
        with self._metrics_lock:
            self._metrics.total_executions += 1

            if success:
                self._metrics.successful_executions += 1
            else:
                self._metrics.failed_executions += 1
                if timeout:
                    self._metrics.timed_out_executions += 1

            self._metrics.total_execution_time_ms += execution_time
            self._metrics.average_execution_time_ms = (
                self._metrics.total_execution_time_ms / self._metrics.total_executions
            )

    def _increment_active_executions(self) -> None:
        """Increment active executions counter."""
        with self._metrics_lock:
            self._metrics.active_executions += 1

    def _decrement_active_executions(self) -> None:
        """Decrement active executions counter."""
        with self._metrics_lock:
            self._metrics.active_executions = max(0, self._metrics.active_executions - 1)

    # =========================================================================
    # Events
    # =========================================================================

    def on_execution_start(self, callback: Callable) -> None:
        """Register execution start callback.

        Args:
            callback: Callback function.
        """
        self._on_execution_start.append(callback)

    def on_execution_end(self, callback: Callable) -> None:
        """Register execution end callback.

        Args:
            callback: Callback function.
        """
        self._on_execution_end.append(callback)

    async def _emit_execution_start(
        self,
        execution_id: str,
        tool_name: str,
        parameters: dict,
    ) -> None:
        """Emit execution start event."""
        for callback in self._on_execution_start:
            try:
                callback(execution_id, tool_name, parameters)
            except Exception:
                pass

    async def _emit_execution_end(
        self,
        execution_id: str,
        tool_name: str,
    ) -> None:
        """Emit execution end event."""
        for callback in self._on_execution_end:
            try:
                callback(execution_id, tool_name)
            except Exception:
                pass

    # =========================================================================
    # Utility
    # =========================================================================

    def _create_error_result(
        self,
        execution_id: str,
        tool_name: str,
        error: str,
        start_time: float,
    ) -> ToolResult:
        """Create error result.

        Args:
            execution_id: Execution ID.
            tool_name: Tool name.
            error: Error message.
            start_time: Start time.

        Returns:
            Error result.
        """
        return ToolResult(
            tool_id=tool_name,
            execution_id=execution_id,
            status=ExecutionStatus.FAILED,
            error=error,
            execution_time_ms=(time.time() - start_time) * 1000,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def get_metrics_summary(self) -> dict:
        """Get metrics summary.

        Returns:
            Metrics dictionary.
        """
        with self._metrics_lock:
            success_rate = (
                self._metrics.successful_executions / self._metrics.total_executions * 100
                if self._metrics.total_executions > 0
                else 0
            )

            return {
                "total_executions": self._metrics.total_executions,
                "successful_executions": self._metrics.successful_executions,
                "failed_executions": self._metrics.failed_executions,
                "timed_out_executions": self._metrics.timed_out_executions,
                "success_rate": f"{success_rate:.2f}%",
                "average_execution_time_ms": f"{self._metrics.average_execution_time_ms:.2f}",
                "active_executions": self._metrics.active_executions,
            }

    def shutdown(self) -> None:
        """Shutdown execution runtime."""
        self._sandbox_manager.shutdown()
        self._state = ExecutionEngineState.IDLE
