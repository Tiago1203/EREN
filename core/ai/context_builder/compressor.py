"""Context Compressor - Compresor de contexto."""

from __future__ import annotations

import re
from typing import Any, Callable

from core.ai.context_builder.models import ContextItem, ContextSource


class ContextCompressor:
    """
    Compresor de contexto.
    
    Reduce el tamaño del contexto manteniendo
    la información más importante.
    """

    def __init__(
        self,
        strategies: list[CompressionStrategy] | None = None,
    ) -> None:
        self.strategies = strategies or [
            RemoveDuplicatesStrategy(),
            TrimWhitespaceStrategy(),
            RemoveRedundantInfoStrategy(),
            SummarizeStrategy(),
        ]

    def compress(
        self,
        items: list[ContextItem],
        target_tokens: int | None = None,
    ) -> list[ContextItem]:
        """
        Comprime una lista de ítems de contexto.
        
        Args:
            items: Lista de ítems a comprimir
            target_tokens: Tokens objetivo (opcional)
            
        Returns:
            Lista de ítems comprimidos
        """
        result = list(items)
        
        for strategy in self.strategies:
            result = strategy.compress(result)
            
            if target_tokens:
                current_tokens = sum(item.token_count for item in result)
                if current_tokens <= target_tokens:
                    break
        
        return result

    def compress_item(
        self,
        item: ContextItem,
        max_tokens: int | None = None,
    ) -> ContextItem:
        """Comprime un ítem individual."""
        content = item.content
        
        # Aplicar estrategias básicas
        content = self._remove_extra_whitespace(content)
        content = self._remove_redundant_phrases(content)
        
        # Si aún es muy largo, truncar
        if max_tokens:
            tokens = len(content) // 4
            if tokens > max_tokens:
                content = self._truncate(content, max_tokens * 4)
        
        # Crear nuevo ítem con contenido comprimido
        return ContextItem(
            id=item.id,
            source=item.source,
            content=content,
            priority=item.priority,
            created_at=item.created_at,
            relevance_score=item.relevance_score,
            metadata={**item.metadata, "compressed": True},
            token_count=len(content) // 4,
        )

    def _remove_extra_whitespace(self, text: str) -> str:
        """Remueve espacios en blanco extra."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _remove_redundant_phrases(self, text: str) -> str:
        """Remueve frases redundantes."""
        redundant = [
            r'como se mencionó anteriormente',
            r'como se indicated anteriormente',
            r'en resumen,',
            r'para resumir,',
            r'vale la pena mencionar que',
            r'es importante notar que',
            r'cabe destacar que',
        ]
        
        for pattern in redundant:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text

    def _truncate(self, text: str, max_chars: int) -> str:
        """Trunca texto respetando palabras."""
        if len(text) <= max_chars:
            return text
        
        truncated = text[:max_chars]
        last_space = truncated.rfind(' ')
        
        if last_space > max_chars * 0.8:
            truncated = truncated[:last_space]
        
        return truncated + "..."


class CompressionStrategy:
    """Estrategia base de compresión."""
    
    def compress(self, items: list[ContextItem]) -> list[ContextItem]:
        raise NotImplementedError


class RemoveDuplicatesStrategy(CompressionStrategy):
    """Remueve ítems duplicados."""
    
    def compress(self, items: list[ContextItem]) -> list[ContextItem]:
        seen_content: set[str] = set()
        result: list[ContextItem] = []
        
        for item in items:
            # Crear clave de contenido normalizado
            content_key = self._normalize(item.content)
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                result.append(item)
            else:
                # Merge metadata de duplicados
                pass
        
        return result
    
    def _normalize(self, text: str) -> str:
        """Normaliza texto para comparación."""
        return re.sub(r'\s+', ' ', text.lower().strip())


class TrimWhitespaceStrategy(CompressionStrategy):
    """Remueve espacios en blanco extra."""
    
    def compress(self, items: list[ContextItem]) -> list[ContextItem]:
        result = []
        
        for item in items:
            content = re.sub(r'\s+', ' ', item.content)
            content = content.strip()
            
            if content:
                result.append(ContextItem(
                    id=item.id,
                    source=item.source,
                    content=content,
                    priority=item.priority,
                    created_at=item.created_at,
                    relevance_score=item.relevance_score,
                    metadata=item.metadata,
                    token_count=len(content) // 4,
                ))
        
        return result


class RemoveRedundantInfoStrategy(CompressionStrategy):
    """Remueve información redundante dentro de ítems."""
    
    def compress(self, items: list[ContextItem]) -> list[ContextItem]:
        result = []
        
        for item in items:
            content = self._remove_redundant(item.content)
            
            result.append(ContextItem(
                id=item.id,
                source=item.source,
                content=content,
                priority=item.priority,
                created_at=item.created_at,
                relevance_score=item.relevance_score,
                metadata=item.metadata,
                token_count=len(content) // 4,
            ))
        
        return result
    
    def _remove_redundant(self, text: str) -> str:
        """Remueve información redundante."""
        redundant_patterns = [
            r'\[ المصدر: [^\]]+\]',  # [Source: ...]
            r'\(تم الإبلاغ في [^)]+\)',  # (Reported in ...)
            r'Last updated: \d{4}-\d{2}-\d{2}',  # Last updated: YYYY-MM-DD
        ]
        
        for pattern in redundant_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text


class SummarizeStrategy(CompressionStrategy):
    """Resume ítems que excedan el límite de tokens."""
    
    def __init__(self, max_tokens_per_item: int = 512) -> None:
        self.max_tokens_per_item = max_tokens_per_item
    
    def compress(self, items: list[ContextItem]) -> list[ContextItem]:
        result = []
        
        for item in items:
            if item.token_count <= self.max_tokens_per_item:
                result.append(item)
            else:
                # Resumir
                summarized = self._summarize(item)
                result.append(summarized)
        
        return result
    
    def _summarize(self, item: ContextItem) -> ContextItem:
        """Resume un ítem."""
        # Placeholder: En producción usar un LLM para resumir
        # Por ahora, truncar inteligentemente
        
        max_chars = self.max_tokens_per_item * 4
        content = item.content[:max_chars]
        
        # Encontrar último punto o newline
        last_period = content.rfind('.')
        last_newline = content.rfind('\n')
        
        cut_point = max(last_period, last_newline)
        if cut_point > max_chars * 0.7:
            content = content[:cut_point + 1]
        
        return ContextItem(
            id=item.id,
            source=item.source,
            content=content + " [resumedido]",
            priority=item.priority,
            created_at=item.created_at,
            relevance_score=item.relevance_score,
            metadata={**item.metadata, "summarized": True},
            token_count=len(content) // 4,
        )


class SourceBasedCompressionStrategy(CompressionStrategy):
    """Compresión basada en fuente de contexto."""
    
    def __init__(
        self,
        source_weights: dict[ContextSource, float] | None = None,
    ) -> None:
        self.source_weights = source_weights or {
            ContextSource.SYSTEM: 1.0,
            ContextSource.USER: 0.9,
            ContextSource.CONVERSATION: 0.8,
            ContextSource.KNOWLEDGE: 0.7,
            ContextSource.MEMORY: 0.6,
            ContextSource.DEVICE: 0.5,
            ContextSource.INCIDENT: 0.5,
            ContextSource.HOSPITAL: 0.4,
            ContextSource.SESSION: 0.3,
        }
    
    def compress(self, items: list[ContextItem]) -> list[ContextItem]:
        # Ordenar por peso de fuente
        weighted = [
            (item, self.source_weights.get(item.source, 0.5))
            for item in items
        ]
        weighted.sort(key=lambda x: x[1], reverse=True)
        
        # Mantener solo los de mayor peso hasta el límite
        return [item for item, _ in weighted]


class IntelligentCompressor(ContextCompressor):
    """
    Compresor inteligente con múltiples estrategias.
    
    Usa una combinación de estrategias para
    comprimir el contexto de manera inteligente.
    """
    
    def __init__(self) -> None:
        super().__init__([
            RemoveDuplicatesStrategy(),
            TrimWhitespaceStrategy(),
            RemoveRedundantInfoStrategy(),
            SourceBasedCompressionStrategy(),
            SummarizeStrategy(max_tokens_per_item=256),
        ])
    
    def compress(
        self,
        items: list[ContextItem],
        target_tokens: int | None = None,
        preserve_sources: list[ContextSource] | None = None,
    ) -> list[ContextItem]:
        """
        Comprime con preservación de fuentes críticas.
        
        Args:
            items: Ítems a comprimir
            target_tokens: Tokens objetivo
            preserve_sources: Fuentes que no deben comprimirse
        """
        # Separar ítems preservables
        preserved: list[ContextItem] = []
        compressible: list[ContextItem] = []
        
        if preserve_sources:
            for item in items:
                if item.source in preserve_sources:
                    preserved.append(item)
                else:
                    compressible.append(item)
        else:
            compressible = list(items)
        
        # Comprimir ítems compresibles
        compressed = super().compress(compressible, target_tokens)
        
        # Combinar y reordenar por prioridad
        result = preserved + compressed
        result.sort(key=lambda x: x.priority.value)
        
        return result
