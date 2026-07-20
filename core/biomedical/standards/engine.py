"""Healthcare Standards Platform Engine for EREN OS.

Provides validation, conversion, and mapping for healthcare standards.
"""

from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from core.biomedical.standards.types import (
    CodeMapping,
    FHIRPatient,
    FHIRObservation,
    HL7Message,
    HL7Segment,
    ICD10Code,
    LOINCConcept,
    RxNormConcept,
    SNOMEDConcept,
    StandardType,
    ValidationResult,
)


class StandardsEngine:
    """Engine for healthcare standards support.

    Features:
    - FHIR resource validation and conversion
    - HL7 message parsing
    - Terminology validation (SNOMED CT, LOINC, ICD-10)
    - Code mapping between systems
    """

    def __init__(self):
        """Initialize standards engine."""
        self._fhir_mappings: dict[str, str] = {}
        self._code_mappings: dict[str, CodeMapping] = {}
        self._snomed_cache: dict[str, SNOMEDConcept] = {}
        self._loinc_cache: dict[str, LOINCConcept] = {}
        self._icd10_cache: dict[str, ICD10Code] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # FHIR
    # =========================================================================

    def validate_fhir_patient(self, patient: FHIRPatient) -> ValidationResult:
        """Validate FHIR Patient resource."""
        errors = []

        if not patient.id:
            errors.append("Patient id is required")

        if not patient.name:
            errors.append("Patient name is required")

        if patient.gender not in ("male", "female", "other", "unknown", ""):
            errors.append(f"Invalid gender: {patient.gender}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            standard=StandardType.FHIR,
        )

    def validate_fhir_observation(self, obs: FHIRObservation) -> ValidationResult:
        """Validate FHIR Observation resource."""
        errors = []

        if not obs.code:
            errors.append("Observation code is required")

        if obs.status not in ("registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"):
            errors.append(f"Invalid status: {obs.status}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            standard=StandardType.FHIR,
        )

    # =========================================================================
    # HL7
    # =========================================================================

    def parse_hl7_message(self, message_text: str) -> HL7Message | None:
        """Parse HL7 message text."""
        try:
            segments = []
            for line in message_text.split("\r"):
                if line.strip():
                    fields = line.split("|")
                    if fields:
                        segments.append(fields[0])

            return HL7Message(
                message_type=self._get_hl7_field(segments, "MSH", 9, 0),
                message_id=self._get_hl7_field(segments, "MSH", 10),
                timestamp=datetime.now(UTC),
                segments=segments,
            )
        except Exception:
            return None

    def _get_hl7_field(self, segments: list, segment_type: str, field_idx: int, sub_idx: int | None = None) -> str:
        """Get field from HL7 segment."""
        for seg in segments:
            if seg[0:3] == segment_type:
                fields = seg.split("|")
                if len(fields) > field_idx:
                    val = fields[field_idx]
                    if sub_idx is not None:
                        components = val.split("^")
                        if len(components) > sub_idx:
                            return components[sub_idx]
                    return val
        return ""

    # =========================================================================
    # Terminology
    # =========================================================================

    def validate_snomed_ct(self, concept_id: str) -> bool:
        """Validate SNOMED CT concept ID."""
        # SNOMED CT IDs are 6-18 digits
        if not concept_id.isdigit():
            return False
        return 100000 <= int(concept_id) <= 999999999999999999

    def validate_loinc(self, code: str) -> bool:
        """Validate LOINC code."""
        # LOINC codes are 1-5 digits optionally followed by dash and suffix
        import re
        return bool(re.match(r"^\d{1,5}(-\d)?$", code))

    def validate_icd10(self, code: str) -> bool:
        """Validate ICD-10 code."""
        import re
        # ICD-10 codes: letter + 2 digits optionally followed by . and more
        return bool(re.match(r"^[A-Z]\d{2}(\.\d{1,4})?$", code.upper()))

    # =========================================================================
    # Code Mapping
    # =========================================================================

    def add_code_mapping(self, mapping: CodeMapping) -> None:
        """Add code mapping."""
        key = f"{mapping.source_system.value}:{mapping.source_code}"
        self._code_mappings[key] = mapping

    def map_code(
        self,
        code: str,
        source: StandardType,
        target: StandardType,
    ) -> str | None:
        """Map code between systems."""
        key = f"{source.value}:{code}"
        mapping = self._code_mappings.get(key)

        if mapping and mapping.target_system == target:
            return mapping.target_code

        # Try reverse lookup
        for k, m in self._code_mappings.items():
            if m.target_code == code and m.target_system == source and m.source_system == target:
                return m.source_code

        return None


# =============================================================================
# Singleton
# =============================================================================

_global_engine: StandardsEngine | None = None
_engine_lock = threading.Lock()


def get_standards_engine() -> StandardsEngine:
    """Get global standards engine."""
    global _global_engine
    with _engine_lock:
        if _global_engine is None:
            _global_engine = StandardsEngine()
        return _global_engine


def reset_standards_engine() -> None:
    """Reset global engine."""
    global _global_engine
    with _engine_lock:
        _global_engine = None
