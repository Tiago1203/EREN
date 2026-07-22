"""
EREN Integrations Module

Connects EREN with external systems:
- Hospital Systems (FHIR, HL7, DICOM)
- Medical Devices (Philips, GE, Dräger, Mindray)
- Enterprise (ServiceNow, SAP, Maximo, Azure AD)
"""
__version__ = "1.0.0"

from core.PHASE_3.integrations.hospital import (
    FHIRClient,
    HL7Listener,
    DICOMClient,
    DICOMWebClient,
    HospitalSystemConfig,
)
from core.PHASE_3.integrations.devices import (
    MedicalDeviceAdapter,
    DeviceAdapterRegistry,
    PhilipsIntelliVueAdapter,
    GEHealthcareAdapter,
    DraegerMedicalAdapter,
    MindrayAdapter,
    get_adapter_registry,
)

__all__ = [
    "FHIRClient",
    "HL7Listener",
    "DICOMClient",
    "DICOMWebClient",
    "HospitalSystemConfig",
    "MedicalDeviceAdapter",
    "DeviceAdapterRegistry",
    "PhilipsIntelliVueAdapter",
    "GEHealthcareAdapter",
    "DraegerMedicalAdapter",
    "MindrayAdapter",
    "get_adapter_registry",
]
