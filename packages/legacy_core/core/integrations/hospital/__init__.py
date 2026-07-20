"""Hospital Systems Integration - FHIR, HL7, DICOM."""
from dataclasses import dataclass


@dataclass
class HospitalSystemConfig:
    """Configuration for hospital systems."""
    fhir_base_url: str | None = None
    hl7_port: int = 2575
    dicom_ae_title: str | None = None
    dicom_host: str | None = None


@dataclass
class FHIRDevice:
    """FHIR Device resource."""
    id: str
    identifier: str
    status: str
    device_type: str


@dataclass
class HL7Message:
    """Parsed HL7 message."""
    message_type: str
    trigger_event: str
    segments: dict
