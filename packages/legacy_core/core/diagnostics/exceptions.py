"""Diagnostic exceptions for EREN OS diagnostics system.

Defines all exceptions that can be raised during diagnostics operations.
Following EREN's philosophy: diagnostics should be comprehensive and report all issues.
"""

from __future__ import annotations


class DiagnosticsException(Exception):
    """Base exception for all diagnostics errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DiagnosticsInitializationError(DiagnosticsException):
    """Raised when diagnostics engine fails to initialize."""
    pass


class ValidationError(DiagnosticsException):
    """Raised when a validation check fails."""

    def __init__(self, message: str, component: str = "", validation_type: str = ""):
        super().__init__(message, {
            "component": component,
            "validation_type": validation_type,
        })
        self.component = component
        self.validation_type = validation_type


class ArchitectureError(ValidationError):
    """Raised when architecture validation fails."""
    pass


class ContractViolationError(ValidationError):
    """Raised when a contract is violated."""
    pass


class DependencyError(DiagnosticsException):
    """Raised when dependency validation fails."""

    def __init__(self, message: str, dependency: str = "", source: str = ""):
        super().__init__(message, {
            "dependency": dependency,
            "source": source,
        })
        self.dependency = dependency
        self.source = source


class CircularDependencyError(DependencyError):
    """Raised when circular dependencies are detected."""

    def __init__(self, cycle: list[str]):
        cycle_str = " -> ".join(cycle)
        super().__init__(
            f"Circular dependency detected: {cycle_str}",
            dependency=cycle_str,
        )
        self.cycle = cycle


class IntegrationError(DiagnosticsException):
    """Raised when integration validation fails."""

    def __init__(self, message: str, source_component: str = "", target_component: str = ""):
        super().__init__(message, {
            "source": source_component,
            "target": target_component,
        })
        self.source_component = source_component
        self.target_component = target_component


class HealthCheckError(DiagnosticsException):
    """Raised when a health check fails."""

    def __init__(self, message: str, component: str = "", health_status: str = ""):
        super().__init__(message, {
            "component": component,
            "health_status": health_status,
        })
        self.component = component
        self.health_status = health_status


class ReadinessCheckError(HealthCheckError):
    """Raised when readiness check fails."""
    pass


class LivenessCheckError(HealthCheckError):
    """Raised when liveness check fails."""
    pass


class PerformanceError(DiagnosticsException):
    """Raised when performance is below acceptable thresholds."""

    def __init__(self, message: str, metric: str = "", value: float = 0, threshold: float = 0):
        super().__init__(message, {
            "metric": metric,
            "value": value,
            "threshold": threshold,
        })
        self.metric = metric
        self.value = value
        self.threshold = threshold


class TimeoutError(DiagnosticsException):
    """Raised when a diagnostics operation times out."""

    def __init__(self, operation: str, timeout_seconds: float):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds}s",
            {"operation": operation, "timeout_seconds": timeout_seconds},
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class ConfigurationError(DiagnosticsException):
    """Raised when diagnostics configuration is invalid."""

    def __init__(self, message: str, config_key: str = ""):
        super().__init__(message, {"config_key": config_key})
        self.config_key = config_key


class ComponentNotFoundError(DiagnosticsException):
    """Raised when a required component is not found."""

    def __init__(self, component: str, component_type: str = ""):
        super().__init__(
            f"Required component '{component}' not found",
            {"component": component, "type": component_type},
        )
        self.component = component
        self.component_type = component_type


class EventBusError(DiagnosticsException):
    """Raised when event bus validation fails."""

    def __init__(self, message: str, event_type: str = ""):
        super().__init__(message, {"event_type": event_type})
        self.event_type = event_type


class RegistryError(DiagnosticsException):
    """Raised when registry validation fails."""

    def __init__(self, message: str, registry_type: str = ""):
        super().__init__(message, {"registry_type": registry_type})
        self.registry_type = registry_type


class ContainerError(DiagnosticsException):
    """Raised when dependency injection container validation fails."""
    pass


class BootError(DiagnosticsException):
    """Raised when boot process validation fails."""
    pass


class RuntimeError(DiagnosticsException):
    """Raised when runtime validation fails."""
    pass


class SchedulerError(DiagnosticsException):
    """Raised when scheduler validation fails."""
    pass


class SessionError(DiagnosticsException):
    """Raised when session manager validation fails."""
    pass


class ContextError(DiagnosticsException):
    """Raised when context manager validation fails."""
    pass


class BlackboardError(DiagnosticsException):
    """Raised when blackboard validation fails."""
    pass


class OrchestratorError(DiagnosticsException):
    """Raised when orchestrator validation fails."""
    pass


class PlannerError(DiagnosticsException):
    """Raised when planner validation fails."""
    pass


class KnowledgeError(DiagnosticsException):
    """Raised when knowledge engine validation fails."""
    pass


class MemoryError(DiagnosticsException):
    """Raised when memory engine validation fails."""
    pass


class ReasoningError(DiagnosticsException):
    """Raised when reasoning engine validation fails."""
    pass


class DecisionError(DiagnosticsException):
    """Raised when decision engine validation fails."""
    pass


class ToolEngineError(DiagnosticsException):
    """Raised when tool engine validation fails."""
    pass


class LifecycleError(DiagnosticsException):
    """Raised when lifecycle manager validation fails."""
    pass
