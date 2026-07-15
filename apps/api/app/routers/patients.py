"""Patient endpoints.

CRUD operations for patients.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.events.publisher import EventPublisher
from app.middleware.request_context import get_request_context
from app.models.patient import Patient
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


def get_tenant_id(request: Request) -> str:
    """Extract tenant_id from request context."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant not resolved",
        )
    return tenant_id


def get_current_user_id(request: Request) -> str | None:
    """Extract current user ID from request context."""
    principal = getattr(request.state, "principal", None)
    if principal:
        return principal.principal_id
    return None


def get_correlation_id(request: Request) -> str | None:
    """Extract correlation_id from request context."""
    return getattr(request.state, "request_id", None)


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Patient:
    """Create a new patient.

    Requires authentication and valid tenant context.
    Publishes PatientCreated event via outbox pattern.
    """
    created_by = get_current_user_id(request)
    correlation_id = get_correlation_id(request)

    # Generate UUID v7 (time-ordered)
    patient_id = str(uuid.uuid7())

    # Create patient
    patient = Patient(
        id=patient_id,
        tenant_id=tenant_id,
        mrn=patient_data.mrn,
        given_name=patient_data.given_name,
        family_name=patient_data.family_name,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        email=patient_data.email,
        phone=patient_data.phone,
        blood_type=patient_data.blood_type,
        allergies=patient_data.allergies,
        created_by=created_by,
    )

    db.add(patient)

    # Publish PatientCreated event via outbox
    event_publisher = EventPublisher(db)
    await event_publisher.publish(
        aggregate_type="Patient",
        aggregate_id=patient_id,
        event_type="PatientCreated",
        payload={
            "mrn": patient_data.mrn,
            "given_name": patient_data.given_name,
            "family_name": patient_data.family_name,
            "created_by": created_by,
        },
        tenant_id=tenant_id,
        correlation_id=correlation_id,
    )

    await db.commit()
    await db.refresh(patient)

    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Patient:
    """Get a patient by ID.

    Requires authentication and valid tenant context.
    """
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.tenant_id == tenant_id,
        )
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


@router.get("", response_model=PatientListResponse)
async def list_patients(
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 50,
) -> PatientListResponse:
    """List patients for the current tenant.

    Requires authentication and valid tenant context.
    """
    offset = (page - 1) * page_size

    # Count total
    count_result = await db.execute(
        select(func.count(Patient.id)).where(Patient.tenant_id == tenant_id)
    )
    total = count_result.scalar() or 0

    # Get patients
    result = await db.execute(
        select(Patient)
        .where(Patient.tenant_id == tenant_id)
        .order_by(Patient.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    patients = list(result.scalars().all())

    return PatientListResponse(
        items=patients,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Patient:
    """Update a patient.

    Requires authentication and valid tenant context.
    """
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.tenant_id == tenant_id,
        )
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # Update fields
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    # Publish PatientUpdated event
    event_publisher = EventPublisher(db)
    await event_publisher.publish(
        aggregate_type="Patient",
        aggregate_id=patient_id,
        event_type="PatientUpdated",
        payload={"changes": update_data},
        tenant_id=tenant_id,
    )

    await db.commit()
    await db.refresh(patient)

    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft-delete a patient.

    Requires authentication and valid tenant context.
    """
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.tenant_id == tenant_id,
        )
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # Soft delete
    patient.is_active = False

    # Publish PatientDeleted event
    event_publisher = EventPublisher(db)
    await event_publisher.publish(
        aggregate_type="Patient",
        aggregate_id=patient_id,
        event_type="PatientDeleted",
        payload={"deleted_by": get_current_user_id(None)},
        tenant_id=tenant_id,
    )

    await db.commit()
