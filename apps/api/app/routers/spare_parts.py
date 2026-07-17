"""SpareParts REST API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.spare_part import SparePartCreate, SparePartResponse

router = APIRouter(prefix="/spare-parts", tags=["SpareParts"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[SparePartResponse])
async def list_spare_parts(request: Request):
    get_tenant_id(request)
    return []


@router.post("", response_model=SparePartResponse, status_code=status.HTTP_201_CREATED)
async def create_spare_part(request: Request, data: SparePartCreate):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
