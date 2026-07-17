"""Organizations REST API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.organization import OrganizationCreate, OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["Organizations"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(request: Request):
    get_tenant_id(request)
    return []


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(request: Request, data: OrganizationCreate):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(organization_id: str, request: Request):
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
