"""Clinical Context Types for EREN OS.

Type definitions for clinical context modeling including
patients, professionals, episodes, and medical records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Entity Types
# =============================================================================


class ClinicalEntityType(str, Enum):
    """Types of clinical entities."""

    PATIENT = "patient"
    PROFESSIONAL = "professional"
    HOSPITAL = "hospital"
    EPISODE = "episode"
    CONSULTATION = "consultation"
    PROCEDURE = "procedure"
    MEDICATION = "medication"
    ALLERGY = "allergy"
    LAB_RESULT = "lab_result"
    VITAL_SIGNS = "vital_signs"
    EQUIPMENT = "equipment"
    LOCATION = "location"


# =============================================================================
# Patient
# =============================================================================


@dataclass
class Patient:
    """Patient information."""

    patient_id: str
    mrn: str = ""  # Medical Record Number
    first_name: str = ""
    last_name: str = ""
    date_of_birth: datetime | None = None
    gender: str = ""  # M, F, O
    blood_type: str = ""
    allergies: list[str] = field(default_factory=list)
    emergency_contact: dict = field(default_factory=dict)
    insurance_id: str = ""
    address: dict = field(default_factory=dict)
    phone: str = ""
    email: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def age(self) -> int | None:
        """Calculate patient age."""
        if not self.date_of_birth:
            return None
        today = datetime.now(UTC)
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
            today.month == self.date_of_birth.month and today.day < self.date_of_birth.day
        ):
            age -= 1
        return age

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}".strip()


# =============================================================================
# Professional
# =============================================================================


@dataclass
class Professional:
    """Healthcare professional."""

    professional_id: str
    employee_id: str = ""
    first_name: str = ""
    last_name: str = ""
    specialty: str = ""
    license_number: str = ""
    department: str = ""
    role: str = ""  # physician, nurse, technician
    hospital_id: str = ""
    email: str = ""
    phone: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Episode & Consultation
# =============================================================================


@dataclass
class ClinicalEpisode:
    """A clinical episode (visit, admission)."""

    episode_id: str
    patient_id: str
    hospital_id: str
    episode_type: str = ""  # inpatient, outpatient, emergency
    admission_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    discharge_date: datetime | None = None
    status: str = "active"  # active, discharged, transferred
    chief_complaint: str = ""
    diagnosis: list[str] = field(default_factory=list)
    procedures_performed: list[str] = field(default_factory=list)
    attending_professional_id: str = ""
    room_id: str = ""
    bed_id: str = ""
    notes: str = ""


@dataclass
class Consultation:
    """A consultation within an episode."""

    consultation_id: str
    episode_id: str
    patient_id: str
    professional_id: str
    consultation_type: str = ""  # initial, follow_up, specialty
    date: datetime = field(default_factory=lambda: datetime.now(UTC))
    chief_complaint: str = ""
    history: str = ""
    examination: str = ""
    assessment: str = ""
    plan: str = ""
    icd_codes: list[str] = field(default_factory=list)
    medications: list[dict] = field(default_factory=list)
    orders: list[dict] = field(default_factory=list)


# =============================================================================
# Medical Records
# =============================================================================


@dataclass
class Medication:
    """Medication record."""

    medication_id: str
    patient_id: str
    name: str
    dosage: str = ""
    frequency: str = ""  # QD, BID, TID, etc.
    route: str = ""  # oral, IV, IM, etc.
    start_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_date: datetime | None = None
    prescribing_professional_id: str = ""
    indication: str = ""
    status: str = "active"  # active, discontinued, completed
    refills_remaining: int = 0


@dataclass
class Allergy:
    """Patient allergy record."""

    allergy_id: str
    patient_id: str
    allergen: str
    reaction: str = ""
    severity: str = "mild"  # mild, moderate, severe
    onset_date: datetime | None = None
    verified: bool = False
    verified_by: str = ""


@dataclass
class LabResult:
    """Laboratory result."""

    lab_result_id: str
    patient_id: str
    test_name: str
    test_code: str = ""  # LOINC code
    value: str = ""
    unit: str = ""
    reference_range: str = ""
    is_abnormal: bool = False
    specimen_type: str = ""
    collected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resulted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ordered_by: str = ""


@dataclass
class VitalSigns:
    """Vital signs measurement."""

    vital_signs_id: str
    patient_id: str
    episode_id: str | None = None
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    recorded_by: str = ""

    # Standard vitals
    heart_rate: int | None = None  # bpm
    systolic_bp: int | None = None  # mmHg
    diastolic_bp: int | None = None  # mmHg
    respiratory_rate: int | None = None  # breaths/min
    temperature: float | None = None  # °C
    oxygen_saturation: int | None = None  # %

    # Additional
    pain_level: int | None = None  # 0-10
    weight: float | None = None  # kg
    height: float | None = None  # cm
    bmi: float | None = None


# =============================================================================
# Clinical Context
# =============================================================================


@dataclass
class ClinicalContext:
    """Aggregated clinical context for a patient."""

    context_id: str
    patient: Patient
    episodes: list[ClinicalEpisode] = field(default_factory=list)
    consultations: list[Consultation] = field(default_factory=list)
    medications: list[Medication] = field(default_factory=list)
    allergies: list[Allergy] = field(default_factory=list)
    lab_results: list[LabResult] = field(default_factory=list)
    vital_signs: list[VitalSigns] = field(default_factory=list)

    current_episode: ClinicalEpisode | None = None
    active_medications: list[Medication] = field(default_factory=list)

    temporal_range: tuple[datetime, datetime] | None = None
    relevance_score: float = 1.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "context_id": self.context_id,
            "patient": {
                "patient_id": self.patient.patient_id,
                "full_name": self.patient.full_name,
                "age": self.patient.age,
            },
            "current_episode": self.current_episode.episode_id if self.current_episode else None,
            "episode_count": len(self.episodes),
            "active_medication_count": len(self.active_medications),
            "allergy_count": len(self.allergies),
            "temporal_range": (
                self.temporal_range[0].isoformat() if self.temporal_range else None,
                self.temporal_range[1].isoformat() if self.temporal_range else None,
            ),
            "relevance_score": self.relevance_score,
        }


# =============================================================================
# Context Builder
# =============================================================================


@dataclass
class ContextBuildRequest:
    """Request for building clinical context."""

    request_id: str
    patient_id: str
    include_episodes: bool = True
    include_consultations: bool = True
    include_medications: bool = True
    include_labs: bool = True
    include_vitals: bool = True
    max_temporal_days: int = 365
    relevance_filter: float = 0.5


@dataclass
class ContextBuildResult:
    """Result of building clinical context."""

    request_id: str
    context: ClinicalContext | None = None
    build_time_ms: float = 0.0
    data_sources_queried: list[str] = field(default_factory=list)
    entities_retrieved: int = 0
    success: bool = True
    error: str = ""


# =============================================================================
# Context Policies
# =============================================================================


class PrivacyLevel(str, Enum):
    """Privacy levels for clinical data."""

    PUBLIC = "public"
    BASIC = "basic"  # De-identified
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"  # Only authorized


@dataclass
class ContextPolicy:
    """Policy for clinical context handling."""

    privacy_level: PrivacyLevel = PrivacyLevel.SENSITIVE
    retain_days: int = 365
    allow_sharing: bool = False
    required_roles: list[str] = field(default_factory=list)
    mask_identifiers: bool = True
    audit_access: bool = True
