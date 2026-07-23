"""
PHASE 4 - EPIC 3: Clinical Embedding Engine

Genera embeddings especializados para conocimiento biomédico:
- Modelos biomédicos (BioBERT, PubMedBERT, ClinicalBERT)
- Versionado de embeddings
- Optimización de batch processing
- Cache de embeddings
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol
import hashlib
import json

from core.PHASE_4.foundation import EmbeddingVector


class EmbeddingModel(str, Enum):
    """Modelos de embedding biomédico."""
    PUBMEDBERT = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    BIOBERT = "dmis-lab/biobert-base-cased-v1.2"
    BIOMEDBERT = "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext"
    CLINICALBERT = "emilyalsentzer/Bio_ClinicalBERT"
    SCIBERT = "allenai/scibert_scivocab_uncased"
    BLUEBERT = "bionlp/bluebert_pubmed_mimic_uncased"


class EmbeddingDimension(str, Enum):
    """Dimensiones de embedding."""
    BASE = "base"    # 768
    LARGE = "large"  # 1024
    SMALL = "small"  # 384


class NormalizationMethod(str, Enum):
    """Métodos de normalización."""
    NONE = "none"
    L2 = "l2"
    MIN_MAX = "min_max"
    MEAN = "mean"


@dataclass
class EmbeddingConfig:
    """Configuración para generación de embeddings."""
    model: EmbeddingModel = EmbeddingModel.PUBMEDBERT
    dimension: EmbeddingDimension = EmbeddingDimension.BASE
    batch_size: int = 32
    max_sequence_length: int = 512
    normalize: NormalizationMethod = NormalizationMethod.L2
    pooling_strategy: str = "mean"  # mean, cls, max
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600


@dataclass
class CachedEmbedding:
    """Embedding con cache metadata."""
    embedding: EmbeddingVector
    text_hash: str
    model: str
    cached_at: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class EmbeddingVersion:
    """Versión de un embedding."""
    version_id: str
    model: str
    dimension: int
    created_at: datetime
    text_hash: str
    embedding_id: str


@dataclass
class EmbeddingBatch:
    """Batch de embeddings."""
    batch_id: str
    texts: list[str]
    embeddings: list[EmbeddingVector]
    model: str
    processing_time_ms: int
    failed_count: int = 0
    errors: list[str] = field(default_factory=list)


class IEmbeddingProvider(Protocol):
    """Protocolo para provider de embeddings."""
    
    async def generate(self, text: str, config: EmbeddingConfig) -> EmbeddingVector:
        """Genera embedding para texto."""
        ...
    
    async def generate_batch(
        self,
        texts: list[str],
        config: EmbeddingConfig,
    ) -> EmbeddingBatch:
        """Genera embeddings para batch."""
        ...


class IEmbeddingCache:
    """Protocolo para cache de embeddings."""
    
    async def get(self, text_hash: str, model: str) -> Optional[CachedEmbedding]:
        """Obtiene embedding del cache."""
        ...
    
    async def set(self, embedding: EmbeddingVector, text_hash: str, model: str) -> bool:
        """Almacena embedding en cache."""
        ...
    
    async def invalidate(self, text_hash: str, model: str) -> bool:
        """Invalida entrada del cache."""
        ...
    
    async def clear(self) -> int:
        """Limpia cache completo."""
        ...


class InMemoryEmbeddingCache(IEmbeddingCache):
    """Cache de embeddings en memoria."""
    
    def __init__(self, max_size: int = 10000):
        self._cache: dict[str, CachedEmbedding] = {}
        self._max_size = max_size
    
    async def get(self, text_hash: str, model: str) -> Optional[CachedEmbedding]:
        """Obtiene embedding del cache."""
        key = self._make_key(text_hash, model)
        cached = self._cache.get(key)
        
        if cached:
            cached.access_count += 1
            cached.last_accessed = datetime.now(UTC)
        
        return cached
    
    async def set(
        self,
        embedding: EmbeddingVector,
        text_hash: str,
        model: str,
    ) -> bool:
        """Almacena embedding en cache."""
        # Evict if full
        if len(self._cache) >= self._max_size:
            await self._evict_lru()
        
        key = self._make_key(text_hash, model)
        self._cache[key] = CachedEmbedding(
            embedding=embedding,
            text_hash=text_hash,
            model=model,
            cached_at=datetime.now(UTC),
        )
        return True
    
    async def invalidate(self, text_hash: str, model: str) -> bool:
        """Invalida entrada del cache."""
        key = self._make_key(text_hash, model)
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    async def clear(self) -> int:
        """Limpia cache completo."""
        count = len(self._cache)
        self._cache.clear()
        return count
    
    async def _evict_lru(self):
        """Evict least recently used."""
        if not self._cache:
            return
        
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed,
        )
        del self._cache[lru_key]
    
    def _make_key(self, text_hash: str, model: str) -> str:
        """Genera clave de cache."""
        return f"{model}:{text_hash}"


class PubMedBERTProvider:
    """Provider de embeddings PubMedBERT."""
    
    def __init__(self, cache: IEmbeddingCache | None = None):
        self.cache = cache or InMemoryEmbeddingCache()
        self._model = None
    
    async def _load_model(self):
        """Carga modelo bajo demanda."""
        if self._model is None:
            # Placeholder - would load transformers model
            pass
    
    async def generate(self, text: str, config: EmbeddingConfig) -> EmbeddingVector:
        """Genera embedding para texto."""
        # Check cache
        text_hash = self._hash_text(text)
        if config.cache_enabled:
            cached = await self.cache.get(text_hash, config.model.value)
            if cached:
                return cached.embedding
        
        # Load model if needed
        await self._load_model()
        
        # Generate embedding
        # Placeholder - would use actual model
        vector = [0.0] * 768
        
        embedding = EmbeddingVector(
            values=vector,
            model=config.model.value,
            dimension=len(vector),
            metadata={"pooling": config.pooling_strategy},
        )
        
        # Cache result
        if config.cache_enabled:
            await self.cache.set(embedding, text_hash, config.model.value)
        
        return embedding
    
    async def generate_batch(
        self,
        texts: list[str],
        config: EmbeddingConfig,
    ) -> EmbeddingBatch:
        """Genera embeddings para batch."""
        import time
        import uuid
        start = time.time()
        
        embeddings = []
        errors = []
        
        for text in texts:
            try:
                emb = await self.generate(text, config)
                embeddings.append(emb)
            except Exception as e:
                errors.append(str(e))
        
        processing_time_ms = int((time.time() - start) * 1000)
        
        return EmbeddingBatch(
            batch_id=str(uuid.uuid4()),
            texts=texts,
            embeddings=embeddings,
            model=config.model.value,
            processing_time_ms=processing_time_ms,
            failed_count=len(errors),
            errors=errors,
        )
    
    def _hash_text(self, text: str) -> str:
        """Genera hash de texto."""
        return hashlib.sha256(text.encode()).hexdigest()[:32]


class ClinicalEmbeddingEngine:
    """Motor de embeddings clínicos."""
    
    def __init__(
        self,
        provider: IEmbeddingProvider | None = None,
        cache: IEmbeddingCache | None = None,
    ):
        self.provider = provider or PubMedBERTProvider(cache)
        self.cache = cache or InMemoryEmbeddingCache()
        self._version_registry: dict[str, EmbeddingVersion] = {}
    
    async def embed(
        self,
        text: str,
        model: EmbeddingModel = EmbeddingModel.PUBMEDBERT,
        normalize: bool = True,
    ) -> EmbeddingVector:
        """Genera embedding para texto."""
        config = EmbeddingConfig(
            model=model,
            normalize=NormalizationMethod.L2 if normalize else NormalizationMethod.NONE,
        )
        
        return await self.provider.generate(text, config)
    
    async def embed_batch(
        self,
        texts: list[str],
        model: EmbeddingModel = EmbeddingModel.PUBMEDBERT,
    ) -> EmbeddingBatch:
        """Genera embeddings para batch de textos."""
        config = EmbeddingConfig(
            model=model,
            batch_size=len(texts),
        )
        
        return await self.provider.generate_batch(texts, config)
    
    async def embed_medical_entities(
        self,
        entities: list[dict],
        model: EmbeddingModel = EmbeddingModel.PUBMEDBERT,
    ) -> list[EmbeddingVector]:
        """Genera embeddings para entidades médicas."""
        texts = [e.get("text", "") for e in entities]
        batch = await self.embed_batch(texts, model)
        return batch.embeddings
    
    async def embed_clinical_notes(
        self,
        notes: list[str],
        model: EmbeddingModel = EmbeddingModel.CLINICALBERT,
    ) -> list[EmbeddingVector]:
        """Genera embeddings para notas clínicas."""
        batch = await self.embed_batch(notes, model)
        return batch.embeddings
    
    async def embed_knowledge_chunks(
        self,
        chunks: list[str],
        model: EmbeddingModel = EmbeddingModel.PUBMEDBERT,
    ) -> list[EmbeddingVector]:
        """Genera embeddings para chunks de conocimiento."""
        batch = await self.embed_batch(chunks, model)
        return batch.embeddings
    
    def register_version(
        self,
        embedding_id: str,
        model: str,
        dimension: int,
        text_hash: str,
    ) -> EmbeddingVersion:
        """Registra versión de embedding."""
        import uuid
        
        version = EmbeddingVersion(
            version_id=str(uuid.uuid4()),
            model=model,
            dimension=dimension,
            created_at=datetime.now(UTC),
            text_hash=text_hash,
            embedding_id=embedding_id,
        )
        
        self._version_registry[version.version_id] = version
        return version
    
    def get_version(self, version_id: str) -> Optional[EmbeddingVersion]:
        """Obtiene versión de embedding."""
        return self._version_registry.get(version_id)
    
    def list_versions(self, embedding_id: str) -> list[EmbeddingVersion]:
        """Lista versiones de un embedding."""
        return [
            v for v in self._version_registry.values()
            if v.embedding_id == embedding_id
        ]
    
    async def invalidate_cache(self, text_hash: str | None = None) -> int:
        """Invalida cache."""
        if text_hash:
            # Invalidate specific entry
            for model in EmbeddingModel:
                await self.cache.invalidate(text_hash, model.value)
            return 1
        else:
            # Clear all
            return await self.cache.clear()


class EmbeddingOptimizer:
    """Optimizador de embeddings."""
    
    @staticmethod
    def quantize(embedding: EmbeddingVector, bits: int = 8) -> EmbeddingVector:
        """Cuantiza embedding a menor precisión."""
        import numpy as np
        
        values = np.array(embedding.values)
        
        if bits == 8:
            # INT8 quantization
            min_val, max_val = values.min(), values.max()
            scale = (max_val - min_val) / 255
            quantized = ((values - min_val) / scale).astype(np.uint8)
            
            # Store quantized values + scale + min for reconstruction
            return EmbeddingVector(
                values=quantized.tolist(),
                model=embedding.model,
                dimension=embedding.dimension,
                metadata={
                    **embedding.metadata,
                    "quantized": True,
                    "bits": 8,
                    "scale": float(scale),
                    "min": float(min_val),
                },
            )
        
        return embedding
    
    @staticmethod
    def reduce_dimension(
        embedding: EmbeddingVector,
        target_dim: int,
    ) -> EmbeddingVector:
        """Reduce dimensionalidad usando PCA o truncamiento."""
        import numpy as np
        
        if target_dim >= embedding.dimension:
            return embedding
        
        values = np.array(embedding.values)
        
        # Simple truncation
        reduced = values[:target_dim]
        
        return EmbeddingVector(
            values=reduced.tolist(),
            model=embedding.model,
            dimension=target_dim,
            metadata={
                **embedding.metadata,
                "reduced": True,
                "original_dim": embedding.dimension,
            },
        )
    
    @staticmethod
    def cosine_similarity(v1: EmbeddingVector, v2: EmbeddingVector) -> float:
        """Calcula similitud coseno entre embeddings."""
        import numpy as np
        
        a = np.array(v1.values)
        b = np.array(v2.values)
        
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot / (norm_a * norm_b))


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Providers
from core.PHASE_4.epic3_clinical_embeddings.providers import (
    EmbeddingModel,
    EmbeddingConfig,
    GeneratedEmbedding,
    BaseEmbeddingProvider,
    MockEmbeddingProvider,
    SentenceTransformerProvider,
    OllamaProvider,
    OpenAIProvider,
    EmbeddingProviderFactory,
)

# Cache
from core.PHASE_4.epic3_clinical_embeddings.cache import (
    CachedEmbedding,
    BaseEmbeddingCache,
    InMemoryEmbeddingCache,
    PersistentEmbeddingCache,
)

# Versioning
from core.PHASE_4.epic3_clinical_embeddings.versioning import (
    EmbeddingVersionStatus,
    EmbeddingVersion,
    BaseVersionManager,
    InMemoryVersionManager,
    VersionComparator,
)

# Pipelines
from core.PHASE_4.epic3_clinical_embeddings.pipelines import (
    EmbeddingBatch,
    EmbeddingMetadata,
    EmbeddingResult,
    EmbeddingPipeline,
    BatchGenerator,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    # Enums
    "EmbeddingModel",
    "EmbeddingDimension",
    "NormalizationMethod",
    # Data Classes
    "EmbeddingConfig",
    "CachedEmbedding",
    "EmbeddingVersion",
    "EmbeddingBatch",
    "EmbeddingMetadata",
    "EmbeddingResult",
    # Protocols
    "IEmbeddingProvider",
    "IEmbeddingCache",
    # Implementations
    "InMemoryEmbeddingCache",
    "PubMedBERTProvider",
    # Engines
    "ClinicalEmbeddingEngine",
    "EmbeddingOptimizer",
    # Providers (new)
    "GeneratedEmbedding",
    "BaseEmbeddingProvider",
    "MockEmbeddingProvider",
    "SentenceTransformerProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "EmbeddingProviderFactory",
    # Cache (new)
    "PersistentEmbeddingCache",
    # Versioning (new)
    "EmbeddingVersionStatus",
    "InMemoryVersionManager",
    "VersionComparator",
    # Pipelines (new)
    "EmbeddingPipeline",
    "BatchGenerator",
]
