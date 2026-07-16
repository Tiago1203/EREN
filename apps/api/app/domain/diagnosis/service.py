"""Diagnosis service.

Application service: orchestrates domain operations and infrastructure.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.domain.diagnosis.events import (
    DiagnosisAmended,
    DiagnosisDeleted,
    DiagnosisRecorded,
)
from app.domain.diagnosis.repository import DiagnosisRepository
from app.infrastructure.events import EventBus

if TYPE_CHECKING:
    from app.models.diagnosis import Diagnosis


@dataclass
class DiagnosisService:
    """Application service for diagnosis operations.

    This service orchestrates:
    1. Domain logic (via aggregate methods)
    2. Persistence (via repository)
    3. Events (via event bus)

    It does NOT contain:
    - SQL queries (in repository)
    - HTTP handling (in router)
    - Authentication (in middleware)
    """

    repository: DiagnosisRepository
    event_bus: EventBus

    async def record_diagnosis(
        self,
        tenant_id: str,
        patient_id: str,
        diagnosis_code: str,
        diagnosis_name: str,
        created_by: str | None = None,
        description: str | None = None,
        correlation_id: str | None = None,
    ) -> Diagnosis:
        """Record a new diagnosis.

        Returns:
            Created diagnosis

        Raises:
            ValueError: If data is invalid
        """
        try:
            diagnosis_id = str(uuid.uuid7())
        except AttributeError:
            diagnosis_id = str(uuid.uuid4())

        # Create domain event (before saving)
        domain_event = DiagnosisRecorded(
            diagnosis_id=diagnosis_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            diagnosis_code=diagnosis_code,
            diagnosis_name=diagnosis_name,
            description=description,
            caused_by=created_by,
            correlation_id=correlation_id,
        )

        # Save via repository
        diagnosis = await self.repository.save(
            tenant_id=tenant_id,
            diagnosis_id=diagnosis_id,
            patient_id=patient_id,
            diagnosis_code=diagnosis_code,
            diagnosis_name=diagnosis_name,
            created_by=created_by,
            description=description,
        )

        # Publish domain event
        await self.event_bus.publish(
            aggregate_type="Diagnosis",
            aggregate_id=diagnosis_id,
            event_type=domain_event.event_type,
            payload={
                "diagnosis_code": diagnosis_code,
                "diagnosis_name": diagnosis_name,
                "description": description,
                "created_by": created_by,
            },
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

        return diagnosis

    async def get_diagnosis(
        self,
        diagnosis_id: str,
        tenant_id: str,
    ) -> Diagnosis | None:
        """Get a diagnosis by ID."""
        return await self.repository.get_by_id(diagnosis_id, tenant_id)

    async def list_diagnoses_by_patient(
        self,
        patient_id: str,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Diagnosis], int]:
        """List diagnoses for a patient."""
        return await self.repository.list_by_patient(patient_id, tenant_id, page, page_size)

    async def list_diagnoses_by_tenant(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Diagnosis], int]:
        """List diagnoses for a tenant."""
        return await self.repository.list_by_tenant(tenant_id, page, page_size)

    async def amend_diagnosis(
        self,
        diagnosis_id: str,
        tenant_id: str,
        expected_version: int,
        correlation_id: str | None = None,
        **updates,
    ) -> Diagnosis | None:
        """Amend a diagnosis with optimistic locking."""
        diagnosis = await self.repository.get_by_id(diagnosis_id, tenant_id)
        if diagnosis is None:
            return None

        changes = dict(updates)

        updated = await self.repository.update(diagnosis, expected_version, **updates)
        if updated is None:
            return None

        domain_event = DiagnosisAmended(
            diagnosis_id=diagnosis_id,
            tenant_id=tenant_id,
            patient_id=diagnosis.patient_id,
            changes=changes,
            previous_version=expected_version,
            correlation_id=correlation_id,
        )

        await self.event_bus.publish(
            aggregate_type="Diagnosis",
            aggregate_id=diagnosis_id,
            event_type=domain_event.event_type,
            payload={
                "changes": changes,
                "version": expected_version + 1,
            },
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

        return updated

    async def delete_diagnosis(
        self,
        diagnosis_id: str,
        tenant_id: str,
        deleted_by: str | None = None,
        delete_reason: str | None = None,
        correlation_id: str | None = None,
    ) -> bool:
        """Soft-delete a diagnosis with metadata."""
        diagnosis = await self.repository.get_by_id(diagnosis_id, tenant_id)
        if diagnosis is None:
            return False

        success = await self.repository.soft_delete(
            diagnosis_id,
            tenant_id,
            deleted_by=deleted_by,
            delete_reason=delete_reason,
        )
        if not success:
            return False

        domain_event = DiagnosisDeleted(
            diagnosis_id=diagnosis_id,
            tenant_id=tenant_id,
            patient_id=diagnosis.patient_id,
            caused_by=deleted_by,
            correlation_id=correlation_id,
        )

        await self.event_bus.publish(
            aggregate_type="Diagnosis",
            aggregate_id=diagnosis_id,
            event_type=domain_event.event_type,
            payload={"deleted_by": deleted_by, "delete_reason": delete_reason},
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

        return True
