"""Buildings REST API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.building import BuildingCreate, BuildingResponse

router = APIRouter(prefix="/buildings", tags=["Buildings"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[BuildingResponse])
async def list_buildings(request: Request):
    get_tenant_id(request)
    return []


@router.post("", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
async def create_building(request: Request, data: BuildingCreate):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(building_id: str, request: Request):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
