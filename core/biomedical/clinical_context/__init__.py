"""Clinical Context Engine for EREN OS.

PR-061: Clinical Context Engine

Provides clinical context modeling for patient data,
medical records, and temporal context management.
"""

from __future__ import annotations

from core.biomedical.clinical_context.engine import (
    ClinicalContextEngine,
    get_clinical_context_engine,
    reset_clinical_context_engine,
)
from core.biomedical.clinical_context.types import (
    Allergy,
    ClinicalContext,
    ClinicalEpisode,
    ClinicalEntityType,
    Consultation,
    ContextBuildRequest,
    ContextBuildResult,
    ContextPolicy,
    LabResult,
    Medication,
    Patient,
    PrivacyLevel,
    Professional,
    VitalSigns,
)

__all__ = [
    # Engine
    "ClinicalContextEngine",
    "get_clinical_context_engine",
    "reset_clinical_context_engine",
    # Types
    "ClinicalEntityType",
    "Patient",
    "Professional",
    "ClinicalEpisode",
    "Consultation",
    "Medication",
    "Allergy",
    "LabResult",
    "VitalSigns",
    "ClinicalContext",
    "ContextBuildRequest",
    "ContextBuildResult",
    "ContextPolicy",
    "PrivacyLevel",
]
