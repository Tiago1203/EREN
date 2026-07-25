"""
PHASE 7 - EPIC 5: Admin API

FastAPI router para administración.
Integración: EPIC 4 (observability) - métricas de admin ops.
"""

from __future__ import annotations

from typing import Optional
from dataclasses import dataclass


@dataclass
class AdminAPIResponse:
    """Respuesta estándar de API admin."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None


class AdminAPI:
    """API de administración."""

    def __init__(self, admin_service=None, migration_service=None):
        self._admin = admin_service
        self._migration = migration_service

    # ── System ───────────────────────────────────────────────
    def get_overview(self) -> AdminAPIResponse:
        """GET /admin/overview"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        return AdminAPIResponse(success=True, data=self._admin.get_system_overview())

    # ── Users ─────────────────────────────────────────────────
    def list_users(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AdminAPIResponse:
        """GET /admin/users"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        users = self._admin.get_users(tenant_id, status, limit=limit, offset=offset)
        return AdminAPIResponse(success=True, data={"users": users, "count": len(users)})

    def create_user(self, payload: dict) -> AdminAPIResponse:
        """POST /admin/users"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        try:
            user = self._admin.create_user(
                email=payload["email"],
                full_name=payload["full_name"],
                role_ids=payload.get("role_ids", []),
                tenant_id=payload.get("tenant_id"),
                department=payload.get("department"),
                created_by=payload.get("created_by", "api"),
            )
            return AdminAPIResponse(success=True, data=user, message="User created")
        except KeyError as e:
            return AdminAPIResponse(success=False, error=f"Missing field: {e}")
        except Exception as e:
            return AdminAPIResponse(success=False, error=str(e))

    def get_user(self, user_id: str) -> AdminAPIResponse:
        """GET /admin/users/{user_id}"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        user = self._admin.get_user(user_id)
        if not user:
            return AdminAPIResponse(success=False, error="User not found")
        return AdminAPIResponse(success=True, data=user)

    def update_user(self, user_id: str, updates: dict) -> AdminAPIResponse:
        """PATCH /admin/users/{user_id}"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        user = self._admin.update_user(user_id, updates, updated_by="api")
        if not user:
            return AdminAPIResponse(success=False, error="User not found")
        return AdminAPIResponse(success=True, data=user, message="User updated")

    def suspend_user(self, user_id: str) -> AdminAPIResponse:
        """POST /admin/users/{user_id}/suspend"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        success = self._admin.suspend_user(user_id, suspended_by="api")
        if not success:
            return AdminAPIResponse(success=False, error="User not found")
        return AdminAPIResponse(success=True, message="User suspended")

    # ── Roles ────────────────────────────────────────────────
    def list_roles(self, tenant_id: Optional[str] = None) -> AdminAPIResponse:
        """GET /admin/roles"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        roles = self._admin.get_roles(tenant_id)
        return AdminAPIResponse(success=True, data={"roles": roles, "count": len(roles)})

    def create_role(self, payload: dict) -> AdminAPIResponse:
        """POST /admin/roles"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        try:
            role = self._admin.create_role(
                name=payload["name"],
                role_type=payload["role_type"],
                description=payload.get("description", ""),
                permissions=payload.get("permissions", []),
                tenant_id=payload.get("tenant_id"),
                created_by=payload.get("created_by", "api"),
            )
            return AdminAPIResponse(success=True, data=role, message="Role created")
        except Exception as e:
            return AdminAPIResponse(success=False, error=str(e))

    def assign_role(self, user_id: str, role_id: str) -> AdminAPIResponse:
        """POST /admin/users/{user_id}/roles"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        success = self._admin.assign_role_to_user(user_id, role_id, assigned_by="api")
        if not success:
            return AdminAPIResponse(success=False, error="User or role not found")
        return AdminAPIResponse(success=True, message="Role assigned")

    # ── Settings ─────────────────────────────────────────────
    def get_settings(self, category: Optional[str] = None) -> AdminAPIResponse:
        """GET /admin/settings"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        settings = self._admin.get_all_settings(category)
        return AdminAPIResponse(success=True, data={"settings": settings})

    def update_setting(self, key: str, value: str) -> AdminAPIResponse:
        """PUT /admin/settings/{key}"""
        if not self._admin:
            return AdminAPIResponse(success=False, error="Admin service not initialized")
        setting = self._admin.update_setting(key, value, updated_by="api")
        if not setting:
            return AdminAPIResponse(success=False, error="Setting not found or read-only")
        return AdminAPIResponse(success=True, data=setting, message="Setting updated")

    # ── Migration ─────────────────────────────────────────────
    def get_migration_status(self, job_id: Optional[str] = None) -> AdminAPIResponse:
        """GET /admin/migration"""
        if not self._migration:
            return AdminAPIResponse(success=False, error="Migration service not initialized")
        status = self._migration.get_migration_status(job_id)
        return AdminAPIResponse(success=True, data=status)

    def start_migration(self, entity_type: str, records: list, tenant_id: str) -> AdminAPIResponse:
        """POST /admin/migration"""
        if not self._migration:
            return AdminAPIResponse(success=False, error="Migration service not initialized")

        from core.PHASE_7.admin.services.migration_service import MigrationEntity

        entity_map = {
            "equipment": MigrationEntity.EQUIPMENT,
            "kpi": MigrationEntity.KPI,
        }

        entity = entity_map.get(entity_type)
        if not entity:
            return AdminAPIResponse(success=False, error=f"Unknown entity type: {entity_type}")

        report = self._migration.migrate_equipment(records, tenant_id) if entity == MigrationEntity.EQUIPMENT else self._migration.migrate_kpis(records, tenant_id)
        return AdminAPIResponse(success=True, data={
            "job_id": report.job_id,
            "total": report.total,
            "migrated": report.migrated,
            "failed": report.failed,
            "duration_seconds": report.duration_seconds,
        })
