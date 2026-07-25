"""
PHASE 7 - EPIC 4: Log Aggregator

Centralized log aggregation:
- Multi-source ingestion
- Log levels filtering
- Tenant-based filtering
- Retention policies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import threading


class LogSource(str, Enum):
    """Fuentes de log."""
    APPLICATION = "application"
    API = "api"
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    AUDIT = "audit"


@dataclass
class LogEntry:
    """Entrada de log."""
    entry_id: str
    timestamp: datetime
    level: str
    source: LogSource
    message: str
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class LogAggregator:
    """Agregador centralizado de logs."""

    def __init__(self, max_entries: int = 100000):
        self._entries: list[LogEntry] = []
        self._entries_by_tenant: dict[str, list[LogEntry]] = {}
        self._entries_by_source: dict[str, list[LogEntry]] = {}
        self._entries_by_level: dict[str, list[LogEntry]] = {}
        self._max_entries = max_entries
        self._lock = threading.RLock()

    def ingest(
        self,
        level: str,
        source: LogSource,
        message: str,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> LogEntry:
        """Ingesta una entrada de log."""
        import uuid
        entry = LogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            level=level,
            source=source,
            message=message,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            user_id=user_id,
            metadata=metadata or {},
        )

        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_entries:
                removed = self._entries[:len(self._entries) - self._max_entries]
                self._entries = self._entries[len(self._entries) - self._max_entries:]
                self._cleanup_secondary_indices(removed)

            if tenant_id:
                self._entries_by_tenant.setdefault(tenant_id, []).append(entry)
            self._entries_by_source.setdefault(source.value, []).append(entry)
            self._entries_by_level.setdefault(level, []).append(entry)

        return entry

    def _cleanup_secondary_indices(self, removed: list[LogEntry]) -> None:
        """Limpia índices secundarios."""
        for e in removed:
            if e.tenant_id and e.tenant_id in self._entries_by_tenant:
                try:
                    self._entries_by_tenant[e.tenant_id].remove(e)
                except ValueError:
                    pass
            if e.source.value in self._entries_by_source:
                try:
                    self._entries_by_source[e.source.value].remove(e)
                except ValueError:
                    pass
            if e.level in self._entries_by_level:
                try:
                    self._entries_by_level[e.level].remove(e)
                except ValueError:
                    pass

    def query(
        self,
        level: Optional[str] = None,
        source: Optional[LogSource] = None,
        tenant_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[LogEntry]:
        """Query logs con filtros."""
        with self._lock:
            results = self._entries

            if level:
                results = [e for e in results if e.level == level]
            if source:
                results = [e for e in results if e.source == source]
            if tenant_id:
                results = [e for e in results if e.tenant_id == tenant_id]
            if start_time:
                results = [e for e in results if e.timestamp >= start_time]
            if end_time:
                results = [e for e in results if e.timestamp <= end_time]

            return sorted(results, key=lambda e: e.timestamp, reverse=True)[offset:offset+limit]

    def count_by_level(self, tenant_id: Optional[str] = None) -> dict:
        """Cuenta logs por nivel."""
        with self._lock:
            entries = self._entries
            if tenant_id:
                entries = [e for e in entries if e.tenant_id == tenant_id]
            counts = {}
            for e in entries:
                counts[e.level] = counts.get(e.level, 0) + 1
            return counts

    def count_by_source(self, tenant_id: Optional[str] = None) -> dict:
        """Cuenta logs por fuente."""
        with self._lock:
            entries = self._entries
            if tenant_id:
                entries = [e for e in entries if e.tenant_id == tenant_id]
            counts = {}
            for e in entries:
                counts[e.source.value] = counts.get(e.source.value, 0) + 1
            return counts

    def get_stats(self, tenant_id: Optional[str] = None) -> dict:
        """Estadísticas de logs."""
        with self._lock:
            entries = self._entries
            if tenant_id:
                entries = [e for e in entries if e.tenant_id == tenant_id]

            return {
                "total_entries": len(entries),
                "by_level": self.count_by_level(tenant_id),
                "by_source": self.count_by_source(tenant_id),
                "tenants_with_logs": len(set(e.tenant_id for e in entries if e.tenant_id)),
                "oldest_entry": min((e.timestamp for e in entries), default=None),
                "newest_entry": max((e.timestamp for e in entries), default=None),
            }
