"""System Health Module for EREN OS Diagnostics.

Provides comprehensive health status reporting for all kernel components.
Health status follows a four-tier system: HEALTHY, DEGRADED, UNHEALTHY, FAILED.

Philosophy:
    Every component must report its health status. No component should assume
    another component is healthy.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class HealthStatus(str, Enum):
    """Health status levels for components.

    Components should report their true status, not an optimistic one.
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"

    @classmethod
    def from_score(cls, score: float) -> HealthStatus:
        """Determine health status from a numeric score (0-100).

        Args:
            score: Health score from 0 to 100.

        Returns:
            Corresponding HealthStatus.
        """
        if score >= 90:
            return cls.HEALTHY
        elif score >= 70:
            return cls.DEGRADED
        elif score >= 40:
            return cls.UNHEALTHY
        else:
            return cls.FAILED


class ComponentHealth:
    """Health status for a single component."""

    def __init__(
        self,
        component_name: str,
        status: HealthStatus,
        message: str = "",
        details: dict | None = None,
    ):
        self.component_name = component_name
        self.status = status
        self.message = message
        self.details = details or {}
        self.checked_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "component_name": self.component_name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""

    overall_status: HealthStatus
    overall_score: float
    component_checks: list[ComponentHealth]
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_ms: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """Check if overall status is healthy."""
        return self.overall_status == HealthStatus.HEALTHY

    @property
    def is_production_ready(self) -> bool:
        """Check if system is production ready.

        System is production ready if status is HEALTHY or DEGRADED
        with score >= 80.
        """
        return self.overall_status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED) and self.overall_score >= 80

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "overall_status": self.overall_status.value,
            "overall_score": self.overall_score,
            "component_checks": [c.to_dict() for c in self.component_checks],
            "checked_at": self.checked_at.isoformat(),
            "duration_ms": self.duration_ms,
            "errors": self.errors,
            "warnings": self.warnings,
            "is_healthy": self.is_healthy,
            "is_production_ready": self.is_production_ready,
        }


class SystemHealth:
    """Central health status aggregator for EREN OS.

    Collects and aggregates health status from all kernel components.
    Thread-safe for concurrent access.
    """

    # Core components that must be checked
    REQUIRED_COMPONENTS = {
        "composition_root",
        "dependency_container",
        "boot_manager",
        "event_bus",
        "capability_registry",
        "context_manager",
        "blackboard",
        "runtime",
        "orchestrator",
        "scheduler",
        "session_manager",
        "lifecycle_manager",
        "planner",
        "knowledge_engine",
        "memory_engine",
        "tool_engine",
        "reasoning_engine",
        "decision_engine",
    }

    def __init__(self):
        self._component_health: dict[str, ComponentHealth] = {}
        self._lock = threading.RLock()
        self._last_full_check: datetime | None = None
        self._check_count = 0

    def register_component_health(
        self,
        component_name: str,
        status: HealthStatus,
        message: str = "",
        details: dict | None = None,
    ) -> None:
        """Register health status for a component.

        Args:
            component_name: Name of the component.
            status: Current health status.
            message: Optional status message.
            details: Optional additional details.
        """
        with self._lock:
            self._component_health[component_name] = ComponentHealth(
                component_name=component_name,
                status=status,
                message=message,
                details=details,
            )

    def get_component_health(self, component_name: str) -> ComponentHealth | None:
        """Get health status for a specific component.

        Args:
            component_name: Name of the component.

        Returns:
            ComponentHealth if found, None otherwise.
        """
        with self._lock:
            return self._component_health.get(component_name)

    def get_all_health(self) -> dict[str, ComponentHealth]:
        """Get health status for all registered components.

        Returns:
            Dictionary of component names to health status.
        """
        with self._lock:
            return dict(self._component_health)

    def get_overall_status(self) -> tuple[HealthStatus, float]:
        """Calculate overall system health status.

        Returns:
            Tuple of (overall_status, overall_score).
        """
        with self._lock:
            if not self._component_health:
                return HealthStatus.FAILED, 0.0

            # Calculate score based on component statuses
            status_scores = {
                HealthStatus.HEALTHY: 100,
                HealthStatus.DEGRADED: 70,
                HealthStatus.UNHEALTHY: 40,
                HealthStatus.FAILED: 0,
            }

            total_score = 0
            max_score = 0
            failed_count = 0
            unhealthy_count = 0
            degraded_count = 0

            for component, health in self._component_health.items():
                score = status_scores.get(health.status, 0)
                total_score += score
                max_score += 100

                if health.status == HealthStatus.FAILED:
                    failed_count += 1
                elif health.status == HealthStatus.UNHEALTHY:
                    unhealthy_count += 1
                elif health.status == HealthStatus.DEGRADED:
                    degraded_count += 1

            overall_score = (total_score / max_score * 100) if max_score > 0 else 0

            # Determine overall status
            if failed_count > 0:
                overall_status = HealthStatus.FAILED
            elif unhealthy_count > len(self._component_health) * 0.3:
                overall_status = HealthStatus.UNHEALTHY
            elif degraded_count > len(self._component_health) * 0.5:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.from_score(overall_score)

            return overall_status, overall_score

    def check_all_components(self) -> HealthCheckResult:
        """Perform a full health check of all required components.

        Returns:
            HealthCheckResult with complete system health status.
        """
        import time
        start_time = time.time()

        with self._lock:
            component_checks = []
            errors = []
            warnings = []
            missing_components = set(self.REQUIRED_COMPONENTS) - set(self._component_health.keys())

            # Check registered components
            for component_name, health in self._component_health.items():
                component_checks.append(health)
                if health.status == HealthStatus.FAILED:
                    errors.append(f"{component_name}: {health.message or 'FAILED'}")
                elif health.status == HealthStatus.UNHEALTHY:
                    warnings.append(f"{component_name}: {health.message or 'UNHEALTHY'}")

            # Report missing components
            for component in missing_components:
                component_checks.append(ComponentHealth(
                    component_name=component,
                    status=HealthStatus.FAILED,
                    message="Component not registered for health checks",
                ))
                errors.append(f"{component}: Component not found")

            overall_status, overall_score = self.get_overall_status()

            self._last_full_check = datetime.now(UTC)
            self._check_count += 1

            duration_ms = int((time.time() - start_time) * 1000)

            return HealthCheckResult(
                overall_status=overall_status,
                overall_score=overall_score,
                component_checks=component_checks,
                duration_ms=duration_ms,
                errors=errors,
                warnings=warnings,
            )

    def get_statistics(self) -> dict:
        """Get health statistics.

        Returns:
            Dictionary with health statistics.
        """
        with self._lock:
            status_counts = {
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "failed": 0,
            }

            for health in self._component_health.values():
                status_counts[health.status.value] += 1

            overall_status, overall_score = self.get_overall_status()

            return {
                "total_components": len(self._component_health),
                "required_components": len(self.REQUIRED_COMPONENTS),
                "missing_components": list(set(self.REQUIRED_COMPONENTS) - set(self._component_health.keys())),
                "status_counts": status_counts,
                "overall_status": overall_status.value,
                "overall_score": overall_score,
                "last_full_check": self._last_full_check.isoformat() if self._last_full_check else None,
                "check_count": self._check_count,
            }
