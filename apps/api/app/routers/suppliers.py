"""Suppliers REST API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.supplier import SupplierCreate, SupplierResponse

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[SupplierResponse])
async def list_suppliers(request: Request):
    get_tenant_id(request)
    return []
