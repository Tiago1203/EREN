"""Audit Middleware.

Logs all significant actions for HIPAA compliance.
This is a transversal middleware that runs on every request.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

if TYPE_CHECKING:
    from core.PHASE_1.infrastructure.contracts.security.audit import AuditProvider

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Severity level of audit events."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AuditCategory(Enum):
    """Categories of auditable events."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_CREATION = "data_creation"
    DATA_DELETION = "data_deletion"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    CLINICAL = "clinical"


@dataclass(frozen=True)
class AuditEntry:
    """A single audit entry (immutable)."""

    event_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Who
    principal_id: str | None = None
    session_id: str | None = None
    ip_address: str | None = None

    # What
    category: AuditCategory = AuditCategory.SYSTEM
    action: str = ""
    level: AuditLevel = AuditLevel.MEDIUM
    outcome: str = "success"

    # Where
    resource_type: str | None = None
    resource_id: str | None = None
    component: str = "api"

    # Details
    description: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    # Tracing
    correlation_id: str | None = None
    request_id: str | None = None

    # PHI (for HIPAA)
    phi_exposed: bool = False
    patient_id: str | None = None


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that audits every significant action.

    This is TRANSVERSAL - it runs on EVERY request.
    PHI access is logged with additional details.
    """

    def __init__(self, app, audit_provider: AuditProvider | None = None):
        super().__init__(app)
        self._audit_provider = audit_provider

    async def dispatch(self, request: Request, call_next) -> Response:
        """Audit the request."""
        # Extract context
        request_id = getattr(request.state, "request_id", None)
        principal = getattr(request.state, "principal", None)
        tenant_id = getattr(request.state, "tenant_id", None)

        # Extract client info
        client_ip = request.client.host if request.client else None

        # Build audit entry
        audit_entry = AuditEntry(
            event_id=str(uuid.uuid4()),
            principal_id=principal.principal_id if principal else None,
            session_id=None,  # TODO: Extract from token
            ip_address=client_ip,
            action=f"{request.method} {request.url.path}",
            description=f"HTTP {request.method} to {request.url.path}",
            component="api",
            correlation_id=tenant_id,
            request_id=request_id,
            phi_exposed=self._is_phi_path(request.url.path),
        )

        # Determine category based on path
        audit_entry.category = self._categorize_path(request.url.path)
        audit_entry.level = self._determine_level(request.method, audit_entry.category)

        # Process request
        response = None
        try:
            response = await call_next(request)
            audit_entry.outcome = "success"
        except Exception as e:
            audit_entry.outcome = "failure"
            audit_entry.details["error"] = str(e)
            raise
        finally:
            # Record audit asynchronously (don't block response)
            if self._audit_provider:
                try:
                    await self._record_audit(audit_entry, response)
                except Exception as e:
                    logger.error(f"Failed to record audit: {e}")
            else:
                # Fallback: log to standard logger
                self._log_audit(audit_entry, response)

        return response

    def _is_phi_path(self, path: str) -> bool:
        """Check if path accesses PHI."""
        phi_paths = {"/patients", "/diagnoses", "/treatments", "/vitals"}
        return any(path.startswith(p) for p in phi_paths)

    def _categorize_path(self, path: str) -> AuditCategory:
        """Categorize request based on path."""
        if "/auth" in path:
            return AuditCategory.AUTHENTICATION
        if "/patients" in path:
            return AuditCategory.DATA_ACCESS
        if "/diagnoses" in path:
            return AuditCategory.DATA_ACCESS
        if "/treatments" in path:
            return AuditCategory.DATA_ACCESS
        return AuditCategory.SYSTEM

    def _determine_level(self, method: str, category: AuditCategory) -> AuditLevel:
        """Determine audit level based on request."""
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            if category == AuditCategory.AUTHENTICATION:
                return AuditLevel.HIGH
            return AuditLevel.MEDIUM
        return AuditLevel.LOW

    async def _record_audit(self, entry: AuditEntry, response: Response | None) -> None:
        """Record audit via AuditProvider."""
        if not self._audit_provider:
            return

        from core.PHASE_1.infrastructure.contracts.security.audit import AuditCategory as ContractCategory
        from core.PHASE_1.infrastructure.contracts.security.audit import AuditEntry as ContractAuditEntry
        from core.PHASE_1.infrastructure.contracts.security.audit import AuditLevel as ContractAuditLevel

        # Map to contract types
        contract_category = ContractCategory(entry.category.value.upper())
        contract_level = ContractAuditLevel(entry.level.value.upper())

        await self._audit_provider.log(
            event=ContractAuditEntry(
                event_id=entry.event_id,
                timestamp=entry.timestamp,
                principal_id=entry.principal_id,
                principal_type="human" if entry.principal_id else None,
                session_id=entry.session_id,
                ip_address=entry.ip_address,
                user_agent=None,
                category=contract_category,
                action=entry.action,
                level=contract_level,
                outcome=entry.outcome,
                resource_type=entry.resource_type,
                resource_id=entry.resource_id,
                component=entry.component,
                description=entry.description,
                details=tuple(entry.details.items()),
                phi_exposure=(
                    ContractAuditEntry.phi_exposure.field.type.__class__.__name__
                    if entry.phi_exposed
                    else "NONE"
                ),
                patient_id=entry.patient_id,
                patient_accessed=entry.phi_exposed,
                correlation_id=entry.correlation_id,
            )
        )

    def _log_audit(self, entry: AuditEntry, response: Response | None) -> None:
        """Fallback: log audit to standard logger."""
        logger.info(
            "audit_entry",
            extra={
                "event_id": entry.event_id,
                "timestamp": entry.timestamp.isoformat(),
                "principal_id": entry.principal_id,
                "category": entry.category.value,
                "action": entry.action,
                "level": entry.level.value,
                "outcome": entry.outcome,
                "phi_exposed": entry.phi_exposed,
                "correlation_id": entry.correlation_id,
            },
        )
