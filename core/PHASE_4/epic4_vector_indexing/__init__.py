"""
PHASE 4 - EPIC 4: Vector Indexing Engine

Indexa vectores en Qdrant con colecciones especializadas:
- Gestión de colecciones
- Índices optimizados
- Payloads estructurados
- Sharding y replicación
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol
import uuid

from core.PHASE_4.foundation import (
    EmbeddingVector,
    IndexedVector,
    SearchResult,
    KnowledgeDomain,
)


class DistanceMetric(str, Enum):
    """Métricas de distancia."""
    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"


class IndexType(str, Enum):
    """Tipos de índice."""
    HNSW = "hnsw"
    IVF = "ivf"
    FLAT = "flat"
    DISK = "disk"


class CollectionType(str, Enum):
    """Tipos de colección."""
    KNOWLEDGE = "knowledge"
    KNOWLEDGE_ARTICLES = "knowledge_articles"
    DEVICE_MANUALS = "device_manuals"
    CLINICAL_GUIDELINES = "clinical_guidelines"
    REGULATORY_DOCS = "regulatory_docs"
    PUBMED_ABSTRACTS = "pubmed_abstracts"
    CLINICAL_NOTES = "clinical_notes"
    EVIDENCE_BASE = "evidence_base"
    SAFETY_ALERTS = "safety_alerts"
    ENTITIES = "entities"


@dataclass
class CollectionConfig:
    """Configuración de colección Qdrant."""
    name: str
    description: str = ""
    
    # Vector config
    vector_size: int = 768
    distance: DistanceMetric = DistanceMetric.COSINE
    
    # Index config
    index_type: IndexType = IndexType.HNSW
    m: int = 16  # HNSW M parameter
    ef_construct: int = 200  # HNSW ef_construct
    
    # Sharding
    shard_number: int = 1
    replication_factor: int = 1
    
    # TTL
    ttl_seconds: int | None = None
    
    # Metadata
    domain: KnowledgeDomain | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class IndexPayload:
    """Payload para vector indexado."""
    # Document info
    document_id: str
    title: str
    content: str
    
    # Knowledge metadata
    domain: str = ""
    medical_specialty: str = ""
    device_categories: list[str] = field(default_factory=list)
    
    # Codes
    icd_codes: list[str] = field(default_factory=list)
    snomed_codes: list[str] = field(default_factory=list)
    loinc_codes: list[str] = field(default_factory=list)
    
    # Quality
    quality_score: float = 0.0
    evidence_level: str = ""
    
    # Governance
    governance_status: str = "published"
    version: str = "1.0.0"
    
    # Source
    source_type: str = ""
    source_id: str = ""
    
    # Timestamps
    created_at: str = ""
    updated_at: str = ""
    
    # Extracted entities
    entities: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


@dataclass
class IndexingResult:
    """Resultado de indexación."""
    operation_id: str
    collection: str
    vectors_indexed: int
    failed: int
    duration_ms: int
    errors: list[str] = field(default_factory=list)


@dataclass
class CollectionStats:
    """Estadísticas de colección."""
    name: str
    vector_count: int
    point_count: int
    segments_count: int
    status: str
    vector_dimension: int
    distance_metric: str
    index_type: str
    disk_size_bytes: int = 0
    ram_size_bytes: int = 0


class IQdrantClient(Protocol):
    """Protocolo para cliente Qdrant."""
    
    async def create_collection(self, config: CollectionConfig) -> bool:
        """Crea colección."""
        ...
    
    async def delete_collection(self, name: str) -> bool:
        """Elimina colección."""
        ...
    
    async def collection_exists(self, name: str) -> bool:
        """Verifica existencia de colección."""
        ...
    
    async def get_stats(self, name: str) -> CollectionStats:
        """Obtiene estadísticas."""
        ...
    
    async def upsert(
        self,
        collection: str,
        vectors: list[IndexedVector],
    ) -> IndexingResult:
        """Inserta/actualiza vectores."""
        ...
    
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict | None = None,
        with_payload: bool = True,
    ) -> list[SearchResult]:
        """Busca vectores similares."""
        ...
    
    async def delete_vectors(
        self,
        collection: str,
        vector_ids: list[str],
    ) -> bool:
        """Elimina vectores."""
        ...


class InMemoryQdrantClient(IQdrantClient):
    """Cliente Qdrant en memoria para desarrollo/pruebas."""
    
    def __init__(self):
        self._collections: dict[str, dict[str, tuple]] = {}  # collection -> {id: (vector, payload)}
        self._configs: dict[str, CollectionConfig] = {}
    
    async def create_collection(self, config: CollectionConfig) -> bool:
        """Crea colección."""
        if config.name in self._collections:
            return False
        
        self._collections[config.name] = {}
        self._configs[config.name] = config
        return True
    
    async def delete_collection(self, name: str) -> bool:
        """Elimina colección."""
        if name in self._collections:
            del self._collections[name]
            del self._configs[name]
            return True
        return False
    
    async def collection_exists(self, name: str) -> bool:
        """Verifica existencia de colección."""
        return name in self._collections
    
    async def get_stats(self, name: str) -> CollectionStats:
        """Obtiene estadísticas."""
        if name not in self._collections:
            raise ValueError(f"Collection {name} not found")
        
        config = self._configs[name]
        return CollectionStats(
            name=name,
            vector_count=len(self._collections[name]),
            point_count=len(self._collections[name]),
            segments_count=1,
            status="green",
            vector_dimension=config.vector_size,
            distance_metric=config.distance.value,
            index_type=config.index_type.value,
        )
    
    async def upsert(
        self,
        collection: str,
        vectors: list[IndexedVector],
    ) -> IndexingResult:
        """Inserta/actualiza vectores."""
        import time
        start = time.time()
        
        if collection not in self._collections:
            await self.create_collection(CollectionConfig(name=collection))
        
        indexed = 0
        failed = 0
        errors = []
        
        for vec in vectors:
            try:
                self._collections[collection][vec.vector_id] = (
                    vec.embedding.values,
                    vec.payload,
                )
                indexed += 1
            except Exception as e:
                failed += 1
                errors.append(str(e))
        
        duration_ms = int((time.time() - start) * 1000)
        
        return IndexingResult(
            operation_id=str(uuid.uuid4()),
            collection=collection,
            vectors_indexed=indexed,
            failed=failed,
            duration_ms=duration_ms,
            errors=errors,
        )
    
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict | None = None,
        with_payload: bool = True,
    ) -> list[SearchResult]:
        """Busca vectores similares."""
        if collection not in self._collections:
            return []
        
        # Calculate cosine similarity for all vectors
        import numpy as np
        
        results = []
        query = np.array(query_vector)
        
        for vec_id, (vec_values, payload) in self._collections[collection].items():
            vec = np.array(vec_values)
            
            # Cosine similarity
            dot = np.dot(query, vec)
            norm_q = np.linalg.norm(query)
            norm_v = np.linalg.norm(vec)
            
            if norm_q > 0 and norm_v > 0:
                score = float(dot / (norm_q * norm_v))
                
                results.append(SearchResult(
                    result_id=vec_id,
                    score=score,
                    payload=payload if with_payload else {},
                ))
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:top_k]
    
    async def delete_vectors(
        self,
        collection: str,
        vector_ids: list[str],
    ) -> bool:
        """Elimina vectores."""
        if collection not in self._collections:
            return False
        
        for vec_id in vector_ids:
            if vec_id in self._collections[collection]:
                del self._collections[collection][vec_id]
        
        return True


class CollectionManager:
    """Gestor de colecciones Qdrant."""
    
    def __init__(self, client: IQdrantClient):
        self.client = client
        self._default_collections = self._create_default_configs()
    
    def _create_default_configs(self) -> dict[str, CollectionConfig]:
        """Crea configuraciones por defecto."""
        return {
            CollectionType.KNOWLEDGE_ARTICLES.value: CollectionConfig(
                name=CollectionType.KNOWLEDGE_ARTICLES.value,
                description="Knowledge articles and KB entries",
                vector_size=768,
            ),
            CollectionType.DEVICE_MANUALS.value: CollectionConfig(
                name=CollectionType.DEVICE_MANUALS.value,
                description="Medical device manuals",
                vector_size=768,
            ),
            CollectionType.CLINICAL_GUIDELINES.value: CollectionConfig(
                name=CollectionType.CLINICAL_GUIDELINES.value,
                description="Clinical practice guidelines",
                vector_size=768,
            ),
            CollectionType.REGULATORY_DOCS.value: CollectionConfig(
                name=CollectionType.REGULATORY_DOCS.value,
                description="FDA, EMA regulatory documents",
                vector_size=768,
            ),
            CollectionType.PUBMED_ABSTRACTS.value: CollectionConfig(
                name=CollectionType.PUBMED_ABSTRACTS.value,
                description="PubMed article abstracts",
                vector_size=768,
            ),
            CollectionType.EVIDENCE_BASE.value: CollectionConfig(
                name=CollectionType.EVIDENCE_BASE.value,
                description="Clinical evidence base",
                vector_size=768,
            ),
            CollectionType.SAFETY_ALERTS.value: CollectionConfig(
                name=CollectionType.SAFETY_ALERTS.value,
                description="Medical device safety alerts",
                vector_size=768,
            ),
        }
    
    async def create_collection(self, config: CollectionConfig) -> bool:
        """Crea colección."""
        return await self.client.create_collection(config)
    
    async def create_default_collections(self) -> dict[str, bool]:
        """Crea todas las colecciones por defecto."""
        results = {}
        for config in self._default_collections.values():
            results[config.name] = await self.client.create_collection(config)
        return results
    
    async def delete_collection(self, name: str) -> bool:
        """Elimina colección."""
        return await self.client.delete_collection(name)
    
    async def get_collection(self, name: str) -> Optional[CollectionConfig]:
        """Obtiene configuración de colección."""
        if name in self._default_collections:
            return self._default_collections[name]
        return None
    
    async def list_collections(self) -> list[str]:
        """Lista todas las colecciones."""
        return list(self._default_collections.keys())


class VectorIndexer:
    """Indexador de vectores."""
    
    def __init__(self, client: IQdrantClient):
        self.client = client
    
    async def index(
        self,
        collection: str,
        vectors: list[IndexedVector],
    ) -> IndexingResult:
        """Indexa vectores en colección."""
        return await self.client.upsert(collection, vectors)
    
    async def index_knowledge_asset(
        self,
        collection: str,
        asset_id: str,
        content: str,
        embedding: EmbeddingVector,
        payload: IndexPayload,
    ) -> bool:
        """Indexa asset de conocimiento."""
        import uuid
        
        vector = IndexedVector(
            vector_id=str(uuid.uuid4()),
            embedding=embedding,
            collection=collection,
            payload=payload.__dict__,
        )
        
        result = await self.client.upsert(collection, [vector])
        return result.failed == 0
    
    async def index_batch(
        self,
        collection: str,
        items: list[tuple[str, EmbeddingVector, IndexPayload]],
    ) -> IndexingResult:
        """Indexa batch de items."""
        import uuid
        
        vectors = []
        for content, embedding, payload in items:
            vectors.append(IndexedVector(
                vector_id=str(uuid.uuid4()),
                embedding=embedding,
                collection=collection,
                payload=payload.__dict__,
            ))
        
        return await self.client.upsert(collection, vectors)
    
    async def delete(self, collection: str, vector_ids: list[str]) -> bool:
        """Elimina vectores."""
        return await self.client.delete_vectors(collection, vector_ids)
    
    async def reindex(
        self,
        collection: str,
        vector_id: str,
        new_embedding: EmbeddingVector,
    ) -> bool:
        """Reindexa vector con nuevo embedding."""
        # Get existing payload
        results = await self.client.search(
            collection,
            new_embedding.values,
            top_k=1,
        )
        
        if not results:
            return False
        
        # Delete old and insert new
        await self.client.delete_vectors(collection, [vector_id])
        
        vector = IndexedVector(
            vector_id=vector_id,
            embedding=new_embedding,
            collection=collection,
            payload=results[0].payload,
        )
        
        result = await self.client.upsert(collection, [vector])
        return result.failed == 0


class VectorSearchEngine:
    """Motor de búsqueda vectorial."""
    
    def __init__(self, client: IQdrantClient):
        self.client = client
    
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        domain_filter: str | None = None,
        quality_min: float | None = None,
        evidence_level: str | None = None,
    ) -> list[SearchResult]:
        """Busca vectores similares."""
        # Build filters
        filters = {}
        
        if domain_filter:
            filters["domain"] = domain_filter
        
        if quality_min is not None:
            filters["quality_score"] = {"gte": quality_min}
        
        if evidence_level:
            filters["evidence_level"] = evidence_level
        
        return await self.client.search(
            collection,
            query_vector,
            top_k,
            filters if filters else None,
        )
    
    async def search_multi_collection(
        self,
        query_vector: list[float],
        collections: list[str],
        top_k: int = 10,
    ) -> dict[str, list[SearchResult]]:
        """Busca en múltiples colecciones."""
        results = {}
        
        for collection in collections:
            collection_results = await self.search(
                collection,
                query_vector,
                top_k,
            )
            results[collection] = collection_results
        
        return results


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Qdrant
from core.PHASE_4.epic4_vector_indexing.qdrant import (
    DistanceMetric as _DistanceMetric,
    QdrantConfig,
    BaseQdrantClient,
    InMemoryQdrantClient,
    QdrantClientWrapper,
)

# Collections
from core.PHASE_4.epic4_vector_indexing.collections import (
    CollectionType as _CollectionType,
    IndexType,
    CollectionConfig,
    CollectionStats,
    VectorPoint,
    VectorCollection,
    BaseCollectionManager,
    InMemoryCollectionManager,
    CollectionFactory,
)

# Payloads
from core.PHASE_4.epic4_vector_indexing.payloads import (
    VectorPayload,
    BasePayloadBuilder,
    KnowledgePayloadBuilder,
    EntityPayloadBuilder,
    PayloadSchema,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    # Enums
    "DistanceMetric",
    "IndexType",
    "CollectionType",
    # Data Classes
    "CollectionConfig",
    "IndexPayload",
    "IndexingResult",
    "CollectionStats",
    "VectorPoint",
    "VectorCollection",
    "VectorPayload",
    # Protocols
    "IQdrantClient",
    "BaseQdrantClient",
    "BaseCollectionManager",
    "BasePayloadBuilder",
    # Implementations
    "InMemoryQdrantClient",
    "QdrantClientWrapper",
    "InMemoryCollectionManager",
    "KnowledgePayloadBuilder",
    "EntityPayloadBuilder",
    # Managers
    "CollectionManager",
    "VectorIndexer",
    "VectorSearchEngine",
    # Factory
    "CollectionFactory",
    # Schema
    "PayloadSchema",
    # Config
    "QdrantConfig",
]
