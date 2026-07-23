"""
PHASE 5 - EPIC 3: Diagnostic Agent

Agente especializado en diagnóstico técnico.
Analiza fallas, genera hipótesis y construye diagnósticos.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_3"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic3_diagnostic_agent.domain import (
    # Diagnostic Task
    DiagnosticTask,
    DiagnosticTaskType,
    # Failure Pattern
    FailurePattern,
    FailureSeverity,
    # Diagnostic Report
    DiagnosticReport,
    DiagnosisConfidence,
)

# Engines
from core.PHASE_5.epic3_diagnostic_agent.engines import (
    # Failure Analyzer
    FailureAnalyzer,
    FailureAnalysisResult,
    # Root Cause Analyzer
    RootCauseAnalyzer,
    RootCauseAnalysisResult,
    # Diagnostic Planner
    DiagnosticPlanner,
    DiagnosticPlan,
    # Fault Correlation
    FaultCorrelator,
    CorrelationResult,
)

# Agent
from core.PHASE_5.epic3_diagnostic_agent.agent import (
    DiagnosticAgent,
    DiagnosticAgentConfig,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "__epic__",
    "__phase__",
    # Domain
    "DiagnosticTask",
    "DiagnosticTaskType",
    "FailurePattern",
    "FailureSeverity",
    "DiagnosticReport",
    "DiagnosisConfidence",
    # Engines
    "FailureAnalyzer",
    "FailureAnalysisResult",
    "RootCauseAnalyzer",
    "RootCauseAnalysisResult",
    "DiagnosticPlanner",
    "DiagnosticPlan",
    "FaultCorrelator",
    "CorrelationResult",
    # Agent
    "DiagnosticAgent",
    "DiagnosticAgentConfig",
]
