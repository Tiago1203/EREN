"""
PHASE 4 - EPIC 9: Repository Module

Gestión del repositorio:
- Repository Manager
- Source Registry
- Repository Stats
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class RepositoryType(str, Enum):
    """Tipos de repositorio."""
    PRIMARY = "primary"
    ARCHIVE = "archive"
    STAGING = "staging"
    VALIDATION = "validation"


class RepositoryStatus(str, Enum):
    """Estados del repositorio."""
    ACTIVE = "active"
    READ_ONLY = "read_only"
    ARCHIVED = "archived"


@dataclass
class RepositoryStats:
    """Estadísticas del repositorio."""
    total_documents: int = 0
    total_chunks: int = 0
    total_versions: int = 0
    total_collections: int = 0
    total_size_bytes: int = 0
    
    last_updated: str = ""
    last_document_added: str = ""
    
    quality_distribution: dict[str, int] = field(default_factory=dict)
    domain_distribution: dict[str, int] = field(default_factory=dict)


@dataclass
class Repository:
    """Repositorio de conocimiento."""
    repository_id: str
    name: str
    repository_type: RepositoryType
    
    # Stats
    stats: RepositoryStats = field(default_factory=RepositoryStats)
    
    # Config
    status: RepositoryStatus = RepositoryStatus.ACTIVE
    max_documents: int = 0
    auto_archive: bool = False
    
    # Metadata
    created_at: str = ""
    updated_at: str = ""
    description: str = ""
    
    # Indexing
    indexed: bool = False
    index_version: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


class SourceRegistryEntry:
    """Entrada del registro de fuentes."""
    source_id: str
    repository_id: str
    
    # Source info
    source_type: str
    title: str
    url: str = ""
    doi: str = ""
    pmid: str = ""
    
    # Status
    status: str = "active"
    is_indexed: bool = False
    
    # Timestamps
    registered_at: str = ""
    last_accessed: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now().isoformat()


class BaseRepositoryManager(ABC):
    """Clase base para gestores de repositorio."""
    
    @abstractmethod
    async def create_repository(self, repo: Repository) -> Repository:
        """Crea repositorio."""
        ...
    
    @abstractmethod
    async def get_repository(self, repository_id: str) -> Repository | None:
        """Obtiene repositorio."""
        ...
    
    @abstractmethod
    async def update_repository(self, repo: Repository) -> Repository:
        """Actualiza repositorio."""
        ...
    
    @abstractmethod
    async def delete_repository(self, repository_id: str) -> bool:
        """Elimina repositorio."""
        ...


class InMemoryRepositoryManager(BaseRepositoryManager):
    """Gestor de repositorios en memoria."""
    
    def __init__(self):
        self._repositories: dict[str, Repository] = {}
        self._sources: dict[str, SourceRegistryEntry] = {}
    
    async def create_repository(self, repo: Repository) -> Repository:
        """Crea repositorio."""
        if repo.repository_id in self._repositories:
            raise ValueError(f"Repository {repo.repository_id} exists")
        
        self._repositories[repo.repository_id] = repo
        return repo
    
    async def get_repository(self, repository_id: str) -> Repository | None:
        """Obtiene repositorio."""
        return self._repositories.get(repository_id)
    
    async def update_repository(self, repo: Repository) -> Repository:
        """Actualiza repositorio."""
        if repo.repository_id not in self._repositories:
            raise ValueError(f"Repository {repo.repository_id} not found")
        
        repo.updated_at = datetime.now().isoformat()
        self._repositories[repo.repository_id] = repo
        return repo
    
    async def delete_repository(self, repository_id: str) -> bool:
        """Elimina repositorio."""
        if repository_id in self._repositories:
            del self._repositories[repository_id]
            return True
        return False
    
    async def list_repositories(self) -> list[Repository]:
        """Lista repositorios."""
        return list(self._repositories.values())
    
    async def register_source(self, entry: SourceRegistryEntry) -> SourceRegistryEntry:
        """Registra fuente."""
        self._sources[entry.source_id] = entry
        return entry
    
    async def get_source(self, source_id: str) -> SourceRegistryEntry | None:
        """Obtiene fuente."""
        return self._sources.get(source_id)
    
    async def list_sources(self, repository_id: str | None = None) -> list[SourceRegistryEntry]:
        """Lista fuentes."""
        if repository_id:
            return [s for s in self._sources.values() if s.repository_id == repository_id]
        return list(self._sources.values())


__all__ = [
    "RepositoryType",
    "RepositoryStatus",
    "RepositoryStats",
    "Repository",
    "SourceRegistryEntry",
    "BaseRepositoryManager",
    "InMemoryRepositoryManager",
]
