"""
PHASE 4 - EPIC 4: Collections Module

Gestión de colecciones en Qdrant:
- Collection Manager
- Collection Config
- Collection Stats
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class CollectionType(str, Enum):
    """Tipos de colección."""
    KNOWLEDGE = "knowledge"
    DOCUMENTS = "documents"
    ENTITIES = "entities"
    CONCEPTS = "concepts"
    EMBEDDINGS = "embeddings"


class IndexType(str, Enum):
    """Tipos de índice."""
    HNSW = "hnsw"
    IVF = "ivf"
    FLAT = "flat"


@dataclass
class CollectionConfig:
    """Configuración de colección."""
    name: str
    vector_size: int
    distance: str = "Cosine"  # Cosine, Euclid, Dot
    index_type: IndexType = IndexType.HNSW
    
    # HNSW params
    m: int = 16  # Number of connections
    ef_construct: int = 200  # Construction-time search depth
    
    # Sharding
    shard_number: int = 1
    replication_factor: int = 1
    
    # Payload
    payload_schema: dict | None = None
    
    def to_vectors_config(self) -> dict:
        """Convierte a config de Qdrant."""
        return {
            "size": self.vector_size,
            "distance": self.distance,
        }


@dataclass
class CollectionStats:
    """Estadísticas de colección."""
    name: str
    points_count: int = 0
    vectors_count: int = 0
    segments_count: int = 0
    disk_size_bytes: int = 0
    ram_size_bytes: int = 0
    status: str = "green"
    last_updated: str = ""


@dataclass
class VectorPoint:
    """Punto vectorial."""
    point_id: str
    vector: list[float]
    payload: dict = field(default_factory=dict)
    score: float = 0.0


@dataclass
class VectorCollection:
    """Colección vectorial."""
    collection_id: str
    name: str
    type: CollectionType
    config: CollectionConfig
    created_at: str
    updated_at: str = ""
    status: str = "active"
    
    @classmethod
    def create(
        cls,
        name: str,
        collection_type: CollectionType,
        vector_size: int,
    ) -> "VectorCollection":
        """Crea una nueva colección."""
        now = datetime.now().isoformat()
        
        return cls(
            collection_id=str(uuid.uuid4()),
            name=name,
            type=collection_type,
            config=CollectionConfig(
                name=name,
                vector_size=vector_size,
            ),
            created_at=now,
            updated_at=now,
        )


class BaseCollectionManager(ABC):
    """Clase base para gestión de colecciones."""
    
    @abstractmethod
    async def create(self, collection: VectorCollection) -> bool:
        """Crea una colección."""
        ...
    
    @abstractmethod
    async def delete(self, name: str) -> bool:
        """Elimina una colección."""
        ...
    
    @abstractmethod
    async def exists(self, name: str) -> bool:
        """Verifica si existe."""
        ...
    
    @abstractmethod
    async def get(self, name: str) -> VectorCollection | None:
        """Obtiene una colección."""
        ...
    
    @abstractmethod
    async def list_all(self) -> list[VectorCollection]:
        """Lista todas las colecciones."""
        ...
    
    @abstractmethod
    async def stats(self, name: str) -> CollectionStats | None:
        """Obtiene estadísticas."""
        ...


class InMemoryCollectionManager(BaseCollectionManager):
    """Gestor de colecciones en memoria."""
    
    def __init__(self):
        self._collections: dict[str, VectorCollection] = {}
        self._stats: dict[str, CollectionStats] = {}
    
    async def create(self, collection: VectorCollection) -> bool:
        """Crea una colección."""
        if collection.name in self._collections:
            return False
        
        self._collections[collection.name] = collection
        self._stats[collection.name] = CollectionStats(
            name=collection.name,
            points_count=0,
            last_updated=datetime.now().isoformat(),
        )
        return True
    
    async def delete(self, name: str) -> bool:
        """Elimina una colección."""
        if name not in self._collections:
            return False
        
        del self._collections[name]
        if name in self._stats:
            del self._stats[name]
        return True
    
    async def exists(self, name: str) -> bool:
        """Verifica si existe."""
        return name in self._collections
    
    async def get(self, name: str) -> VectorCollection | None:
        """Obtiene una colección."""
        return self._collections.get(name)
    
    async def list_all(self) -> list[VectorCollection]:
        """Lista todas las colecciones."""
        return list(self._collections.values())
    
    async def stats(self, name: str) -> CollectionStats | None:
        """Obtiene estadísticas."""
        return self._stats.get(name)
    
    async def update_stats(self, name: str, stats: CollectionStats) -> None:
        """Actualiza estadísticas."""
        self._stats[name] = stats


class CollectionFactory:
    """Fábrica de colecciones."""
    
    # Templates de colecciones
    TEMPLATES = {
        "knowledge": CollectionConfig(
            name="knowledge",
            vector_size=384,
            distance="Cosine",
            index_type=IndexType.HNSW,
            m=16,
            ef_construct=200,
        ),
        "entities": CollectionConfig(
            name="entities",
            vector_size=384,
            distance="Cosine",
            index_type=IndexType.HNSW,
            m=12,
            ef_construct=150,
        ),
        "concepts": CollectionConfig(
            name="concepts",
            vector_size=384,
            distance="Cosine",
            index_type=IndexType.HNSW,
            m=16,
            ef_construct=200,
        ),
    }
    
    @staticmethod
    def create_collection(
        name: str,
        collection_type: CollectionType,
        vector_size: int,
        template: str | None = None,
    ) -> VectorCollection:
        """Crea una colección."""
        if template and template in CollectionFactory.TEMPLATES:
            config = CollectionFactory.TEMPLATES[template].__class__(
                name=name,
                vector_size=vector_size,
                distance=CollectionFactory.TEMPLATES[template].distance,
                index_type=CollectionFactory.TEMPLATES[template].index_type,
                m=CollectionFactory.TEMPLATES[template].m,
                ef_construct=CollectionFactory.TEMPLATES[template].ef_construct,
            )
        else:
            config = CollectionConfig(name=name, vector_size=vector_size)
        
        return VectorCollection(
            collection_id=str(uuid.uuid4()),
            name=name,
            type=collection_type,
            config=config,
            created_at=datetime.now().isoformat(),
        )
    
    @staticmethod
    def create_knowledge_collection(
        name: str,
        vector_size: int = 384,
    ) -> VectorCollection:
        """Crea colección de conocimiento."""
        return CollectionFactory.create_collection(
            name=name,
            collection_type=CollectionType.KNOWLEDGE,
            vector_size=vector_size,
            template="knowledge",
        )
    
    @staticmethod
    def create_entity_collection(
        name: str,
        vector_size: int = 384,
    ) -> VectorCollection:
        """Crea colección de entidades."""
        return CollectionFactory.create_collection(
            name=name,
            collection_type=CollectionType.ENTITIES,
            vector_size=vector_size,
            template="entities",
        )


__all__ = [
    "CollectionType",
    "IndexType",
    "CollectionConfig",
    "CollectionStats",
    "VectorPoint",
    "VectorCollection",
    "BaseCollectionManager",
    "InMemoryCollectionManager",
    "CollectionFactory",
]
