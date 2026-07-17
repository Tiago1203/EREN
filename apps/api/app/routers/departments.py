"""Departments REST API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])


def get_tenant_id(request: Request) -> str:
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(request: Request) -> list[DepartmentResponse]:
    get_tenant_id(request)
    return []


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(request: Request, payload: DepartmentCreate) -> DepartmentResponse:
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not yet implemented")


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(request: Request, department_id: str) -> DepartmentResponse:
    get_tenant_id(request)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not yet implemented")
