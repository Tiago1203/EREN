"""Domain service for Engineering Incident."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.shared import (
    DeviceId,
    EngineerId,
    IncidentId,
    Priority,
    Result,
    SafetyLevel,
    TenantId,
)

from ..entities import EngineeringIncident, Investigation
from ..repositories.incident_repository import IncidentRepository
from ..value_objects import IncidentStatus, Resolution, Symptom

if TYPE_CHECKING:
    pass


class IncidentService:
    """Domain service for Engineering Incident operations.

    This service orchestrates operations on the EngineeringIncident
    aggregate and coordinates with the repository.
    """

    def __init__(self, repository: IncidentRepository) -> None:
        self._repository = repository

    async def create_incident(
        self,
        tenant_id: TenantId,
        device_id: DeviceId,
        reported_by: EngineerId,
        symptom: Symptom,
        description: str,
        correlation_id: str | None = None,
    ) -> Result[EngineeringIncident, str]:
        """Create a new engineering incident."""
        incident = EngineeringIncident(
            id=IncidentId.generate(),
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=reported_by,
            symptom=symptom,
            description=description,
            priority=Priority.medium(),  # Default priority
            correlation_id=correlation_id,
        )

        result = await self._repository.save(incident)
        if result.is_err():
            return result

        saved_incident = result.unwrap()
        return Result.Ok(saved_incident)

    async def report_incident(
        self,
        tenant_id: TenantId,
        device_id: DeviceId,
        reported_by: EngineerId,
        symptom_description: str,
        description: str,
    ) -> Result[EngineeringIncident, str]:
        """Report a new incident and return with events."""
        symptom = Symptom(description=symptom_description)
        incident_result = await self.create_incident(
            tenant_id=tenant_id,
            device_id=device_id,
            reported_by=reported_by,
            symptom=symptom,
            description=description,
        )

        if incident_result.is_err():
            return incident_result

        incident = incident_result.unwrap()
        return Result.Ok(incident)

    async def triage_incident(
        self,
        incident_id: IncidentId,
        priority: Priority,
        safety_classification: SafetyLevel,
        triage_notes: str,
    ) -> Result[EngineeringIncident, str]:
        """Triage an incident and assign priority."""
        result = await self._repository.get_by_id(incident_id)
        if result.is_err():
            return result

        incident = result.unwrap()
        if incident is None:
            return Result.Err(f"Incident {incident_id} not found")

        if not incident.can_be_modified():
            return Result.Err(f"Incident {incident_id} is closed and cannot be modified")

        try:
            incident.triage(
                priority=priority,
                safety_classification=safety_classification,
                triage_notes=triage_notes,
                expected_version=incident.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(incident)

    async def assign_incident(
        self,
        incident_id: IncidentId,
        engineer_id: EngineerId,
    ) -> Result[EngineeringIncident, str]:
        """Assign an incident to an engineer."""
        result = await self._repository.get_by_id(incident_id)
        if result.is_err():
            return result

        incident = result.unwrap()
        if incident is None:
            return Result.Err(f"Incident {incident_id} not found")

        try:
            incident.assign(
                engineer_id=engineer_id,
                expected_version=incident.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(incident)

    async def resolve_incident(
        self,
        incident_id: IncidentId,
        resolution: Resolution,
        resolved_by: EngineerId,
        investigation: Investigation | None = None,
    ) -> Result[EngineeringIncident, str]:
        """Resolve an incident."""
        result = await self._repository.get_by_id(incident_id)
        if result.is_err():
            return result

        incident = result.unwrap()
        if incident is None:
            return Result.Err(f"Incident {incident_id} not found")

        actions_count = investigation.get_actions_count() if investigation else 0

        try:
            incident.resolve(
                resolution=resolution,
                resolved_by=resolved_by,
                actions_count=actions_count,
                expected_version=incident.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(incident)

    async def close_incident(
        self,
        incident_id: IncidentId,
        closed_by: EngineerId,
        feedback_content: str | None = None,
        recommendation_accepted: bool = False,
    ) -> Result[EngineeringIncident, str]:
        """Close a resolved incident."""
        result = await self._repository.get_by_id(incident_id)
        if result.is_err():
            return result

        incident = result.unwrap()
        if incident is None:
            return Result.Err(f"Incident {incident_id} not found")

        feedback = None
        if feedback_content:
            from ..value_objects import Feedback

            feedback = Feedback(feedback_type="neutral", content=feedback_content)

        try:
            incident.close(
                feedback=feedback,
                recommendation_accepted=recommendation_accepted,
                closed_by=closed_by,
                expected_version=incident.version,
            )
        except Exception as e:
            return Result.Err(str(e))

        return await self._repository.save(incident)

    async def get_incident(self, incident_id: IncidentId) -> Result[EngineeringIncident | None, str]:
        """Get an incident by ID."""
        return await self._repository.get_by_id(incident_id)

    async def get_open_incidents(
        self,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        """Get all open incidents for a tenant."""
        return await self._repository.get_open_incidents(tenant_id, limit)

    async def get_incidents_by_device(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        """Get all incidents for a device."""
        return await self._repository.get_by_device(device_id, tenant_id, limit)

    async def get_incidents_by_engineer(
        self,
        engineer_id: EngineerId,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        """Get all incidents assigned to an engineer."""
        return await self._repository.get_by_engineer(engineer_id, tenant_id, limit)
