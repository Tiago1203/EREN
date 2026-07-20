"""Execution Validator for EREN OS Cognitive Execution Coordinator.

Validates that all required components are available before execution.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from core.execution.types import ComponentStatus, ValidationResult

if TYPE_CHECKING:
    pass


class ExecutionValidator:
    """Validates execution prerequisites.

    Checks that all required components are available and healthy
    before starting an execution cycle.
    """

    def __init__(self):
        """Initialize the validator."""
        self._component_checkers: dict[str, Callable[[], ComponentStatus]] = {}

    def register_checker(
        self,
        component_name: str,
        checker: Callable[[], ComponentStatus],
    ) -> None:
        """Register a component checker.

        Args:
            component_name: Name of the component.
            checker: Function that returns ComponentStatus.
        """
        self._component_checkers[component_name] = checker

    def validate(self) -> ValidationResult:
        """Validate all registered components.

        Returns:
            ValidationResult with validation status.
        """
        result = ValidationResult(is_valid=True)
        result.component_statuses = []

        for name, checker in self._component_checkers.items():
            try:
                status = checker()
                result.component_statuses.append(status)

                if not status.available:
                    result.is_valid = False
                    result.errors.append(f"Component '{name}' is not available")
                elif not status.healthy:
                    result.warnings.append(f"Component '{name}' is not healthy: {status.error}")

            except Exception as e:
                result.is_valid = False
                status = ComponentStatus(
                    name=name,
                    available=False,
                    healthy=False,
                    error=str(e),
                )
                result.component_statuses.append(status)
                result.errors.append(f"Component '{name}' check failed: {e}")

        return result

    def validate_components(
        self,
        components: list[str],
    ) -> ValidationResult:
        """Validate specific components.

        Args:
            components: List of component names to validate.

        Returns:
            ValidationResult with validation status.
        """
        result = ValidationResult(is_valid=True)
        result.component_statuses = []

        for name in components:
            if name not in self._component_checkers:
                result.is_valid = False
                result.errors.append(f"Component '{name}' has no registered checker")
                continue

            try:
                status = self._component_checkers[name]()
                result.component_statuses.append(status)

                if not status.available:
                    result.is_valid = False
                    result.errors.append(f"Component '{name}' is not available")

            except Exception as e:
                result.is_valid = False
                status = ComponentStatus(
                    name=name,
                    available=False,
                    healthy=False,
                    error=str(e),
                )
                result.component_statuses.append(status)
                result.errors.append(f"Component '{name}' check failed: {e}")

        return result

    def check_router_available(self) -> ComponentStatus:
        """Check if router is available."""
        from core.router import get_routing_registry

        try:
            registry = get_routing_registry()
            pipeline_count = registry.get_pipeline_count()

            return ComponentStatus(
                name="router",
                available=True,
                healthy=pipeline_count > 0,
                error="" if pipeline_count > 0 else "No pipelines registered",
            )
        except Exception as e:
            return ComponentStatus(
                name="router",
                available=False,
                healthy=False,
                error=str(e),
            )

    def check_pipeline_available(self) -> ComponentStatus:
        """Check if pipeline is available."""

        try:
            # Check if at least one pipeline type exists
            from core.pipeline.stage import PlanningStage
            stage = PlanningStage()

            return ComponentStatus(
                name="pipeline",
                available=True,
                healthy=True,
            )
        except Exception as e:
            return ComponentStatus(
                name="pipeline",
                available=False,
                healthy=False,
                error=str(e),
            )

    def check_session_manager_available(self) -> ComponentStatus:
        """Check if session manager is available."""
        try:
            from core.session import get_session_manager

            manager = get_session_manager()
            return ComponentStatus(
                name="session_manager",
                available=True,
                healthy=True,
            )
        except Exception:
            # Session manager might not be initialized yet
            return ComponentStatus(
                name="session_manager",
                available=False,
                healthy=False,
                error="Session manager not initialized",
            )

    def check_event_bus_available(self) -> ComponentStatus:
        """Check if event bus is available."""
        try:
            from core.events import get_global_bus

            bus = get_global_bus()
            return ComponentStatus(
                name="event_bus",
                available=True,
                healthy=True,
            )
        except Exception:
            return ComponentStatus(
                name="event_bus",
                available=False,
                healthy=False,
                error="Event bus not available",
            )

    def register_default_checkers(self) -> None:
        """Register default component checkers."""
        self.register_checker("router", self.check_router_available)
        self.register_checker("pipeline", self.check_pipeline_available)
        self.register_checker("session_manager", self.check_session_manager_available)
        self.register_checker("event_bus", self.check_event_bus_available)
