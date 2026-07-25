"""
PHASE 7 - EPIC 3: Backup Manager

Automated backup management:
- Full and incremental backups
- Backup scheduling
- Retention policies
- Backup verification
- Integration con EPIC 1 (audit) y EPIC 2 (multi-tenant)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
import uuid


class BackupType(str, Enum):
    """Tipos de backup."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(str, Enum):
    """Estados de backup."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class BackupJob:
    """Job de backup."""
    job_id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    size_bytes: int = 0
    duration_seconds: float = 0.0
    checksum: str = ""
    error: str = ""
    tenant_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class BackupRetention:
    """Retention policy para backups."""
    name: str
    full_retention_days: int = 30
    incremental_retention_days: int = 7
    weekly_retention_count: int = 4
    monthly_retention_count: int = 12
    yearly_retention_count: int = 3
    verify_after_days: int = 7


class BackupManager:
    """Gestor de backups automatizados."""

    # Retention policies predefinidas
    HIPAA_RETENTION = BackupRetention(
        name="hipaa",
        full_retention_days=2555,      # ~7 years HIPAA
        incremental_retention_days=90,
    )

    STANDARD_RETENTION = BackupRetention(
        name="standard",
        full_retention_days=30,
        incremental_retention_days=7,
        weekly_retention_count=4,
        monthly_retention_count=12,
    )

    COMPLIANCE_RETENTION = BackupRetention(
        name="compliance",
        full_retention_days=2555,
        incremental_retention_days=365,
        yearly_retention_count=7,
    )

    def __init__(self):
        self._jobs: list[BackupJob] = []
        self._retention_policies: dict[str, BackupRetention] = {
            "hipaa": self.HIPAA_RETENTION,
            "standard": self.STANDARD_RETENTION,
            "compliance": self.COMPLIANCE_RETENTION,
        }

    def create_backup_job(
        self,
        backup_type: BackupType,
        tenant_id: Optional[str] = None,
        retention_policy: str = "standard",
    ) -> BackupJob:
        """Crea un job de backup."""
        job = BackupJob(
            job_id=f"backup-{uuid.uuid4().hex[:12]}",
            backup_type=backup_type,
            status=BackupStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            tenant_id=tenant_id,
            metadata={"retention_policy": retention_policy},
        )
        self._jobs.append(job)
        return job

    def start_backup(self, job_id: str) -> BackupJob:
        """Inicia un backup."""
        job = self._get_job(job_id)
        if not job:
            raise ValueError(f"Backup job {job_id} not found")

        job.status = BackupStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        return job

    def complete_backup(
        self,
        job_id: str,
        size_bytes: int,
        checksum: str,
    ) -> BackupJob:
        """Completa un backup."""
        job = self._get_job(job_id)
        if not job:
            raise ValueError(f"Backup job {job_id} not found")

        job.status = BackupStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.size_bytes = size_bytes
        job.checksum = checksum
        job.duration_seconds = (
            job.completed_at - job.started_at
        ).total_seconds() if job.started_at else 0

        return job

    def fail_backup(self, job_id: str, error: str) -> BackupJob:
        """Marca backup como fallido."""
        job = self._get_job(job_id)
        if not job:
            raise ValueError(f"Backup job {job_id} not found")

        job.status = BackupStatus.FAILED
        job.completed_at = datetime.now(timezone.utc)
        job.error = error

        return job

    def verify_backup(self, job_id: str) -> bool:
        """Verifica integridad de backup."""
        job = self._get_job(job_id)
        if not job:
            return False

        # In production: verify checksum
        if job.checksum:
            job.status = BackupStatus.VERIFIED
            return True
        return False

    def _get_job(self, job_id: str) -> Optional[BackupJob]:
        """Obtiene un job."""
        for job in self._jobs:
            if job.job_id == job_id:
                return job
        return None

    def get_backup_schedule(
        self,
        retention_policy: str = "standard",
    ) -> dict:
        """Genera schedule de backups."""
        policy = self._retention_policies.get(retention_policy, self.STANDARD_RETENTION)

        now = datetime.now(timezone.utc)
        schedule = {
            "policy": retention_policy,
            "jobs": [
                {
                    "type": BackupType.FULL.value,
                    "cron": "0 2 * * 0",         # Weekly on Sunday at 2am
                    "retention_days": policy.full_retention_days,
                },
                {
                    "type": BackupType.INCREMENTAL.value,
                    "cron": "0 2 * * 1-6",       # Daily except Sunday at 2am
                    "retention_days": policy.incremental_retention_days,
                },
                {
                    "type": BackupType.FULL.value,
                    "cron": "0 3 1 * *",          # Monthly on 1st at 3am
                    "retention_days": policy.monthly_retention_count * 30,
                },
            ],
        }
        return schedule

    def cleanup_old_backups(
        self,
        retention_policy: str = "standard",
    ) -> list[str]:
        """Limpia backups antiguos según política de retención."""
        policy = self._retention_policies.get(retention_policy, self.STANDARD_RETENTION)
        now = datetime.now(timezone.utc)
        to_delete: list[str] = []

        for job in self._jobs:
            if job.status not in (BackupStatus.COMPLETED, BackupStatus.VERIFIED):
                continue

            if job.completed_at:
                age_days = (now - job.completed_at).days

                if job.backup_type == BackupType.FULL:
                    if age_days > policy.full_retention_days:
                        to_delete.append(job.job_id)
                elif job.backup_type == BackupType.INCREMENTAL:
                    if age_days > policy.incremental_retention_days:
                        to_delete.append(job.job_id)

        return to_delete

    def get_backup_status(self, tenant_id: Optional[str] = None) -> dict:
        """Obtiene estado de backups."""
        jobs = self._jobs
        if tenant_id:
            jobs = [j for j in jobs if j.tenant_id == tenant_id]

        by_status = {}
        for job in jobs:
            key = job.status.value
            by_status[key] = by_status.get(key, 0) + 1

        total_size = sum(j.size_bytes for j in jobs)
        recent = sorted(
            [j for j in jobs if j.status == BackupStatus.COMPLETED],
            key=lambda j: j.completed_at or datetime.min,
            reverse=True,
        )[:10]

        return {
            "total_jobs": len(jobs),
            "by_status": by_status,
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024**3), 2),
            "recent_backups": [
                {
                    "job_id": j.job_id,
                    "type": j.backup_type.value,
                    "status": j.status.value,
                    "size_gb": round(j.size_bytes / (1024**3), 2),
                    "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                }
                for j in recent
            ],
        }

    def estimate_backup_size(
        self,
        backup_type: BackupType,
        tenant_id: Optional[str] = None,
    ) -> dict:
        """Estima tamaño de backup."""
        # In production: query database for data size
        estimated_size_bytes = 0

        if backup_type == BackupType.FULL:
            estimated_size_bytes = 10 * 1024 * 1024 * 1024  # 10GB estimate
        elif backup_type == BackupType.INCREMENTAL:
            estimated_size_bytes = 1 * 1024 * 1024 * 1024   # 1GB estimate
        else:
            estimated_size_bytes = 5 * 1024 * 1024 * 1024   # 5GB estimate

        return {
            "estimated_size_bytes": estimated_size_bytes,
            "estimated_size_gb": round(estimated_size_bytes / (1024**3), 2),
            "backup_type": backup_type.value,
            "estimated_duration_minutes": round(estimated_size_bytes / (50 * 1024 * 1024), 1),  # ~50MB/min
        }
