"""Hospital Systems Integration - FHIR, HL7, DICOM."""
from dataclasses import dataclass

from core.integrations.hospital.fhir import (
    FHIRClient,
    FHIRDevice,
    FHIRPatient,
    FHIRObservation,
    FHIRResourceType,
    create_fhir_client,
)
from core.integrations.hospital.hl7 import (
    HL7Listener,
    HL7Message,
    HL7Parser,
    HL7Segment,
    HL7MessageType,
    create_hl7_listener,
)
from core.integrations.hospital.dicom import (
    DICOMClient,
    DICOMPatient,
    DICOMStudy,
    DICOMSeries,
    DICOMInstance,
    DICOMWebClient,
    DICOMPriority,
    create_dicom_client,
    create_dicom_web_client,
)


@dataclass
class HospitalSystemConfig:
    """Configuration for hospital systems."""
    fhir_base_url: str | None = None
    hl7_port: int = 2575
    dicom_ae_title: str | None = None
    dicom_host: str | None = None
    dicom_port: int = 11112


__all__ = [
    "FHIRClient",
    "FHIRDevice",
    "FHIRPatient",
    "FHIRObservation",
    "FHIRResourceType",
    "create_fhir_client",
    "HL7Listener",
    "HL7Message",
    "HL7Parser",
    "HL7Segment",
    "HL7MessageType",
    "create_hl7_listener",
    "DICOMClient",
    "DICOMPatient",
    "DICOMStudy",
    "DICOMSeries",
    "DICOMInstance",
    "DICOMWebClient",
    "DICOMPriority",
    "create_dicom_client",
    "create_dicom_web_client",
    "HospitalSystemConfig",
]
