"""HTTP presentation layer (FastAPI routers).

``api_router`` aggregates every versioned router and is mounted in
``app.main`` under the configured API prefix.
"""

from fastapi import APIRouter

from app.routers import auth, beds, departments, devices, diagnosis, health, patients, staff, work_orders

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(diagnosis.router)
api_router.include_router(devices.router)
api_router.include_router(work_orders.router)
# EPIC 3 — Hospital Management
api_router.include_router(beds.router)
api_router.include_router(staff.router)
api_router.include_router(departments.router)

__all__ = ["api_router"]
