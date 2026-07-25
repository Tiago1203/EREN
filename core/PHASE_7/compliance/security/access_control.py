"""
PHASE 7 - EPIC 0: Access Control Framework

Framework de control de acceso:
- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)
- Permissions hierarchy
- Access grants con contexto
- HIPAA access controls
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable
import uuid


class Role(str, Enum):
    """Roles predefinidos."""
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    CLINICAL_ENGINEER = "clinical_engineer"
    BIOMEDICAL_STAFF = "biomedical_staff"
    TECHNICIAN = "technician"
    NURSE = "nurse"
    PHYSICIAN = "physician"
    AUDITOR = "auditor"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permisos granulares."""
    # Equipos
    EQUIPOS_READ = "equipos:read"
    EQUIPOS_WRITE = "equipos:write"
    EQUIPOS_DELETE = "equipos:delete"
    EQUIPOS_EXPORT = "equipos:export"

    # Mantenimientos
    MANTENIMIENTOS_READ = "mantenimientos:read"
    MANTENIMIENTOS_WRITE = "mantenimientos:write"
    MANTENIMIENTOS_DELETE = "mantenimientos:delete"

    # Establecimientos
    ESTABLECIMIENTOS_READ = "establecimientos:read"
    ESTABLECIMIENTOS_WRITE = "establecimientos:write"
    ESTABLECIMIENTOS_DELETE = "establecimientos:delete"

    # Pacientes (PHI)
    PHI_READ = "phi:read"
    PHI_WRITE = "phi:write"
    PHI_EXPORT = "phi:export"
    PHI_ANONYMIZE = "phi:anonymize"

    # AI
    AI_QUERY = "ai:query"
    AI_ADMIN = "ai:admin"

    # Admin
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"
    ROLES_READ = "roles:read"
    ROLES_WRITE = "roles:write"
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_ADMIN = "system:admin"


class Resource(str, Enum):
    """Recursos del sistema."""
    EQUIPO = "equipo"
    MANTENIMIENTO = "mantenimiento"
    ESTABLECIMIENTO = "establecimiento"
    PACIENTE = "paciente"
    USUARIO = "usuario"
    AUDITORIA = "auditoria"
    AI_AGENT = "ai_agent"
    CONFIGURACION = "configuracion"


