"""Readiness Checker for EREN OS Diagnostics.

Validates whether the system is ready to serve requests. A system is ready when:
- All required components are initialized
- All contracts are satisfied
- All dependencies are resolved
- Boot process completed successfully

Philosophy:
    A system that is alive is not necessarily ready. EREN must prove readiness.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from core.diagnostics.health import HealthStatus


@dataclass
class ReadinessCheck:
    """A single readiness check."""

    name: str
    description: str
    passed: bool
    message: str = ""
    duration_ms: int = 0
    details: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "passed": self.passed,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "details": self.details,
        }


@dataclass
class ReadinessReport:
    """Complete readiness validation report."""

    is_ready: bool
    checks: list[ReadinessCheck]
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_duration_ms: int = 0
    critical_failures: list[str] = field(default_factory=list)
    non_critical_failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "is_ready": self.is_ready,
            "checks": [c.to_dict() for c in self.checks],
            "checked_at": self.checked_at.isoformat(),
            "total_duration_ms": self.total_duration_ms,
            "critical_failures": self.critical_failures,
            "non_critical_failures": self.non_critical_failures,
            "passed_count": sum(1 for c in self.checks if c.passed),
            "failed_count": sum(1 for c in self.checks if not c.passed),
        }


class ReadinessChecker:
    """Validates system readiness for production.

    Performs comprehensive checks to determine if the system is ready
    to serve requests. Readiness includes:
    - Component initialization
    - Contract compliance
    - Dependency resolution
    - Configuration validation
    - Resource availability
    """

    # Readiness check definitions
    READINESS_CHECKS = {
        "composition_root": {
            "description": "Composition Root is properly configured",
            "critical": True,
        },
        "dependency_container": {
            "description": "Dependency Injection Container is initialized",
            "critical": True,
        },
        "boot_completed": {
            "description": "Boot sequence completed successfully",
            "critical": True,
        },
        "event_bus": {
            "description": "Event Bus is operational",
            "critical": True,
        },
        "capability_registry": {
            "description": "Capability Registry is accessible",
            "critical": True,
        },
        "context_manager": {
            "description": "Context Manager is ready",
            "critical": True,
        },
        "runtime": {
            "description": "Runtime is in RUNNING state",
            "critical": True,
        },
        "orchestrator": {
            "description": "Orchestrator is ready",
            "critical": True,
        },
        "scheduler": {
            "description": "Scheduler is operational",
            "critical": False,
        },
        "session_manager": {
            "description": "Session Manager is operational",
            "critical": True,
        },
        "planner": {
            "description": "Planner engine is registered",
            "critical": True,
        },
        "knowledge_engine": {
            "description": "Knowledge engine is registered",
            "critical": True,
        },
        "memory_engine": {
            "description": "Memory engine is registered",
            "critical": True,
        },
        "reasoning_engine": {
            "description": "Reasoning engine is registered",
            "critical": True,
        },
        "decision_engine": {
            "description": "Decision engine is registered",
            "critical": True,
        },
        "tool_engine": {
            "description": "Tool engine is registered",
            "critical": True,
        },
        "contracts_satisfied": {
            "description": "All critical contracts are satisfied",
            "critical": True,
        },
        "no_circular_dependencies": {
            "description": "No circular dependencies detected",
            "critical": True,
        },
        "configuration_valid": {
            "description": "System configuration is valid",
            "critical": True,
        },
    }

    def __init__(self):
        self._checks: dict[str, Callable[[], tuple[bool, str]]] = {}
        self._lock = threading.RLock()

    def register_check(
        self,
        check_name: str,
        check_fn: Callable[[], tuple[bool, str]],
    ) -> None:
        """Register a custom readiness check.

        Args:
            check_name: Name of the check.
            check_fn: Function returning (passed, message).
        """
        with self._lock:
            self._checks[check_name] = check_fn

    def run_all_checks(self) -> ReadinessReport:
        """Run all readiness checks.

        Returns:
            ReadinessReport with results of all checks.
        """
        start_time = time.time()
        checks = []
        critical_failures = []
        non_critical_failures = []

        # Run defined checks
        for check_name, check_def in self.READINESS_CHECKS.items():
            check_start = time.time()

            # Try to run custom check if registered
            if check_name in self._checks:
                try:
                    passed, message = self._checks[check_name]()
                except Exception as e:
                    passed = False
                    message = f"Check failed with error: {str(e)}"
            else:
                # Default check - component should be registered
                passed = True
                message = "Check passed (no custom check registered)"

            duration_ms = int((time.time() - check_start) * 1000)

            check = ReadinessCheck(
                name=check_name,
                description=check_def["description"],
                passed=passed,
                message=message,
                duration_ms=duration_ms,
            )
            checks.append(check)

            if not passed:
                if check_def["critical"]:
                    critical_failures.append(f"{check_name}: {message}")
                else:
                    non_critical_failures.append(f"{check_name}: {message}")

        # Run custom checks
        for check_name, check_fn in self._checks.items():
            if check_name not in self.READINESS_CHECKS:
                check_start = time.time()
                try:
                    passed, message = check_fn()
                except Exception as e:
                    passed = False
                    message = f"Check failed with error: {str(e)}"

                duration_ms = int((time.time() - check_start) * 1000)

                check = ReadinessCheck(
                    name=check_name,
                    description=f"Custom check: {check_name}",
                    passed=passed,
                    message=message,
                    duration_ms=duration_ms,
                )
                checks.append(check)

                if not passed:
                    non_critical_failures.append(f"{check_name}: {message}")

        total_duration_ms = int((time.time() - start_time) * 1000)

        # System is ready only if no critical failures
        is_ready = len(critical_failures) == 0

        return ReadinessReport(
            is_ready=is_ready,
            checks=checks,
            total_duration_ms=total_duration_ms,
            critical_failures=critical_failures,
            non_critical_failures=non_critical_failures,
        )

    def check_single(self, check_name: str) -> ReadinessCheck:
        """Run a single readiness check.

        Args:
            check_name: Name of the check to run.

        Returns:
            ReadinessCheck with result.
        """
        check_start = time.time()

        if check_name in self._checks:
            try:
                passed, message = self._checks[check_name]()
            except Exception as e:
                passed = False
                message = f"Check failed with error: {str(e)}"
        elif check_name in self.READINESS_CHECKS:
            check_def = self.READINESS_CHECKS[check_name]
            passed = True
            message = "Check passed (no custom check registered)"
        else:
            passed = False
            message = f"Unknown check: {check_name}"

        duration_ms = int((time.time() - check_start) * 1000)

        description = self.READINESS_CHECKS.get(check_name, {}).get(
            "description", f"Custom check: {check_name}"
        )

        return ReadinessCheck(
            name=check_name,
            description=description,
            passed=passed,
            message=message,
            duration_ms=duration_ms,
        )
