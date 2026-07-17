"""Staff REST API endpoints.

Staffing Context — Staff, Shift, Team management.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.schemas.staff import (
    ShiftCreate,
    ShiftResponse,
    StaffCreate,
    StaffResponse,
)

router = APIRouter(prefix="/staff", tags=["Staff"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[StaffResponse])
async def list_staff(
    request: Request,
    staff_type: str | None = None,
    employment_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[StaffResponse]:
    """List staff with optional filtering."""
    get_tenant_id(request)
    return []


@router.post("", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(request: Request, payload: StaffCreate) -> StaffResponse:
    """Register a new staff member."""
    get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Staff creation not yet implemented",
    )


@router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff(request: Request, staff_id: str) -> StaffResponse:
    """Get a specific staff member."""
    get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Staff retrieval not yet implemented",
    )


@router.post("/{staff_id}/terminate", response_model=StaffResponse)
async def terminate_staff(request: Request, staff_id: str) -> StaffResponse:
    """Terminate staff employment."""
    get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Staff termination not yet implemented",
    )


@router.get("/{staff_id}/shifts", response_model=list[ShiftResponse])
async def list_staff_shifts(
    request: Request,
    staff_id: str,
    limit: int = 50,
) -> list[ShiftResponse]:
    """List shifts for a staff member."""
    get_tenant_id(request)
    return []


@router.post("/{staff_id}/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def schedule_shift(
    request: Request,
    staff_id: str,
    payload: ShiftCreate,
) -> ShiftResponse:
    """Schedule a new shift for a staff member."""
    get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Shift scheduling not yet implemented",
    )
