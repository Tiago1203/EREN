"""
PHASE 4 - EPIC 11: Lifecycle Module

Gestión del ciclo de vida:
- Lifecycle Manager
- Version Control
- Rollback Manager
- Archive Manager
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class LifecycleStage(str, Enum):
    """Etapas del ciclo de vida."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class ArchiveReason(str, Enum):
    """Razones de archivado."""
    SUPERSEDED = "superseded"
    RETENTION_PERIOD = "retention_period"
    MANUAL = "manual"
    COMPLIANCE = "compliance"


@dataclass
class KnowledgeSnapshot:
    """Snapshot de conocimiento."""
    snapshot_id: str
    document_id: str
    
    # Content
    content: str
    content_hash: str
    
    # Metadata
    version: str
    stage: LifecycleStage
    
    # Timestamps
    created_at: str = ""
    snapshot_reason: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class RollbackPlan:
    """Plan de rollback."""
    plan_id: str
    document_id: str
    
    # Target
    target_snapshot_id: str
    current_version: str
    
    # Plan
    steps: list[str] = field(default_factory=list)
    estimated_duration_minutes: int = 0
    
    # Status
    is_safe: bool = True
    warnings: list[str] = field(default_factory=list)
    
    created_at: str = ""


class BaseLifecycleManager(ABC):
    """Clase base para gestión de ciclo de vida."""
    
    @abstractmethod
    async def create_snapshot(self, document_id: str, content: str) -> KnowledgeSnapshot:
        """Crea snapshot."""
        ...
    
    @abstractmethod
    async def rollback_to(self, document_id: str, snapshot_id: str) -> bool:
        """Rollback a snapshot."""
        ...


class InMemoryLifecycleManager(BaseLifecycleManager):
    """Gestor de ciclo de vida en memoria."""
    
    def __init__(self):
        self._snapshots: dict[str, list[KnowledgeSnapshot]] = {}
    
    async def create_snapshot(self, document_id: str, content: str) -> KnowledgeSnapshot:
        """Crea snapshot."""
        import hashlib
        import uuid
        
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        snapshot = KnowledgeSnapshot(
            snapshot_id=str(uuid.uuid4())[:16],
            document_id=document_id,
            content=content,
            content_hash=content_hash,
            version=f"v{datetime.now().strftime('%Y%m%d%H%M%S')}",
            stage=LifecycleStage.DRAFT,
        )
        
        if document_id not in self._snapshots:
            self._snapshots[document_id] = []
        
        self._snapshots[document_id].append(snapshot)
        
        return snapshot
    
    async def rollback_to(self, document_id: str, snapshot_id: str) -> bool:
        """Rollback a snapshot."""
        snapshots = self._snapshots.get(document_id, [])
        
        for snapshot in snapshots:
            if snapshot.snapshot_id == snapshot_id:
                return True
        
        return False
    
    async def get_snapshots(self, document_id: str) -> list[KnowledgeSnapshot]:
        """Obtiene snapshots."""
        return self._snapshots.get(document_id, [])
    
    async def get_latest_snapshot(self, document_id: str) -> KnowledgeSnapshot | None:
        """Obtiene último snapshot."""
        snapshots = self._snapshots.get(document_id, [])
        return snapshots[-1] if snapshots else None


class RollbackManager:
    """Gestor de rollbacks."""
    
    def __init__(self, lifecycle_manager: BaseLifecycleManager):
        self._lifecycle = lifecycle_manager
    
    async def create_plan(
        self,
        document_id: str,
        target_snapshot_id: str,
    ) -> RollbackPlan:
        """Crea plan de rollback."""
        import uuid
        
        snapshots = await self._lifecycle.get_snapshots(document_id)
        current = await self._lifecycle.get_latest_snapshot(document_id)
        
        target = None
        for s in snapshots:
            if s.snapshot_id == target_snapshot_id:
                target = s
                break
        
        warnings = []
        is_safe = True
        
        if not target:
            warnings.append("Target snapshot not found")
            is_safe = False
        
        if current:
            age = datetime.now() - datetime.fromisoformat(current.created_at)
            if age > timedelta(days=30):
                warnings.append("Current version is older than 30 days")
        
        plan = RollbackPlan(
            plan_id=str(uuid.uuid4())[:16],
            document_id=document_id,
            target_snapshot_id=target_snapshot_id,
            current_version=current.version if current else "unknown",
            steps=[
                "1. Create backup of current version",
                "2. Load target snapshot content",
                "3. Update document with snapshot content",
                "4. Create new snapshot of rolled-back version",
                "5. Update metadata",
            ],
            estimated_duration_minutes=5,
            is_safe=is_safe,
            warnings=warnings,
        )
        
        return plan
    
    async def execute_plan(self, plan: RollbackPlan) -> bool:
        """Ejecuta plan de rollback."""
        if not plan.is_safe:
            return False
        
        return await self._lifecycle.rollback_to(
            plan.document_id,
            plan.target_snapshot_id,
        )


__all__ = [
    "LifecycleStage",
    "ArchiveReason",
    "KnowledgeSnapshot",
    "RollbackPlan",
    "BaseLifecycleManager",
    "InMemoryLifecycleManager",
    "RollbackManager",
]
