"""Device lifecycle REST API endpoints.

Full CRUD + lifecycle operations for biomedical devices.
All endpoints enforce tenant isolation and optimistic locking.
"""

from __future__ import annotations

import logging
from math import ceil
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.device import DeviceService
from app.domain.device.cache import DeviceCacheService
from app.domain.device.repository import SQLAlchemyDeviceRepository
from app.infrastructure.messaging import CacheService
from app.infrastructure.messaging.cache import get_redis as redis_dep
from app.schemas.device import (
    CalibrationRequest,
    DecommissionRequest,
    DeviceCreate,
    DeviceDeleteResponse,
    DeviceListResponse,
    DeviceResponse,
    DeviceTransfer,
    DeviceUpdate,
    ErrorResponse,
    MaintenanceFinishRequest,
    MaintenanceScheduleRequest,
    MaintenanceStartRequest,
    OutOfServiceRequest,
    ReturnToServiceRequest,
    SortOrder,
)

router = APIRouter(prefix="/devices", tags=["Devices"])
logger = logging.getLogger(__name__)


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
    result: str | None = None
    return result


def get_correlation_id(request: Request) -> str | None:
    rid = getattr(request.state, "request_id", None)
    result: str | None = str(rid) if rid is not None else None
    return result


async def get_device_cache() -> DeviceCacheService:
    redis_client = redis_dep()
    cache = CacheService(redis_client)
    return DeviceCacheService(cache)


async def get_device_service(db: Annotated[AsyncSession, Depends(get_db)]) -> DeviceService:
    repository = SQLAlchemyDeviceRepository(db)
    from app.infrastructure.messaging.outbox import TransactionalOutbox

    outbox = TransactionalOutbox(db)
    return DeviceService(repository=repository, outbox=outbox)


def _to_response(device: Any) -> DeviceResponse:
    return DeviceResponse(
        id=str(device.id),
        tenant_id=device.tenant_id,
        serial_number=device.serial_number,
        manufacturer_name=device.manufacturer_name,
        manufacturer_model=device.manufacturer_model,
        manufacturer_country=device.manufacturer_country,
        device_type=device.device_type,
        name=device.name,
        description=device.description,
        is_critical=device.is_critical,
        status=device.status,
        location_building=device.location_building,
        location_floor=device.location_floor,
        location_room=device.location_room,
        location_department=device.location_department,
        calibration_last=device.calibration_last,
        calibration_next=device.calibration_next,
        calibration_interval_days=device.calibration_interval_days,
        maintenance_interval_days=device.maintenance_interval_days,
        notes=device.notes,
        registered_at=device.registered_at,
        registered_by=device.registered_by,
        last_status_change=device.last_status_change,
        version=device.version,
        created_at=device.created_at,
        updated_at=device.updated_at,
    )


# ─── POST /devices ────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
async def register_device(
    data: DeviceCreate,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    try:
        device = await service.register_device(
            tenant_id=tenant_id,
            serial_number=data.serial_number,
            name=data.name,
            device_type=data.device_type.value,
            manufacturer_name=data.manufacturer_name,
            manufacturer_model=data.manufacturer_model,
            manufacturer_country=data.manufacturer_country,
            building=data.building,
            floor=data.floor,
            room=data.room,
            department=data.department,
            description=data.description,
            is_critical=data.is_critical,
            calibration_last=data.calibration_last,
            calibration_next=data.calibration_next,
            calibration_interval_days=data.calibration_interval_days,
            maintenance_interval_days=data.maintenance_interval_days,
            registered_by=get_current_user_id(request),
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, str(device.id), data.serial_number)
    return _to_response(device)


# ─── GET /devices ─────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=DeviceListResponse,
    responses={403: {"model": ErrorResponse}},
)
async def list_devices(
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    page: int = 1,
    page_size: int = Query(default=50, ge=1, le=200),
    status: str | None = None,
    device_type: str | None = None,
    building: str | None = None,
    department: str | None = None,
    is_critical: bool | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: SortOrder = SortOrder.DESC,
) -> DeviceListResponse:
    devices, total = await service.list_devices(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        status=status,
        device_type=device_type,
        building=building,
        department=department,
        is_critical=is_critical,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order.value,
    )
    return DeviceListResponse(
        items=[_to_response(d) for d in devices],
        total=total,
        page=page,
        page_size=page_size,
        pages=ceil(total / page_size) if total > 0 else 0,
    )


# ─── GET /devices/{id} ────────────────────────────────────────────────────────


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_device(
    device_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
) -> DeviceResponse:
    cached = await cache_service.get_by_id(tenant_id, device_id)
    if cached is not None:
        return DeviceResponse(**cached)
    device = await service.get_device(device_id, tenant_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found",
        )
    response = _to_response(device)
    await cache_service.set_by_id(tenant_id, device_id, response.model_dump(mode="json"))
    return response


