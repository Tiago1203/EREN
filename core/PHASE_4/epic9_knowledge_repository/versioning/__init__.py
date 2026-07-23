"""
PHASE 4 - EPIC 9: Versioning Module

Control de versiones:
- Version Manager
- Knowledge Version
- Version History
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class VersionStatus(str, Enum):
    """Estados de versión."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class VersionType(str, Enum):
    """Tipos de versión."""
    MAJOR = "major"       # Breaking changes
    MINOR = "minor"       # New features
    PATCH = "patch"       # Bug fixes


@dataclass
class KnowledgeVersion:
    """Versión de conocimiento."""
    version_id: str
    document_id: str
    version_number: str
    
    # Type
    version_type: VersionType = VersionType.MINOR
    
    # Status
    status: VersionStatus = VersionStatus.DRAFT
    
    # Content
    content_hash: str = ""
    content_size: int = 0
    
    # Changes
    changes_summary: str = ""
    changes_detail: list[str] = field(default_factory=list)
    
    # Metadata
    author: str = ""
    created_at: str = ""
    published_at: str = ""
    archived_at: str = ""
    
    # Parent
    parent_version_id: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def get_version_string(self) -> str:
        """Obtiene string de versión."""
        return self.version_number


@dataclass
class VersionHistory:
    """Historial de versiones."""
    document_id: str
    versions: list[KnowledgeVersion] = field(default_factory=list)
    
    current_version: str = ""
    latest_published: str = ""
    
    def add_version(self, version: KnowledgeVersion) -> None:
        """Añade versión."""
        self.versions.append(version)
        self.versions.sort(key=lambda v: v.created_at, reverse=True)
    
    def get_version(self, version_id: str) -> KnowledgeVersion | None:
        """Obtiene versión específica."""
        for v in self.versions:
            if v.version_id == version_id:
                return v
        return None
    
    def get_published_versions(self) -> list[KnowledgeVersion]:
        """Obtiene versiones publicadas."""
        return [v for v in self.versions if v.status == VersionStatus.PUBLISHED]


class BaseVersionManager(ABC):
    """Clase base para gestores de versiones."""
    
    @abstractmethod
    async def create_version(self, version: KnowledgeVersion) -> KnowledgeVersion:
        """Crea versión."""
        ...
    
    @abstractmethod
    async def get_version(self, version_id: str) -> KnowledgeVersion | None:
        """Obtiene versión."""
        ...
    
    @abstractmethod
    async def publish_version(self, version_id: str) -> KnowledgeVersion:
        """Publica versión."""
        ...
    
    @abstractmethod
    async def archive_version(self, version_id: str) -> KnowledgeVersion:
        """Archiva versión."""
        ...


class InMemoryVersionManager(BaseVersionManager):
    """Gestor de versiones en memoria."""
    
    def __init__(self):
        self._versions: dict[str, KnowledgeVersion] = {}
        self._history: dict[str, VersionHistory] = {}
    
    async def create_version(self, version: KnowledgeVersion) -> KnowledgeVersion:
        """Crea versión."""
        self._versions[version.version_id] = version
        
        # Update history
        if version.document_id not in self._history:
            self._history[version.document_id] = VersionHistory(
                document_id=version.document_id
            )
        
        self._history[version.document_id].add_version(version)
        
        return version
    
    async def get_version(self, version_id: str) -> KnowledgeVersion | None:
        """Obtiene versión."""
        return self._versions.get(version_id)
    
    async def publish_version(self, version_id: str) -> KnowledgeVersion:
        """Publica versión."""
        version = self._versions.get(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        version.status = VersionStatus.PUBLISHED
        version.published_at = datetime.now().isoformat()
        
        # Update history
        if version.document_id in self._history:
            self._history[version.document_id].latest_published = version_id
        
        return version
    
    async def archive_version(self, version_id: str) -> KnowledgeVersion:
        """Archiva versión."""
        version = self._versions.get(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        version.status = VersionStatus.ARCHIVED
        version.archived_at = datetime.now().isoformat()
        
        return version
    
    async def get_history(self, document_id: str) -> VersionHistory | None:
        """Obtiene historial."""
        return self._history.get(document_id)
    
    async def get_latest_version(self, document_id: str) -> KnowledgeVersion | None:
        """Obtiene última versión."""
        history = self._history.get(document_id)
        if history and history.versions:
            return history.versions[0]
        return None


class VersionComparator:
    """Comparador de versiones."""
    
    def compare(
        self,
        version1: KnowledgeVersion,
        version2: KnowledgeVersion,
    ) -> dict:
        """Compara dos versiones."""
        return {
            "same_content": version1.content_hash == version2.content_hash,
            "same_type": version1.version_type == version2.version_type,
            "older": version1.created_at < version2.created_at,
            "newer": version1.created_at > version2.created_at,
        }


__all__ = [
    "VersionStatus",
    "VersionType",
    "KnowledgeVersion",
    "VersionHistory",
    "BaseVersionManager",
    "InMemoryVersionManager",
    "VersionComparator",
]
