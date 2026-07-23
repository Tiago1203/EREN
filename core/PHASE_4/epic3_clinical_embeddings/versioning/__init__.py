"""
PHASE 4 - EPIC 3: Versioning Module

Versionado de embeddings:
- Version tracking
- Version history
- Version comparison
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib


class EmbeddingVersionStatus(str, Enum):
    """Estados de versión de embedding."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


@dataclass
class EmbeddingVersion:
    """Versión de un embedding."""
    version_id: str
    text_hash: str
    model: str
    version: str  # Semver
    vector: list[float]
    dimension: int
    created_at: str
    status: EmbeddingVersionStatus = EmbeddingVersionStatus.ACTIVE
    parent_version_id: str | None = None
    changelog: str = ""
    quality_score: float = 0.0
    
    def is_active(self) -> bool:
        """Verifica si la versión está activa."""
        return self.status == EmbeddingVersionStatus.ACTIVE
    
    def is_compatible_with(self, other: "EmbeddingVersion") -> bool:
        """Verifica compatibilidad con otra versión."""
        return self.dimension == other.dimension and self.model == other.model


@dataclass
class VersionInfo:
    """Información de versión."""
    version: str
    model: str
    dimension: int
    created_at: str
    status: EmbeddingVersionStatus
    changelog: str


class BaseVersionManager(ABC):
    """Clase base para gestión de versiones."""
    
    @abstractmethod
    def create_version(
        self,
        text_hash: str,
        model: str,
        vector: list[float],
        changelog: str = "",
    ) -> EmbeddingVersion:
        """Crea nueva versión."""
        ...
    
    @abstractmethod
    def get_version(self, version_id: str) -> Optional[EmbeddingVersion]:
        """Obtiene versión por ID."""
        ...
    
    @abstractmethod
    def get_latest(self, text_hash: str) -> Optional[EmbeddingVersion]:
        """Obtiene última versión activa."""
        ...
    
    @abstractmethod
    def deprecate(self, version_id: str) -> bool:
        """Depreca una versión."""
        ...


class InMemoryVersionManager(BaseVersionManager):
    """Gestor de versiones en memoria."""
    
    def __init__(self):
        self._versions: dict[str, EmbeddingVersion] = {}
        self._by_text_hash: dict[str, list[str]] = {}  # text_hash -> [version_ids]
        self._counters: dict[str, int] = {}  # text_hash -> minor version counter
    
    def create_version(
        self,
        text_hash: str,
        model: str,
        vector: list[float],
        changelog: str = "",
    ) -> EmbeddingVersion:
        """Crea nueva versión."""
        from datetime import datetime
        
        # Get next version number
        if text_hash not in self._counters:
            self._counters[text_hash] = 1
            version_str = "1.0.0"
        else:
            self._counters[text_hash] += 1
            current = self._counters[text_hash]
            version_str = f"1.{current}.0"
        
        # Get parent version
        parent_id = None
        latest = self.get_latest(text_hash)
        if latest:
            parent_id = latest.version_id
        
        # Deprecate previous versions
        if latest:
            latest.status = EmbeddingVersionStatus.DEPRECATED
        
        version_id = hashlib.sha256(
            f"{text_hash}:{version_str}".encode()
        ).hexdigest()[:16]
        
        embedding = EmbeddingVersion(
            version_id=version_id,
            text_hash=text_hash,
            model=model,
            version=version_str,
            vector=vector,
            dimension=len(vector),
            created_at=datetime.now().isoformat(),
            status=EmbeddingVersionStatus.ACTIVE,
            parent_version_id=parent_id,
            changelog=changelog,
        )
        
        self._versions[version_id] = embedding
        
        if text_hash not in self._by_text_hash:
            self._by_text_hash[text_hash] = []
        self._by_text_hash[text_hash].append(version_id)
        
        return embedding
    
    def get_version(self, version_id: str) -> Optional[EmbeddingVersion]:
        """Obtiene versión por ID."""
        return self._versions.get(version_id)
    
    def get_latest(self, text_hash: str) -> Optional[EmbeddingVersion]:
        """Obtiene última versión activa."""
        version_ids = self._by_text_hash.get(text_hash, [])
        
        for vid in reversed(version_ids):
            version = self._versions.get(vid)
            if version and version.is_active():
                return version
        
        return None
    
    def get_all_versions(self, text_hash: str) -> list[EmbeddingVersion]:
        """Obtiene todas las versiones."""
        version_ids = self._by_text_hash.get(text_hash, [])
        return [
            self._versions[vid]
            for vid in version_ids
            if vid in self._versions
        ]
    
    def deprecate(self, version_id: str) -> bool:
        """Depreca una versión."""
        version = self._versions.get(version_id)
        if version:
            version.status = EmbeddingVersionStatus.DEPRECATED
            return True
        return False
    
    def retire(self, version_id: str) -> bool:
        """Retira una versión."""
        version = self._versions.get(version_id)
        if version:
            version.status = EmbeddingVersionStatus.RETIRED
            return True
        return False
    
    def stats(self) -> dict:
        """Retorna estadísticas."""
        active = sum(1 for v in self._versions.values() if v.is_active())
        deprecated = sum(1 for v in self._versions.values() 
                        if v.status == EmbeddingVersionStatus.DEPRECATED)
        retired = sum(1 for v in self._versions.values() 
                     if v.status == EmbeddingVersionStatus.RETIRED)
        
        return {
            "total_versions": len(self._versions),
            "active": active,
            "deprecated": deprecated,
            "retired": retired,
            "unique_texts": len(self._by_text_hash),
        }


class VersionComparator:
    """Compara versiones de embeddings."""
    
    @staticmethod
    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Calcula similitud coseno."""
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = sum(a * a for a in v1) ** 0.5
        mag2 = sum(b * b for b in v2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    @staticmethod
    def euclidean_distance(v1: list[float], v2: list[float]) -> float:
        """Calcula distancia euclidiana."""
        return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5
    
    @staticmethod
    def compare_versions(
        v1: EmbeddingVersion,
        v2: EmbeddingVersion,
    ) -> dict:
        """Compara dos versiones."""
        if v1.dimension != v2.dimension:
            return {"compatible": False, "reason": "Different dimensions"}
        
        similarity = VersionComparator.cosine_similarity(v1.vector, v2.vector)
        distance = VersionComparator.euclidean_distance(v1.vector, v2.vector)
        
        return {
            "compatible": True,
            "cosine_similarity": similarity,
            "euclidean_distance": distance,
            "model_same": v1.model == v2.model,
            "version_differs": v1.version != v2.version,
        }


__all__ = [
    "EmbeddingVersionStatus",
    "EmbeddingVersion",
    "VersionInfo",
    "BaseVersionManager",
    "InMemoryVersionManager",
    "VersionComparator",
]
