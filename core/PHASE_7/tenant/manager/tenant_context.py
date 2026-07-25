"""
PHASE 7 - EPIC 2: Tenant Context

Thread-local tenant context:
- Establece tenant activo en el contexto de ejecución
- Previene cross-tenant data access
- Soporta async contexts
- Integration con EPIC 1 (audit logging)
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import threading


# Context variables (async-safe)
_tenant_context: ContextVar[Optional["TenantContext"]] = ContextVar(
    "tenant_context", default=None
)


@dataclass
class TenantContext:
    """
    Contexto del tenant activo.
    Thread-safe y async-safe.
    """
    tenant_id: str
    user_id: str
    user_role: str

    # Scope
    establishment_id: Optional[str] = None
    department_id: Optional[str] = None

    # Access
    is_super_admin: bool = False
    purpose_of_use: str = "treatment"

    # Session
    session_id: str = ""
    ip_address: str = ""
    workstation: str = ""

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Metadata
    request_id: str = ""
    user_agent: str = ""

    def is_emergency_access(self) -> bool:
        """Check if emergency access override is active."""
        return self.purpose_of_use == "emergency"

    def get_scope(self) -> dict:
        """Returns full scope for audit logging."""
        return {
            "tenant_id": self.tenant_id,
            "establishment_id": self.establishment_id,
            "department_id": self.department_id,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "is_super_admin": self.is_super_admin,
            "purpose_of_use": self.purpose_of_use,
        }


class TenantContextManager:
    """
    Gestor del contexto de tenant.
    Provee API para establecer/obtener/anular el contexto.
    """

    def __init__(self):
        self._local = threading.local()
        self._backup: dict = {}  # thread_id -> previous context

    def set_context(self, ctx: TenantContext) -> None:
        """Establece el contexto de tenant para el thread/async actual."""
        _tenant_context.set(ctx)

    def get_context(self) -> Optional[TenantContext]:
        """Obtiene el contexto actual."""
        return _tenant_context.get()

    def clear_context(self) -> None:
        """Limpia el contexto actual."""
        _tenant_context.set(None)

    def get_required_context(self) -> TenantContext:
        """Obtiene contexto, levanta excepción si no existe."""
        ctx = self.get_context()
        if ctx is None:
            raise RuntimeError("No tenant context set. Ensure request is within tenant scope.")
        return ctx

    def get_tenant_id(self) -> str:
        """Obtiene tenant_id del contexto actual."""
        return self.get_required_context().tenant_id

    def get_establishment_id(self) -> Optional[str]:
        """Obtiene establishment_id del contexto actual."""
        return self.get_context().establishment_id if self.get_context() else None

    def has_permission(self, permission: str) -> bool:
        """Check if current context has a permission."""
        ctx = self.get_context()
        if not ctx:
            return False
        if ctx.is_super_admin:
            return True
        # Role-based check
        return self._role_has_permission(ctx.user_role, permission)

    def _role_has_permission(self, role: str, permission: str) -> bool:
        """Check if role has permission (simplified)."""
        # This would integrate with EPIC 0 access control
        admin_perms = {"read", "write", "admin", "delete"}
        if role in ["admin", "super_admin"]:
            return True
        if permission in admin_perms:
            return False
        return True

    def __enter__(self) -> "TenantContextManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - always clears context."""
        self.clear_context()


# Global instance
_context_manager = TenantContextManager()


def get_tenant_context_manager() -> TenantContextManager:
    """Obtiene el context manager global."""
    return _context_manager


def set_tenant_context(
    tenant_id: str,
    user_id: str,
    user_role: str,
    establishment_id: Optional[str] = None,
    is_super_admin: bool = False,
    purpose_of_use: str = "treatment",
    session_id: str = "",
    ip_address: str = "",
) -> TenantContext:
    """Helper para establecer contexto rápidamente."""
    ctx = TenantContext(
        tenant_id=tenant_id,
        user_id=user_id,
        user_role=user_role,
        establishment_id=establishment_id,
        is_super_admin=is_super_admin,
        purpose_of_use=purpose_of_use,
        session_id=session_id,
        ip_address=ip_address,
    )
    _context_manager.set_context(ctx)
    return ctx


def require_tenant_context() -> TenantContext:
    """Require tenant context, raises if not set."""
    return _context_manager.get_required_context()


def get_current_tenant_id() -> str:
    """Get current tenant ID from context."""
    return _context_manager.get_tenant_id()
