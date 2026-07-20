"""Circuit Breaker for EREN OS Multi-Provider Layer.

Implements circuit breaker pattern for provider resilience.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.providers.provider import BaseProvider


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes before closing
    timeout_seconds: float = 30.0  # Time before trying half-open
    half_open_max_calls: int = 3  # Max calls in half-open state
    window_seconds: float = 60.0  # Time window for failure counting
    slow_call_threshold_ms: int = 2000  # Slow call threshold
    slow_call_percentage: float = 50.0  # Slow call percentage threshold


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""

    provider_id: str
    circuit_state: CircuitState
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    slow_calls: int = 0
    rejected_calls: int = 0
    last_failure: datetime | None = None
    last_success: datetime | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    failure_count_in_window: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "circuit_state": self.circuit_state.value,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "slow_calls": self.slow_calls,
            "rejected_calls": self.rejected_calls,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "failure_count_in_window": self.failure_count_in_window,
        }


class CircuitBreaker:
    """Circuit breaker for provider resilience.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Provider is failing, requests are rejected
    - HALF_OPEN: Testing if provider has recovered

    Transitions:
    - CLOSED -> OPEN: When failure threshold is exceeded
    - OPEN -> HALF_OPEN: After timeout expires
    - HALF_OPEN -> CLOSED: When success threshold is reached
    - HALF_OPEN -> OPEN: When a failure occurs
    """

    def __init__(
        self,
        provider_id: str,
        config: CircuitBreakerConfig | None = None,
    ):
        """Initialize circuit breaker.

        Args:
            provider_id: Provider identifier.
            config: Circuit breaker configuration.
        """
        self._provider_id = provider_id
        self._config = config or CircuitBreakerConfig()

        self._state = CircuitState.CLOSED
        self._lock = threading.RLock()

        # Counters
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0

        # Timing
        self._last_failure_time: datetime | None = None
        self._opened_at: datetime | None = None
        self._window_start: datetime = datetime.now(UTC)

        # Stats
        self._stats = CircuitBreakerStats(
            provider_id=provider_id,
            circuit_state=self._state,
        )

    @property
    def provider_id(self) -> str:
        """Get provider identifier."""
        return self._provider_id

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            return self._get_state_unlocked()

    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed."""
        return self.state == CircuitState.CLOSED

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open."""
        return self.state == CircuitState.HALF_OPEN

    @property
    def stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        with self._lock:
            return self._stats

    def _get_state_unlocked(self) -> CircuitState:
        """Get state without locking (caller must hold lock)."""
        if self._state == CircuitState.OPEN:
            # Check if we should transition to half-open
            if self._should_attempt_reset():
                self._transition_to_half_open_unlocked()
        return self._state

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if self._last_failure_time is None:
            return True

        elapsed = (datetime.now(UTC) - self._last_failure_time).total_seconds()
        return elapsed >= self._config.timeout_seconds

    def _transition_to_half_open_unlocked(self) -> None:
        """Transition to half-open state (caller must hold lock)."""
        self._state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._stats.circuit_state = self._state

    def _transition_to_open(self) -> None:
        """Transition to open state."""
        with self._lock:
            if self._state != CircuitState.OPEN:
                self._state = CircuitState.OPEN
                self._opened_at = datetime.now(UTC)
                self._failure_count = 0
                self._stats.circuit_state = self._state
                self._stats.opened_at = self._opened_at

    def _transition_to_closed(self) -> None:
        """Transition to closed state."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            self._stats.circuit_state = self._state
            self._stats.closed_at = datetime.now(UTC)

    def can_execute(self) -> bool:
        """Check if a request can be executed.

        Returns:
            True if request can proceed.
        """
        with self._lock:
            state = self._get_state_unlocked()

            if state == CircuitState.CLOSED:
                return True

            if state == CircuitState.HALF_OPEN:
                return self._half_open_calls < self._config.half_open_max_calls

            return False

    def record_success(self, duration_ms: int = 0) -> None:
        """Record a successful call.

        Args:
            duration_ms: Call duration in milliseconds.
        """
        with self._lock:
            self._stats.total_calls += 1
            self._stats.successful_calls += 1
            self._stats.last_success = datetime.now(UTC)

            # Check for slow call
            if duration_ms >= self._config.slow_call_threshold_ms:
                self._stats.slow_calls += 1

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._config.success_threshold:
                    self._transition_to_closed()

            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0

    def record_failure(self, duration_ms: int = 0) -> None:
        """Record a failed call.

        Args:
            duration_ms: Call duration in milliseconds.
        """
        with self._lock:
            self._stats.total_calls += 1
            self._stats.failed_calls += 1
            self._stats.last_failure = datetime.now(UTC)
            self._last_failure_time = datetime.now(UTC)

            # Check for slow call
            if duration_ms >= self._config.slow_call_threshold_ms:
                self._stats.slow_calls += 1

            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open opens the circuit
                self._transition_to_open()

            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                self._success_count = 0

                # Check if we should open
                if self._should_open():
                    self._transition_to_open()

    def _should_open(self) -> bool:
        """Check if circuit should open based on failure count."""
        now = datetime.now(UTC)
        window_elapsed = (now - self._window_start).total_seconds()

        # Reset window if expired
        if window_elapsed >= self._config.window_seconds:
            self._window_start = now
            self._stats.failure_count_in_window = 0

        self._stats.failure_count_in_window = self._failure_count

        return self._failure_count >= self._config.failure_threshold

    def record_rejection(self) -> None:
        """Record a rejected call."""
        with self._lock:
            self._stats.rejected_calls += 1

    def reset(self) -> None:
        """Reset the circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            self._opened_at = None
            self._last_failure_time = None
            self._window_start = datetime.now(UTC)

            # Reset stats
            self._stats = CircuitBreakerStats(
                provider_id=self._provider_id,
                circuit_state=self._state,
            )

    def increment_half_open_calls(self) -> None:
        """Increment half-open call counter."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        with self._lock:
            return {
                "provider_id": self._provider_id,
                "state": self._state.value,
                "config": {
                    "failure_threshold": self._config.failure_threshold,
                    "success_threshold": self._config.success_threshold,
                    "timeout_seconds": self._config.timeout_seconds,
                    "half_open_max_calls": self._config.half_open_max_calls,
                    "window_seconds": self._config.window_seconds,
                    "slow_call_threshold_ms": self._config.slow_call_threshold_ms,
                    "slow_call_percentage": self._config.slow_call_percentage,
                },
                "stats": self._stats.to_dict(),
            }


