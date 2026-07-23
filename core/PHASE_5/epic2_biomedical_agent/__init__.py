"""
PHASE 5 - EPIC 2: Biomedical Agent

Agente especializado en Ingeniería Clínica.
Experticia en equipos médicos, mantenimiento, normas IEC, protocolos, fabricantes y calibraciones.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_2"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic2_biomedical_agent.domain import (
    # Biomedical Task
    BiomedicalTask,
    BiomedicalTaskType,
    # Device Assessment
    DeviceAssessment,
    AssessmentSeverity,
    AssessmentStatus,
    # Maintenance Recommendation
    MaintenanceRecommendation,
    MaintenancePriority,
    MaintenanceType,
)

# Experts
from core.PHASE_5.epic2_biomedical_agent.experts import (
    # Equipment Expert
    EquipmentExpert,
    EquipmentAnalysis,
    # Maintenance Expert
    MaintenanceExpert,
    MaintenanceAdvice,
    # Manufacturer Expert
    ManufacturerExpert,
    ManufacturerInfo,
    # Standards Expert
    StandardsExpert,
    StandardReference,
    # Calibration Expert
    CalibrationExpert,
    CalibrationRecord,
)

# Agent
from core.PHASE_5.epic2_biomedical_agent.agent import (
    BiomedicalAgent,
    BiomedicalAgentConfig,
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
    "BiomedicalTask",
    "BiomedicalTaskType",
    "DeviceAssessment",
    "AssessmentSeverity",
    "AssessmentStatus",
    "MaintenanceRecommendation",
    "MaintenancePriority",
    "MaintenanceType",
    # Experts
    "EquipmentExpert",
    "EquipmentAnalysis",
    "MaintenanceExpert",
    "MaintenanceAdvice",
    "ManufacturerExpert",
    "ManufacturerInfo",
    "StandardsExpert",
    "StandardReference",
    "CalibrationExpert",
    "CalibrationRecord",
    # Agent
    "BiomedicalAgent",
    "BiomedicalAgentConfig",
]
