"""
PHASE 4 - EPIC 10: Sync Module

Sincronización de conocimiento:
- Sync Manager
- Sync Job
- Delta Processor
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SyncSource(str, Enum):
    """Fuentes de sincronización."""
    PUBMED = "pubmed"
    FDA = "fda"
    EMA = "ema"
    CLINICAL_GUIDELINES = "clinical_guidelines"
    DEVICE_MANUFACTURERS = "device_manufacturers"
    STANDARDS_BODIES = "standards_bodies"


class SyncStatus(str, Enum):
    """Estado de sincronización."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class SyncPriority(str, Enum):
    """Prioridad de sincronización."""
    CRITICAL = "critical"    # Recall, safety alerts
    HIGH = "high"          # Guidelines updates
    NORMAL = "normal"      # Regular updates
    LOW = "low"           # Background sync


@dataclass
class SyncJob:
    """Trabajo de sincronización."""
    job_id: str
    source: SyncSource
    
    # Status
    status: SyncStatus = SyncStatus.PENDING
    priority: SyncPriority = SyncPriority.NORMAL
    
    # Content
    items_to_sync: int = 0
    items_synced: int = 0
    items_failed: int = 0
    
    # Metadata
    started_at: str = ""
    completed_at: str = ""
    error_message: str = ""
    
    # Tracking
    last_sync_time: str = ""
    next_sync_time: str = ""
    
    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().isoformat()
    
    def get_progress(self) -> float:
        """Obtiene progreso."""
        if self.items_to_sync == 0:
            return 0.0
        return self.items_synced / self.items_to_sync
    
    def is_complete(self) -> bool:
        """Verifica si está completo."""
        return self.status == SyncStatus.COMPLETED


@dataclass
class UpdatePackage:
    """Paquete de actualización."""
    package_id: str
    source: SyncSource
    documents: list[dict] = field(default_factory=list)
    
    # Changes
    added_count: int = 0
    updated_count: int = 0
    deleted_count: int = 0
    
    # Metadata
    sync_job_id: str = ""
    created_at: str = ""
    version: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class SyncDelta:
    """Delta de sincronización."""
    document_id: str
    source: SyncSource
    
    # Change type
    change_type: str  # "added", "updated", "deleted"
    
    # Content
    content_hash: str = ""
    version: str = ""
    
    # Timestamp
    changed_at: str = ""
    
    def is_addition(self) -> bool:
        """Es adición."""
        return self.change_type == "added"
    
    def is_update(self) -> bool:
        """Es actualización."""
        return self.change_type == "updated"
    
    def is_deletion(self) -> bool:
        """Es eliminación."""
        return self.change_type == "deleted"


class BaseSyncManager(ABC):
    """Clase base para gestores de sincronización."""
    
    @abstractmethod
    async def start_sync(self, source: SyncSource) -> SyncJob:
        """Inicia sincronización."""
        ...
    
    @abstractmethod
    async def get_job_status(self, job_id: str) -> SyncJob | None:
        """Obtiene estado del trabajo."""
        ...
    
    @abstractmethod
    async def get_delta(self, source: SyncSource, since: str) -> list[SyncDelta]:
        """Obtiene delta desde última sync."""
        ...


class InMemorySyncManager(BaseSyncManager):
    """Gestor de sincronización en memoria."""
    
    def __init__(self):
        self._jobs: dict[str, SyncJob] = {}
        self._deltas: dict[str, list[SyncDelta]] = {}
    
    async def start_sync(self, source: SyncSource) -> SyncJob:
        """Inicia sincronización."""
        import uuid
        
        job = SyncJob(
            job_id=str(uuid.uuid4())[:16],
            source=source,
            status=SyncStatus.IN_PROGRESS,
            started_at=datetime.now().isoformat(),
        )
        
        self._jobs[job.job_id] = job
        return job
    
    async def get_job_status(self, job_id: str) -> SyncJob | None:
        """Obtiene estado del trabajo."""
        return self._jobs.get(job_id)
    
    async def get_delta(self, source: SyncSource, since: str) -> list[SyncDelta]:
        """Obtiene delta desde última sync."""
        key = f"{source.value}:{since}"
        return self._deltas.get(key, [])
    
    async def update_job(self, job: SyncJob) -> None:
        """Actualiza trabajo."""
        self._jobs[job.job_id] = job
    
    async def complete_job(
        self,
        job_id: str,
        items_synced: int = 0,
        items_failed: int = 0,
    ) -> SyncJob:
        """Completa trabajo."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = SyncStatus.COMPLETED
        job.items_synced = items_synced
        job.items_failed = items_failed
        job.completed_at = datetime.now().isoformat()
        
        return job


class DeltaProcessor:
    """Procesador de deltas."""
    
    def __init__(self):
        self._processed: set[str] = set()
    
    def process(self, deltas: list[SyncDelta]) -> dict:
        """Procesa deltas."""
        additions = []
        updates = []
        deletions = []
        
        for delta in deltas:
            if delta.document_id in self._processed:
                continue
            
            if delta.is_addition():
                additions.append(delta)
            elif delta.is_update():
                updates.append(delta)
            elif delta.is_deletion():
                deletions.append(delta)
            
            self._processed.add(delta.document_id)
        
        return {
            "additions": additions,
            "updates": updates,
            "deletions": deletions,
            "total": len(deltas),
        }


__all__ = [
    "SyncSource",
    "SyncStatus",
    "SyncPriority",
    "SyncJob",
    "UpdatePackage",
    "SyncDelta",
    "BaseSyncManager",
    "InMemorySyncManager",
    "DeltaProcessor",
]
