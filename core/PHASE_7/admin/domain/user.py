"""
PHASE 7 - EPIC 5: Domain Models

User, Role, Permission, SystemSetting models.
Integración: EPIC 1 (audit), EPIC 2 (multi-tenant).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class UserStatus(str, Enum):
    """Estado de usuario."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class RoleType(str, Enum):
    """Tipo de rol."""
    SYSTEM_ADMIN = "system_admin"
    TENANT_ADMIN = "tenant_admin"
    DEPARTMENT_HEAD = "department_head"
    TECHNICIAN = "technician"
    CLINICAL_STAFF = "clinical_staff"
    VIEWER = "viewer"


@dataclass
class User:
    """Usuario extendido."""
    user_id: str
    email: str
    full_name: str
    status: UserStatus
    tenant_id: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    role_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    must_change_password: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class Permission:
    """Permiso."""
    permission_id: str
    name: str
    resource: str         # e.g., "equipment", "maintenance", "user", "tenant"
    action: str          # "create", "read", "update", "delete", "admin"
    description: str
    scope: str = "own"   # "own", "department", "tenant", "system"


@dataclass
class Role:
    """Rol con permisos."""
    role_id: str
    name: str
    role_type: RoleType
    description: str
    permissions: list[Permission] = field(default_factory=list)
    tenant_id: Optional[str] = None    # None = system role
    is_system: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RoleAssignment:
    """Asignación de rol a usuario."""
    assignment_id: str
    user_id: str
    role_id: str
    assigned_by: str
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


@dataclass
class SystemSetting:
    """Configuración del sistema."""
    setting_id: str
    key: str
    value: str
    category: str        # "general", "security", "notifications", "integrations"
    description: str
    is_encrypted: bool = False
    is_readonly: bool = False
    updated_by: Optional[str] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
