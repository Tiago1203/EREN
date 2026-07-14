"""EREN core — Diagnostic (DEPRECATED)

This module is DEPRECATED and will be removed in version 2.0.0.

All functionality has been moved to `core.diagnostics`.

Migration:
    from core.diagnostic import DiagnosticEngine
    # BECOMES
    from core.diagnostics import DiagnosticEngine

For more information, see:
- docs/architecture/MIGRATION_GUIDE.md
- docs/adr/ADR-001-duplicate-modules.md

---

Deprecated: 2026-07-14
Removal: Version 2.0.0 (planned)
"""

from __future__ import annotations

import warnings

# Emit deprecation warning on import
warnings.warn(
    "core.diagnostic is DEPRECATED and will be removed in version 2.0.0. "
    "Please use core.diagnostics instead. "
    "See: docs/architecture/MIGRATION_GUIDE.md",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical location
from core.diagnostics import (
    # Architecture
    ArchitectureValidator,
    CircularDependencyValidator,
    ContractCompliance,
    # Contracts
    ContractValidator,
    ContractViolation,
    ContractViolationError,
    DependencyError,
    DependencyGraphValidator,
    DependencyHealth,
    DependencyIssue,
    # Dependencies
    DependencyValidator,
    DiagnosticEngine,
    # Exceptions
    DiagnosticError,
    # Metrics
    DiagnosticMetrics,
    # Report
    DiagnosticReport,
    DiagnosticsCompleted,
    DiagnosticScore,
    DiagnosticsFailed,
    # Events
    DiagnosticsStarted,
    DiagnosticTrace,
    # Main engine
    ERENDiagnostics,
    HealthCheckCompleted,
    HealthCheckError,
    HealthCheckStarted,
    HealthStatus,
    IntegrationCheck,
    IntegrationCheckCompleted,
    IntegrationResult,
    # Integration
    IntegrationValidator,
    LayerDependencyValidator,
    LivenessCheck,
    PerformanceIssue,
    PerformanceMeasured,
    PerformanceMetrics,
    # Performance
    PerformanceProfiler,
    ReadinessCheck,
    RecoveryHealth,
    ReportGenerated,
    ReportGenerator,
    RuntimeHealth,
    RuntimeMetrics,
    # Runtime
    RuntimeValidator,
    ShutdownHealth,
    StartupHealth,
    # Health
    SystemHealth,
    ValidationCompleted,
    ValidationStarted,
    get_diagnostics,
    reset_diagnostics,
)
from core.diagnostics import (
    ValidationError as DiagnosticValidationError,
)

__all__ = [
    # Main engine
    "ERENDiagnostics",
    "DiagnosticEngine",
    "get_diagnostics",
    "reset_diagnostics",
    # Architecture
    "ArchitectureValidator",
    "DependencyGraphValidator",
    "CircularDependencyValidator",
    "LayerDependencyValidator",
    # Health
    "SystemHealth",
    "HealthStatus",
    "ReadinessCheck",
    "LivenessCheck",
    "StartupHealth",
    "ShutdownHealth",
    "RecoveryHealth",
    # Contracts
    "ContractValidator",
    "ContractCompliance",
    "ContractViolation",
    # Integration
    "IntegrationValidator",
    "IntegrationCheck",
    "IntegrationResult",
    # Dependencies
    "DependencyValidator",
    "DependencyHealth",
    "DependencyIssue",
    # Runtime
    "RuntimeValidator",
    "RuntimeHealth",
    "RuntimeMetrics",
    # Performance
    "PerformanceProfiler",
    "PerformanceMetrics",
    "PerformanceIssue",
    # Report
    "DiagnosticReport",
    "DiagnosticScore",
    "ReportGenerator",
    # Events
    "DiagnosticsStarted",
    "HealthCheckStarted",
    "HealthCheckCompleted",
    "ValidationStarted",
    "ValidationCompleted",
    "IntegrationCheckCompleted",
    "PerformanceMeasured",
    "ReportGenerated",
    "DiagnosticsCompleted",
    "DiagnosticsFailed",
    # Metrics
    "DiagnosticMetrics",
    "DiagnosticTrace",
    # Exceptions
    "DiagnosticError",
    "DiagnosticValidationError",
    "HealthCheckError",
    "ContractViolationError",
    "DependencyError",
]

# Deprecation metadata
__deprecated__ = True
__deprecated_since__ = "2026-07-14"
__deprecated_remove__ = "2.0.0"
__deprecated_replacement__ = "core.diagnostics"
