"""
PHASE 7 - EPIC 1: Archive Service

Servicio de archivado de auditoría:
- Archivage de eventos antiguos
- Compression
- Archive retrieval
- Retention management
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
import hashlib


class ArchiveStatus(str, Enum):
    """Estados de archive."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPRESSED = "compressed"
    DELETED = "deleted"


class ArchiveFormat(str, Enum):
    """Formatos de archive."""
    JSON = "json"
    JSON_GZ = "json_gz"
    PARQUET = "parquet"


@dataclass
class ArchiveMetadata:
    """Metadata de un archive."""
    archive_id: str
    archive_name: str
    start_date: datetime
    end_date: datetime
    total_events: int
    compressed_size_bytes: int
    original_size_bytes: int
    format: ArchiveFormat
    status: ArchiveStatus = ArchiveStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    checksum: str = ""
    retention_until: Optional[datetime] = None
    tenant_id: str = ""


@dataclass
class ArchiveRetentionRule:
    """Regla de retención."""
    rule_id: str
    name: str
    archive_after_days: int      # Mover a archive después de N días
    delete_after_days: int       # Eliminar después de N días
    min_events_for_archive: int = 1000
    compress: bool = True


class ArchiveService:
    """Servicio de archivado de auditoría."""

    # HIPAA: 6 years retention
    HIPAA_RETENTION = ArchiveRetentionRule(
        rule_id="hipaa",
        name="HIPAA 6-Year Retention",
        archive_after_days=365,
        delete_after_days=2190,
        min_events_for_archive=100,
    )

    # Standard: 2 years online, then archive
    STANDARD_RETENTION = ArchiveRetentionRule(
        rule_id="standard",
        name="Standard Retention",
        archive_after_days=730,
        delete_after_days=2555,
        min_events_for_archive=100,
    )

    def __init__(self):
        self._archives: dict[str, ArchiveMetadata] = {}
        self._archive_data: dict[str, list[dict]] = {}  # archive_id -> events
        self._retention_rules: dict[str, ArchiveRetentionRule] = {
            "hipaa": self.HIPAA_RETENTION,
            "standard": self.STANDARD_RETENTION,
        }

    def create_archive(
        self,
        events: list[dict],
        start_date: datetime,
        end_date: datetime,
        rule_id: str = "hipaa",
        tenant_id: str = "",
        name: str = "",
    ) -> ArchiveMetadata:
        """Crea archive de eventos."""
        import uuid
        archive_id = f"archive-{uuid.uuid4().hex[:12]}"

        # Determine retention rule
        rule = self._retention_rules.get(rule_id, self.HIPAA_RETENTION)

        # Calculate sizes
        original_json = json.dumps(events, default=str).encode("utf-8")
        original_size = len(original_json)

        compressed = gzip.compress(original_json) if rule.compress else original_json
        compressed_size = len(compressed)

        # Compute checksum
        checksum = hashlib.sha256(compressed).hexdigest()

        metadata = ArchiveMetadata(
            archive_id=archive_id,
            archive_name=name or f"Audit Archive {start_date.date()} to {end_date.date()}",
            start_date=start_date,
            end_date=end_date,
            total_events=len(events),
            compressed_size_bytes=compressed_size,
            original_size_bytes=original_size,
            format=ArchiveFormat.JSON_GZ if rule.compress else ArchiveFormat.JSON,
            checksum=checksum,
            tenant_id=tenant_id,
            retention_until=end_date + timedelta(days=rule.delete_after_days),
        )

        self._archives[archive_id] = metadata
        self._archive_data[archive_id] = events

        return metadata

    def get_archive(self, archive_id: str) -> Optional[ArchiveMetadata]:
        """Obtiene metadata de archive."""
        return self._archives.get(archive_id)

    def get_archived_events(self, archive_id: str) -> Optional[list[dict]]:
        """Obtiene eventos de archive."""
        return self._archive_data.get(archive_id)

    def retrieve_from_archive(
        self,
        archive_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        actor_id: Optional[str] = None,
    ) -> list[dict]:
        """Recupera eventos del archive con filtros."""
        events = self._archive_data.get(archive_id, [])
        filtered = events

        if since:
            filtered = [e for e in filtered if e.get("timestamp", datetime.min) >= since]
        if until:
            filtered = [e for e in filtered if e.get("timestamp", datetime.max) <= until]
        if actor_id:
            filtered = [e for e in filtered if e.get("actor_id") == actor_id]

        return filtered

    def verify_archive_integrity(self, archive_id: str) -> tuple[bool, str]:
        """Verifica integridad de archive."""
        metadata = self._archives.get(archive_id)
        if not metadata:
            return False, "Archive not found"

        events = self._archive_data.get(archive_id, [])
        import gzip
        import json
        json_data = json.dumps(events, default=str).encode("utf-8")
        compressed = gzip.compress(json_data)
        checksum = hashlib.sha256(compressed).hexdigest()

        if checksum == metadata.checksum:
            return True, "Archive integrity verified"
        return False, f"Checksum mismatch: expected {metadata.checksum}, got {checksum}"

    def get_archives_by_tenant(self, tenant_id: str) -> list[ArchiveMetadata]:
        """Obtiene archives de un tenant."""
        return [
            a for a in self._archives.values()
            if a.tenant_id == tenant_id
        ]

    def get_expiring_archives(
        self,
        within_days: int = 30,
    ) -> list[ArchiveMetadata]:
        """Obtiene archives próximos a expirar."""
        cutoff = datetime.now(timezone.utc) + timedelta(days=within_days)
        return [
            a for a in self._archives.values()
            if a.retention_until and a.retention_until <= cutoff
        ]

    def delete_archive(self, archive_id: str) -> bool:
        """Elimina archive (soft delete)."""
        if archive_id in self._archives:
            self._archives[archive_id].status = ArchiveStatus.DELETED
            # Remove data
            if archive_id in self._archive_data:
                del self._archive_data[archive_id]
            return True
        return False

    def get_archive_statistics(self) -> dict:
        """Obtiene estadísticas de archivado."""
        total_archives = len(self._archives)
        total_events = sum(a.total_events for a in self._archives.values())
        total_size = sum(a.compressed_size_bytes for a in self._archives.values())
        total_original = sum(a.original_size_bytes for a in self._archives.values())

        by_status = {}
        for a in self._archives.values():
            by_status[a.status.value] = by_status.get(a.status.value, 0) + 1

        return {
            "total_archives": total_archives,
            "total_events_archived": total_events,
            "total_size_compressed_mb": round(total_size / 1024 / 1024, 2),
            "total_size_original_mb": round(total_original / 1024 / 1024, 2),
            "compression_ratio": round((1 - total_size / total_original) * 100, 1) if total_original else 0,
            "by_status": by_status,
            "expiring_within_30_days": len(self.get_expiring_archives(30)),
        }
