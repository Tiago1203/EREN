"""Campuses REST API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.campus import CampusCreate, CampusResponse, CampusUpdate

router = APIRouter(prefix="/campuses", tags=["Campuses"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[CampusResponse])
async def list_campuses(request: Request):
    tenant_id = get_tenant_id(request)
    return []


@router.post("", response_model=CampusResponse, status_code=status.HTTP_201_CREATED)
async def create_campus(request: Request, data: CampusCreate):
    tenant_id = get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.get("/{campus_id}", response_model=CampusResponse)
async def get_campus(campus_id: str, request: Request):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.patch("/{campus_id}", response_model=CampusResponse)
async def update_campus(campus_id: str, data: CampusUpdate, request: Request):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
