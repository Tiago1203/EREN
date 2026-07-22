"""FHIR Client for Hospital Systems Integration."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import httpx


class FHIRResourceType(str, Enum):
    DEVICE = "Device"
    PATIENT = "Patient"
    LOCATION = "Location"
    ORGANIZATION = "Organization"
    OBSERVATION = "Observation"
    ENCOUNTER = "Encounter"


@dataclass
class FHIRDevice:
    """FHIR Device resource."""
    id: str
    identifier: str
    status: str
    device_type: str
    manufacturer: str | None = None
    model: str | None = None
    version: str | None = None


@dataclass
class FHIRPatient:
    """FHIR Patient resource."""
    id: str
    identifier: str
    name: str
    birth_date: str | None = None
    gender: str | None = None


@dataclass
class FHIRObservation:
    """FHIR Observation resource."""
    id: str
    status: str
    code: str
    value: str | None
    device_id: str | None = None
    effective_datetime: str | None = None


class FHIRClient:
    """
    FHIR R4 Client for hospital systems integration.
    
    Supports Device, Patient, Location, and Observation resources.
    """

    def __init__(
        self,
        base_url: str,
        auth_token: str | None = None,
        timeout: float = 30.0,
    ):
        """
        Initialize FHIR client.
        
        Args:
            base_url: FHIR server base URL
            auth_token: Optional authentication token
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        headers = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        self._client = httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def get_device(self, device_id: str) -> FHIRDevice | None:
        """
        Retrieve a Device resource by ID.
        
        Args:
            device_id: Device resource ID
            
        Returns:
            FHIRDevice if found, None otherwise
        """
        response = await self._client.get(
            f"{self.base_url}/Device/{device_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_device(data)
        return None

    async def search_devices(
        self,
        status: str | None = None,
        device_type: str | None = None,
        organization: str | None = None,
    ) -> list[FHIRDevice]:
        """
        Search for Device resources.
        
        Args:
            status: Filter by device status
            device_type: Filter by device type
            organization: Filter by managing organization
            
        Returns:
            List of matching FHIRDevice resources
        """
        params = {}
        if status:
            params["status"] = status
        if device_type:
            params["type"] = device_type
        if organization:
            params["organization"] = organization
        
        response = await self._client.get(
            f"{self.base_url}/Device",
            params=params,
        )
        
        if response.status_code == 200:
            bundle = response.json()
            devices = []
            for entry in bundle.get("entry", []):
                if entry.get("resource", {}).get("resourceType") == "Device":
                    devices.append(self._parse_device(entry["resource"]))
            return devices
        return []

    async def create_device(
        self,
        identifier: str,
        status: str,
        device_type: str,
        manufacturer: str | None = None,
        model: str | None = None,
    ) -> FHIRDevice | None:
        """
        Create a new Device resource.
        
        Args:
            identifier: Device identifier
            status: Device status (active, inactive, entered-in-error)
            device_type: Type of device
            manufacturer: Device manufacturer
            model: Device model
            
        Returns:
            Created FHIRDevice if successful
        """
        resource = {
            "resourceType": "Device",
            "identifier": [
                {
                    "system": "urn:eren:device",
                    "value": identifier,
                }
            ],
            "status": status,
            "type": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": device_type,
                    }
                ]
            },
        }
        
        if manufacturer:
            resource["manufacturer"] = manufacturer
        if model:
            resource["modelNumber"] = model
        
        response = await self._client.post(
            f"{self.base_url}/Device",
            json=resource,
        )
        
        if response.status_code in (200, 201):
            return self._parse_device(response.json())
        return None

    async def update_device(
        self,
        device_id: str,
        status: str | None = None,
        **kwargs,
    ) -> FHIRDevice | None:
        """
        Update an existing Device resource.
        
        Args:
            device_id: Device resource ID
            status: New device status
            **kwargs: Additional fields to update
            
        Returns:
            Updated FHIRDevice if successful
        """
        # Get existing resource
        existing = await self.get_device(device_id)
        if not existing:
            return None
        
        # Build update payload
        resource = {
            "resourceType": "Device",
            "id": device_id,
            "identifier": [
                {
                    "system": "urn:eren:device",
                    "value": existing.identifier,
                }
            ],
        }
        
        if status:
            resource["status"] = status
        
        for key, value in kwargs.items():
            if key not in ("id", "resourceType"):
                resource[key] = value
        
        response = await self._client.put(
            f"{self.base_url}/Device/{device_id}",
            json=resource,
        )
        
        if response.status_code in (200, 201):
            return self._parse_device(response.json())
        return None

    async def get_patient(self, patient_id: str) -> FHIRPatient | None:
        """
        Retrieve a Patient resource by ID.
        
        Args:
            patient_id: Patient resource ID
            
        Returns:
            FHIRPatient if found, None otherwise
        """
        response = await self._client.get(
            f"{self.base_url}/Patient/{patient_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_patient(data)
        return None

    async def create_observation(
        self,
        code: str,
        value: str,
        device_id: str | None = None,
        status: str = "final",
    ) -> FHIRObservation | None:
        """
        Create an Observation resource.
        
        Args:
            code: Observation code (e.g., SNOMED code)
            value: Observation value
            device_id: Associated device ID
            status: Observation status
            
        Returns:
            Created FHIRObservation if successful
        """
        resource = {
            "resourceType": "Observation",
            "status": status,
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": code,
                    }
                ]
            },
            "valueString": value,
            "effectiveDateTime": datetime.utcnow().isoformat(),
        }
        
        if device_id:
            resource["device"] = {
                "reference": f"Device/{device_id}"
            }
        
        response = await self._client.post(
            f"{self.base_url}/Observation",
            json=resource,
        )
        
        if response.status_code in (200, 201):
            data = response.json()
            return FHIRObservation(
                id=data.get("id", ""),
                status=data.get("status", ""),
                code=code,
                value=value,
                device_id=device_id,
                effective_datetime=data.get("effectiveDateTime"),
            )
        return None

    def _parse_device(self, data: dict[str, Any]) -> FHIRDevice:
        """Parse FHIR Device resource to FHIRDevice dataclass."""
        # Extract identifier
        identifier = ""
        for ident in data.get("identifier", []):
            if ident.get("system") == "urn:eren:device":
                identifier = ident.get("value", "")
                break
        if not identifier:
            identifier = data.get("id", "")
        
        # Extract device type
        device_type = ""
        type_coding = data.get("type", {}).get("coding", [])
        if type_coding:
            device_type = type_coding[0].get("code", "")
        
        return FHIRDevice(
            id=data.get("id", ""),
            identifier=identifier,
            status=data.get("status", ""),
            device_type=device_type,
            manufacturer=data.get("manufacturer"),
            model=data.get("modelNumber"),
            version=data.get("versionNumber"),
        )

    def _parse_patient(self, data: dict[str, Any]) -> FHIRPatient:
        """Parse FHIR Patient resource to FHIRPatient dataclass."""
        # Extract identifier
        identifier = ""
        for ident in data.get("identifier", []):
            identifier = ident.get("value", "")
            break
        
        # Extract name
        name_parts = data.get("name", [{}])[0]
        name = ""
        if name_parts:
            given = name_parts.get("given", [])
            family = name_parts.get("family", "")
            name = f"{' '.join(given)} {family}".strip()
        
        return FHIRPatient(
            id=data.get("id", ""),
            identifier=identifier,
            name=name,
            birth_date=data.get("birthDate"),
            gender=data.get("gender"),
        )


# Factory function
def create_fhir_client(
    base_url: str,
    auth_token: str | None = None,
) -> FHIRClient:
    """
    Create a FHIR client instance.
    
    Args:
        base_url: FHIR server base URL
        auth_token: Optional authentication token
        
    Returns:
        Configured FHIRClient instance
    """
    return FHIRClient(base_url=base_url, auth_token=auth_token)
