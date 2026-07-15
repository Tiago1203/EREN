"""HTTP presentation layer (FastAPI routers).

``api_router`` aggregates every versioned router and is mounted in
``app.main`` under the configured API prefix.
"""

from fastapi import APIRouter

from app.routers import auth, diagnosis, health, patients

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(diagnosis.router)

__all__ = ["api_router"]