class CircuitBreakerRegistry:
    """Registry for managing circuit breakers."""

    def __init__(self):
        """Initialize circuit breaker registry."""
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()

    def get_or_create(
        self,
        provider_id: str,
        config: CircuitBreakerConfig | None = None,
    ) -> CircuitBreaker:
        """Get or create a circuit breaker.

        Args:
            provider_id: Provider identifier.
            config: Circuit breaker configuration.

        Returns:
            Circuit breaker instance.
        """
        with self._lock:
            if provider_id not in self._breakers:
                self._breakers[provider_id] = CircuitBreaker(provider_id, config)
            return self._breakers[provider_id]

    def get(self, provider_id: str) -> CircuitBreaker | None:
        """Get a circuit breaker.

        Args:
            provider_id: Provider identifier.

        Returns:
            Circuit breaker or None.
        """
        with self._lock:
            return self._breakers.get(provider_id)

    def remove(self, provider_id: str) -> bool:
        """Remove a circuit breaker.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if removed.
        """
        with self._lock:
            if provider_id in self._breakers:
                del self._breakers[provider_id]
                return True
            return False

    def reset_all(self) -> None:
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()

    def get_all_stats(self) -> dict[str, dict]:
        """Get statistics for all circuit breakers.

        Returns:
            Dictionary of provider_id -> stats.
        """
        with self._lock:
            return {
                provider_id: breaker.to_dict()
                for provider_id, breaker in self._breakers.items()
            }

    def __len__(self) -> int:
        """Get number of circuit breakers."""
        with self._lock:
            return len(self._breakers)

    def __contains__(self, provider_id: str) -> bool:
        """Check if circuit breaker exists."""
        with self._lock:
            return provider_id in self._breakers
