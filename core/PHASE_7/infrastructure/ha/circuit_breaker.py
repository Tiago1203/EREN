"""
PHASE 7 - EPIC 3: Circuit Breaker

Resilience pattern para evitar cascading failures:
- States: CLOSED, OPEN, HALF_OPEN
- Failure threshold
- Recovery timeout
- Integration con EPIC 2 (multi-tenant)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Callable, Optional
import threading
import time


class CircuitState(str, Enum):
    """Estados del circuit breaker."""
    CLOSED = "closed"         # Normal operation
    OPEN = "open"            # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker."""
    failure_threshold: int = 5        # Failures before opening
    success_threshold: int = 3        # Successes in half-open before closing
    timeout: int = 60                 # Seconds before trying half-open
    half_open_max_calls: int = 3     # Max calls in half-open state


@dataclass
class CircuitBreakerStats:
    """Estadísticas del circuit breaker."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_transitions: list = field(default_factory=list)


class CircuitBreakerOpenError(Exception):
    """Circuit breaker está abierto."""
    def __init__(self, circuit_name: str, retry_after: int):
        self.circuit_name = circuit_name
        self.retry_after = retry_after
        super().__init__(f"Circuit '{circuit_name}' is OPEN. Retry after {retry_after}s")


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        self._name = name
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
        self._lock = threading.Lock()
        self._stats = CircuitBreakerStats()

    @property
    def state(self) -> CircuitState:
        """Obtiene estado actual (recalcula si necesario)."""
        with self._lock:
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    def _should_attempt_reset(self) -> bool:
        """Check si debe intentar resetear."""
        if self._last_failure_time:
            elapsed = (datetime.now(timezone.utc) - self._last_failure_time).total_seconds()
            return elapsed >= self._config.timeout
        return False

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transición de estado."""
        old_state = self._state
        self._state = new_state
        self._stats.state_transitions.append({
            "from": old_state.value,
            "to": new_state.value,
            "at": datetime.now(timezone.utc).isoformat(),
        })

        if new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        elif new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0

    def record_success(self) -> None:
        """Registra una llamada exitosa."""
        with self._lock:
            self._stats.successful_calls += 1
            self._stats.total_calls += 1

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self) -> None:
        """Registra una llamada fallida."""
        with self._lock:
            self._stats.failed_calls += 1
            self._stats.total_calls += 1
            self._failure_count += 1
            self._last_failure_time = datetime.now(timezone.utc)

            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self._config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def allow_request(self) -> bool:
        """Check si permite una nueva request."""
        state = self.state  # This may trigger state transition

        with self._lock:
            if state == CircuitState.CLOSED:
                return True
            elif state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self._config.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            else:  # OPEN
                self._stats.rejected_calls += 1
                return False

    def call(self, func: Callable, *args, **kwargs):
        """Ejecuta función con circuit breaker."""
        if not self.allow_request():
            retry_after = self._config.timeout
            if self._last_failure_time:
                elapsed = (datetime.now(timezone.utc) - self._last_failure_time).total_seconds()
                retry_after = max(0, self._config.timeout - int(elapsed))
            raise CircuitBreakerOpenError(self._name, retry_after)

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise

    def get_stats(self) -> dict:
        """Obtiene estadísticas."""
        with self._lock:
            return {
                "name": self._name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "total_calls": self._stats.total_calls,
                "successful_calls": self._stats.successful_calls,
                "failed_calls": self._stats.failed_calls,
                "rejected_calls": self._stats.rejected_calls,
                "last_failure": self._last_failure_time.isoformat() if self._last_failure_time else None,
                "recent_transitions": self._stats.state_transitions[-5:],
            }

    def reset(self) -> None:
        """Resetea el circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            self._last_failure_time = None


# Circuit breaker registry for multiple services

class CircuitBreakerRegistry:
    """Registry de circuit breakers por servicio."""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """Obtiene o crea un circuit breaker."""
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
            return self._breakers[name]

    def get_all_stats(self) -> dict:
        """Obtiene estadísticas de todos los breakers."""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }
