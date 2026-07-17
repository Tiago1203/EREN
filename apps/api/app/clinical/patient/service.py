"""Patient service.

Application service: orchestrates domain operations and infrastructure.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.clinical.patient.events import PatientCreated, PatientDeleted, PatientUpdated
from app.clinical.patient.repository import PatientRepository
from app.infrastructure.events import EventBus

if TYPE_CHECKING:
    from app.models.patient import Patient


@dataclass
class PatientService:
    """Application service for patient operations.

    This service orchestrates:
    1. Domain logic (via aggregate methods)
    2. Persistence (via repository)
    3. Events (via event bus)

    It does NOT contain:
    - SQL queries (in repository)
    - HTTP handling (in router)
    - Authentication (in middleware)
    """

    repository: PatientRepository
    event_bus: EventBus

    async def create_patient(
        self,
        tenant_id: str,
        mrn: str,
        given_name: str,
        family_name: str,
        created_by: str | None = None,
        correlation_id: str | None = None,
        date_of_birth=None,
        gender=None,
        email=None,
        phone=None,
        blood_type=None,
        allergies=None,
    ) -> Patient:
        """Create a new patient.

        Returns:
            Created patient

        Raises:
            ValueError: If data is invalid
        """
        # Generate ID (UUID v7 for time-ordered IDs - fallback to v4 for compatibility)
        try:
            patient_id = str(uuid.uuid7())
        except AttributeError:
            patient_id = str(uuid.uuid4())

        # Create domain event (before saving)
        domain_event = PatientCreated(
            patient_id=patient_id,
            tenant_id=tenant_id,
            mrn=mrn,
            given_name=given_name,
            family_name=family_name,
            caused_by=created_by,
            correlation_id=correlation_id,
        )

        # Save via repository
        patient = await self.repository.save(
            tenant_id=tenant_id,
            patient_id=patient_id,
            mrn=mrn,
            given_name=given_name,
            family_name=family_name,
            created_by=created_by,
            date_of_birth=date_of_birth,
            gender=gender,
            email=email,
            phone=phone,
            blood_type=blood_type,
            allergies=allergies,
        )

        # Publish domain event
        await self.event_bus.publish(
            aggregate_type="Patient",
            aggregate_id=patient_id,
            event_type=domain_event.event_type,
            payload={
                "mrn": mrn,
                "given_name": given_name,
                "family_name": family_name,
                "created_by": created_by,
            },
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

        return patient

    async def get_patient(
        self,
        patient_id: str,
        tenant_id: str,
    ) -> Patient | None:
        """Get a patient by ID."""
        return await self.repository.get_by_id(patient_id, tenant_id)

    async def list_patients(
        self,
        tenant_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Patient], int]:
        """List patients for a tenant."""
        return await self.repository.list_by_tenant(tenant_id, page, page_size)

    async def update_patient(
        self,
        patient_id: str,
        tenant_id: str,
        expected_version: int,
        correlation_id: str | None = None,
        **updates,
    ) -> Patient | None:
        """Update a patient with optimistic locking."""
        patient = await self.repository.get_by_id(patient_id, tenant_id)
        if patient is None:
            return None

        # Track changes for event
        changes = dict(updates)

        # Update via repository with optimistic locking
        updated = await self.repository.update(patient, expected_version, **updates)
        if updated is None:
            return None  # Concurrent modification detected

        # Publish event
        domain_event = PatientUpdated(
            patient_id=patient_id,
            tenant_id=tenant_id,
            changes=changes,
            correlation_id=correlation_id,
        )

        await self.event_bus.publish(
            aggregate_type="Patient",
            aggregate_id=patient_id,
            event_type=domain_event.event_type,
            payload={"changes": changes, "version": expected_version + 1},
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

        return updated

    async def delete_patient(
        self,
        patient_id: str,
        tenant_id: str,
        deleted_by: str | None = None,
        delete_reason: str | None = None,
        correlation_id: str | None = None,
    ) -> bool:
        """Soft-delete a patient with metadata."""
        # Check exists first
        patient = await self.repository.get_by_id(patient_id, tenant_id)
        if patient is None:
            return False

        # Delete via repository with metadata
        success = await self.repository.soft_delete(
            patient_id,
            tenant_id,
            deleted_by=deleted_by,
            delete_reason=delete_reason,
        )
        if not success:
            return False

        # Publish event
        domain_event = PatientDeleted(
            patient_id=patient_id,
            tenant_id=tenant_id,
            caused_by=deleted_by,
            correlation_id=correlation_id,
        )

        await self.event_bus.publish(
            aggregate_type="Patient",
            aggregate_id=patient_id,
            event_type=domain_event.event_type,
            payload={"deleted_by": deleted_by, "delete_reason": delete_reason},
            tenant_id=tenant_id,
            correlation_id=correlation_id,
        )

        return True
