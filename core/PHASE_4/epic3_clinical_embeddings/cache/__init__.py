"""
PHASE 4 - EPIC 3: Cache Module

Cache para embeddings:
- In-memory cache
- Persistent cache
- Cache invalidation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import json


@dataclass
class CachedEmbedding:
    """Embedding en cache."""
    text_hash: str
    text: str
    vector: list[float]
    model: str
    dimension: int
    created_at: str
    accessed_at: str
    access_count: int = 0
    ttl_seconds: int | None = None
    
    def is_expired(self) -> bool:
        """Verifica si el cache expiró."""
        if self.ttl_seconds is None:
            return False
        
        created = datetime.fromisoformat(self.created_at)
        return datetime.now() - created > timedelta(seconds=self.ttl_seconds)
    
    def touch(self) -> None:
        """Actualiza último acceso."""
        self.accessed_at = datetime.now().isoformat()
        self.access_count += 1


class BaseEmbeddingCache(ABC):
    """Clase base para cache de embeddings."""
    
    @abstractmethod
    def get(self, text: str, model: str) -> Optional[CachedEmbedding]:
        """Obtiene embedding del cache."""
        ...
    
    @abstractmethod
    def set(self, embedding: CachedEmbedding) -> None:
        """Guarda embedding en cache."""
        ...
    
    @abstractmethod
    def delete(self, text_hash: str) -> bool:
        """Elimina embedding del cache."""
        ...
    
    @abstractmethod
    def clear(self) -> None:
        """Limpia todo el cache."""
        ...
    
    @abstractmethod
    def stats(self) -> dict:
        """Retorna estadísticas del cache."""
        ...


class InMemoryEmbeddingCache(BaseEmbeddingCache):
    """Cache en memoria para embeddings."""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int | None = 86400):
        self._cache: dict[str, CachedEmbedding] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def _compute_hash(self, text: str, model: str) -> str:
        """Computa hash para texto y modelo."""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def get(self, text: str, model: str) -> Optional[CachedEmbedding]:
        """Obtiene embedding del cache."""
        text_hash = self._compute_hash(text, model)
        embedding = self._cache.get(text_hash)
        
        if embedding is None:
            self._misses += 1
            return None
        
        # Check expiration
        if embedding.is_expired():
            del self._cache[text_hash]
            self._misses += 1
            return None
        
        # Update access
        embedding.touch()
        self._hits += 1
        return embedding
    
    def set(self, embedding: CachedEmbedding) -> None:
        """Guarda embedding en cache."""
        # Evict if full
        if len(self._cache) >= self._max_size:
            self._evict_lru()
        
        self._cache[embedding.text_hash] = embedding
    
    def delete(self, text_hash: str) -> bool:
        """Elimina embedding del cache."""
        if text_hash in self._cache:
            del self._cache[text_hash]
            return True
        return False
    
    def clear(self) -> None:
        """Limpia todo el cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def stats(self) -> dict:
        """Retorna estadísticas del cache."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self._ttl_seconds,
        }
    
    def _evict_lru(self) -> None:
        """Evict least recently used."""
        if not self._cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].accessed_at,
        )
        del self._cache[lru_key]


class PersistentEmbeddingCache(BaseEmbeddingCache):
    """Cache persistente usando archivo JSON."""
    
    def __init__(self, path: str, max_size: int = 50000):
        self._path = path
        self._max_size = max_size
        self._cache: dict[str, CachedEmbedding] = {}
        self._load()
    
    def _load(self) -> None:
        """Carga cache desde archivo."""
        import os
        
        if os.path.exists(self._path):
            try:
                with open(self._path, 'r') as f:
                    data = json.load(f)
                    
                for item in data.get("embeddings", []):
                    embedding = CachedEmbedding(
                        text_hash=item["text_hash"],
                        text=item["text"],
                        vector=item["vector"],
                        model=item["model"],
                        dimension=item["dimension"],
                        created_at=item["created_at"],
                        accessed_at=item["accessed_at"],
                        access_count=item["access_count"],
                        ttl_seconds=item.get("ttl_seconds"),
                    )
                    self._cache[embedding.text_hash] = embedding
            except Exception:
                pass  # Start fresh if loading fails
    
    def _save(self) -> None:
        """Guarda cache a archivo."""
        import os
        
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        
        data = {
            "embeddings": [
                {
                    "text_hash": e.text_hash,
                    "text": e.text,
                    "vector": e.vector,
                    "model": e.model,
                    "dimension": e.dimension,
                    "created_at": e.created_at,
                    "accessed_at": e.accessed_at,
                    "access_count": e.access_count,
                    "ttl_seconds": e.ttl_seconds,
                }
                for e in self._cache.values()
            ]
        }
        
        with open(self._path, 'w') as f:
            json.dump(data, f)
    
    def get(self, text: str, model: str) -> Optional[CachedEmbedding]:
        """Obtiene embedding del cache."""
        text_hash = self._compute_hash(text, model)
        embedding = self._cache.get(text_hash)
        
        if embedding and not embedding.is_expired():
            embedding.touch()
            return embedding
        
        return None
    
    def set(self, embedding: CachedEmbedding) -> None:
        """Guarda embedding en cache."""
        if len(self._cache) >= self._max_size:
            self._evict_lru()
        
        self._cache[embedding.text_hash] = embedding
        self._save()
    
    def delete(self, text_hash: str) -> bool:
        """Elimina embedding del cache."""
        if text_hash in self._cache:
            del self._cache[text_hash]
            self._save()
            return True
        return False
    
    def clear(self) -> None:
        """Limpia todo el cache."""
        self._cache.clear()
        self._save()
    
    def stats(self) -> dict:
        """Retorna estadísticas del cache."""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "path": self._path,
        }
    
    def _compute_hash(self, text: str, model: str) -> str:
        """Computa hash."""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def _evict_lru(self) -> None:
        """Evict least recently used."""
        if not self._cache:
            return
        
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].accessed_at,
        )
        del self._cache[lru_key]


class EmbeddingCacheDecorator(BaseEmbeddingCache):
    """Decorador que agrega funcionalidad a un cache."""
    
    def __init__(self, cache: BaseEmbeddingCache):
        self._cache = cache
    
    def get(self, text: str, model: str) -> Optional[CachedEmbedding]:
        return self._cache.get(text, model)
    
    def set(self, embedding: CachedEmbedding) -> None:
        self._cache.set(embedding)
    
    def delete(self, text_hash: str) -> bool:
        return self._cache.delete(text_hash)
    
    def clear(self) -> None:
        self._cache.clear()
    
    def stats(self) -> dict:
        return self._cache.stats()


class LRUCacheDecorator(EmbeddingCacheDecorator):
    """Decorador que implementa LRU con límite de tamaño."""
    
    def __init__(self, cache: BaseEmbeddingCache, max_size: int):
        super().__init__(cache)
        self._max_size = max_size
    
    def set(self, embedding: CachedEmbedding) -> None:
        """Set con eviction LRU."""
        if len(self._cache.stats()["size"]) >= self._max_size:
            # Find and remove LRU
            self._evict_lru()
        
        self._cache.set(embedding)


__all__ = [
    "CachedEmbedding",
    "BaseEmbeddingCache",
    "InMemoryEmbeddingCache",
    "PersistentEmbeddingCache",
    "EmbeddingCacheDecorator",
    "LRUCacheDecorator",
]
