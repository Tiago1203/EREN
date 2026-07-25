"""
PHASE 7 - EPIC 0: Data Classification

Sistema de clasificación de datos según sensibilidad:
- PHI (Protected Health Information)
- PII (Personally Identifiable Information)
- Clinical Data
- Public Data
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class DataSensitivityLevel(str, Enum):
    """Niveles de sensibilidad de datos."""
    PUBLIC = "public"                    # Información pública
    INTERNAL = "internal"                # Información interna
    CONFIDENTIAL = "confidential"       # Información confidencial
    RESTRICTED = "restricted"           # Información restringida (PHI/PII)


class DataCategory(str, Enum):
    """Categorías de datos."""
    PHI = "phi"                          # Protected Health Information
    PII = "pii"                         # Personally Identifiable Information
    CLINICAL = "clinical"               # Datos clínicos
    OPERATIONAL = "operational"         # Datos operativos
    FINANCIAL = "financial"              # Datos financieros
    ADMINISTRATIVE = "administrative"   # Datos administrativos
    PUBLIC = "public"                    # Datos públicos


# Mapeo de campos a categorías PHI
PHI_FIELDS = {
    "patient_name", "patient_id", "ssn", "social_security",
    "date_of_birth", "dob", "address", "phone", "email",
    "medical_record_number", "mrn", "health_plan_number",
    "account_number", "certificate_license_number",
    "diagnosis", "treatment", "medications",
    "lab_results", "imaging", "genetic_information",
    "mental_health_records", "substance_abuse",
    "biometric_identifiers", "photos",
}

PII_FIELDS = {
    "name", "first_name", "last_name", "full_name",
    "email", "phone", "phone_number", "address",
    "date_of_birth", "dob", "age", "gender",
    "national_id", "passport", "driver_license",
    "ip_address", "device_id", "cookie_id",
    "employee_id", "tax_id",
}

CLINICAL_FIELDS = {
    "diagnosis", "icd_code", "icd10_code", "icd9_code",
    "procedure", "cpt_code", "medication", "prescription",
    "lab_test", "lab_result", "vital_signs",
    "blood_pressure", "heart_rate", "temperature",
    "allergies", "conditions", "symptoms",
    "vital_signs", "imaging_results", "pathology",
}


@dataclass
class DataClassification:
    """Clasificación de un dato o campo."""
    field_name: str
    category: DataCategory
    sensitivity: DataSensitivityLevel
    is_phi: bool = False
    is_pii: bool = False
    requires_encryption: bool = False
    requires_audit: bool = False
    retention_policy: str = "standard"
    description: str = ""
    examples: list[str] = field(default_factory=list)


@dataclass
class DataSubject:
    """Sujeto de datos (paciente, usuario, etc.)."""
    subject_id: str
    subject_type: str  # patient, staff, visitor
    sensitivity_override: Optional[DataSensitivityLevel] = None


class DataClassifier:
    """Clasificador de datos."""

    def __init__(self):
        self._classifications: dict[str, DataClassification] = {}
        self._subjects: dict[str, DataSubject] = {}
        self._classify_defaults()

    def _classify_defaults(self) -> None:
        """Clasifica campos por defecto."""
        # PHI fields
        for field_name in PHI_FIELDS:
            self._classifications[field_name] = DataClassification(
                field_name=field_name,
                category=DataCategory.PHI,
                sensitivity=DataSensitivityLevel.RESTRICTED,
                is_phi=True,
                requires_encryption=True,
                requires_audit=True,
                retention_policy="permanent",
                description=f"PHI field: {field_name}",
            )

        # PII fields
        for field_name in PII_FIELDS:
            if field_name not in self._classifications:
                self._classifications[field_name] = DataClassification(
                    field_name=field_name,
                    category=DataCategory.PII,
                    sensitivity=DataSensitivityLevel.CONFIDENTIAL,
                    is_pii=True,
                    requires_encryption=True,
                    requires_audit=True,
                    retention_policy="standard",
                    description=f"PII field: {field_name}",
                )

        # Clinical fields
        for field_name in CLINICAL_FIELDS:
            if field_name not in self._classifications:
                self._classifications[field_name] = DataClassification(
                    field_name=field_name,
                    category=DataCategory.CLINICAL,
                    sensitivity=DataSensitivityLevel.RESTRICTED,
                    is_phi=True,
                    requires_encryption=True,
                    requires_audit=True,
                    retention_policy="permanent",
                    description=f"Clinical field: {field_name}",
                )

    def classify(
        self,
        field_name: str,
        value: any,
        subject: Optional[DataSubject] = None,
    ) -> DataClassification:
        """Clasifica un campo por nombre y contexto."""
        # Check for known classification
        field_lower = field_name.lower()

        # Direct match
        if field_lower in self._classifications:
            return self._classifications[field_lower]

        # Check if it contains PHI/PII patterns
        phi_indicators = ["patient", "ssn", "mrn", "medical", "health"]
        pii_indicators = ["name", "email", "phone", "address", "dob"]

        if any(ind in field_lower for ind in phi_indicators):
            return DataClassification(
                field_name=field_name,
                category=DataCategory.PHI,
                sensitivity=DataSensitivityLevel.RESTRICTED,
                is_phi=True,
                requires_encryption=True,
                requires_audit=True,
                retention_policy="permanent",
            )

        if any(ind in field_lower for ind in pii_indicators):
            return DataClassification(
                field_name=field_name,
                category=DataCategory.PII,
                sensitivity=DataSensitivityLevel.CONFIDENTIAL,
                is_pii=True,
                requires_encryption=True,
                requires_audit=True,
                retention_policy="standard",
            )

        # Default: operational
        return DataClassification(
            field_name=field_name,
            category=DataCategory.OPERATIONAL,
            sensitivity=DataSensitivityLevel.INTERNAL,
            requires_encryption=False,
            requires_audit=False,
            retention_policy="standard",
        )

    def register_classification(
        self,
        classification: DataClassification,
    ) -> None:
        """Registra una clasificación custom."""
        self._classifications[classification.field_name.lower()] = classification

    def get_phi_fields(self) -> list[DataClassification]:
        """Obtiene todos los campos PHI."""
        return [c for c in self._classifications.values() if c.is_phi]

    def get_pii_fields(self) -> list[DataClassification]:
        """Obtiene todos los campos PII."""
        return [c for c in self._classifications.values() if c.is_pii]

    def requires_encryption(self, field_name: str) -> bool:
        """Verifica si campo requiere encriptación."""
        classification = self.classify(field_name, None)
        return classification.requires_encryption

    def requires_audit(self, field_name: str) -> bool:
        """Verifica si campo requiere auditoría."""
        classification = self.classify(field_name, None)
        return classification.requires_audit
