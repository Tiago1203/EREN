"""Healthcare Standards Platform Types for EREN OS.

Type definitions for FHIR, HL7, DICOM, SNOMED CT, LOINC, ICD-10 support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Standard Types
# =============================================================================


class StandardType(str, Enum):
    """Types of healthcare standards."""

    FHIR = "fhir"
    HL7_V2 = "hl7_v2"
    HL7_V3 = "hl7_v3"
    DICOM = "dicom"
    SNOMED_CT = "snomed_ct"
    LOINC = "loinc"
    ICD_10 = "icd_10"
    RXNORM = "rxnorm"
    IEC_60601 = "iec_60601"
    ISO_13485 = "iso_13485"
    ISO_14971 = "iso_14971"


# =============================================================================
# FHIR Types
# =============================================================================


@dataclass
class FHIRResource:
    """Base FHIR resource."""

    resource_type: str = ""
    id: str = ""
    meta: dict = field(default_factory=dict)


@dataclass
class FHIRPatient(FHIRResource):
    """FHIR Patient resource."""

    resource_type: str = "Patient"
    identifier: list[dict] = field(default_factory=list)
    name: list[dict] = field(default_factory=list)
    gender: str = ""
    birthDate: str = ""


@dataclass
class FHIRObservation(FHIRResource):
    """FHIR Observation resource."""

    resource_type: str = "Observation"
    status: str = "final"
    code: dict = field(default_factory=dict)
    valueQuantity: dict = field(default_factory=dict)
    subject: dict = field(default_factory=dict)


# =============================================================================
# HL7 Types
# =============================================================================


@dataclass
class HL7Message:
    """HL7 message."""

    message_type: str = ""
    message_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    segments: list[str] = field(default_factory=list)


@dataclass
class HL7Segment:
    """HL7 segment."""

    segment_type: str = ""  # PID, OBR, OBX, etc.
    fields: list[str] = field(default_factory=list)


# =============================================================================
# Terminology Types
# =============================================================================


@dataclass
class SNOMEDConcept:
    """SNOMED CT concept."""

    concept_id: str
    fully_specified_name: str = ""
    preferred_term: str = ""
    semantic_tag: str = ""
    parents: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)


@dataclass
class LOINCConcept:
    """LOINC concept."""

    code: str
    name: str = ""
    component: str = ""
    property: str = ""
    time_aspect: str = ""
    system: str = ""
    scale_type: str = ""
    method_type: str = ""


@dataclass
class ICD10Code:
    """ICD-10 code."""

    code: str
    description: str = ""
    category: str = ""
    chapter: str = ""


@dataclass
class RxNormConcept:
    """RxNorm concept."""

    rxcui: str
    name: str = ""
    tty: str = ""  # Term type (SCDC, BN, etc.)
    synonym: str = ""


# =============================================================================
# Validation
# =============================================================================


@dataclass
class ValidationResult:
    """Result of validation against a standard."""

    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    standard: StandardType | None = None


# =============================================================================
# Code Mapping
# =============================================================================


@dataclass
class CodeMapping:
    """Mapping between code systems."""

    source_system: StandardType
    source_code: str
    target_system: StandardType
    target_code: str
    description: str = ""
    confidence: float = 1.0
