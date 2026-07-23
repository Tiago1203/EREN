"""
PHASE 4 - EPIC 4: Qdrant Module

Integración con Qdrant vector database:
- Qdrant client wrapper
- Connection management
- Query execution
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import asyncio


class DistanceMetric(str):
    """Métricas de distancia para Qdrant."""
    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"


@dataclass
class QdrantConfig:
    """Configuración de Qdrant."""
    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    api_key: str = ""
    timeout: int = 30
    prefer_grpc: bool = True
    https: bool = False


class BaseQdrantClient(ABC):
    """Clase base para cliente Qdrant."""
    
    @abstractmethod
    async def create_collection(self, name: str, vectors_config: dict) -> bool:
        """Crea una colección."""
        ...
    
    @abstractmethod
    async def delete_collection(self, name: str) -> bool:
        """Elimina una colección."""
        ...
    
    @abstractmethod
    async def collection_exists(self, name: str) -> bool:
        """Verifica si existe una colección."""
        ...
    
    @abstractmethod
    async def upsert(self, collection_name: str, points: list[dict]) -> bool:
        """Inserta o actualiza puntos."""
        ...
    
    @abstractmethod
    async def search(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[dict]:
        """Busca vectores similares."""
        ...
    
    @abstractmethod
    async def scroll(self, collection_name: str, limit: int = 100) -> list[dict]:
        """Obtiene puntos de una colección."""
        ...


class InMemoryQdrantClient(BaseQdrantClient):
    """Cliente Qdrant en memoria (para testing)."""
    
    def __init__(self):
        self._collections: dict[str, dict] = {}
        self._points: dict[str, dict] = {}  # collection_name -> {point_id -> point}
    
    async def create_collection(self, name: str, vectors_config: dict) -> bool:
        """Crea una colección."""
        if name in self._collections:
            return False
        
        self._collections[name] = vectors_config
        self._points[name] = {}
        return True
    
    async def delete_collection(self, name: str) -> bool:
        """Elimina una colección."""
        if name not in self._collections:
            return False
        
        del self._collections[name]
        del self._points[name]
        return True
    
    async def collection_exists(self, name: str) -> bool:
        """Verifica si existe una colección."""
        return name in self._collections
    
    async def upsert(self, collection_name: str, points: list[dict]) -> bool:
        """Inserta o actualiza puntos."""
        if collection_name not in self._collections:
            return False
        
        for point in points:
            point_id = point.get("id", str(uuid.uuid4()))
            self._points[collection_name][point_id] = point
        
        return True
    
    async def search(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[dict]:
        """Busca vectores similares (mock)."""
        if collection_name not in self._collections:
            return []
        
        points = list(self._points[collection_name].values())
        
        # Simple similarity: just return first N points
        results = []
        for point in points[:limit]:
            results.append({
                "id": point.get("id"),
                "score": 0.9,  # Mock score
                "payload": point.get("payload", {}),
            })
        
        return results
    
    async def scroll(self, collection_name: str, limit: int = 100) -> list[dict]:
        """Obtiene puntos de una colección."""
        if collection_name not in self._collections:
            return []
        
        points = list(self._points[collection_name].values())
        return points[:limit]
    
    async def get_collection_info(self, name: str) -> dict | None:
        """Obtiene información de una colección."""
        if name not in self._collections:
            return None
        
        return {
            "name": name,
            "vectors_config": self._collections[name],
            "points_count": len(self._points[name]),
        }


class QdrantClientWrapper(BaseQdrantClient):
    """Wrapper para cliente Qdrant real."""
    
    def __init__(self, config: QdrantConfig):
        self.config = config
        self._client = None
    
    def _get_client(self):
        """Obtiene cliente Qdrant."""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
                
                self._client = QdrantClient(
                    host=self.config.host,
                    port=self.config.port,
                    api_key=self.config.api_key or None,
                    timeout=self.config.timeout,
                    prefer_grpc=self.config.prefer_grpc,
                )
            except ImportError:
                # Fallback to in-memory
                return InMemoryQdrantClient()
        
        return self._client
    
    async def create_collection(self, name: str, vectors_config: dict) -> bool:
        """Crea una colección."""
        client = self._get_client()
        
        if isinstance(client, InMemoryQdrantClient):
            return await client.create_collection(name, vectors_config)
        
        try:
            from qdrant_client.models import Distance, VectorParams
            
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclid": Distance.EUCLID,
                "Dot": Distance.DOT,
            }
            
            distance = distance_map.get(
                vectors_config.get("distance", "Cosine"),
                Distance.COSINE
            )
            
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=vectors_config.get("size", 384),
                    distance=distance,
                )
            )
            return True
        except Exception:
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """Elimina una colección."""
        client = self._get_client()
        
        if isinstance(client, InMemoryQdrantClient):
            return await client.delete_collection(name)
        
        try:
            client.delete_collection(collection_name=name)
            return True
        except Exception:
            return False
    
    async def collection_exists(self, name: str) -> bool:
        """Verifica si existe una colección."""
        client = self._get_client()
        
        if isinstance(client, InMemoryQdrantClient):
            return await client.collection_exists(name)
        
        try:
            return client.collection_exists(name)
        except Exception:
            return False
    
    async def upsert(self, collection_name: str, points: list[dict]) -> bool:
        """Inserta o actualiza puntos."""
        client = self._get_client()
        
        if isinstance(client, InMemoryQdrantClient):
            return await client.upsert(collection_name, points)
        
        try:
            from qdrant_client.models import PointStruct
            
            qdrant_points = [
                PointStruct(
                    id=p.get("id"),
                    vector=p.get("vector"),
                    payload=p.get("payload", {}),
                )
                for p in points
            ]
            
            client.upsert(
                collection_name=collection_name,
                points=qdrant_points,
            )
            return True
        except Exception:
            return False
    
    async def search(
        self,
        collection_name: str,
        vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[dict]:
        """Busca vectores similares."""
        client = self._get_client()
        
        if isinstance(client, InMemoryQdrantClient):
            return await client.search(collection_name, vector, limit, score_threshold)
        
        try:
            from qdrant_client.models import Filter, SearchParams
            
            search_params = SearchParams(hnsw_ef=128) if score_threshold else None
            
            results = client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
                score_threshold=score_threshold,
                search_params=search_params,
            )
            
            return [
                {
                    "id": r.id,
                    "score": r.score,
                    "payload": r.payload,
                }
                for r in results
            ]
        except Exception:
            return []
    
    async def scroll(self, collection_name: str, limit: int = 100) -> list[dict]:
        """Obtiene puntos de una colección."""
        client = self._get_client()
        
        if isinstance(client, InMemoryQdrantClient):
            return await client.scroll(collection_name, limit)
        
        try:
            results, _ = client.scroll(
                collection_name=collection_name,
                limit=limit,
            )
            
            return [
                {
                    "id": r.id,
                    "vector": r.vector,
                    "payload": r.payload,
                }
                for r in results
            ]
        except Exception:
            return []


import uuid


__all__ = [
    "DistanceMetric",
    "QdrantConfig",
    "BaseQdrantClient",
    "InMemoryQdrantClient",
    "QdrantClientWrapper",
]
