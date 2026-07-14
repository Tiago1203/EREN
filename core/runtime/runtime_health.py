"""Runtime health system for the Cognitive Operating System.

Provides health checks and status reporting for all runtime components,
including the container, event bus, capability registry, and all engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(str, Enum):
    """Types of components that can be health-checked."""

    CONTAINER = "container"
    EVENT_BUS = "event_bus"
    CAPABILITY_REGISTRY = "capability_registry"
    BOOT_MANAGER = "boot_manager"
    SESSION_MANAGER = "session_manager"
    LIFECYCLE_MANAGER = "lifecycle_manager"
    ORCHESTRATOR = "orchestrator"
    SCHEDULER = "scheduler"
    PLANNER = "planner"
    KNOWLEDGE_ENGINE = "knowledge_engine"
    MEMORY_ENGINE = "memory_engine"
    REASONING_ENGINE = "reasoning_engine"
    DECISION_ENGINE = "decision_engine"
    TOOL_ENGINE = "tool_engine"
    COGNITIVE_CONTEXT = "cognitive_context"


@dataclass
class ComponentHealth:
    """Health status of a single component."""

    component_type: ComponentType
    component_name: str
    status: HealthStatus
    message: str = ""
    last_check: str = ""
    response_time_ms: int = 0
    details: dict[str, Any] = field(default_factory=dict)
    is_critical: bool = False

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.last_check:
            self.last_check = datetime.now(UTC).isoformat()

    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == HealthStatus.HEALTHY

    def is_degraded(self) -> bool:
        """Check if component is degraded."""
        return self.status == HealthStatus.DEGRADED

    def is_unhealthy(self) -> bool:
        """Check if component is unhealthy."""
        return self.status == HealthStatus.UNHEALTHY

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component_type": self.component_type.value,
            "component_name": self.component_name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check,
            "response_time_ms": self.response_time_ms,
            "details": self.details,
            "is_critical": self.is_critical,
        }


@dataclass
class RuntimeHealth:
    """Complete health status of the Cognitive Runtime.

    Provides an overview of all components and determines
    the overall runtime health status.
    """

    runtime_id: str
    timestamp: str = ""
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    components: dict[str, ComponentHealth] = field(default_factory=dict)
    summary: dict[str, int] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize timestamp and summary."""
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()
        if not self.summary:
            self._update_summary()

    def add_component(self, health: ComponentHealth) -> None:
        """Add a component health check result.

        Args:
            health: The component health status.
        """
        self.components[health.component_type.value] = health
        self._update_summary()
        self._update_overall_status()

    def get_component(self, component_type: ComponentType) -> ComponentHealth | None:
        """Get health status for a specific component.

        Args:
            component_type: The component type.

        Returns:
            The component health or None.
        """
        return self.components.get(component_type.value)

    def get_critical_components(self) -> list[ComponentHealth]:
        """Get all critical components that are unhealthy.

        Returns:
            List of critical unhealthy components.
        """
        return [
            c for c in self.components.values()
            if c.is_critical and c.status != HealthStatus.HEALTHY
        ]

    def is_ready(self) -> bool:
        """Check if runtime is ready to serve requests.

        Returns:
            True if runtime is healthy and ready.
        """
        return self.overall_status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)

    def _update_summary(self) -> None:
        """Update the health summary."""
        self.summary = {
            "total": len(self.components),
            "healthy": sum(1 for c in self.components.values() if c.is_healthy()),
            "degraded": sum(1 for c in self.components.values() if c.is_degraded()),
            "unhealthy": sum(1 for c in self.components.values() if c.is_unhealthy()),
            "unknown": sum(1 for c in self.components.values()
                          if c.status == HealthStatus.UNKNOWN),
            "critical_unhealthy": len(self.get_critical_components()),
        }

    def _update_overall_status(self) -> None:
        """Update the overall runtime health status."""
        # Check for critical unhealthy components
        critical = self.get_critical_components()
        if critical:
            self.overall_status = HealthStatus.UNHEALTHY
            self._generate_recommendations()
            return

        # Check for any unhealthy components
        unhealthy = sum(1 for c in self.components.values() if c.is_unhealthy())
        if unhealthy > 0:
            self.overall_status = HealthStatus.UNHEALTHY
            self._generate_recommendations()
            return

        # Check for degraded components
        degraded = sum(1 for c in self.components.values() if c.is_degraded())
        if degraded > 0:
            self.overall_status = HealthStatus.DEGRADED
            self._generate_recommendations()
            return

        # All components are healthy
        if len(self.components) > 0:
            self.overall_status = HealthStatus.HEALTHY
        else:
            self.overall_status = HealthStatus.UNKNOWN

        self.recommendations.clear()

    def _generate_recommendations(self) -> None:
        """Generate health recommendations."""
        self.recommendations.clear()

        for component in self.components.values():
            if component.status == HealthStatus.UNHEALTHY:
                if component.is_critical:
                    self.recommendations.append(
                        f"CRITICAL: {component.component_name} is unhealthy. "
                        f"Action required: {component.message}"
                    )
                else:
                    self.recommendations.append(
                        f"{component.component_name} is unhealthy: {component.message}"
                    )
            elif component.status == HealthStatus.DEGRADED:
                self.recommendations.append(
                    f"{component.component_name} is degraded: {component.message}"
                )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "runtime_id": self.runtime_id,
            "timestamp": self.timestamp,
            "overall_status": self.overall_status.value,
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "summary": self.summary,
            "recommendations": self.recommendations,
            "is_ready": self.is_ready(),
        }