# ─── PATCH /devices/{id} ─────────────────────────────────────────────────────


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def update_device(
    device_id: str,
    data: DeviceUpdate,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    version = data.version
    fields = data.model_dump(exclude_unset=True, exclude={"version"})
    try:
        device = await service.update_device(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=version,
            correlation_id=get_correlation_id(request),
            updated_by=get_current_user_id(request),
            **fields,
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "concurrent" in msg.lower() or "version mismatch" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id, fields.get("serial_number"))
    return _to_response(device)


# ─── DELETE /devices/{id} ────────────────────────────────────────────────────


@router.delete(
    "/{device_id}",
    response_model=DeviceDeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def delete_device(
    device_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceDeleteResponse:
    device = await service.get_device(device_id, tenant_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found",
        )
    success = await service.delete_device(device_id, tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found",
        )
    await db.commit()
    await cache_service.invalidate(tenant_id, device_id)
    return DeviceDeleteResponse(deleted=True, device_id=device_id)


# ─── POST /devices/{id}/transfer ─────────────────────────────────────────────


@router.post(
    "/{device_id}/transfer",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def transfer_device(
    device_id: str,
    data: DeviceTransfer,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    try:
        device = await service.transfer_device(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            new_building=data.building,
            new_floor=data.floor,
            new_room=data.room,
            new_department=data.department,
            transfer_reason=data.reason,
            transferred_by=get_current_user_id(request),
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "decommissioned" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)


# ─── POST /devices/{id}/maintenance ──────────────────────────────────────────


@router.post(
    "/{device_id}/maintenance",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def schedule_maintenance(
    device_id: str,
    data: MaintenanceScheduleRequest,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    try:
        device = await service.schedule_maintenance(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            maintenance_type=data.maintenance_type,
            scheduled_date=data.scheduled_date,
            estimated_duration_hours=data.estimated_duration_hours,
            technician_id=data.technician_id,
            scheduled_by=get_current_user_id(request),
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "decommissioned" in msg.lower() or "already in maintenance" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)


# ─── POST /devices/{id}/maintenance/start ─────────────────────────────────────


@router.post(
    "/{device_id}/maintenance/start",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def start_maintenance(
    device_id: str,
    data: MaintenanceStartRequest,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    try:
        device = await service.start_maintenance(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            maintenance_type=data.maintenance_type,
            technician_id=data.technician_id,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "decommissioned" in msg.lower() or "already in maintenance" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)


# ─── POST /devices/{id}/maintenance/finish ────────────────────────────────────


@router.post(
    "/{device_id}/maintenance/finish",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def finish_maintenance(
    device_id: str,
    data: MaintenanceFinishRequest,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    completed_by = get_current_user_id(request) or "system"
    try:
        device = await service.finish_maintenance(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            completed_by=completed_by,
            next_calibration_date=data.next_calibration_date,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "not in maintenance" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)


# ─── POST /devices/{id}/calibrate ─────────────────────────────────────────────


@router.post(
    "/{device_id}/calibrate",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def calibrate_device(
    device_id: str,
    data: CalibrationRequest,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    calibrated_by = get_current_user_id(request) or "system"
    try:
        device = await service.calibrate_device(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            calibration_last=data.calibration_last,
            calibration_next=data.calibration_next,
            calibration_interval_days=data.calibration_interval_days,
            calibration_certificate=data.calibration_certificate,
            calibrated_by=calibrated_by,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "decommissioned" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)


# ─── POST /devices/{id}/out-of-service ───────────────────────────────────────


@router.post(
    "/{device_id}/out-of-service",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def take_out_of_service(
    device_id: str,
    data: OutOfServiceRequest,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    taken_by = get_current_user_id(request) or "system"
    try:
        device = await service.take_out_of_service(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            reason=data.reason,
            taken_by=taken_by,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "already" in msg.lower() or "decommissioned" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)


# ─── POST /devices/{id}/return-service ───────────────────────────────────────


@router.post(
    "/{device_id}/return-service",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def return_to_service(
    device_id: str,
    data: ReturnToServiceRequest,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    returned_by = get_current_user_id(request) or "system"
    try:
        device = await service.return_to_service(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            returned_by=returned_by,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "not out of service" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "calibration" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)


# ─── POST /devices/{id}/decommission ─────────────────────────────────────────


@router.post(
    "/{device_id}/decommission",
    response_model=DeviceResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def decommission_device(
    device_id: str,
    data: DecommissionRequest,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    cache_service: Annotated[DeviceCacheService, Depends(get_device_cache)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeviceResponse:
    decommissioned_by = get_current_user_id(request) or "system"
    try:
        device = await service.decommission_device(
            device_id=device_id,
            tenant_id=tenant_id,
            expected_version=data.version,
            reason=data.reason,
            decommissioned_by=decommissioned_by,
            correlation_id=get_correlation_id(request),
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
        if "already decommissioned" in msg.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e
        if "concurrent" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    await db.commit()
    await db.refresh(device)
    await cache_service.invalidate(tenant_id, device_id)
    return _to_response(device)
