"""
PHASE 7 - EPIC 5: Migration Service

Migration de equipos, mantenimientos, establecimientos y KPIs
desde PHASE_1 hacia el sistema EPIC 5.
Integración: PHASE_1 (datos legacy), EPIC 2 (multi-tenant).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import threading
import uuid


class MigrationStatus(str, Enum):
    """Estado de migración."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class MigrationEntity(str, Enum):
    """Entidades migrables."""
    EQUIPMENT = "equipment"
    MAINTENANCE = "maintenance"
    ESTABLISHMENT = "establishment"
    KPI = "kpi"
    USER = "user"
    AUDIT_LOG = "audit_log"


@dataclass
class MigrationJob:
    """Job de migración."""
    job_id: str
    entity_type: MigrationEntity
    status: MigrationStatus
    total_records: int = 0
    migrated_records: int = 0
    failed_records: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    errors: list = field(default_factory=list)
    tenant_id: Optional[str] = None
    source_system: str = "PHASE_1"
    target_system: str = "PHASE_7"


@dataclass
class MigrationReport:
    """Reporte de migración."""
    job_id: str
    entity_type: str
    total: int
    migrated: int
    failed: int
    duration_seconds: float
    errors: list
    warnings: list


class MigrationService:
    """Servicio de migración de datos."""

    def __init__(self):
        self._jobs: dict[str, MigrationJob] = {}
        self._lock = threading.Lock()

    def create_migration_job(
        self,
        entity_type: MigrationEntity,
        total_records: int,
        tenant_id: Optional[str] = None,
    ) -> MigrationJob:
        """Crea job de migración."""
        job_id = f"mig-{uuid.uuid4().hex[:12]}"
        job = MigrationJob(
            job_id=job_id,
            entity_type=entity_type,
            status=MigrationStatus.PENDING,
            total_records=total_records,
            tenant_id=tenant_id,
        )

        with self._lock:
            self._jobs[job_id] = job

        return job

    def start_migration(self, job_id: str) -> bool:
        """Inicia migración."""
        with self._lock:
            if job_id not in self._jobs:
                return False
            job = self._jobs[job_id]
            job.status = MigrationStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
        return True

    def update_progress(
        self,
        job_id: str,
        migrated: int,
        failed: int,
        error: Optional[str] = None,
    ) -> None:
        """Actualiza progreso de migración."""
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.migrated_records = migrated
                job.failed_records = failed
                if error:
                    job.errors.append({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "error": error,
                    })

    def complete_migration(self, job_id: str) -> Optional[MigrationReport]:
        """Completa migración y genera reporte."""
        with self._lock:
            if job_id not in self._jobs:
                return None

            job = self._jobs[job_id]
            job.status = MigrationStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)

            duration = 0.0
            if job.started_at and job.completed_at:
                duration = (job.completed_at - job.started_at).total_seconds()

            report = MigrationReport(
                job_id=job_id,
                entity_type=job.entity_type.value,
                total=job.total_records,
                migrated=job.migrated_records,
                failed=job.failed_records,
                duration_seconds=duration,
                errors=job.errors[:50],  # Limit errors in report
                warnings=[
                    f"Failed records: {job.failed_records}/{job.total_records}"
                ] if job.failed_records > 0 else [],
            )

        return report

    def migrate_equipment(
        self,
        source_equipment: list[dict],
        tenant_id: str,
        migrate_by: str = "system",
    ) -> MigrationReport:
        """Migra equipos desde PHASE_1."""
        job = self.create_migration_job(
            MigrationEntity.EQUIPMENT,
            total_records=len(source_equipment),
            tenant_id=tenant_id,
        )
        self.start_migration(job.job_id)

        migrated = 0
        failed = 0
        errors = []

        for eq in source_equipment:
            try:
                # Map PHASE_1 equipment to PHASE_7 format
                migrated_equipment = {
                    "equipment_id": eq.get("id", f"eq-{uuid.uuid4().hex[:12]}"),
                    "name": eq.get("name", "Unknown"),
                    "serial_number": eq.get("serial_number", ""),
                    "model": eq.get("model", ""),
                    "manufacturer": eq.get("manufacturer", ""),
                    "status": eq.get("status", "active"),
                    "tenant_id": tenant_id,
                    "migrated_from": "PHASE_1",
                    "migrated_at": datetime.now(timezone.utc).isoformat(),
                    "migrated_by": migrate_by,
                }
                migrated += 1
            except Exception as e:
                failed += 1
                errors.append(str(e))

        self.update_progress(job.job_id, migrated, failed)
        report = self.complete_migration(job.job_id)

        return report

    def migrate_kpis(
        self,
        source_kpis: list[dict],
        tenant_id: str,
        migrate_by: str = "system",
    ) -> MigrationReport:
        """Migra KPIs."""
        job = self.create_migration_job(
            MigrationEntity.KPI,
            total_records=len(source_kpis),
            tenant_id=tenant_id,
        )
        self.start_migration(job.job_id)

        migrated = 0
        failed = 0

        for kpi in source_kpis:
            try:
                migrated_kpi = {
                    "kpi_id": kpi.get("id", f"kpi-{uuid.uuid4().hex[:12]}"),
                    "name": kpi.get("name", "Unknown KPI"),
                    "value": kpi.get("value", 0),
                    "unit": kpi.get("unit", ""),
                    "category": kpi.get("category", "general"),
                    "tenant_id": tenant_id,
                    "migrated_from": "PHASE_1",
                    "migrated_at": datetime.now(timezone.utc).isoformat(),
                    "migrated_by": migrate_by,
                }
                migrated += 1
            except Exception:
                failed += 1

        self.update_progress(job.job_id, migrated, failed)
        return self.complete_migration(job.job_id)

    def get_migration_status(self, job_id: Optional[str] = None) -> dict:
        """Estado de migraciones."""
        with self._lock:
            if job_id:
                job = self._jobs.get(job_id)
                if not job:
                    return {}
                return {
                    "job_id": job.job_id,
                    "entity_type": job.entity_type.value,
                    "status": job.status.value,
                    "total": job.total_records,
                    "migrated": job.migrated_records,
                    "failed": job.failed_records,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error_count": len(job.errors),
                }

            pending = sum(1 for j in self._jobs.values() if j.status == MigrationStatus.PENDING)
            running = sum(1 for j in self._jobs.values() if j.status == MigrationStatus.RUNNING)
            completed = sum(1 for j in self._jobs.values() if j.status == MigrationStatus.COMPLETED)
            failed = sum(1 for j in self._jobs.values() if j.status == MigrationStatus.FAILED)

            return {
                "total_jobs": len(self._jobs),
                "pending": pending,
                "running": running,
                "completed": completed,
                "failed": failed,
            }