class Action(str, Enum):
    """Acciones sobre recursos."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXPORT = "export"
    ADMIN = "admin"


# Matriz de permisos por rol (HIPAA-aligned)
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: {
        Permission.EQUIPOS_READ, Permission.EQUIPOS_WRITE, Permission.EQUIPOS_DELETE, Permission.EQUIPOS_EXPORT,
        Permission.MANTENIMIENTOS_READ, Permission.MANTENIMIENTOS_WRITE, Permission.MANTENIMIENTOS_DELETE,
        Permission.ESTABLECIMIENTOS_READ, Permission.ESTABLECIMIENTOS_WRITE, Permission.ESTABLECIMIENTOS_DELETE,
        Permission.PHI_READ, Permission.PHI_WRITE, Permission.PHI_EXPORT, Permission.PHI_ANONYMIZE,
        Permission.AI_QUERY, Permission.AI_ADMIN,
        Permission.USERS_READ, Permission.USERS_WRITE, Permission.USERS_DELETE,
        Permission.ROLES_READ, Permission.ROLES_WRITE,
        Permission.AUDIT_READ, Permission.AUDIT_EXPORT,
        Permission.SYSTEM_CONFIG, Permission.SYSTEM_ADMIN,
    },
    Role.TENANT_ADMIN: {
        Permission.EQUIPOS_READ, Permission.EQUIPOS_WRITE, Permission.EQUIPOS_DELETE, Permission.EQUIPOS_EXPORT,
        Permission.MANTENIMIENTOS_READ, Permission.MANTENIMIENTOS_WRITE, Permission.MANTENIMIENTOS_DELETE,
        Permission.ESTABLECIMIENTOS_READ, Permission.ESTABLECIMIENTOS_WRITE,
        Permission.PHI_READ, Permission.PHI_WRITE, Permission.PHI_EXPORT,
        Permission.AI_QUERY,
        Permission.USERS_READ, Permission.USERS_WRITE,
        Permission.AUDIT_READ,
    },
    Role.CLINICAL_ENGINEER: {
        Permission.EQUIPOS_READ, Permission.EQUIPOS_WRITE,
        Permission.MANTENIMIENTOS_READ, Permission.MANTENIMIENTOS_WRITE,
        Permission.ESTABLECIMIENTOS_READ,
        Permission.PHI_READ,
        Permission.AI_QUERY,
    },
    Role.BIOMEDICAL_STAFF: {
        Permission.EQUIPOS_READ,
        Permission.MANTENIMIENTOS_READ, Permission.MANTENIMIENTOS_WRITE,
        Permission.ESTABLECIMIENTOS_READ,
    },
    Role.TECHNICIAN: {
        Permission.EQUIPOS_READ,
        Permission.MANTENIMIENTOS_READ,
        Permission.ESTABLECIMIENTOS_READ,
    },
    Role.PHYSICIAN: {
        Permission.EQUIPOS_READ,
        Permission.PHI_READ, Permission.PHI_WRITE,
        Permission.AI_QUERY,
    },
    Role.NURSE: {
        Permission.EQUIPOS_READ,
        Permission.PHI_READ,
    },
    Role.AUDITOR: {
        Permission.EQUIPOS_READ, Permission.EQUIPOS_EXPORT,
        Permission.MANTENIMIENTOS_READ, Permission.MANTENIMIENTOS_READ,
        Permission.ESTABLECIMIENTOS_READ,
        Permission.AUDIT_READ, Permission.AUDIT_EXPORT,
    },
    Role.VIEWER: {
        Permission.EQUIPOS_READ,
        Permission.ESTABLECIMIENTOS_READ,
    },
}


@dataclass
class AccessContext:
    """Contexto de acceso para ABAC."""
    user_id: str
    role: Role
    tenant_id: Optional[str] = None
    establishment_id: Optional[str] = None
    department_id: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""
    session_id: str = ""
    time_of_access: Optional[datetime] = None
    purpose_of_use: str = "treatment"  # treatment, payment, operations, research
    is_emergency: bool = False

    # Attributes for ABAC
    attributes: dict = field(default_factory=dict)


@dataclass
class AccessGrant:
    """Concesiones de acceso."""
    grant_id: str
    user_id: str
    role: Role
    permissions: set[Permission]
    tenant_id: Optional[str] = None
    establishment_ids: set[str] = field(default_factory=set)
    department_ids: set[str] = field(default_factory=set)
    granted_by: str = ""
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    conditions: dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True


@dataclass
class AccessDecision:
    """Decisión de acceso."""
    granted: bool
    reason: str
    permissions: set[Permission]
    conditions: dict = field(default_factory=dict)


class AccessControlService:
    """Servicio de control de acceso RBAC + ABAC."""

    def __init__(self):
        self._grants: dict[str, AccessGrant] = {}  # user_id -> grant
        self._policies: list[Callable[[AccessContext, str, str], bool]] = []
        self._load_default_policies()

    def _load_default_policies(self) -> None:
        """Carga políticas por defecto (HIPAA minimum necessary)."""
        # Policy: Emergency access bypass (grants PHI access in emergencies)
        def emergency_override(ctx: AccessContext, resource: str, action: str) -> bool:
            if ctx.is_emergency and ctx.purpose_of_use == "treatment":
                return True  # Allow emergency access to PHI
            return False

        # Policy: Audit all PHI access (marks for audit logging)
        def phi_audit_required(ctx: AccessContext, resource: str, action: str) -> bool:
            phi_resources = {"paciente", "patient"}
            if resource in phi_resources and action == "read":
                return True  # PHI reads must be audited
            return False

        self._policies = [emergency_override, phi_audit_required]

    def grant_access(
        self,
        user_id: str,
        role: Role,
        tenant_id: Optional[str] = None,
        establishment_ids: Optional[set[str]] = None,
        department_ids: Optional[set[str]] = None,
        granted_by: str = "",
        expires_at: Optional[datetime] = None,
        conditions: Optional[dict] = None,
    ) -> AccessGrant:
        """Concede acceso a un usuario."""
        grant = AccessGrant(
            grant_id=str(uuid.uuid4()),
            user_id=user_id,
            role=role,
            permissions=ROLE_PERMISSIONS.get(role, set()),
            tenant_id=tenant_id,
            establishment_ids=establishment_ids or set(),
            department_ids=department_ids or set(),
            granted_by=granted_by,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            conditions=conditions or {},
        )
        self._grants[user_id] = grant
        return grant

    def revoke_access(self, user_id: str) -> bool:
        """Revoca acceso de un usuario."""
        if user_id in self._grants:
            del self._grants[user_id]
            return True
        return False

    def get_grant(self, user_id: str) -> Optional[AccessGrant]:
        """Obtiene grant de un usuario."""
        return self._grants.get(user_id)

    def check_permission(
        self,
        ctx: AccessContext,
        permission: Permission,
    ) -> AccessDecision:
        """Verifica si usuario tiene permiso (RBAC + ABAC)."""
        grant = self._grants.get(ctx.user_id)

        if not grant or not grant.is_valid():
            return AccessDecision(
                granted=False,
                reason="No access grant found or grant expired",
                permissions=set(),
            )

        # ABAC context checks
        conditions = dict(grant.conditions)

        # Check establishment scope
        if grant.establishment_ids and ctx.establishment_id:
            if ctx.establishment_id not in grant.establishment_ids:
                return AccessDecision(
                    granted=False,
                    reason=f"User not authorized for establishment {ctx.establishment_id}",
                    permissions=grant.permissions,
                )

        # Apply policies first (can grant additional access)
        # Priority: emergency_override takes precedence
        resource = self._permission_to_resource(permission)
        action = self._permission_to_action(permission)
        for policy in self._policies:
            if policy(ctx, resource, action):
                if "policy_override" not in conditions:
                    conditions["policy_override"] = policy.__name__

        # Policy override: emergency bypass grants PHI access
        if "policy_override" in conditions and conditions["policy_override"] == "emergency_override":
            return AccessDecision(
                granted=True,
                reason=f"Emergency access override for {permission.value}",
                permissions=grant.permissions,
                conditions=conditions,
            )

        # RBAC check: does role have this permission?
        if permission not in grant.permissions:
            return AccessDecision(
                granted=False,
                reason=f"Permission {permission.value} not in role {ctx.role.value}",
                permissions=grant.permissions,
            )

        return AccessDecision(
            granted=True,
            reason=f"Permission {permission.value} granted via role {grant.role.value}",
            permissions=grant.permissions,
            conditions=conditions,
        )

    def check_resource_access(
        self,
        ctx: AccessContext,
        resource: str,
        action: str,
    ) -> AccessDecision:
        """Verifica acceso a recurso específico."""
        permission = self._resource_action_to_permission(resource, action)
        return self.check_permission(ctx, permission)

    def _permission_to_resource(self, permission: Permission) -> str:
        """Convierte permiso a recurso."""
        mapping = {
            Permission.EQUIPOS_READ: "equipo",
            Permission.EQUIPOS_WRITE: "equipo",
            Permission.EQUIPOS_DELETE: "equipo",
            Permission.MANTENIMIENTOS_READ: "mantenimiento",
            Permission.MANTENIMIENTOS_WRITE: "mantenimiento",
            Permission.ESTABLECIMIENTOS_READ: "establecimiento",
            Permission.PHI_READ: "paciente",
            Permission.PHI_WRITE: "paciente",
            Permission.PHI_EXPORT: "paciente",
            Permission.AUDIT_READ: "auditoria",
            Permission.USERS_READ: "usuario",
            Permission.USERS_WRITE: "usuario",
            Permission.AI_QUERY: "ai_agent",
        }
        return mapping.get(permission, "unknown")

    def _permission_to_action(self, permission: Permission) -> str:
        """Convierte permiso a acción."""
        if permission.value.endswith(":read"):
            return "read"
        elif permission.value.endswith(":write"):
            return "write"
        elif permission.value.endswith(":delete"):
            return "delete"
        elif permission.value.endswith(":export"):
            return "export"
        return "admin"

    def _resource_action_to_permission(self, resource: str, action: str) -> Permission:
        """Convierte recurso+acción a permiso."""
        key = f"{resource.upper()}_{action.upper()}"
        try:
            return Permission[key]
        except KeyError:
            return Permission.EQUIPOS_READ  # Default

    def get_user_permissions(self, user_id: str) -> set[Permission]:
        """Obtiene todos los permisos de un usuario."""
        grant = self._grants.get(user_id)
        if not grant:
            return set()
        return grant.permissions

    def get_authorized_establishments(self, user_id: str) -> set[str]:
        """Obtiene establecimientos autorizados."""
        grant = self._grants.get(user_id)
        if not grant:
            return set()
        return grant.establishment_ids
