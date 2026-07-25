"""
PHASE 7 - EPIC 3: Restore Service

Data restoration procedures:
- Point-in-time recovery
- Selective table restore
- Cross-tenant restore (EPIC 2)
- Restore verification
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class RestoreType(str, Enum):
    """Tipos de restore."""
    FULL = "full"
    POINT_IN_TIME = "point_in_time"
    SELECTIVE = "selective"
    CROSS_TENANT = "cross_tenant"


class RestoreStatus(str, Enum):
    """Estados de restore."""
    PENDING = "pending"
    VALIDATING = "validating"
    RESTORING = "restoring"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RestoreJob:
    """Job de restore."""
    job_id: str
    restore_type: RestoreType
    status: RestoreStatus
    backup_job_id: str
    target_tenant_id: Optional[str]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tables_restored: int = 0
    records_restored: int = 0
    duration_seconds: float = 0.0
    error: str = ""


class RestoreService:
    """Servicio de restauración."""

    def __init__(self):
        self._jobs: list[RestoreJob] = []

    def create_restore_job(
        self,
        restore_type: RestoreType,
        backup_job_id: str,
        target_tenant_id: Optional[str] = None,
    ) -> RestoreJob:
        """Crea job de restore."""
        job = RestoreJob(
            job_id=f"restore-{datetime.now().strftime('%Y%m%d%H%M%S')}-{backup_job_id[:8]}",
            restore_type=restore_type,
            status=RestoreStatus.PENDING,
            backup_job_id=backup_job_id,
            target_tenant_id=target_tenant_id,
            created_at=datetime.now(timezone.utc),
        )
        self._jobs.append(job)
        return job

    def execute_restore(self, job_id: str) -> RestoreJob:
        """Ejecuta restore."""
        job = self._get_job(job_id)
        if not job:
            raise ValueError(f"Restore job {job_id} not found")

        job.status = RestoreStatus.RESTORING
        job.started_at = datetime.now(timezone.utc)

        # In production: execute restore
        # 1. Validate backup
        job.status = RestoreStatus.VALIDATING
        # 2. Restore data
        job.status = RestoreStatus.RESTORING
        # 3. Verify
        job.status = RestoreStatus.VERIFYING
        # 4. Complete
        job.status = RestoreStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.tables_restored = 10
        job.records_restored = 50000
        job.duration_seconds = 300.0

        return job

    def fail_restore(self, job_id: str, error: str) -> RestoreJob:
        """Marca restore como fallido."""
        job = self._get_job(job_id)
        if not job:
            raise ValueError(f"Restore job {job_id} not found")

        job.status = RestoreStatus.FAILED
        job.completed_at = datetime.now(timezone.utc)
        job.error = error

        return job

    def _get_job(self, job_id: str) -> Optional[RestoreJob]:
        for job in self._jobs:
            if job.job_id == job_id:
                return job
        return None

    def get_restore_status(self) -> dict:
        """Estado de restores."""
        recent = sorted(self._jobs, key=lambda j: j.created_at, reverse=True)[:20]
        return {
            "total_jobs": len(self._jobs),
            "recent": [
                {
                    "job_id": j.job_id,
                    "type": j.restore_type.value,
                    "status": j.status.value,
                    "duration_seconds": j.duration_seconds,
                    "records_restored": j.records_restored,
                }
                for j in recent
            ],
        }
