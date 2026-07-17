"""Units REST API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.unit import UnitCreate, UnitResponse

router = APIRouter(prefix="/units", tags=["Units"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[UnitResponse])
async def list_units(request: Request):
    get_tenant_id(request)
    return []


@router.post("", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(request: Request, data: UnitCreate):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
