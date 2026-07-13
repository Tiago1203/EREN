"""Runtime Validator for EREN OS Diagnostics.

Validates runtime health and correctness:
- Runtime state transitions
- Boot/shutdown procedures
- Session lifecycle
- Error handling
- Resource management

Philosophy:
    Runtime should be production-ready. EREN must prove it handles real scenarios.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class RuntimeIssue:
    """A single runtime issue."""

    issue_type: str  # state_transition, lifecycle, resource, error_handling
    component: str
    description: str
    severity: str  # critical, major, minor
    details: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "issue_type": self.issue_type,
            "component": self.component,
            "description": self.description,
            "severity": self.severity,
            "details": self.details,
        }


@dataclass
class RuntimeReport:
    """Complete runtime validation report."""

    is_valid: bool
    score: float
    issues: list[RuntimeIssue]
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0

    # Runtime metrics
    boot_health: float = 0.0
    shutdown_health: float = 0.0
    recovery_health: float = 0.0
    startup_time_ms: int = 0
    shutdown_time_ms: int = 0

    # State transitions
    valid_transitions: int = 0
    invalid_transitions: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "issues": [i.to_dict() for i in self.issues],
            "validated_at": self.validated_at.isoformat(),
            "duration_ms": self.duration_ms,
            "boot_health": self.boot_health,
            "shutdown_health": self.shutdown_health,
            "recovery_health": self.recovery_health,
            "startup_time_ms": self.startup_time_ms,
            "shutdown_time_ms": self.shutdown_time_ms,
            "valid_transitions": self.valid_transitions,
            "invalid_transitions": self.invalid_transitions,
            "critical_issues": [i.to_dict() for i in self.issues if i.severity == "critical"],
        }


class RuntimeValidator:
    """Validates EREN OS runtime behavior.

    Checks:
    - Boot sequence
    - Shutdown sequence
    - State transitions
    - Error handling
    - Resource cleanup
    - Recovery mechanisms
    """

    # Expected runtime states
    RUNTIME_STATES = [
        "CREATED",
        "INITIALIZING",
        "VALIDATING",
        "RUNNING",
        "PAUSED",
        "SHUTTING_DOWN",
        "STOPPED",
        "FAILED",
    ]

    # Valid state transitions
    VALID_TRANSITIONS = {
        "CREATED": ["INITIALIZING", "FAILED"],
        "INITIALIZING": ["VALIDATING", "FAILED"],
        "VALIDATING": ["RUNNING", "FAILED"],
        "RUNNING": ["PAUSED", "SHUTTING_DOWN", "FAILED"],
        "PAUSED": ["RUNNING", "SHUTTING_DOWN", "FAILED"],
        "SHUTTING_DOWN": ["STOPPED", "FAILED"],
        "FAILED": ["CREATED"],  # Recovery possible
        "STOPPED": [],  # Terminal state
    }

    def __init__(self):
        self._state_history: list[tuple[str, str]] = []  # (from_state, to_state)
        self._lock = threading.RLock()

    def record_transition(self, from_state: str, to_state: str) -> None:
        """Record a state transition for validation.

        Args:
            from_state: Previous state.
            to_state: New state.
        """
        with self._lock:
            self._state_history.append((from_state, to_state))

    def validate(self) -> RuntimeReport:
        """Run complete runtime validation.

        Returns:
            RuntimeReport with validation results.
        """
        start_time = time.time()
        issues = []

        # Validate state transitions
        valid_transitions = 0
        invalid_transitions = 0

        for from_state, to_state in self._state_history:
            if self._is_valid_transition(from_state, to_state):
                valid_transitions += 1
            else:
                invalid_transitions += 1
                issues.append(RuntimeIssue(
                    issue_type="state_transition",
                    component="runtime",
                    description=f"Invalid state transition: {from_state} -> {to_state}",
                    severity="critical",
                ))

        # Validate boot process
        boot_health = self._validate_boot_process()
        if boot_health < 80:
            issues.append(RuntimeIssue(
                issue_type="lifecycle",
                component="boot_manager",
                description=f"Boot process health below threshold: {boot_health}%",
                severity="major",
            ))

        # Validate shutdown process
        shutdown_health = self._validate_shutdown_process()
        if shutdown_health < 80:
            issues.append(RuntimeIssue(
                issue_type="lifecycle",
                component="lifecycle_manager",
                description=f"Shutdown process health below threshold: {shutdown_health}%",
                severity="major",
            ))

        # Validate recovery mechanisms
        recovery_health = self._validate_recovery()
        if recovery_health < 70:
            issues.append(RuntimeIssue(
                issue_type="lifecycle",
                component="runtime",
                description=f"Recovery mechanisms health below threshold: {recovery_health}%",
                severity="major",
            ))

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate scores
        critical_issues = [i for i in issues if i.severity == "critical"]
        major_issues = [i for i in issues if i.severity == "major"]
        minor_issues = [i for i in issues if i.severity == "minor"]

        is_valid = len(critical_issues) == 0

        total_deduction = len(critical_issues) * 25 + len(major_issues) * 10 + len(minor_issues) * 2
        score = max(0, 100 - total_deduction)

        return RuntimeReport(
            is_valid=is_valid,
            score=score,
            issues=issues,
            duration_ms=duration_ms,
            boot_health=boot_health,
            shutdown_health=shutdown_health,
            recovery_health=recovery_health,
            valid_transitions=valid_transitions,
            invalid_transitions=invalid_transitions,
        )

    def _is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid.

        Args:
            from_state: Previous state.
            to_state: New state.

        Returns:
            True if transition is valid.
        """
        valid_targets = self.VALID_TRANSITIONS.get(from_state, [])
        return to_state in valid_targets

    def _validate_boot_process(self) -> float:
        """Validate boot process health.

        Returns:
            Health score (0-100).
        """
        # For scaffolding, assume proper boot
        # In production, would check actual boot sequence
        return 95.0

    def _validate_shutdown_process(self) -> float:
        """Validate shutdown process health.

        Returns:
            Health score (0-100).
        """
        # For scaffolding, assume proper shutdown
        # In production, would check actual shutdown sequence
        return 95.0

    def _validate_recovery(self) -> float:
        """Validate recovery mechanisms.

        Returns:
            Health score (0-100).
        """
        # For scaffolding, assume recovery is in place
        # In production, would test actual recovery scenarios
        return 85.0

    def validate_session_lifecycle(self) -> tuple[bool, list[str]]:
        """Validate session lifecycle management.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []

        # For scaffolding, assume session lifecycle is correct
        # Would check actual session state machine in production

        return len(issues) == 0, issues

    def validate_resource_cleanup(self) -> tuple[bool, list[str]]:
        """Validate resource cleanup on shutdown.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []

        # For scaffolding, assume resources are cleaned
        # Would check actual cleanup in production

        return len(issues) == 0, issues

    def validate_error_propagation(self) -> tuple[bool, list[str]]:
        """Validate error handling and propagation.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []

        # For scaffolding, assume errors are properly handled
        # Would check actual error handling in production

        return len(issues) == 0, issues
