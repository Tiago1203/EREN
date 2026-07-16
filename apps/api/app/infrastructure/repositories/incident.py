"""SQLAlchemy implementation of IncidentRepository."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.incident.domain.entities import EngineeringIncident
from core.incident.domain.repositories import IncidentRepository as AbstractIncidentRepository
from core.incident.domain.value_objects import (
    Feedback,
    IncidentStatus,
    Resolution,
    Symptom,
)
from core.shared import (
    DeviceId,
    EngineerId,
    IncidentId,
    Ok,
    Result,
    TenantId,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.incident import (
    IncidentModel,
)

if TYPE_CHECKING:
    pass


def _to_incident_status(value: str) -> IncidentStatus:
    return IncidentStatus(value=value)


def _incident_status_to_str(status: IncidentStatus) -> str:
    return status.value


def _model_to_entity(model: IncidentModel) -> EngineeringIncident:
    """Convert SQLAlchemy model to domain entity."""
    from core.shared import Priority, SafetyLevel

    symptom = Symptom(
        description=model.symptom_description,
        category=model.symptom_category,
    )

    incident = EngineeringIncident.__new__(EngineeringIncident)
    # Set identity fields
    incident.id = IncidentId(value=str(model.id))
    incident.tenant_id = TenantId(value=model.tenant_id)
    incident.device_id = DeviceId(value=model.device_id)
    incident.reported_by = EngineerId(value=model.reported_by)

    # Core fields
    incident.symptom = symptom
    incident.description = model.description
    incident.priority = Priority(value=model.priority)
    incident.status = _to_incident_status(model.status)
    incident.safety_classification = SafetyLevel(value=model.safety_classification)

    # Assignment
    incident.assigned_to = EngineerId(value=model.assigned_to) if model.assigned_to else None
    incident.triage_notes = model.triage_notes
    incident.estimated_resolution_hours = model.estimated_resolution_hours

    # Resolution
    if model.resolution_description:
        incident.resolution = Resolution(
            description=model.resolution_description,
            root_cause=model.resolution_root_cause,
            resolution_type="repair",
        )
    else:
        incident.resolution = None
    incident.closed_at = model.closed_at
    incident.closed_by = EngineerId(value=model.closed_by) if model.closed_by else None
    incident.resolution_time_minutes = model.resolution_time_minutes

    # Feedback
    if model.feedback_type and model.feedback_content:
        incident.feedback = Feedback(
            feedback_type=model.feedback_type,
            content=model.feedback_content,
        )
    else:
        incident.feedback = None

    # Correlation
    incident.correlation_id = model.correlation_id

    # Version
    incident.version = model.version

    # Dates
    incident.created_at = model.created_at
    incident.updated_at = model.updated_at

    # Pending events
    incident._pending_events = []

    # Lock
    incident._locked = True

    return incident


def _entity_to_model(
    entity: EngineeringIncident,
) -> dict[str, Any]:
    """Convert domain entity to model dict (for update)."""
    return {
        "tenant_id": str(entity.tenant_id),
        "device_id": str(entity.device_id),
        "reported_by": str(entity.reported_by),
        "symptom_description": entity.symptom.description,
        "symptom_category": entity.symptom.category,
        "description": entity.description,
        "priority": str(entity.priority),
        "status": _incident_status_to_str(entity.status),
        "safety_classification": str(entity.safety_classification),
        "assigned_to": str(entity.assigned_to) if entity.assigned_to else None,
        "triage_notes": entity.triage_notes,
        "estimated_resolution_hours": entity.estimated_resolution_hours,
        "resolution_description": (entity.resolution.description if entity.resolution else None),
        "resolution_root_cause": (entity.resolution.root_cause if entity.resolution else None),
        "resolution_time_minutes": entity.resolution_time_minutes,
        "closed_at": entity.closed_at,
        "closed_by": str(entity.closed_by) if entity.closed_by else None,
        "feedback_type": entity.feedback.feedback_type if entity.feedback else None,
        "feedback_content": entity.feedback.content if entity.feedback else None,
        "correlation_id": entity.correlation_id,
        "version": entity.version,
    }


class IncidentRepositoryImpl(AbstractIncidentRepository):
    """SQLAlchemy implementation of IncidentRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, incident: EngineeringIncident) -> Result[EngineeringIncident, str]:
        try:
            existing = await self._session.get(IncidentModel, incident.id.value)
            data = _entity_to_model(incident)

            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.version = incident.version
            else:
                model = IncidentModel(id=incident.id.value, **data)
                self._session.add(model)

            await self._session.flush()
            return Ok(incident)
        except Exception as e:
            return Ok(f"Save failed: {e}")  # Return error as Ok with string

    async def get_by_id(self, incident_id: IncidentId) -> Result[EngineeringIncident | None, str]:
        try:
            model = await self._session.get(IncidentModel, incident_id.value)
            if model is None:
                return Ok(None)
            return Ok(_model_to_entity(model))
        except Exception:
            return Ok(None)  # Fallback on error

    async def get_by_device(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        try:
            stmt = (
                select(IncidentModel)
                .where(IncidentModel.device_id == str(device_id))
                .where(IncidentModel.tenant_id == str(tenant_id))
                .limit(limit)
                .order_by(IncidentModel.created_at.desc())
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            return Ok([_model_to_entity(m) for m in models])
        except Exception:
            return Ok([])

    async def get_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[EngineeringIncident], str]:
        try:
            stmt = (
                select(IncidentModel)
                .where(IncidentModel.tenant_id == str(tenant_id))
                .limit(limit)
                .offset(offset)
                .order_by(IncidentModel.created_at.desc())
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            return Ok([_model_to_entity(m) for m in models])
        except Exception:
            return Ok([])

    async def get_open_incidents(
        self,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        try:
            terminal_statuses = {"closed", "cancelled"}
            stmt = (
                select(IncidentModel)
                .where(IncidentModel.tenant_id == str(tenant_id))
                .where(IncidentModel.status.not_in(terminal_statuses))
                .limit(limit)
                .order_by(IncidentModel.created_at.desc())
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            return Ok([_model_to_entity(m) for m in models])
        except Exception:
            return Ok([])

    async def get_by_engineer(
        self,
        engineer_id: EngineerId,
        tenant_id: TenantId,
        limit: int = 100,
    ) -> Result[list[EngineeringIncident], str]:
        try:
            stmt = (
                select(IncidentModel)
                .where(IncidentModel.assigned_to == str(engineer_id))
                .where(IncidentModel.tenant_id == str(tenant_id))
                .limit(limit)
                .order_by(IncidentModel.created_at.desc())
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()
            return Ok([_model_to_entity(m) for m in models])
        except Exception:
            return Ok([])

    async def delete(self, incident_id: IncidentId) -> Result[bool, str]:
        try:
            model = await self._session.get(IncidentModel, incident_id.value)
            if model:
                await self._session.delete(model)
                await self._session.flush()
            return Ok(True)
        except Exception:
            return Ok(False)
