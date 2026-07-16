"""Work Order lifecycle REST API endpoints.

Full CRUD + lifecycle operations for biomedical maintenance work orders.
All endpoints enforce tenant isolation and optimistic locking.
"""

from __future__ import annotations

from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.work_order import WorkOrderRepository, SQLAlchemyWorkOrderRepository, WorkOrderService
from app.infrastructure.messaging.outbox import TransactionalOutbox
from app.schemas.work_order import (
    ErrorResponse,
    SortOrder,
    WorkOrderAssign,
    WorkOrderCancel,
    WorkOrderComplete,
    WorkOrderCreate,
    WorkOrderDeleteResponse,
    WorkOrderHold,
    WorkOrderListResponse,
    WorkOrderResponse,
    WorkOrderSchedule,
    WorkOrderUpdate,
)

router = APIRouter(prefix="/work-orders", tags=["Work Orders"])


def get_tenant_id(request: Request) -> str:
    tenant_id: str | None = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant not resolved")
    return tenant_id


def get_current_user_id(request: Request) -> str | None:
    principal = getattr(request.state, "principal", None)
    if principal is not None:
        pid = getattr(principal, "principal_id", None)
        return str(pid) if pid is not None else None
    return None


def get_correlation_id(request: Request) -> str | None:
    rid = getattr(request.state, "request_id", None)
    return str(rid) if rid is not None else None


async def get_work_order_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderService:
    repository = SQLAlchemyWorkOrderRepository(db)
    outbox = TransactionalOutbox(db)
    return WorkOrderService(repository=repository, outbox=outbox)


def _to_response(wo: object) -> WorkOrderResponse:
    d = wo.__dict__
    return WorkOrderResponse(
        id=str(d.get("id", "")),
        tenant_id=d.get("tenant_id", ""),
        device_id=str(d.get("device_id", "")),
        work_order_type=d.get("work_order_type", ""),
        description=d.get("description", ""),
        notes=d.get("notes"),
        resolution_summary=d.get("resolution_summary"),
        cancellation_reason=d.get("cancellation_reason"),
        priority=d.get("priority", "medium"),
        status=d.get("status", "draft"),
        assigned_to=d.get("assigned_to"),
        assigned_by=d.get("assigned_by"),
        assigned_at=d.get("assigned_at"),
        scheduled_date=d.get("scheduled_date"),
        estimated_duration_hours=d.get("estimated_duration_hours"),
        actual_labor_hours=d.get("actual_labor_hours"),
        started_at=d.get("started_at"),
        completed_at=d.get("completed_at"),
        completed_by=d.get("completed_by"),
        sla_deadline=d.get("sla_deadline"),
        sla_breached=d.get("sla_breached"),
        on_hold_reason=d.get("on_hold_reason"),
        on_hold_at=d.get("on_hold_at"),
        incident_id=str(d["incident_id"]) if d.get("incident_id") else None,
        preventive_schedule_id=d.get("preventive_schedule_id"),
        parts_used=d.get("parts_used"),
        next_calibration_date=d.get("next_calibration_date"),
        created_at=d.get("created_at"),
        updated_at=d.get("updated_at"),
        created_by=d.get("created_by"),
        cancelled_by=d.get("cancelled_by"),
        version=d.get("version", 1),
    )


