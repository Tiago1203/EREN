"""Healthcare Standards Platform for EREN OS.

PR-063: Healthcare Standards Platform

Provides support for FHIR, HL7, DICOM, SNOMED CT, LOINC, ICD-10 validation.
"""

from __future__ import annotations

from core.PHASE_1.infrastructure.biomedical.standards.engine import (
    StandardsEngine,
    get_standards_engine,
    reset_standards_engine,
)
from core.PHASE_1.infrastructure.biomedical.standards.types import (
    CodeMapping,
    FHIRPatient,
    FHIRObservation,
    FHIRResource,
    HL7Message,
    HL7Segment,
    ICD10Code,
    LOINCConcept,
    RxNormConcept,
    SNOMEDConcept,
    StandardType,
    ValidationResult,
)

__all__ = [
    # Engine
    "StandardsEngine",
    "get_standards_engine",
    "reset_standards_engine",
    # Types
    "StandardType",
    "FHIRResource",
    "FHIRPatient",
    "FHIRObservation",
    "HL7Message",
    "HL7Segment",
    "SNOMEDConcept",
    "LOINCConcept",
    "ICD10Code",
    "RxNormConcept",
    "CodeMapping",
    "ValidationResult",
]
