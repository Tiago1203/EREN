"""Runtime validator for the Cognitive Operating System.

Validates the runtime configuration, components, and state before
allowing the runtime to start. Ensures all prerequisites are met.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ValidationResult:
    """Result of a validation check."""

    check_name: str
    passed: bool
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    is_critical: bool = False
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "is_critical": self.is_critical,
            "timestamp": self.timestamp,
        }


@dataclass
class ValidationReport:
    """Complete validation report for the runtime."""

    runtime_id: str
    timestamp: str = ""
    is_valid: bool = True
    results: list[ValidationResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    critical_failures: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()

    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result.

        Args:
            result: The validation result to add.
        """
        self.results.append(result)

        if not result.passed:
            self.is_valid = False
            if result.is_critical:
                self.critical_failures.append(
                    f"[CRITICAL] {result.check_name}: {result.message}"
                )
                self.errors.append(
                    f"{result.check_name}: {result.message}"
                )
            else:
                self.warnings.append(
                    f"{result.check_name}: {result.message}"
                )

    def get_failed_checks(self) -> list[ValidationResult]:
        """Get all failed validation checks.

        Returns:
            List of failed validation results.
        """
        return [r for r in self.results if not r.passed]

    def get_critical_failures(self) -> list[ValidationResult]:
        """Get all critical validation failures.

        Returns:
            List of critical failed validation results.
        """
        return [
            r for r in self.results
            if not r.passed and r.is_critical
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "runtime_id": self.runtime_id,
            "timestamp": self.timestamp,
            "is_valid": self.is_valid,
            "total_checks": len(self.results),
            "passed_checks": sum(1 for r in self.results if r.passed),
            "failed_checks": sum(1 for r in self.results if not r.passed),
            "critical_failures_count": len(self.critical_failures),
            "results": [r.to_dict() for r in self.results],
            "errors": self.errors,
            "warnings": self.warnings,
            "critical_failures": self.critical_failures,
        }


