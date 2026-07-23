"""
PHASE 4 - EPIC 6: Context Module

Construcción de contexto clínico:
- ClinicalContext
- Context Builder
- Context Optimizer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import hashlib


@dataclass
class ClinicalContext:
    """Contexto clínico."""
    query: str
    query_type: str
    intent_confidence: float
    
    # Retrieved knowledge
    retrieved_chunks: list[dict] = field(default_factory=list)
    total_sources: int = 0
    
    # Context chunks
    context_chunks: list[str] = field(default_factory=list)
    total_tokens: int = 0
    
    # Medical entities
    entities: list[str] = field(default_factory=list)
    medical_terms: list[str] = field(default_factory=list)
    
    # Quality metrics
    context_quality: float = 0.0
    relevance_score: float = 0.0
    
    # Metadata
    created_at: str = ""
    version: str = "1.0.0"
    
    def to_prompt_text(self) -> str:
        """Convierte contexto a texto para prompt."""
        if not self.context_chunks:
            return ""
        
        return "\n\n".join([
            f"[Source {i+1}]: {chunk}"
            for i, chunk in enumerate(self.context_chunks)
        ])
    
    def get_context_hash(self) -> str:
        """Obtiene hash del contexto."""
        content = f"{self.query}:{':'.join(self.entities)}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class ContextChunk:
    """Chunk de contexto."""
    content: str
    source_id: str
    score: float
    relevance: float
    chunk_index: int = 0


@dataclass
class ContextConfig:
    """Configuración de contexto."""
    max_chunks: int = 5
    max_tokens: int = 4000
    overlap_tokens: int = 200
    min_relevance: float = 0.3


class BaseContextBuilder(ABC):
    """Clase base para builder de contexto."""
    
    @abstractmethod
    def build(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> ClinicalContext:
        """Construye contexto."""
        ...


class ClinicalContextBuilder(BaseContextBuilder):
    """Builder de contexto clínico."""
    
    def __init__(self, config: ContextConfig | None = None):
        self.config = config or ContextConfig()
    
    def build(
        self,
        query: str,
        retrieved_chunks: list[dict],
    ) -> ClinicalContext:
        """Construye contexto clínico."""
        from datetime import datetime
        
        # Sort by relevance
        sorted_chunks = sorted(
            retrieved_chunks,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
        
        # Filter by relevance
        filtered = [
            c for c in sorted_chunks
            if c.get("score", 0) >= self.config.min_relevance
        ]
        
        # Take top N chunks
        top_chunks = filtered[:self.config.max_chunks]
        
        # Extract context text
        context_texts = []
        for chunk in top_chunks:
            text = chunk.get("text", "") or chunk.get("content", "")
            if text:
                context_texts.append(text)
        
        # Calculate metrics
        total_tokens = sum(len(t.split()) for t in context_texts)
        avg_relevance = sum(c.get("score", 0) for c in top_chunks) / len(top_chunks) if top_chunks else 0
        
        return ClinicalContext(
            query=query,
            query_type="clinical",
            intent_confidence=0.8,
            retrieved_chunks=top_chunks,
            total_sources=len(set(c.get("source_id", "") for c in top_chunks)),
            context_chunks=context_texts,
            total_tokens=total_tokens,
            entities=[],
            medical_terms=[],
            context_quality=avg_relevance,
            relevance_score=avg_relevance,
            created_at=datetime.now().isoformat(),
        )


class ContextOptimizer:
    """Optimizador de contexto."""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
    
    def optimize(self, context: ClinicalContext) -> ClinicalContext:
        """Optimiza contexto para fitting en prompt."""
        # Calculate current tokens
        current_tokens = context.total_tokens
        
        if current_tokens <= self.max_tokens:
            return context
        
        # Need to truncate
        target_tokens = self.max_tokens
        
        # Build optimized chunks
        optimized_chunks = []
        accumulated = 0
        
        for chunk in context.context_chunks:
            chunk_tokens = len(chunk.split())
            
            if accumulated + chunk_tokens <= target_tokens:
                optimized_chunks.append(chunk)
                accumulated += chunk_tokens
            else:
                break
        
        # Update context
        context.context_chunks = optimized_chunks
        context.total_tokens = accumulated
        
        return context
    
    def add_overlap(
        self,
        chunks: list[str],
        overlap_tokens: int = 200,
    ) -> list[str]:
        """Añade overlap entre chunks."""
        if len(chunks) <= 1:
            return chunks
        
        overlapped = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev = chunks[i-1]
            curr = chunks[i]
            
            # Get last N tokens from previous
            prev_words = prev.split()
            overlap_words = prev_words[-overlap_tokens:] if len(prev_words) > overlap_tokens else prev_words
            
            # Prepend overlap to current
            overlapped.append(" ".join(overlap_words) + " " + curr)
        
        return overlapped


class PromptContextGenerator:
    """Generador de prompt context."""
    
    def __init__(self, template: str | None = None):
        self.template = template or self._default_template()
    
    def _default_template(self) -> str:
        """Template por defecto."""
        return """You are a clinical expert assistant. Answer the following question based on the provided context.

Question: {query}

Context:
{context}

Instructions:
- Answer based only on the provided context
- Cite specific sources when making claims
- If the context is insufficient, indicate that
- Prioritize recent and authoritative sources

Answer:"""
    
    def generate(self, context: ClinicalContext) -> str:
        """Genera prompt context."""
        context_text = context.to_prompt_text()
        
        prompt = self.template.format(
            query=context.query,
            context=context_text or "No relevant context found.",
        )
        
        return prompt
    
    def generate_with_citations(self, context: ClinicalContext) -> str:
        """Genera prompt con citaciones."""
        context_text = self._format_with_citations(context)
        
        prompt = self.template.format(
            query=context.query,
            context=context_text,
        )
        
        return prompt
    
    def _format_with_citations(self, context: ClinicalContext) -> str:
        """Formatea contexto con citaciones."""
        parts = []
        
        for i, chunk in enumerate(context.context_chunks):
            source_id = context.retrieved_chunks[i].get("source_id", f"source_{i+1}")
            citation = f"[{source_id}]"
            parts.append(f"{citation} {chunk}")
        
        return "\n\n".join(parts)


__all__ = [
    "ClinicalContext",
    "ContextChunk",
    "ContextConfig",
    "BaseContextBuilder",
    "ClinicalContextBuilder",
    "ContextOptimizer",
    "PromptContextGenerator",
]