class RuntimeHealthChecker:
    """Performs health checks on runtime components.

    Validates that all required components are available and functioning
    before allowing the runtime to start.
    """

    def __init__(self, runtime_id: str):
        """Initialize the health checker.

        Args:
            runtime_id: The runtime instance ID.
        """
        self._runtime_id = runtime_id
        self._runtime_health = RuntimeHealth(runtime_id=runtime_id)

    @property
    def health(self) -> RuntimeHealth:
        """Get the current health status."""
        return self._runtime_health

    def check_all(
        self,
        container=None,
        event_bus=None,
        capability_registry=None,
        boot_manager=None,
        session_manager=None,
        lifecycle_manager=None,
        orchestrator=None,
        scheduler=None,
        planner=None,
        knowledge_engine=None,
        memory_engine=None,
        reasoning_engine=None,
        decision_engine=None,
        tool_engine=None,
    ) -> RuntimeHealth:
        """Perform health checks on all components.

        Args:
            container: DI Container instance.
            event_bus: Event Bus instance.
            capability_registry: Capability Registry instance.
            boot_manager: Boot Manager instance.
            session_manager: Session Manager instance.
            lifecycle_manager: Lifecycle Manager instance.
            orchestrator: Orchestrator instance.
            scheduler: Scheduler instance.
            planner: Planner instance.
            knowledge_engine: Knowledge Engine instance.
            memory_engine: Memory Engine instance.
            reasoning_engine: Reasoning Engine instance.
            decision_engine: Decision Engine instance.
            tool_engine: Tool Engine instance.

        Returns:
            Complete health status.
        """
        # Reset health
        self._runtime_health = RuntimeHealth(runtime_id=self._runtime_id)

        # Check each component
        self._check_container(container)
        self._check_event_bus(event_bus)
        self._check_capability_registry(capability_registry)
        self._check_boot_manager(boot_manager)
        self._check_session_manager(session_manager)
        self._check_lifecycle_manager(lifecycle_manager)
        self._check_orchestrator(orchestrator)
        self._check_scheduler(scheduler)
        self._check_planner(planner)
        self._check_knowledge_engine(knowledge_engine)
        self._check_memory_engine(memory_engine)
        self._check_reasoning_engine(reasoning_engine)
        self._check_decision_engine(decision_engine)
        self._check_tool_engine(tool_engine)

        return self._runtime_health

    def _check_container(self, container) -> None:
        """Check the DI Container."""
        start = datetime.now(UTC)

        if container is None:
            health = ComponentHealth(
                component_type=ComponentType.CONTAINER,
                component_name="DI Container",
                status=HealthStatus.UNHEALTHY,
                message="Container not available",
                is_critical=True,
            )
        elif getattr(container, 'is_disposed', False):
            health = ComponentHealth(
                component_type=ComponentType.CONTAINER,
                component_name="DI Container",
                status=HealthStatus.UNHEALTHY,
                message="Container is disposed",
                is_critical=True,
            )
        else:
            response_time = int((datetime.now(UTC) - start).total_seconds() * 1000)
            health = ComponentHealth(
                component_type=ComponentType.CONTAINER,
                component_name="DI Container",
                status=HealthStatus.HEALTHY,
                message="Container is ready",
                response_time_ms=response_time,
                details={"container_id": getattr(container, 'id', 'unknown')},
            )

        self._runtime_health.add_component(health)

    def _check_event_bus(self, event_bus) -> None:
        """Check the Event Bus."""
        start = datetime.now(UTC)

        if event_bus is None:
            health = ComponentHealth(
                component_type=ComponentType.EVENT_BUS,
                component_name="Event Bus",
                status=HealthStatus.UNHEALTHY,
                message="Event Bus not available",
                is_critical=True,
            )
        else:
            subscriber_count = getattr(event_bus, 'get_subscriber_count', lambda: 0)()
            response_time = int((datetime.now(UTC) - start).total_seconds() * 1000)
            health = ComponentHealth(
                component_type=ComponentType.EVENT_BUS,
                component_name="Event Bus",
                status=HealthStatus.HEALTHY,
                message="Event Bus is active",
                response_time_ms=response_time,
                details={"subscriber_count": subscriber_count},
            )

        self._runtime_health.add_component(health)

    def _check_capability_registry(self, registry) -> None:
        """Check the Capability Registry."""
        if registry is None:
            health = ComponentHealth(
                component_type=ComponentType.CAPABILITY_REGISTRY,
                component_name="Capability Registry",
                status=HealthStatus.UNHEALTHY,
                message="Capability Registry not available",
                is_critical=True,
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.CAPABILITY_REGISTRY,
                component_name="Capability Registry",
                status=HealthStatus.HEALTHY,
                message="Capability Registry is active",
                details={"registered": getattr(registry, 'count', lambda: 0)()},
            )

        self._runtime_health.add_component(health)

    def _check_boot_manager(self, boot_manager) -> None:
        """Check the Boot Manager."""
        if boot_manager is None:
            health = ComponentHealth(
                component_type=ComponentType.BOOT_MANAGER,
                component_name="Boot Manager",
                status=HealthStatus.UNHEALTHY,
                message="Boot Manager not available",
                is_critical=True,
            )
        else:
            state = getattr(boot_manager, 'state', 'unknown')
            is_ready = state == 'ready'
            health = ComponentHealth(
                component_type=ComponentType.BOOT_MANAGER,
                component_name="Boot Manager",
                status=HealthStatus.HEALTHY if is_ready else HealthStatus.DEGRADED,
                message=f"Boot Manager state: {state}",
                details={"state": state},
            )

        self._runtime_health.add_component(health)

    def _check_session_manager(self, manager) -> None:
        """Check the Session Manager."""
        if manager is None:
            health = ComponentHealth(
                component_type=ComponentType.SESSION_MANAGER,
                component_name="Session Manager",
                status=HealthStatus.UNHEALTHY,
                message="Session Manager not available",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.SESSION_MANAGER,
                component_name="Session Manager",
                status=HealthStatus.HEALTHY,
                message="Session Manager is ready",
                details={"sessions": len(getattr(manager, '_sessions', {}))},
            )

        self._runtime_health.add_component(health)

    def _check_lifecycle_manager(self, manager) -> None:
        """Check the Lifecycle Manager."""
        if manager is None:
            health = ComponentHealth(
                component_type=ComponentType.LIFECYCLE_MANAGER,
                component_name="Lifecycle Manager",
                status=HealthStatus.UNHEALTHY,
                message="Lifecycle Manager not available",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.LIFECYCLE_MANAGER,
                component_name="Lifecycle Manager",
                status=HealthStatus.HEALTHY,
                message="Lifecycle Manager is ready",
            )

        self._runtime_health.add_component(health)

    def _check_orchestrator(self, orchestrator) -> None:
        """Check the Orchestrator."""
        if orchestrator is None:
            health = ComponentHealth(
                component_type=ComponentType.ORCHESTRATOR,
                component_name="Cognitive Orchestrator",
                status=HealthStatus.UNHEALTHY,
                message="Orchestrator not available",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.ORCHESTRATOR,
                component_name="Cognitive Orchestrator",
                status=HealthStatus.HEALTHY,
                message="Orchestrator is ready",
            )

        self._runtime_health.add_component(health)

    def _check_scheduler(self, scheduler) -> None:
        """Check the Scheduler."""
        if scheduler is None:
            health = ComponentHealth(
                component_type=ComponentType.SCHEDULER,
                component_name="Cognitive Scheduler",
                status=HealthStatus.UNHEALTHY,
                message="Scheduler not available",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.SCHEDULER,
                component_name="Cognitive Scheduler",
                status=HealthStatus.HEALTHY,
                message="Scheduler is ready",
            )

        self._runtime_health.add_component(health)

    def _check_planner(self, planner) -> None:
        """Check the Planner."""
        if planner is None:
            health = ComponentHealth(
                component_type=ComponentType.PLANNER,
                component_name="Planner Engine",
                status=HealthStatus.DEGRADED,
                message="Planner not available (simulation mode)",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.PLANNER,
                component_name="Planner Engine",
                status=HealthStatus.HEALTHY,
                message="Planner is ready",
            )

        self._runtime_health.add_component(health)

    def _check_knowledge_engine(self, engine) -> None:
        """Check the Knowledge Engine."""
        if engine is None:
            health = ComponentHealth(
                component_type=ComponentType.KNOWLEDGE_ENGINE,
                component_name="Knowledge Engine",
                status=HealthStatus.DEGRADED,
                message="Knowledge Engine not available (simulation mode)",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.KNOWLEDGE_ENGINE,
                component_name="Knowledge Engine",
                status=HealthStatus.HEALTHY,
                message="Knowledge Engine is ready",
            )

        self._runtime_health.add_component(health)

    def _check_memory_engine(self, engine) -> None:
        """Check the Memory Engine."""
        if engine is None:
            health = ComponentHealth(
                component_type=ComponentType.MEMORY_ENGINE,
                component_name="Memory Engine",
                status=HealthStatus.DEGRADED,
                message="Memory Engine not available (simulation mode)",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.MEMORY_ENGINE,
                component_name="Memory Engine",
                status=HealthStatus.HEALTHY,
                message="Memory Engine is ready",
            )

        self._runtime_health.add_component(health)

    def _check_reasoning_engine(self, engine) -> None:
        """Check the Reasoning Engine."""
        if engine is None:
            health = ComponentHealth(
                component_type=ComponentType.REASONING_ENGINE,
                component_name="Reasoning Engine",
                status=HealthStatus.DEGRADED,
                message="Reasoning Engine not available (simulation mode)",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.REASONING_ENGINE,
                component_name="Reasoning Engine",
                status=HealthStatus.HEALTHY,
                message="Reasoning Engine is ready",
            )

        self._runtime_health.add_component(health)

    def _check_decision_engine(self, engine) -> None:
        """Check the Decision Engine."""
        if engine is None:
            health = ComponentHealth(
                component_type=ComponentType.DECISION_ENGINE,
                component_name="Decision Engine",
                status=HealthStatus.DEGRADED,
                message="Decision Engine not available (simulation mode)",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.DECISION_ENGINE,
                component_name="Decision Engine",
                status=HealthStatus.HEALTHY,
                message="Decision Engine is ready",
            )

        self._runtime_health.add_component(health)

    def _check_tool_engine(self, engine) -> None:
        """Check the Tool Engine."""
        if engine is None:
            health = ComponentHealth(
                component_type=ComponentType.TOOL_ENGINE,
                component_name="Tool Engine",
                status=HealthStatus.DEGRADED,
                message="Tool Engine not available (simulation mode)",
            )
        else:
            health = ComponentHealth(
                component_type=ComponentType.TOOL_ENGINE,
                component_name="Tool Engine",
                status=HealthStatus.HEALTHY,
                message="Tool Engine is ready",
            )

        self._runtime_health.add_component(health)
