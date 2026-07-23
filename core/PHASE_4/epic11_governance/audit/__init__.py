"""
PHASE 4 - EPIC 11: Audit Module

Gestión de auditoría:
- Audit Manager
- Audit Entry
- Audit Trail
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AuditAction(str, Enum):
    """Acciones de auditoría."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    VIEWED = "viewed"
    EXPORTED = "exported"
    ROLLED_BACK = "rolled_back"
    STATUS_CHANGED = "status_changed"
    POLICY_APPLIED = "policy_applied"
    SYNC_COMPLETED = "sync_completed"


class AuditSeverity(str, Enum):
    """Severidad de auditoría."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """Entrada de auditoría."""
    entry_id: str
    timestamp: str
    
    # Action
    action: AuditAction
    severity: AuditSeverity = AuditSeverity.INFO
    
    # Who
    user_id: str = ""
    system_id: str = ""
    
    # What
    entity_type: str = ""
    entity_id: str = ""
    asset_id: str = ""
    
    # Details
    details: dict = field(default_factory=dict)
    previous_state: str = ""
    new_state: str = ""
    
    # Result
    success: bool = True
    error_message: str = ""
    
    # Metadata
    ip_address: str = ""
    user_agent: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class AuditQuery:
    """Consulta de auditoría."""
    entity_type: str | None = None
    entity_id: str | None = None
    action: AuditAction | None = None
    user_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    limit: int = 100


class BaseAuditManager(ABC):
    """Clase base para gestión de auditoría."""
    
    @abstractmethod
    async def log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        **kwargs,
    ) -> AuditEntry:
        """Registra entrada."""
        ...
    
    @abstractmethod
    async def query(self, audit_query: AuditQuery) -> list[AuditEntry]:
        """Consulta entradas."""
        ...


class InMemoryAuditManager(BaseAuditManager):
    """Gestor de auditoría en memoria."""
    
    def __init__(self):
        self._entries: list[AuditEntry] = []
    
    async def log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        **kwargs,
    ) -> AuditEntry:
        """Registra entrada."""
        import uuid
        
        entry = AuditEntry(
            entry_id=str(uuid.uuid4())[:16],
            timestamp=datetime.now().isoformat(),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            severity=kwargs.get("severity", AuditSeverity.INFO),
            user_id=kwargs.get("user_id", ""),
            system_id=kwargs.get("system_id", ""),
            details=kwargs.get("details", {}),
            previous_state=kwargs.get("previous_state", ""),
            new_state=kwargs.get("new_state", ""),
            success=kwargs.get("success", True),
            error_message=kwargs.get("error_message", ""),
        )
        
        self._entries.append(entry)
        return entry
    
    async def query(self, audit_query: AuditQuery) -> list[AuditEntry]:
        """Consulta entradas."""
        results = self._entries
        
        if audit_query.entity_type:
            results = [e for e in results if e.entity_type == audit_query.entity_type]
        
        if audit_query.entity_id:
            results = [e for e in results if e.entity_id == audit_query.entity_id]
        
        if audit_query.action:
            results = [e for e in results if e.action == audit_query.action]
        
        if audit_query.user_id:
            results = [e for e in results if e.user_id == audit_query.user_id]
        
        if audit_query.start_date:
            results = [e for e in results if e.timestamp >= audit_query.start_date]
        
        if audit_query.end_date:
            results = [e for e in results if e.timestamp <= audit_query.end_date]
        
        return results[-audit_query.limit:]
    
    async def get_entity_history(self, entity_id: str) -> list[AuditEntry]:
        """Obtiene historial de entidad."""
        return [e for e in self._entries if e.entity_id == entity_id]
    
    async def get_user_activity(self, user_id: str) -> list[AuditEntry]:
        """Obtiene actividad de usuario."""
        return [e for e in self._entries if e.user_id == user_id]


class AuditReporter:
    """Generador de reportes de auditoría."""
    
    def __init__(self, audit_manager: BaseAuditManager):
        self._manager = audit_manager
    
    async def generate_summary(
        self,
        start_date: str,
        end_date: str,
    ) -> dict:
        """Genera resumen de auditoría."""
        query = AuditQuery(
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )
        
        entries = await self._manager.query(query)
        
        # Count by action
        action_counts = {}
        for entry in entries:
            action = entry.action.value
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for entry in entries:
            severity = entry.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count errors
        error_count = sum(1 for e in entries if not e.success)
        
        return {
            "total_entries": len(entries),
            "action_counts": action_counts,
            "severity_counts": severity_counts,
            "error_count": error_count,
            "date_range": {
                "start": start_date,
                "end": end_date,
            },
        }


__all__ = [
    "AuditAction",
    "AuditSeverity",
    "AuditEntry",
    "AuditQuery",
    "BaseAuditManager",
    "InMemoryAuditManager",
    "AuditReporter",
]
