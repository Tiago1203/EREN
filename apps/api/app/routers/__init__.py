"""HTTP presentation layer (FastAPI routers).

``api_router`` aggregates every versioned router and is mounted in
``app.main`` under the configured API prefix.
"""

from fastapi import APIRouter

from app.routers import (
    auth,
    beds,
    buildings,
    campuses,
    departments,
    devices,
    diagnosis,
    floors,
    health,
    hospitals,
    organizations,
    patients,
    purchase_orders,
    roles,
    rooms,
    spare_parts,
    staff,
    suppliers,
    teams,
    units,
    warehouses,
    work_orders,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(diagnosis.router)
api_router.include_router(devices.router)
api_router.include_router(work_orders.router)
# EPIC 3 — Hospital Management
api_router.include_router(campuses.router)
api_router.include_router(buildings.router)
api_router.include_router(floors.router)
api_router.include_router(rooms.router)
api_router.include_router(beds.router)
api_router.include_router(staff.router)
api_router.include_router(roles.router)
api_router.include_router(teams.router)
api_router.include_router(departments.router)
api_router.include_router(units.router)
api_router.include_router(organizations.router)
api_router.include_router(hospitals.router)
api_router.include_router(warehouses.router)
api_router.include_router(suppliers.router)
api_router.include_router(spare_parts.router)
api_router.include_router(purchase_orders.router)

__all__ = ["api_router"]