# ─── POST /work-orders ─────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def create_work_order(
    data: WorkOrderCreate,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    try:
        wo = await service.create_work_order(
            tenant_id=tenant_id,
            device_id=data.device_id,
            device_name=data.device_name,
            device_serial=data.device_serial,
            work_order_type=data.work_order_type.value,
            description=data.description,
            priority=data.priority.value,
            incident_id=data.incident_id,
            preventive_schedule_id=data.preventive_schedule_id,
            created_by=get_current_user_id(request),
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── GET /work-orders ───────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=WorkOrderListResponse,
    responses={403: {"model": ErrorResponse}},
)
async def list_work_orders(
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    page: int = 1,
    page_size: int = Query(default=50, ge=1, le=200),
    status: str | None = None,
    priority: str | None = None,
    assigned_to: str | None = None,
    device_id: str | None = None,
    work_order_type: str | None = None,
    sort_by: str = "created_at",
    sort_order: SortOrder = SortOrder.DESC,
) -> WorkOrderListResponse:
    items, total = await service.list_work_orders(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        device_id=device_id,
        work_order_type=work_order_type,
        sort_by=sort_by,
        sort_order=sort_order.value,
    )
    return WorkOrderListResponse(
        items=[_to_response(wo) for wo in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=ceil(total / page_size) if total > 0 else 0,
    )


# ─── GET /work-orders/{work_order_id} ─────────────────────────────────────────


@router.get(
    "/{work_order_id}",
    response_model=WorkOrderResponse,
    responses={
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def get_work_order(
    work_order_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
) -> WorkOrderResponse:
    wo = await service.get_work_order(work_order_id, tenant_id)
    if wo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    return _to_response(wo)


# ─── GET /work-orders/overdue ─────────────────────────────────────────────────


@router.get(
    "/overdue/list",
    response_model=WorkOrderListResponse,
    responses={403: {"model": ErrorResponse}},
)
async def list_overdue_work_orders(
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
) -> WorkOrderListResponse:
    items = await service.list_overdue_work_orders(tenant_id)
    return WorkOrderListResponse(
        items=[_to_response(wo) for wo in items],
        total=len(items),
        page=1,
        page_size=len(items),
        pages=1,
    )


# ─── PATCH /work-orders/{work_order_id} ───────────────────────────────────────


@router.patch(
    "/{work_order_id}",
    response_model=WorkOrderResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def update_work_order(
    work_order_id: str,
    data: WorkOrderUpdate,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    # Get current version
    current = await service.get_work_order(work_order_id, tenant_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    try:
        wo = await service.update_work_order(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            expected_version=current.version,
            updated_by=get_current_user_id(request),
            correlation_id=get_correlation_id(request),
            description=data.description,
            priority=data.priority.value if data.priority else None,
            scheduled_date=data.scheduled_date,
            estimated_duration_hours=data.estimated_duration_hours,
            notes=data.notes,
        )
    except ValueError as e:
        msg = str(e)
        if "version mismatch" in msg or "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── POST /work-orders/{work_order_id}/schedule ───────────────────────────────


@router.post(
    "/{work_order_id}/schedule",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def schedule_work_order(
    work_order_id: str,
    data: WorkOrderSchedule,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    current = await service.get_work_order(work_order_id, tenant_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    try:
        wo = await service.schedule_work_order(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            scheduled_date=data.scheduled_date,
            estimated_duration_hours=data.estimated_duration_hours,
            assigned_to=data.assigned_to,
            expected_version=current.version,
            scheduled_by=get_current_user_id(request) or "system",
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "version mismatch" in msg or "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── POST /work-orders/{work_order_id}/assign ─────────────────────────────────


@router.post(
    "/{work_order_id}/assign",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def assign_work_order(
    work_order_id: str,
    data: WorkOrderAssign,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    current = await service.get_work_order(work_order_id, tenant_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    try:
        wo = await service.assign_work_order(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            assigned_to=data.assigned_to,
            assigned_by=get_current_user_id(request) or "system",
            expected_version=current.version,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "version mismatch" in msg or "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── POST /work-orders/{work_order_id}/start ───────────────────────────────────


@router.post(
    "/{work_order_id}/start",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def start_work_order(
    work_order_id: str,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    current = await service.get_work_order(work_order_id, tenant_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    try:
        wo = await service.start_work_order(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            started_by=get_current_user_id(request) or "system",
            expected_version=current.version,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "version mismatch" in msg or "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── POST /work-orders/{work_order_id}/complete ───────────────────────────────


@router.post(
    "/{work_order_id}/complete",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def complete_work_order(
    work_order_id: str,
    data: WorkOrderComplete,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    current = await service.get_work_order(work_order_id, tenant_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    try:
        wo = await service.complete_work_order(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            completed_by=get_current_user_id(request) or "system",
            expected_version=current.version,
            resolution_summary=data.resolution_summary,
            parts_used=data.parts_used,
            labor_hours=data.labor_hours,
            next_calibration_date=data.next_calibration_date,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "version mismatch" in msg or "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── POST /work-orders/{work_order_id}/cancel ─────────────────────────────────


@router.post(
    "/{work_order_id}/cancel",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def cancel_work_order(
    work_order_id: str,
    data: WorkOrderCancel,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    current = await service.get_work_order(work_order_id, tenant_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    try:
        wo = await service.cancel_work_order(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            cancelled_by=get_current_user_id(request) or "system",
            cancellation_reason=data.cancellation_reason,
            expected_version=current.version,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "version mismatch" in msg or "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── POST /work-orders/{work_order_id}/hold ───────────────────────────────────


@router.post(
    "/{work_order_id}/hold",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def put_work_order_on_hold(
    work_order_id: str,
    data: WorkOrderHold,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderResponse:
    current = await service.get_work_order(work_order_id, tenant_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )
    try:
        wo = await service.put_on_hold(
            work_order_id=work_order_id,
            tenant_id=tenant_id,
            hold_reason=data.hold_reason,
            put_on_hold_by=get_current_user_id(request) or "system",
            expected_version=current.version,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "version mismatch" in msg or "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(wo)
    return _to_response(wo)


# ─── DELETE /work-orders/{work_order_id} ─────────────────────────────────────


@router.delete(
    "/{work_order_id}",
    response_model=WorkOrderDeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def delete_work_order(
    work_order_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[WorkOrderService, Depends(get_work_order_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WorkOrderDeleteResponse:
    try:
        deleted = await service.delete_work_order(work_order_id, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work order '{work_order_id}' not found.",
        )

    await db.commit()
    return WorkOrderDeleteResponse(deleted=True, work_order_id=work_order_id)
