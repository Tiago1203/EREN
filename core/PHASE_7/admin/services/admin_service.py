"""
PHASE 7 - EPIC 5: Admin Service

Main admin service coordinating all admin operations.
Integración: EPIC 1 (audit), EPIC 2 (multi-tenant), EPIC 3 (HA), EPIC 4 (observability).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import threading
import uuid


@dataclass
class AdminOperation:
    """Operación administrativa."""
    operation_id: str
    operation_type: str     # "user_create", "role_assign", "setting_update"
    performed_by: str
    target_type: str       # "user", "role", "tenant", "setting"
    target_id: str
    status: str            # "success", "failed"
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AdminService:
    """Servicio principal de administración."""

    def __init__(self):
        self._users: dict[str, dict] = {}
        self._roles: dict[str, dict] = {}
        self._settings: dict[str, dict] = {}
        self._operations: list[AdminOperation] = []
        self._lock = threading.Lock()

    # ── System Overview ─────────────────────────────────────
    def get_system_overview(self) -> dict:
        """Resumen del sistema."""
        with self._lock:
            total_users = len(self._users)
            active_users = sum(1 for u in self._users.values() if u.get("status") == "active")
            total_roles = len(self._roles)
            total_operations = len(self._operations)

            recent_ops = sorted(
                self._operations,
                key=lambda x: x.timestamp,
                reverse=True,
            )[:20]

            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "total_roles": total_roles,
                "total_settings": len(self._settings),
                "total_admin_operations": total_operations,
                "recent_operations": [
                    {
                        "operation_id": op.operation_id,
                        "operation_type": op.operation_type,
                        "performed_by": op.performed_by,
                        "target_type": op.target_type,
                        "target_id": op.target_id,
                        "status": op.status,
                        "timestamp": op.timestamp.isoformat(),
                    }
                    for op in recent_ops
                ],
            }

    # ── User Management ─────────────────────────────────────
    def create_user(
        self,
        email: str,
        full_name: str,
        role_ids: list[str],
        tenant_id: Optional[str] = None,
        department: Optional[str] = None,
        created_by: str = "system",
    ) -> dict:
        """Crea usuario."""
        user_id = f"user-{uuid.uuid4().hex[:12]}"
        user = {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "status": "active",
            "tenant_id": tenant_id,
            "department": department,
            "role_ids": role_ids,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "failed_login_attempts": 0,
            "must_change_password": True,
        }

        with self._lock:
            self._users[user_id] = user

        self._log_operation(
            "user_create",
            created_by,
            "user",
            user_id,
            "success",
            {"email": email, "tenant_id": tenant_id},
        )

        return user

    def get_user(self, user_id: str) -> Optional[dict]:
        with self._lock:
            return self._users.get(user_id)

    def get_users(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        department: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Lista usuarios con filtros."""
        with self._lock:
            users = list(self._users.values())

            if tenant_id:
                users = [u for u in users if u.get("tenant_id") == tenant_id]
            if status:
                users = [u for u in users if u.get("status") == status]
            if department:
                users = [u for u in users if u.get("department") == department]

            return sorted(users, key=lambda x: x["created_at"], reverse=True)[offset:offset+limit]

    def update_user(self, user_id: str, updates: dict, updated_by: str) -> Optional[dict]:
        """Actualiza usuario."""
        with self._lock:
            if user_id not in self._users:
                return None

            user = self._users[user_id]
            for key, value in updates.items():
                if key not in ("user_id", "created_at"):
                    user[key] = value
            user["updated_at"] = datetime.now(timezone.utc).isoformat()
            updated = dict(user)

        self._log_operation(
            "user_update",
            updated_by,
            "user",
            user_id,
            "success",
            {"updates": list(updates.keys())},
        )

        return updated

    def suspend_user(self, user_id: str, suspended_by: str) -> bool:
        """Suspende usuario."""
        with self._lock:
            if user_id in self._users:
                self._users[user_id]["status"] = "suspended"
                self._users[user_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False

    # ── Role Management ─────────────────────────────────────
    def create_role(
        self,
        name: str,
        role_type: str,
        description: str,
        permissions: list[dict],
        tenant_id: Optional[str] = None,
        created_by: str = "system",
    ) -> dict:
        """Crea rol."""
        role_id = f"role-{uuid.uuid4().hex[:12]}"
        role = {
            "role_id": role_id,
            "name": name,
            "role_type": role_type,
            "description": description,
            "permissions": permissions,
            "tenant_id": tenant_id,
            "is_system": tenant_id is None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            self._roles[role_id] = role

        self._log_operation(
            "role_create",
            created_by,
            "role",
            role_id,
            "success",
            {"name": name, "role_type": role_type},
        )

        return role

    def get_role(self, role_id: str) -> Optional[dict]:
        with self._lock:
            return self._roles.get(role_id)

    def get_roles(self, tenant_id: Optional[str] = None) -> list[dict]:
        """Lista roles."""
        with self._lock:
            roles = list(self._roles.values())
            if tenant_id:
                roles = [r for r in roles if r.get("tenant_id") == tenant_id]
            return roles

    def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str,
    ) -> bool:
        """Asigna rol a usuario."""
        with self._lock:
            if user_id in self._users and role_id in self._roles:
                user = self._users[user_id]
                if role_id not in user["role_ids"]:
                    user["role_ids"].append(role_id)
                    user["updated_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False

    # ── System Settings ──────────────────────────────────────
    def get_setting(self, key: str) -> Optional[dict]:
        with self._lock:
            return self._settings.get(key)

    def get_all_settings(self, category: Optional[str] = None) -> list[dict]:
        with self._lock:
            settings = list(self._settings.values())
            if category:
                settings = [s for s in settings if s.get("category") == category]
            return settings

    def update_setting(
        self,
        key: str,
        value: str,
        updated_by: str,
    ) -> Optional[dict]:
        """Actualiza configuración."""
        with self._lock:
            if key in self._settings and self._settings[key].get("is_readonly"):
                return None

            setting = self._settings.get(key, {
                "setting_id": f"setting-{uuid.uuid4().hex[:12]}",
                "key": key,
                "category": "general",
                "description": "",
                "is_encrypted": False,
                "is_readonly": False,
            })
            setting["value"] = value
            setting["updated_by"] = updated_by
            setting["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._settings[key] = setting

        self._log_operation(
            "setting_update",
            updated_by,
            "setting",
            key,
            "success",
            {"key": key},
        )

        return setting

    # ── Logging ─────────────────────────────────────────────
    def _log_operation(
        self,
        operation_type: str,
        performed_by: str,
        target_type: str,
        target_id: str,
        status: str,
        details: dict,
    ) -> None:
        op = AdminOperation(
            operation_id=f"op-{uuid.uuid4().hex[:12]}",
            operation_type=operation_type,
            performed_by=performed_by,
            target_type=target_type,
            target_id=target_id,
            status=status,
            details=details,
        )
        with self._lock:
            self._operations.append(op)
            if len(self._operations) > 10000:
                self._operations = self._operations[-5000:]
