"""EREN core — Diagnostic engine.

This module provides clinical diagnostic capabilities for EREN.
For production readiness diagnostics, see core.diagnostics.
"""

from .engine import DiagnosticEngine
from .exceptions import DiagnosticError
from .interfaces import DiagnosticPort

# Re-export from production diagnostics for convenience
try:
    from core.diagnostics import (
        ERENDiagnostics,
        DiagnosticReport,
        SystemHealth,
        HealthStatus,
        DiagnosticScore,
    )
except ImportError:
    pass

__all__ = [
    "DiagnosticEngine",
    "DiagnosticError",
    "DiagnosticPort",
    # Production diagnostics
    "ERENDiagnostics",
    "DiagnosticReport",
    "SystemHealth",
    "HealthStatus",
    "DiagnosticScore",
]
