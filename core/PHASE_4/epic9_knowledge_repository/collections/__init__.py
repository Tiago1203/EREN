"""
PHASE 4 - EPIC 9: Collections Module

Gestión de colecciones:
- Collection Manager
- Knowledge Collections
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class CollectionType(str, Enum):
    """Tipos de colección."""
    GUIDELINE = "guideline"
    PROTOCOL = "protocol"
    TRAINING = "training"
    REFERENCE = "reference"
    ARCHIVE = "archive"
    CUSTOM = "custom"


class CollectionStatus(str, Enum):
    """Estados de colección."""
    DRAFT = "draft"
    ACTIVE = "active"
    READ_ONLY = "read_only"
    ARCHIVED = "archived"


@dataclass
class Collection:
    """Colección de conocimiento."""
    collection_id: str
    name: str
    collection_type: CollectionType
    
    # Description
    description: str = ""
    
    # Content
    document_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    
    # Config
    status: CollectionStatus = CollectionStatus.DRAFT
    is_public: bool = False
    auto_update: bool = False
    
    # Metadata
    created_at: str = ""
    updated_at: str = ""
    created_by: str = ""
    
    # Stats
    document_count: int = 0
    last_document_added: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def add_document(self, document_id: str) -> None:
        """Añade documento."""
        if document_id not in self.document_ids:
            self.document_ids.append(document_id)
            self.document_count = len(self.document_ids)
            self.last_document_added = datetime.now().isoformat()
    
    def remove_document(self, document_id: str) -> None:
        """Remueve documento."""
        if document_id in self.document_ids:
            self.document_ids.remove(document_id)
            self.document_count = len(self.document_ids)


@dataclass
class CollectionMetadata:
    """Metadatos de colección."""
    collection_id: str
    
    # Domain
    domain: str = ""
    subdomains: list[str] = field(default_factory=list)
    
    # Coverage
    start_date: str = ""
    end_date: str = ""
    coverage: str = ""
    
    # Quality
    quality_score: float = 0.0
    completeness: float = 0.0
    
    # Access
    access_level: str = "internal"
    requires_auth: bool = True


class BaseCollectionManager(ABC):
    """Clase base para gestores de colecciones."""
    
    @abstractmethod
    async def create_collection(self, collection: Collection) -> Collection:
        """Crea colección."""
        ...
    
    @abstractmethod
    async def get_collection(self, collection_id: str) -> Collection | None:
        """Obtiene colección."""
        ...
    
    @abstractmethod
    async def add_to_collection(
        self,
        collection_id: str,
        document_id: str,
    ) -> Collection:
        """Añade documento a colección."""
        ...
    
    @abstractmethod
    async def remove_from_collection(
        self,
        collection_id: str,
        document_id: str,
    ) -> Collection:
        """Remueve documento de colección."""
        ...


class InMemoryCollectionManager(BaseCollectionManager):
    """Gestor de colecciones en memoria."""
    
    def __init__(self):
        self._collections: dict[str, Collection] = {}
        self._metadata: dict[str, CollectionMetadata] = {}
    
    async def create_collection(self, collection: Collection) -> Collection:
        """Crea colección."""
        self._collections[collection.collection_id] = collection
        return collection
    
    async def get_collection(self, collection_id: str) -> Collection | None:
        """Obtiene colección."""
        return self._collections.get(collection_id)
    
    async def update_collection(self, collection: Collection) -> Collection:
        """Actualiza colección."""
        collection.updated_at = datetime.now().isoformat()
        self._collections[collection.collection_id] = collection
        return collection
    
    async def delete_collection(self, collection_id: str) -> bool:
        """Elimina colección."""
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False
    
    async def list_collections(
        self,
        collection_type: CollectionType | None = None,
        status: CollectionStatus | None = None,
    ) -> list[Collection]:
        """Lista colecciones."""
        results = list(self._collections.values())
        
        if collection_type:
            results = [c for c in results if c.collection_type == collection_type]
        
        if status:
            results = [c for c in results if c.status == status]
        
        return results
    
    async def add_to_collection(
        self,
        collection_id: str,
        document_id: str,
    ) -> Collection:
        """Añade documento a colección."""
        collection = self._collections.get(collection_id)
        if not collection:
            raise ValueError(f"Collection {collection_id} not found")
        
        collection.add_document(document_id)
        collection.updated_at = datetime.now().isoformat()
        
        return collection
    
    async def remove_from_collection(
        self,
        collection_id: str,
        document_id: str,
    ) -> Collection:
        """Remueve documento de colección."""
        collection = self._collections.get(collection_id)
        if not collection:
            raise ValueError(f"Collection {collection_id} not found")
        
        collection.remove_document(document_id)
        collection.updated_at = datetime.now().isoformat()
        
        return collection
    
    async def set_metadata(
        self,
        metadata: CollectionMetadata,
    ) -> CollectionMetadata:
        """Define metadatos de colección."""
        self._metadata[metadata.collection_id] = metadata
        return metadata
    
    async def get_metadata(self, collection_id: str) -> CollectionMetadata | None:
        """Obtiene metadatos de colección."""
        return self._metadata.get(collection_id)


class CollectionSearcher:
    """Buscador de colecciones."""
    
    def __init__(self, manager: BaseCollectionManager):
        self._manager = manager
    
    async def search_by_tags(
        self,
        tags: list[str],
    ) -> list[Collection]:
        """Busca por tags."""
        collections = await self._manager.list_collections()
        
        results = []
        for collection in collections:
            if any(tag in collection.tags for tag in tags):
                results.append(collection)
        
        return results
    
    async def search_by_name(
        self,
        query: str,
    ) -> list[Collection]:
        """Busca por nombre."""
        collections = await self._manager.list_collections()
        query_lower = query.lower()
        
        return [
            c for c in collections
            if query_lower in c.name.lower() or query_lower in c.description.lower()
        ]


__all__ = [
    "CollectionType",
    "CollectionStatus",
    "Collection",
    "CollectionMetadata",
    "BaseCollectionManager",
    "InMemoryCollectionManager",
    "CollectionSearcher",
]
