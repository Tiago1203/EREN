"""Beds REST API endpoints.

Capacity Context — Bed lifecycle operations.
All endpoints enforce tenant isolation.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.schemas.bed import (
    BedCreate,
    BedListResponse,
    BedOccupyRequest,
    BedResponse,
)

router = APIRouter(prefix="/beds", tags=["Beds"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=BedListResponse)
async def list_beds(
    request: Request,
    status: str | None = None,
    bed_type: str | None = None,
    campus_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> BedListResponse:
    """List beds with optional filtering."""
    tenant_id = get_tenant_id(request)

    # TODO: Implement SQLAlchemy repository
    # Until then, return empty response
    return BedListResponse(
        beds=[],
        total=0,
        available_count=0,
        occupied_count=0,
    )


@router.post("", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
async def create_bed(
    request: Request,
    payload: BedCreate,
    room_id: str,
) -> BedResponse:
    """Create a new bed in a room."""
    tenant_id = get_tenant_id(request)

    # TODO: Implement Bed aggregate + repository
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bed creation not yet implemented",
    )


@router.get("/{bed_id}", response_model=BedResponse)
async def get_bed(request: Request, bed_id: str) -> BedResponse:
    """Get a specific bed."""
    get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bed retrieval not yet implemented",
    )


@router.post("/{bed_id}/occupy", response_model=BedResponse)
async def occupy_bed(
    request: Request,
    bed_id: str,
    payload: BedOccupyRequest,
) -> BedResponse:
    """Occupy a bed with a patient."""
    tenant_id = get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bed occupy not yet implemented",
    )


@router.post("/{bed_id}/vacate", response_model=BedResponse)
async def vacate_bed(request: Request, bed_id: str) -> BedResponse:
    """Vacate a bed (patient leaves)."""
    tenant_id = get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bed vacate not yet implemented",
    )


@router.post("/{bed_id}/block", response_model=BedResponse)
async def block_bed(request: Request, bed_id: str) -> BedResponse:
    """Block a bed temporarily."""
    tenant_id = get_tenant_id(request)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bed block not yet implemented",
    )
