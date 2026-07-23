"""
PHASE 4 - EPIC 9: Medical Knowledge Repository

Repositorio de conocimiento médico:
- Gestión de versiones
- Colecciones organizadas
- Metadatos ricos
- Search y browse
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional
import uuid

from core.PHASE_4.foundation import (
    KnowledgeAsset,
    KnowledgeVersion,
    KnowledgeDomain,
    GovernanceStatus,
    ExtractedEntity,
    ExtractedConcept,
    MedicalCode,
)


class RepositoryType(str, Enum):
    """Tipos de repositorio."""
    PRIMARY = "primary"           # Repo principal
    ARCHIVE = "archive"           # Archivo histórico
    STAGING = "staging"           # Pre-publicación
    VALIDATION = "validation"     # Para validación


@dataclass
class RepositoryStats:
    """Estadísticas del repositorio."""
    total_assets: int = 0
    published: int = 0
    draft: int = 0
    archived: int = 0
    by_domain: dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))


class KnowledgeRepository:
    """Repositorio de conocimiento."""
    
    def __init__(self):
        self._assets: dict[str, KnowledgeAsset] = {}
        self._versions: dict[str, list[KnowledgeVersion]] = {}
        self._by_domain: dict[KnowledgeDomain, list[str]] = {}
        self._by_status: dict[GovernanceStatus, list[str]] = {}
    
    async def store(self, asset: KnowledgeAsset) -> str:
        """Almacena asset de conocimiento."""
        # Store asset
        self._assets[asset.asset_id] = asset
        
        # Update indexes
        self._by_domain.setdefault(asset.domain, []).append(asset.asset_id)
        self._by_status.setdefault(asset.governance_status, []).append(asset.asset_id)
        
        # Create initial version
        self._versions.setdefault(asset.asset_id, []).append(KnowledgeVersion(
            version_id=str(uuid.uuid4()),
            document_id=asset.asset_id,
            version_number=asset.version,
            created_at=datetime.now(UTC),
            author=asset.created_by or "system",
        ))
        
        return asset.asset_id
    
    async def get(self, asset_id: str) -> Optional[KnowledgeAsset]:
        """Obtiene asset por ID."""
        return self._assets.get(asset_id)
    
    async def update(
        self,
        asset_id: str,
        updates: dict,
        updated_by: str,
    ) -> bool:
        """Actualiza asset."""
        if asset_id not in self._assets:
            return False
        
        asset = self._assets[asset_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        asset.updated_at = datetime.now(UTC)
        
        # Create new version
        self._versions.setdefault(asset_id, []).append(KnowledgeVersion(
            version_id=str(uuid.uuid4()),
            asset_id=asset_id,
            version_number=asset.version,
            changes_summary=updates.get("change_note", ""),
            created_at=datetime.now(UTC),
            author=updated_by or "system",
        ))
        
        return True
    
    async def list_versions(self, asset_id: str) -> list[KnowledgeVersion]:
        """Lista versiones de un asset."""
        return self._versions.get(asset_id, [])
    
    async def list_by_domain(
        self,
        domain: KnowledgeDomain,
        status: GovernanceStatus | None = None,
        limit: int = 100,
    ) -> list[KnowledgeAsset]:
        """Lista assets por dominio."""
        asset_ids = self._by_domain.get(domain, [])
        
        assets = []
        for aid in asset_ids[:limit]:
            asset = self._assets.get(aid)
            if asset and (status is None or asset.governance_status == status):
                assets.append(asset)
        
        return assets
    
    async def list_by_status(
        self,
        status: GovernanceStatus,
        limit: int = 100,
    ) -> list[KnowledgeAsset]:
        """Lista assets por estado de gobernanza."""
        asset_ids = self._by_status.get(status, [])
        
        return [
            self._assets[aid]
            for aid in asset_ids[:limit]
            if aid in self._assets
        ]
    
    async def publish(self, asset_id: str, approved_by: str) -> bool:
        """Publica asset."""
        if asset_id not in self._assets:
            return False
        
        asset = self._assets[asset_id]
        asset.governance_status = GovernanceStatus.PUBLISHED
        asset.approved_by = approved_by
        asset.published_at = datetime.now(UTC)
        asset.updated_at = datetime.now(UTC)
        
        # Update status index
        old_status = GovernanceStatus.DRAFT
        if asset_id in self._by_status.get(old_status, []):
            self._by_status[old_status].remove(asset_id)
        self._by_status.setdefault(GovernanceStatus.PUBLISHED, []).append(asset_id)
        
        return True
    
    async def archive(self, asset_id: str) -> bool:
        """Archiva asset."""
        if asset_id not in self._assets:
            return False
        
        asset = self._assets[asset_id]
        asset.governance_status = GovernanceStatus.ARCHIVED
        asset.updated_at = datetime.now(UTC)
        
        # Update status index
        old_status = GovernanceStatus.PUBLISHED
        if asset_id in self._by_status.get(old_status, []):
            self._by_status[old_status].remove(asset_id)
        self._by_status.setdefault(GovernanceStatus.ARCHIVED, []).append(asset_id)
        
        return True
    
    async def supersede(
        self,
        old_asset_id: str,
        new_asset_id: str,
    ) -> bool:
        """Supersede old asset with new one."""
        if old_asset_id not in self._assets:
            return False
        
        old_asset = self._assets[old_asset_id]
        old_asset.governance_status = GovernanceStatus.SUPERSEDED
        old_asset.supersedes_id = new_asset_id
        old_asset.updated_at = datetime.now(UTC)
        
        if new_asset_id in self._assets:
            new_asset = self._assets[new_asset_id]
            new_asset.supersedes_id = old_asset_id
        
        return True
    
    async def get_stats(self) -> RepositoryStats:
        """Obtiene estadísticas del repositorio."""
        stats = RepositoryStats()
        
        stats.total_assets = len(self._assets)
        
        for asset in self._assets.values():
            if asset.governance_status == GovernanceStatus.PUBLISHED:
                stats.published += 1
            elif asset.governance_status == GovernanceStatus.DRAFT:
                stats.draft += 1
            elif asset.governance_status == GovernanceStatus.ARCHIVED:
                stats.archived += 1
            
            domain_key = asset.domain.value
            stats.by_domain[domain_key] = stats.by_domain.get(domain_key, 0) + 1
        
        return stats
    
    async def search(
        self,
        query: str,
        domain: KnowledgeDomain | None = None,
        status: GovernanceStatus | None = None,
        limit: int = 50,
    ) -> list[KnowledgeAsset]:
        """Busca assets."""
        results = []
        query_lower = query.lower()
        
        for asset in self._assets.values():
            # Apply filters
            if domain and asset.domain != domain:
                continue
            if status and asset.governance_status != status:
                continue
            
            # Search in content
            if (query_lower in asset.content.lower() or
                query_lower in asset.title.lower()):
                results.append(asset)
        
        return results[:limit]


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Repository
from core.PHASE_4.epic9_knowledge_repository.repository import (
    RepositoryType,
    RepositoryStatus,
    RepositoryStats,
    Repository,
    SourceRegistryEntry,
    BaseRepositoryManager,
    InMemoryRepositoryManager,
)

# Versioning
from core.PHASE_4.epic9_knowledge_repository.versioning import (
    VersionStatus,
    VersionType,
    KnowledgeVersion,
    VersionHistory,
    BaseVersionManager,
    InMemoryVersionManager,
    VersionComparator,
)

# Collections
from core.PHASE_4.epic9_knowledge_repository.collections import (
    CollectionType,
    CollectionStatus,
    Collection,
    CollectionMetadata,
    BaseCollectionManager,
    InMemoryCollectionManager,
    CollectionSearcher,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    # Repository Types
    "RepositoryType",
    "RepositoryStatus",
    "RepositoryStats",
    "Repository",
    "SourceRegistryEntry",
    "BaseRepositoryManager",
    "InMemoryRepositoryManager",
    # Versioning Types
    "VersionStatus",
    "VersionType",
    "KnowledgeVersion",
    "VersionHistory",
    "BaseVersionManager",
    "InMemoryVersionManager",
    "VersionComparator",
    # Collection Types
    "CollectionType",
    "CollectionStatus",
    "Collection",
    "CollectionMetadata",
    "BaseCollectionManager",
    "InMemoryCollectionManager",
    "CollectionSearcher",
    # Main
    "KnowledgeRepository",
]