class RuntimeValidator:
    """Validates the Cognitive Runtime before startup.

    Performs comprehensive validation of:
    - Configuration
    - Composition Root
    - Dependency Injection Container
    - Event Bus
    - Capability Registry
    - All engines and components
    - State and dependencies
    """

    def __init__(self, runtime_id: str):
        """Initialize the validator.

        Args:
            runtime_id: The runtime instance ID.
        """
        self._runtime_id = runtime_id
        self._strict_mode = False

    def set_strict_mode(self, enabled: bool) -> None:
        """Enable or disable strict validation mode.

        In strict mode, warnings are treated as failures.

        Args:
            enabled: Whether to enable strict mode.
        """
        self._strict_mode = enabled

    def validate(
        self,
        configuration=None,
        container=None,
        composition_root=None,
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
    ) -> ValidationReport:
        """Perform comprehensive validation.

        Args:
            configuration: Runtime configuration.
            container: DI Container instance.
            composition_root: Composition Root instance.
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
            Complete validation report.
        """
        report = ValidationReport(runtime_id=self._runtime_id)

        # Validate configuration
        self._validate_configuration(configuration, report)

        # Validate composition root
        self._validate_composition_root(composition_root, report)

        # Validate container
        self._validate_container(container, report)

        # Validate event bus
        self._validate_event_bus(event_bus, report)

        # Validate capability registry
        self._validate_capability_registry(capability_registry, report)

        # Validate boot manager
        self._validate_boot_manager(boot_manager, report)

        # Validate session manager
        self._validate_session_manager(session_manager, report)

        # Validate lifecycle manager
        self._validate_lifecycle_manager(lifecycle_manager, report)

        # Validate orchestrator
        self._validate_orchestrator(orchestrator, report)

        # Validate scheduler
        self._validate_scheduler(scheduler, report)

        # Validate engines
        self._validate_engines(
            planner,
            knowledge_engine,
            memory_engine,
            reasoning_engine,
            decision_engine,
            tool_engine,
            report,
        )

        # Apply strict mode if enabled
        if self._strict_mode and report.warnings:
            report.is_valid = False
            for warning in report.warnings:
                report.errors.append(f"[STRICT] {warning}")

        return report

    def _validate_configuration(
        self,
        configuration,
        report: ValidationReport,
    ) -> None:
        """Validate runtime configuration."""
        if configuration is None:
            report.add_result(ValidationResult(
                check_name="configuration",
                passed=False,
                message="Configuration is None",
                is_critical=True,
            ))
            return

        # Check required fields
        required_fields = ['runtime_name', 'runtime_version']
        for field_name in required_fields:
            if not hasattr(configuration, field_name):
                report.add_result(ValidationResult(
                    check_name=f"configuration.{field_name}",
                    passed=False,
                    message=f"Missing required field: {field_name}",
                    is_critical=True,
                ))

        # Check timeout values are positive
        timeout_fields = [
            'boot_timeout_ms',
            'session_timeout_ms',
            'cycle_timeout_ms',
        ]
        for field_name in timeout_fields:
            value = getattr(configuration, field_name, 0)
            if value <= 0:
                report.add_result(ValidationResult(
                    check_name=f"configuration.{field_name}",
                    passed=False,
                    message=f"Invalid timeout value: {value}",
                    details={"field": field_name, "value": value},
                ))

        # Configuration is valid
        report.add_result(ValidationResult(
            check_name="configuration",
            passed=True,
            message="Configuration is valid",
            details={
                "runtime_name": getattr(configuration, 'runtime_name', 'unknown'),
                "runtime_version": getattr(configuration, 'runtime_version', 'unknown'),
                "environment": getattr(configuration, 'environment', 'unknown'),
            },
        ))

    def _validate_composition_root(
        self,
        composition_root,
        report: ValidationReport,
    ) -> None:
        """Validate Composition Root."""
        if composition_root is None:
            report.add_result(ValidationResult(
                check_name="composition_root",
                passed=False,
                message="Composition Root is None",
                is_critical=True,
            ))
            return

        if not getattr(composition_root, 'is_built', False):
            report.add_result(ValidationResult(
                check_name="composition_root.built",
                passed=False,
                message="Composition Root has not been built",
                is_critical=True,
            ))
            return

        report.add_result(ValidationResult(
            check_name="composition_root",
            passed=True,
            message="Composition Root is valid",
            details={"root_id": getattr(composition_root, 'id', 'unknown')},
        ))

    def _validate_container(
        self,
        container,
        report: ValidationReport,
    ) -> None:
        """Validate DI Container."""
        if container is None:
            report.add_result(ValidationResult(
                check_name="container",
                passed=False,
                message="DI Container is None",
                is_critical=True,
            ))
            return

        if getattr(container, 'is_disposed', False):
            report.add_result(ValidationResult(
                check_name="container.disposed",
                passed=False,
                message="DI Container has been disposed",
                is_critical=True,
            ))
            return

        # Check for registered services
        try:
            registry = getattr(container, '_registry', None)
            service_count = len(getattr(registry, '_services', {})) if registry else 0
            report.add_result(ValidationResult(
                check_name="container",
                passed=True,
                message="DI Container is ready",
                details={
                    "container_id": getattr(container, 'id', 'unknown'),
                    "services_registered": service_count,
                },
            ))
        except Exception as e:
            report.add_result(ValidationResult(
                check_name="container",
                passed=False,
                message=f"Container validation failed: {e!s}",
                is_critical=True,
            ))

    def _validate_event_bus(
        self,
        event_bus,
        report: ValidationReport,
    ) -> None:
        """Validate Event Bus."""
        if event_bus is None:
            report.add_result(ValidationResult(
                check_name="event_bus",
                passed=False,
                message="Event Bus is None",
                is_critical=True,
            ))
            return

        # Check bus has required methods
        required_methods = ['publish', 'subscribe', 'unsubscribe']
        for method_name in required_methods:
            if not hasattr(event_bus, method_name):
                report.add_result(ValidationResult(
                    check_name=f"event_bus.{method_name}",
                    passed=False,
                    message=f"Event Bus missing required method: {method_name}",
                    is_critical=True,
                ))
                return

        report.add_result(ValidationResult(
            check_name="event_bus",
            passed=True,
            message="Event Bus is ready",
        ))

    def _validate_capability_registry(
        self,
        registry,
        report: ValidationReport,
    ) -> None:
        """Validate Capability Registry."""
        if registry is None:
            report.add_result(ValidationResult(
                check_name="capability_registry",
                passed=False,
                message="Capability Registry is None",
                is_critical=True,
            ))
            return

        report.add_result(ValidationResult(
            check_name="capability_registry",
            passed=True,
            message="Capability Registry is ready",
        ))

    def _validate_boot_manager(
        self,
        boot_manager,
        report: ValidationReport,
    ) -> None:
        """Validate Boot Manager."""
        if boot_manager is None:
            report.add_result(ValidationResult(
                check_name="boot_manager",
                passed=False,
                message="Boot Manager is None",
                is_critical=True,
            ))
            return

        state = getattr(boot_manager, 'state', 'unknown')
        if state not in ('ready', 'booted'):
            report.add_result(ValidationResult(
                check_name="boot_manager.state",
                passed=False,
                message=f"Boot Manager not ready, state: {state}",
                is_critical=True,
            ))
            return

        report.add_result(ValidationResult(
            check_name="boot_manager",
            passed=True,
            message="Boot Manager is ready",
            details={"state": state},
        ))

    def _validate_session_manager(
        self,
        manager,
        report: ValidationReport,
    ) -> None:
        """Validate Session Manager."""
        if manager is None:
            report.add_result(ValidationResult(
                check_name="session_manager",
                passed=False,
                message="Session Manager is None",
                is_critical=True,
            ))
            return

        report.add_result(ValidationResult(
            check_name="session_manager",
            passed=True,
            message="Session Manager is ready",
        ))

    def _validate_lifecycle_manager(
        self,
        manager,
        report: ValidationReport,
    ) -> None:
        """Validate Lifecycle Manager."""
        if manager is None:
            report.add_result(ValidationResult(
                check_name="lifecycle_manager",
                passed=False,
                message="Lifecycle Manager is None",
                is_critical=True,
            ))
            return

        report.add_result(ValidationResult(
            check_name="lifecycle_manager",
            passed=True,
            message="Lifecycle Manager is ready",
        ))

    def _validate_orchestrator(
        self,
        orchestrator,
        report: ValidationReport,
    ) -> None:
        """Validate Orchestrator."""
        if orchestrator is None:
            report.add_result(ValidationResult(
                check_name="orchestrator",
                passed=False,
                message="Orchestrator is None",
                is_critical=True,
            ))
            return

        report.add_result(ValidationResult(
            check_name="orchestrator",
            passed=True,
            message="Orchestrator is ready",
        ))

    def _validate_scheduler(
        self,
        scheduler,
        report: ValidationReport,
    ) -> None:
        """Validate Scheduler."""
        if scheduler is None:
            report.add_result(ValidationResult(
                check_name="scheduler",
                passed=False,
                message="Scheduler is None",
                is_critical=True,
            ))
            return

        report.add_result(ValidationResult(
            check_name="scheduler",
            passed=True,
            message="Scheduler is ready",
        ))

    def _validate_engines(
        self,
        planner,
        knowledge_engine,
        memory_engine,
        reasoning_engine,
        decision_engine,
        tool_engine,
        report: ValidationReport,
    ) -> None:
        """Validate all cognitive engines."""
        engines = [
            ("planner", planner, True),
            ("knowledge_engine", knowledge_engine, False),
            ("memory_engine", memory_engine, False),
            ("reasoning_engine", reasoning_engine, False),
            ("decision_engine", decision_engine, False),
            ("tool_engine", tool_engine, False),
        ]

        for engine_name, engine, critical in engines:
            if engine is None:
                status = "degraded" if not critical else "unhealthy"
                report.add_result(ValidationResult(
                    check_name=engine_name,
                    passed=not critical,
                    message=f"{engine_name.replace('_', ' ').title()} not available (simulation mode)",
                    is_critical=critical,
                ))
            else:
                report.add_result(ValidationResult(
                    check_name=engine_name,
                    passed=True,
                    message=f"{engine_name.replace('_', ' ').title()} is ready",
                ))

    def validate_prerequisites(self) -> ValidationReport:
        """Validate runtime prerequisites.

        Returns:
            Validation report for prerequisites.
        """
        report = ValidationReport(runtime_id=self._runtime_id)

        # Check Python version
        import sys
        if sys.version_info < (3, 10):
            report.add_result(ValidationResult(
                check_name="python_version",
                passed=False,
                message=f"Python 3.10+ required, found {sys.version_info.major}.{sys.version_info.minor}",
                is_critical=True,
            ))
        else:
            report.add_result(ValidationResult(
                check_name="python_version",
                passed=True,
                message=f"Python {sys.version_info.major}.{sys.version_info.minor} is supported",
                details={"version": f"{sys.version_info.major}.{sys.version_info.minor}"},
            ))

        # Check required packages
        required_packages = ['pydantic']
        for package in required_packages:
            try:
                __import__(package)
                report.add_result(ValidationResult(
                    check_name=f"package.{package}",
                    passed=True,
                    message=f"Package {package} is available",
                ))
            except ImportError:
                report.add_result(ValidationResult(
                    check_name=f"package.{package}",
                    passed=False,
                    message=f"Required package {package} is not installed",
                    is_critical=True,
                ))

        return report
