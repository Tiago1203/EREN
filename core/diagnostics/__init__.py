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

from core.diagnostics.engine import ERENDiagnostics, DiagnosticsEngine
from core.diagnostics.exceptions import (
    DiagnosticsException,
    DiagnosticsInitializationError,
    ValidationError,
    ArchitectureError,
    ContractViolationError,
    DependencyError,
    CircularDependencyError,
    IntegrationError,
    HealthCheckError,
    ReadinessCheckError,
    LivenessCheckError,
    PerformanceError,
    TimeoutError,
    ConfigurationError,
    ComponentNotFoundError,
    EventBusError,
    RegistryError,
    ContainerError,
    BootError,
    RuntimeError,
    SchedulerError,
    SessionError,
    ContextError,
    BlackboardError,
    OrchestratorError,
    PlannerError,
    KnowledgeError,
    MemoryError,
    ReasoningError,
    DecisionError,
    ToolEngineError,
    LifecycleError,
)
from core.diagnostics.health import SystemHealth, HealthStatus
from core.diagnostics.readiness import ReadinessChecker
from core.diagnostics.liveness import LivenessChecker
from core.diagnostics.architecture import ArchitectureValidator, ArchitectureReport
from core.diagnostics.contracts import ContractValidator, ContractViolation
from core.diagnostics.dependencies import DependencyValidator, DependencyReport
from core.diagnostics.integration import IntegrationValidator, IntegrationReport
from core.diagnostics.runtime import RuntimeValidator, RuntimeReport
from core.diagnostics.performance import PerformanceProfiler
from core.diagnostics.report import DiagnosticReport, ReportGenerator
from core.diagnostics.score import DiagnosticScore, ScoreCategory
from core.diagnostics.events import (
    DiagnosticsEventPublisher,
    DiagnosticsEventType,
)
from core.diagnostics.metrics import DiagnosticsMetrics
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
