"""
PHASE 4 - EPIC 3: Pipelines Module

Pipelines para generación de embeddings:
- Embedding Pipeline
- Batch Generator
- Validation Pipeline
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import asyncio
import hashlib

from core.PHASE_4.foundation import (
    InMemoryEventPublisher,
    DomainEvent,
    EventType,
)


@dataclass
class EmbeddingBatch:
    """Batch de embeddings."""
    batch_id: str
    texts: list[str]
    model: str
    embeddings: list = field(default_factory=list)
    failed_texts: list[str] = field(default_factory=list)
    created_at: str = ""
    completed_at: str = ""
    status: str = "pending"
    error_message: str = ""
    
    def is_complete(self) -> bool:
        """Verifica si el batch está completo."""
        return self.status == "completed"
    
    def success_rate(self) -> float:
        """Calcula tasa de éxito."""
        total = len(self.texts)
        if total == 0:
            return 0.0
        return (total - len(self.failed_texts)) / total


@dataclass
class EmbeddingMetadata:
    """Metadata de embedding."""
    text_hash: str
    text_length: int
    token_count: int
    model: str
    version: str
    dimension: int
    cached: bool = False
    validation_passed: bool = True
    quality_score: float = 0.0


@dataclass
class EmbeddingResult:
    """Resultado de embedding."""
    vector: list[float]
    model: str
    dimension: int
    metadata: EmbeddingMetadata
    cached: bool = False


class EmbeddingPipeline:
    """Pipeline completo para generación de embeddings."""
    
    def __init__(
        self,
        provider,
        cache=None,
        version_manager=None,
        validate: bool = True,
    ):
        self.provider = provider
        self.cache = cache
        self.version_manager = version_manager
        self.validate = validate
        self.event_publisher = InMemoryEventPublisher()
    
    def _compute_hash(self, text: str) -> str:
        """Computa hash del texto."""
        return hashlib.sha256(text.encode()).hexdigest()[:32]
    
    async def generate(
        self,
        text: str,
        use_cache: bool = True,
    ) -> EmbeddingResult:
        """Genera embedding para un texto."""
        from datetime import datetime
        
        text_hash = self._compute_hash(text)
        
        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(text, self.provider.model_name)
            if cached:
                return EmbeddingResult(
                    vector=cached.vector,
                    model=cached.model,
                    dimension=cached.dimension,
                    metadata=EmbeddingMetadata(
                        text_hash=text_hash,
                        text_length=len(text),
                        token_count=len(text.split()),
                        model=cached.model,
                        version="cached",
                        dimension=cached.dimension,
                        cached=True,
                    ),
                    cached=True,
                )
        
        # Generate embedding
        embedding = await self.provider.generate(text)
        
        # Validate
        validation_passed = True
        if self.validate:
            validation_passed = self._validate_embedding(embedding)
        
        # Create version
        if self.version_manager:
            self.version_manager.create_version(
                text_hash=text_hash,
                model=self.provider.model_name,
                vector=embedding.vector,
            )
        
        # Cache
        if use_cache and self.cache:
            from core.PHASE_4.epic3_clinical_embeddings.cache import CachedEmbedding
            
            cached_embedding = CachedEmbedding(
                text_hash=text_hash,
                text=text,
                vector=embedding.vector,
                model=embedding.model,
                dimension=embedding.dimension,
                created_at=embedding.generated_at,
                accessed_at=embedding.generated_at,
            )
            self.cache.set(cached_embedding)
        
        # Publish event
        event = DomainEvent.create(
            event_type=EventType.EMBEDDING_GENERATED,
            metadata={
                "text_hash": text_hash,
                "model": self.provider.model_name,
                "dimension": embedding.dimension,
                "cached": False,
            },
        )
        await self.event_publisher.publish(event)
        
        return EmbeddingResult(
            vector=embedding.vector,
            model=embedding.model,
            dimension=embedding.dimension,
            metadata=EmbeddingMetadata(
                text_hash=text_hash,
                text_length=len(text),
                token_count=len(text.split()),
                model=embedding.model,
                version="1.0.0",
                dimension=embedding.dimension,
                cached=False,
                validation_passed=validation_passed,
            ),
            cached=False,
        )
    
    async def generate_batch(
        self,
        texts: list[str],
        use_cache: bool = True,
    ) -> list[EmbeddingResult]:
        """Genera embeddings para múltiples textos."""
        results = []
        
        for text in texts:
            try:
                result = await self.generate(text, use_cache=use_cache)
                results.append(result)
            except Exception as e:
                # Create failed result
                results.append(EmbeddingResult(
                    vector=[],
                    model=self.provider.model_name,
                    dimension=0,
                    metadata=EmbeddingMetadata(
                        text_hash=self._compute_hash(text),
                        text_length=len(text),
                        token_count=len(text.split()),
                        model=self.provider.model_name,
                        version="error",
                        dimension=0,
                        validation_passed=False,
                    ),
                    cached=False,
                ))
        
        return results
    
    def _validate_embedding(self, embedding) -> bool:
        """Valida embedding generado."""
        # Check dimension
        if len(embedding.vector) != self.provider.dimension:
            return False
        
        # Check for NaN or Inf
        import math
        for v in embedding.vector:
            if math.isnan(v) or math.isinf(v):
                return False
        
        # Check magnitude
        magnitude = sum(v * v for v in embedding.vector) ** 0.5
        if magnitude < 0.01:
            return False
        
        return True


class BatchGenerator:
    """Generador de batches para embeddings."""
    
    def __init__(
        self,
        pipeline: EmbeddingPipeline,
        batch_size: int = 32,
    ):
        self.pipeline = pipeline
        self.batch_size = batch_size
    
    def _create_batches(self, texts: list[str]) -> list[list[str]]:
        """Crea batches de textos."""
        batches = []
        for i in range(0, len(texts), self.batch_size):
            batches.append(texts[i:i + self.batch_size])
        return batches
    
    async def generate(
        self,
        texts: list[str],
        use_cache: bool = True,
        progress_callback=None,
    ) -> list[EmbeddingResult]:
        """Genera embeddings en batches."""
        batches = self._create_batches(texts)
        all_results = []
        
        for i, batch in enumerate(batches):
            # Generate batch
            results = await self.pipeline.generate_batch(batch, use_cache=use_cache)
            all_results.extend(results)
            
            # Report progress
            if progress_callback:
                progress_callback(i + 1, len(batches))
        
        return all_results


__all__ = [
    "EmbeddingBatch",
    "EmbeddingMetadata",
    "EmbeddingResult",
    "EmbeddingPipeline",
    "BatchGenerator",
]
