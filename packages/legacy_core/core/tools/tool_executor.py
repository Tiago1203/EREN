"""Tool executor for the Cognitive Tool Engine.

Handles execution of tools with retry, timeout, and circuit breaker logic.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .exceptions import (
    ToolNotFoundError,
    ToolTimeoutError,
    ToolValidationError,
)
from .tool_descriptor import ToolDescriptor
from .tool_types import (
    CircuitBreakerConfig,
    CircuitState,
    ExecutionContext,
    ExecutionStatus,
    HealthCheckResult,
    HealthStatus,
    RateLimitConfig,
    RateLimitStatus,
    RetryPolicy,
    RetryStrategy,
    ToolMetrics,
    ToolResult,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Circuit Breaker
# =============================================================================


class CircuitBreaker:
    """Circuit breaker for tool execution.

    Prevents cascading failures by stopping requests to failing tools.
    """

    def __init__(self, config: CircuitBreakerConfig) -> None:
        """Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration.
        """
        self._config = config
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            self._check_state_transition()
            return self._state

    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    def is_open(self) -> bool:
        """Check if circuit is open (rejecting requests)."""
        return self.state == CircuitState.OPEN

    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self.state == CircuitState.HALF_OPEN

    def record_success(self) -> None:
        """Record a successful execution."""
        with self._lock:
            self._success_count += 1

            if self._state == CircuitState.HALF_OPEN:
                if self._success_count >= self._config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)

    def record_failure(self) -> None:
        """Record a failed execution."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._failure_count >= self._config.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def _check_state_transition(self) -> None:
        """Check and perform state transitions."""
        if self._state == CircuitState.OPEN:
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self._config.timeout_seconds:
                    self._transition_to(CircuitState.HALF_OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        if self._state == new_state:
            return

        self._state = new_state

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0


# =============================================================================
# Rate Limiter
# =============================================================================


class RateLimiter:
    """Rate limiter for tool execution.

    Limits the number of requests per time unit.
    """

    def __init__(self, config: RateLimitConfig) -> None:
        """Initialize rate limiter.

        Args:
            config: Rate limit configuration.
        """
        self._config = config
        self._requests: list[float] = []
        self._lock = threading.Lock()

    def check(self) -> RateLimitStatus:
        """Check if a request is allowed.

        Returns:
            RateLimitStatus indicating if request is allowed.
        """
        with self._lock:
            now = time.time()
            window_start = now - 1.0  # 1 second window

            # Clean old requests
            self._requests = [t for t in self._requests if t > window_start]

            # Check rate limit
            if len(self._requests) >= self._config.requests_per_second:
                return RateLimitStatus(
                    tool_id="",
                    allowed=False,
                    remaining=0,
                    retry_after_seconds=1.0,
                )

            # Record request
            self._requests.append(now)

            remaining = int(
                self._config.requests_per_second - len(self._requests)
            )

            return RateLimitStatus(
                tool_id="",
                allowed=True,
                remaining=max(0, remaining),
            )


# =============================================================================
# Retry Handler
# =============================================================================


class RetryHandler:
    """Handles retry logic for failed executions."""

    def __init__(self, policy: RetryPolicy) -> None:
        """Initialize retry handler.

        Args:
            policy: Retry policy.
        """
        self._policy = policy

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Check if should retry.

        Args:
            attempt: Current attempt number (0-indexed).
            error: The error that occurred.

        Returns:
            True if should retry.
        """
        if attempt >= self._policy.max_attempts:
            return False

        if isinstance(error, ToolTimeoutError) and not self._policy.retry_on_timeout:
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """Calculate delay before next retry.

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds.
        """
        strategy = self._policy.strategy

        if strategy == RetryStrategy.NONE:
            return 0.0
        elif strategy == RetryStrategy.FIXED:
            delay = self._policy.base_delay_seconds
        elif strategy == RetryStrategy.LINEAR:
            delay = self._policy.base_delay_seconds * (attempt + 1)
        elif strategy == RetryStrategy.EXPONENTIAL:
            delay = self._policy.base_delay_seconds * (2 ** attempt)
        elif strategy == RetryStrategy.FIBONACCI:
            delay = self._policy.base_delay_seconds * self._fibonacci(attempt + 2)
        else:
            delay = self._policy.base_delay_seconds

        # Apply jitter
        if self._policy.jitter:
            import random
            delay = delay * (0.5 + random.random())

        return min(delay, self._policy.max_delay_seconds)

    @staticmethod
    def _fibonacci(n: int) -> int:
        """Calculate Fibonacci number."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b


# =============================================================================
# Tool Executor
# =============================================================================


class ToolExecutor:
    """Executes tools with retry, timeout, and circuit breaker support.

    The executor is responsible for:
    - Validating tool parameters
    - Managing execution lifecycle
    - Applying retry policies
    - Handling timeouts
    - Circuit breaker integration
    - Rate limiting
    - Metrics collection
    """

    def __init__(self) -> None:
        """Initialize the tool executor."""
        self._tools: dict[str, ToolDescriptor] = {}
        self._handlers: dict[str, Callable] = {}  # tool_id -> handler function
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._rate_limiters: dict[str, RateLimiter] = {}
        self._retry_handlers: dict[str, RetryHandler] = {}
        self._metrics: dict[str, ToolMetrics] = {}
        self._lock = threading.Lock()

    def register_tool(
        self,
        tool: ToolDescriptor,
        handler: Callable,
    ) -> None:
        """Register a tool and its handler.

        Args:
            tool: The tool descriptor.
            handler: The function to call for execution.
        """
        with self._lock:
            self._tools[tool.tool_id] = tool
            self._handlers[tool.tool_id] = handler

            # Initialize circuit breaker
            self._circuit_breakers[tool.tool_id] = CircuitBreaker(
                tool.circuit_breaker
            )

            # Initialize rate limiter
            self._rate_limiters[tool.tool_id] = RateLimiter(tool.rate_limit)

            # Initialize retry handler
            self._retry_handlers[tool.tool_id] = RetryHandler(tool.retry_policy)

            # Initialize metrics
            self._metrics[tool.tool_id] = ToolMetrics(tool_id=tool.tool_id)

    def unregister_tool(self, tool_id: str) -> None:
        """Unregister a tool.

        Args:
            tool_id: The tool ID to unregister.
        """
        with self._lock:
            self._tools.pop(tool_id, None)
            self._handlers.pop(tool_id, None)
            self._circuit_breakers.pop(tool_id, None)
            self._rate_limiters.pop(tool_id, None)
            self._retry_handlers.pop(tool_id, None)

    def get_tool(self, tool_id: str) -> ToolDescriptor | None:
        """Get a tool descriptor.

        Args:
            tool_id: The tool ID.

        Returns:
            The tool descriptor or None.
        """
        return self._tools.get(tool_id)

    def execute(
        self,
        tool_id: str,
        parameters: dict,
        context: ExecutionContext | None = None,
    ) -> ToolResult:
        """Execute a tool.

        Args:
            tool_id: The tool ID.
            parameters: Execution parameters.
            context: Optional execution context.

        Returns:
            ToolResult with execution outcome.
        """
        if tool_id not in self._tools:
            raise ToolNotFoundError(tool_id)

        tool = self._tools[tool_id]
        handler = self._handlers[tool_id]

        # Create execution context if not provided
        if context is None:
            context = ExecutionContext()

        execution_id = f"exec_{uuid.uuid4().hex[:16]}"
        start_time = time.time()

        # Check circuit breaker
        circuit_breaker = self._circuit_breakers[tool_id]
        if circuit_breaker.is_open():
            return ToolResult(
                tool_id=tool_id,
                execution_id=execution_id,
                status=ExecutionStatus.FAILED,
                error="Circuit breaker is open",
                error_code="CIRCUIT_OPEN",
                execution_time_ms=0.0,
            )

        # Check rate limit
        rate_limiter = self._rate_limiters[tool_id]
        rate_status = rate_limiter.check()
        if not rate_status.allowed:
            return ToolResult(
                tool_id=tool_id,
                execution_id=execution_id,
                status=ExecutionStatus.RATE_LIMITED,
                error="Rate limit exceeded",
                error_code="RATE_LIMITED",
                execution_time_ms=0.0,
            )

        # Validate parameters
        self._validate_parameters(tool, parameters)

        # Execute with retry
        retry_handler = self._retry_handlers[tool_id]
        attempt = 0

        while True:
            try:
                # Execute
                result = self._execute_with_timeout(
                    handler,
                    parameters,
                    tool.contract.timeout_seconds,
                )

                # Success
                circuit_breaker.record_success()
                execution_time_ms = (time.time() - start_time) * 1000

                # Update metrics
                self._record_success(tool_id, execution_time_ms)

                return ToolResult(
                    tool_id=tool_id,
                    execution_id=execution_id,
                    status=ExecutionStatus.SUCCESS,
                    output=result,
                    execution_time_ms=execution_time_ms,
                    retry_count=attempt,
                )

            except ToolTimeoutError as e:
                if not retry_handler.should_retry(attempt, e):
                    circuit_breaker.record_failure()
                    self._record_failure(tool_id, execution_time_ms, "timeout")
                    return ToolResult(
                        tool_id=tool_id,
                        execution_id=execution_id,
                        status=ExecutionStatus.TIMEOUT,
                        error=str(e),
                        error_code="TIMEOUT",
                        execution_time_ms=(time.time() - start_time) * 1000,
                        retry_count=attempt,
                    )

            except Exception as e:
                if not retry_handler.should_retry(attempt, e):
                    circuit_breaker.record_failure()
                    self._record_failure(tool_id, execution_time_ms, "error")
                    return ToolResult(
                        tool_id=tool_id,
                        execution_id=execution_id,
                        status=ExecutionStatus.FAILED,
                        error=str(e),
                        error_code="EXECUTION_ERROR",
                        execution_time_ms=(time.time() - start_time) * 1000,
                        retry_count=attempt,
                    )

            # Retry
            attempt += 1
            delay = retry_handler.get_delay(attempt - 1)
            if delay > 0:
                time.sleep(delay)

    def _execute_with_timeout(
        self,
        handler: Callable,
        parameters: dict,
        timeout_seconds: float,
    ) -> Any:
        """Execute handler with timeout.

        Args:
            handler: The handler function.
            parameters: Execution parameters.
            timeout_seconds: Timeout in seconds.

        Returns:
            Handler result.

        Raises:
            ToolTimeoutError: If execution times out.
        """
        result: list[Any] = [None]
        error: list[Exception] = [None]
        finished: list[bool] = [False]

        def target() -> None:
            try:
                result[0] = handler(parameters)
            except Exception as e:
                error[0] = e
            finally:
                finished[0] = True

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=timeout_seconds)

        if not finished[0]:
            raise ToolTimeoutError(handler.__name__, timeout_seconds)

        if error[0]:
            raise error[0]

        return result[0]

    def _validate_parameters(
        self,
        tool: ToolDescriptor,
        parameters: dict,
    ) -> None:
        """Validate execution parameters.

        Args:
            tool: The tool descriptor.
            parameters: Parameters to validate.

        Raises:
            ToolValidationError: If validation fails.
        """
        violations = []

        for param in tool.parameters:
            if param.required and param.name not in parameters:
                violations.append(f"Missing required parameter: {param.name}")

        for name, value in parameters.items():
            param = tool.get_parameter(name)
            if param and param.enum and value not in param.enum:
                violations.append(
                    f"Parameter '{name}' must be one of {param.enum}"
                )

        if violations:
            raise ToolValidationError(tool.tool_id, violations)

    def _record_success(self, tool_id: str, execution_time_ms: float) -> None:
        """Record successful execution."""
        with self._lock:
            metrics = self._metrics.get(tool_id)
            if metrics:
                metrics.total_executions += 1
                metrics.successful_executions += 1
                metrics.total_execution_time_ms += execution_time_ms
                metrics.avg_execution_time_ms = (
                    metrics.total_execution_time_ms / metrics.total_executions
                )
                metrics.last_execution = datetime.now(UTC).isoformat()
                metrics.last_success = metrics.last_execution

    def _record_failure(
        self,
        tool_id: str,
        execution_time_ms: float,
        error_type: str,
    ) -> None:
        """Record failed execution."""
        with self._lock:
            metrics = self._metrics.get(tool_id)
            if metrics:
                metrics.total_executions += 1
                metrics.failed_executions += 1
                if error_type == "timeout":
                    metrics.timed_out_executions += 1
                metrics.last_execution = datetime.now(UTC).isoformat()
                metrics.last_failure = metrics.last_execution

    def get_metrics(self, tool_id: str) -> ToolMetrics | None:
        """Get metrics for a tool."""
        return self._metrics.get(tool_id)

    def health_check(self, tool_id: str) -> HealthCheckResult:
        """Perform health check on a tool.

        Args:
            tool_id: The tool ID.

        Returns:
            HealthCheckResult.
        """
        if tool_id not in self._tools:
            return HealthCheckResult(
                tool_id=tool_id,
                status=HealthStatus.UNKNOWN,
                message="Tool not registered",
            )

        circuit_breaker = self._circuit_breakers[tool_id]
        metrics = self._metrics.get(tool_id)

        if circuit_breaker.is_open():
            return HealthCheckResult(
                tool_id=tool_id,
                status=HealthStatus.UNHEALTHY,
                message="Circuit breaker is open",
            )

        if metrics:
            if metrics.success_rate >= 0.95:
                status = HealthStatus.HEALTHY
            elif metrics.success_rate >= 0.8:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY

            return HealthCheckResult(
                tool_id=tool_id,
                status=status,
                latency_ms=metrics.avg_execution_time_ms,
                message=f"Success rate: {metrics.success_rate:.1%}",
                last_check=datetime.now(UTC).isoformat(),
            )

        return HealthCheckResult(
            tool_id=tool_id,
            status=HealthStatus.UNKNOWN,
        )
