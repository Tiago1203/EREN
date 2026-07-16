"""Circuit Breaker pattern for external service calls.

Prevents cascading failures by failing fast when a service is degraded.
Three states: CLOSED (normal) → OPEN (failing fast) → HALF_OPEN (testing).

Usage::

    from app.providers.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

    cb = CircuitBreaker(
        name="fhir-server",
        config=CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=30.0,
            half_open_max_calls=3,
        ),
    )

    async with cb:
        await fhir_client.get_patient(patient_id)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Awaitable, Callable

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker."""

    failure_threshold: int = 5
    """Number of consecutive failures before opening the circuit."""

    recovery_timeout: float = 30.0
    """Seconds to wait before transitioning OPEN → HALF_OPEN."""

    half_open_max_calls: int = 3
    """Max test calls allowed in HALF_OPEN state before deciding."""


class CircuitBreakerOpen(Exception):
    """Raised when the circuit is OPEN and calls are rejected."""

    def __init__(self, name: str, retry_after: float) -> None:
        self.name = name
        self.retry_after = retry_after
        super().__init__(f"Circuit breaker '{name}' is OPEN. Retry after {retry_after:.1f}s")


class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None) -> None:
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at: float | None = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, transitioning OPEN → HALF_OPEN if needed."""
        if self._state == CircuitState.OPEN and self._opened_at is not None:
            elapsed = time.monotonic() - self._opened_at
            if elapsed >= self.config.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info("Circuit breaker '%s' transitioning OPEN → HALF_OPEN", self.name)
        return self._state

    async def call(
        self,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute a function with circuit breaker protection."""
        async with self:
            return await func(*args, **kwargs)

    async def __aenter__(self) -> CircuitBreaker:
        """Check circuit state before allowing a call."""
        async with self._lock:
            state = self.state
            if state == CircuitState.OPEN:
                raise CircuitBreakerOpen(
                    self.name,
                    retry_after=self.config.recovery_timeout,
                )
            if state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
                if self._half_open_calls > self.config.half_open_max_calls:
                    raise CircuitBreakerOpen(
                        self.name,
                        retry_after=self.config.recovery_timeout,
                    )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool | None:
        """Record success or failure after a call completes."""
        async with self._lock:
            if exc_val is not None:
                await self._record_failure()
            else:
                await self._record_success()
        return None

    async def _record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._success_count = 0
        logger.warning(
            "Circuit breaker '%s' recorded failure %d/%d",
            self.name,
            self._failure_count,
            self.config.failure_threshold,
        )
        if self._failure_count >= self.config.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.monotonic()
            logger.error(
                "Circuit breaker '%s' OPENING after %d failures",
                self.name,
                self._failure_count,
            )

    async def _record_success(self) -> None:
        """Record a successful call."""
        self._success_count += 1
        self._failure_count = 0
        if self._state == CircuitState.HALF_OPEN:
            logger.info(
                "Circuit breaker '%s' success %d/%d (HALF_OPEN)",
                self.name,
                self._success_count,
                self.config.half_open_max_calls,
            )
            if self._success_count >= self.config.half_open_max_calls:
                self._state = CircuitState.CLOSED
                self._success_count = 0
                logger.info("Circuit breaker '%s' CLOSING after successful recovery", self.name)

    def reset(self) -> None:
        """Manually reset the circuit to CLOSED."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at = None
        self._half_open_calls = 0
        logger.info("Circuit breaker '%s' manually reset to CLOSED", self.name)
