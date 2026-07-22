"""Liveness Checker for EREN OS Diagnostics.

Validates whether the system is alive and responsive. A system is live when:
- It can respond to requests within acceptable time
- Critical processes are running
- Deadlocks are not present
- Resources are not exhausted

Philosophy:
    Liveness is not just "not dead". EREN must prove it is responsive.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class LivenessCheck:
    """A single liveness check."""

    name: str
    description: str
    passed: bool
    response_time_ms: int = 0
    message: str = ""
    details: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "passed": self.passed,
            "response_time_ms": self.response_time_ms,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class LivenessReport:
    """Complete liveness validation report."""

    is_alive: bool
    checks: list[LivenessCheck]
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    total_duration_ms: int = 0
    average_response_time_ms: int = 0
    timeout_failures: list[str] = field(default_factory=list)
    slow_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "is_alive": self.is_alive,
            "checks": [c.to_dict() for c in self.checks],
            "checked_at": self.checked_at.isoformat(),
            "total_duration_ms": self.total_duration_ms,
            "average_response_time_ms": self.average_response_time_ms,
            "timeout_failures": self.timeout_failures,
            "slow_checks": self.slow_checks,
            "passed_count": sum(1 for c in self.checks if c.passed),
            "failed_count": sum(1 for c in self.checks if not c.passed),
        }


class LivenessChecker:
    """Validates system liveness and responsiveness.

    Performs checks to determine if the system is alive and can
    respond to requests within acceptable time limits.

    Default thresholds:
    - Fast check: < 100ms
    - Normal check: < 500ms
    - Slow check: < 1000ms
    - Timeout: >= 1000ms
    """

    # Liveness check definitions with timeout thresholds (in ms)
    LIVENESS_CHECKS = {
        "event_bus_ping": {
            "description": "Event Bus responds to ping",
            "timeout_ms": 500,
            "threshold_ms": 100,
        },
        "container_resolve": {
            "description": "Container can resolve services",
            "timeout_ms": 500,
            "threshold_ms": 100,
        },
        "registry_query": {
            "description": "Registry can respond to queries",
            "timeout_ms": 500,
            "threshold_ms": 100,
        },
        "context_creation": {
            "description": "Context can be created",
            "timeout_ms": 500,
            "threshold_ms": 100,
        },
        "scheduler_availability": {
            "description": "Scheduler can schedule a task",
            "timeout_ms": 1000,
            "threshold_ms": 500,
        },
        "session_creation": {
            "description": "Session can be created",
            "timeout_ms": 500,
            "threshold_ms": 100,
        },
        "orchestrator_responsive": {
            "description": "Orchestrator is responsive",
            "timeout_ms": 1000,
            "threshold_ms": 500,
        },
        "no_deadlock_indicators": {
            "description": "No deadlock indicators detected",
            "timeout_ms": 500,
            "threshold_ms": 100,
        },
        "memory_available": {
            "description": "Memory resources available",
            "timeout_ms": 200,
            "threshold_ms": 50,
        },
        "threads_available": {
            "description": "Thread resources available",
            "timeout_ms": 200,
            "threshold_ms": 50,
        },
    }

    def __init__(self):
        self._checks: dict[str, Callable[[], tuple[bool, str, int]]] = {}
        self._lock = threading.RLock()
        self._default_timeout_ms = 5000

    def register_check(
        self,
        check_name: str,
        check_fn: Callable[[], tuple[bool, str, int]],
    ) -> None:
        """Register a custom liveness check.

        Args:
            check_name: Name of the check.
            check_fn: Function returning (passed, message, response_time_ms).
        """
        with self._lock:
            self._checks[check_name] = check_fn

    def run_all_checks(self, timeout_ms: int | None = None) -> LivenessReport:
        """Run all liveness checks.

        Args:
            timeout_ms: Optional global timeout override.

        Returns:
            LivenessReport with results of all checks.
        """
        start_time = time.time()
        checks = []
        timeout_failures = []
        slow_checks = []
        total_response_time = 0

        for check_name, check_def in self.LIVENESS_CHECKS.items():
            timeout = timeout_ms or check_def.get("timeout_ms", self._default_timeout_ms)
            threshold = check_def.get("threshold_ms", 100)

            check_start = time.time()

            # Try to run custom check if registered
            if check_name in self._checks:
                try:
                    passed, message, response_time = self._checks[check_name]()
                except Exception as e:
                    passed = False
                    message = f"Check failed: {e!s}"
                    response_time = int((time.time() - check_start) * 1000)
            else:
                # Default simulated check for scaffolding
                response_time = int((time.time() - check_start) * 1000)
                passed = True
                message = "Check passed (simulated for scaffolding)"

            # Check timeout
            if response_time >= timeout:
                passed = False
                timeout_failures.append(f"{check_name}: timed out after {response_time}ms")
                message = f"Timeout: {message}"

            # Check if slow
            if response_time >= threshold * 5:
                slow_checks.append(f"{check_name}: slow response ({response_time}ms)")

            total_response_time += response_time

            check = LivenessCheck(
                name=check_name,
                description=check_def["description"],
                passed=passed,
                response_time_ms=response_time,
                message=message,
            )
            checks.append(check)

        # Run custom checks
        for check_name, check_fn in self._checks.items():
            if check_name not in self.LIVENESS_CHECKS:
                check_start = time.time()
                try:
                    passed, message, response_time = check_fn()
                except Exception as e:
                    passed = False
                    message = f"Check failed: {e!s}"
                    response_time = int((time.time() - check_start) * 1000)

                if response_time >= self._default_timeout_ms:
                    timeout_failures.append(f"{check_name}: timed out")

                total_response_time += response_time

                check = LivenessCheck(
                    name=check_name,
                    description=f"Custom check: {check_name}",
                    passed=passed,
                    response_time_ms=response_time,
                    message=message,
                )
                checks.append(check)

        total_duration_ms = int((time.time() - start_time) * 1000)
        average_response_time = total_response_time // len(checks) if checks else 0

        # System is alive only if no timeout failures
        is_alive = len(timeout_failures) == 0

        return LivenessReport(
            is_alive=is_alive,
            checks=checks,
            total_duration_ms=total_duration_ms,
            average_response_time_ms=average_response_time,
            timeout_failures=timeout_failures,
            slow_checks=slow_checks,
        )

    def check_single(self, check_name: str) -> LivenessCheck:
        """Run a single liveness check.

        Args:
            check_name: Name of the check to run.

        Returns:
            LivenessCheck with result.
        """
        check_start = time.time()

        if check_name in self._checks:
            try:
                passed, message, response_time = self._checks[check_name]()
            except Exception as e:
                passed = False
                message = f"Check failed: {e!s}"
                response_time = int((time.time() - check_start) * 1000)
        elif check_name in self.LIVENESS_CHECKS:
            check_def = self.LIVENESS_CHECKS[check_name]
            response_time = int((time.time() - check_start) * 1000)
            passed = True
            message = "Check passed (simulated for scaffolding)"
        else:
            response_time = int((time.time() - check_start) * 1000)
            passed = False
            message = f"Unknown check: {check_name}"

        description = self.LIVENESS_CHECKS.get(check_name, {}).get(
            "description", f"Custom check: {check_name}"
        )

        return LivenessCheck(
            name=check_name,
            description=description,
            passed=passed,
            response_time_ms=response_time,
            message=message,
        )

    def set_default_timeout(self, timeout_ms: int) -> None:
        """Set the default timeout for checks.

        Args:
            timeout_ms: Default timeout in milliseconds.
        """
        self._default_timeout_ms = timeout_ms
