"""EREN OS Diagnostics System - Production Readiness Certification.

This module implements the official diagnostic, validation, and integration system
for EREN OS. It provides comprehensive auditing capabilities to certify whether
an EREN installation is production-ready.

Philosophy:
    EREN should not assume it is healthy. EREN should demonstrate it.

Key Features:
    - Comprehensive component auditing
    - Contract compliance verification
    - Dependency graph analysis
    - Health and readiness checks
    - Performance profiling
    - Event flow validation
    - Production readiness scoring

Example:
    >>> report = (
    ...     ERENDiagnostics()
    ...         .run_full_system_validation()
    ... )
    >>> print(report.score)
    >>> print(report.production_ready)
    >>> print(report.summary())
"""

from __future__ import annotations

from core.diagnostics.architecture import ArchitectureReport, ArchitectureValidator
from core.diagnostics.contracts import ContractValidator, ContractViolation
from core.diagnostics.dependencies import DependencyReport, DependencyValidator
from core.diagnostics.engine import DiagnosticsEngine, ERENDiagnostics
from core.diagnostics.events import (
    DiagnosticsEventPublisher,
    DiagnosticsEventType,
)
from core.diagnostics.exceptions import (
    ArchitectureError,
    BlackboardError,
    BootError,
    CircularDependencyError,
    ComponentNotFoundError,
    ConfigurationError,
    ContainerError,
    ContextError,
    ContractViolationError,
    DecisionError,
    DependencyError,
    DiagnosticsException,
    DiagnosticsInitializationError,
    EventBusError,
    HealthCheckError,
    IntegrationError,
    KnowledgeError,
    LifecycleError,
    LivenessCheckError,
    MemoryError,
    OrchestratorError,
    PerformanceError,
    PlannerError,
    ReadinessCheckError,
    ReasoningError,
    RegistryError,
    RuntimeError,
    SchedulerError,
    SessionError,
    TimeoutError,
    ToolEngineError,
    ValidationError,
)
from core.diagnostics.health import HealthStatus, SystemHealth
from core.diagnostics.integration import IntegrationReport, IntegrationValidator
from core.diagnostics.liveness import LivenessChecker
from core.diagnostics.metrics import DiagnosticsMetrics
from core.diagnostics.performance import PerformanceProfiler
from core.diagnostics.readiness import ReadinessChecker
from core.diagnostics.report import DiagnosticReport, ReportGenerator
from core.diagnostics.runtime import RuntimeReport, RuntimeValidator
from core.diagnostics.score import DiagnosticScore, ScoreCategory
from core.diagnostics.trace import DiagnosticsTrace

__all__ = [
    # Main Engine
    "ERENDiagnostics",
    "DiagnosticsEngine",
    # Exceptions
    "DiagnosticsException",
    "DiagnosticsInitializationError",
    "ValidationError",
    "ArchitectureError",
    "ContractViolationError",
    "DependencyError",
    "CircularDependencyError",
    "IntegrationError",
    "HealthCheckError",
    "ReadinessCheckError",
    "LivenessCheckError",
    "PerformanceError",
    "TimeoutError",
    "ConfigurationError",
    "ComponentNotFoundError",
    "EventBusError",
    "RegistryError",
    "ContainerError",
    "BootError",
    "RuntimeError",
    "SchedulerError",
    "SessionError",
    "ContextError",
    "BlackboardError",
    "OrchestratorError",
    "PlannerError",
    "KnowledgeError",
    "MemoryError",
    "ReasoningError",
    "DecisionError",
    "ToolEngineError",
    "LifecycleError",
    # Health
    "SystemHealth",
    "HealthStatus",
    # Checkers
    "ReadinessChecker",
    "LivenessChecker",
    # Validators
    "ArchitectureValidator",
    "ArchitectureReport",
    "ContractValidator",
    "ContractViolation",
    "DependencyValidator",
    "DependencyReport",
    "IntegrationValidator",
    "IntegrationReport",
    "RuntimeValidator",
    "RuntimeReport",
    # Performance
    "PerformanceProfiler",
    # Report
    "DiagnosticReport",
    "ReportGenerator",
    # Scoring
    "DiagnosticScore",
    "ScoreCategory",
    # Events
    "DiagnosticsEventPublisher",
    "DiagnosticsEventType",
    # Metrics & Trace
    "DiagnosticsMetrics",
    "DiagnosticsTrace",
]
