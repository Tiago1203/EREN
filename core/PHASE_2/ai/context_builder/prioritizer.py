"""Context Prioritizer - Priorizador de contexto."""

from __future__ import annotations

from typing import Any

from core.PHASE_2.ai.context_builder.models import (
    ContextItem,
    ContextPriority,
    ContextSource,
    ContextWindow,
)


class ContextPrioritizer:
    """
    Priorizador de ítems de contexto.
    
    Determina qué ítems son más importantes basándose
    en múltiples criterios.
    """

    def __init__(
        self,
        recency_weight: float = 0.3,
        relevance_weight: float = 0.4,
        priority_weight: float = 0.3,
    ) -> None:
        self.recency_weight = recency_weight
        self.relevance_weight = relevance_weight
        self.priority_weight = priority_weight

    def prioritize(
        self,
        items: list[ContextItem],
        max_tokens: int | None = None,
    ) -> list[ContextItem]:
        """
        Prioriza una lista de ítems.
        
        Args:
            items: Lista de ítems a priorizar
            max_tokens: Límite de tokens (opcional)
            
        Returns:
            Lista de ítems priorizados
        """
        # Calcular scores
        scored_items = [
            (item, self._calculate_score(item))
            for item in items
        ]
        
        # Ordenar por score descendente
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Filtrar por tokens si se especifica
        result = []
        total_tokens = 0
        
        for item, score in scored_items:
            if max_tokens is not None:
                if total_tokens + item.token_count > max_tokens:
                    # Verificar si es crítico
                    if item.priority == ContextPriority.CRITICAL:
                        # Remover ítems menos importantes para hacer espacio
                        result = self._make_space(result, item, max_tokens, total_tokens)
                        if result and item not in result:
                            # Todavía no cabe, verificar si reemplazamos
                            pass
                        else:
                            total_tokens += item.token_count
                            result.append(item)
                else:
                    total_tokens += item.token_count
                    result.append(item)
            else:
                result.append(item)
        
        return result

    def _calculate_score(self, item: ContextItem) -> float:
        """Calcula el score de un ítem."""
        # Score de prioridad (invertido: menor valor = mayor prioridad)
        priority_score = (5 - item.priority.value) / 4  # Normalizado a 0-1
        
        # Score de relevancia
        relevance_score = item.relevance_score
        
        # Score de recencia (simple: más reciente = mejor)
        age_hours = (item.created_at.timestamp()) / 3600  # Horas desde epoch
        # Normalizar a 0-1 (asumiendo 24 horas como máximo útil)
        recency_score = min(1.0, age_hours / 86400) if age_hours < 86400 else 0.5
        
        # Score final ponderado
        final_score = (
            priority_score * self.priority_weight +
            relevance_score * self.relevance_weight +
            recency_score * self.recency_weight
        )
        
        return final_score

    def _make_space(
        self,
        current_items: list[ContextItem],
        new_item: ContextItem,
        max_tokens: int,
        current_tokens: int,
    ) -> list[ContextItem]:
        """Hace espacio para un ítem crítico."""
        if new_item.priority != ContextPriority.CRITICAL:
            return current_items
        
        # Encontrar ítems de menor prioridad para remover
        candidates = [
            (i, item) for i, item in enumerate(current_items)
            if item.priority.value > ContextPriority.HIGH.value
        ]
        
        # Ordenar por prioridad más baja primero
        candidates.sort(key=lambda x: x[1].priority.value, reverse=True)
        
        space_needed = new_item.token_count - (max_tokens - current_tokens)
        removed_tokens = 0
        
        for i, item in candidates:
            if removed_tokens >= space_needed:
                break
            removed_tokens += item.token_count
            current_items.pop(i)
        
        # Agregar el ítem crítico si hay espacio ahora
        if sum(i.token_count for i in current_items) + new_item.token_count <= max_tokens:
            current_items.append(new_item)
        
        return current_items

    def fill_window(
        self,
        items: list[ContextItem],
        window: ContextWindow,
    ) -> ContextWindow:
        """
        Llena una ventana de contexto con ítems priorizados.
        
        Args:
            items: Lista de ítems disponibles
            window: Ventana de contexto
            
        Returns:
            Ventana llena con ítems priorizados
        """
        # Priorizar ítems
        prioritized = self.prioritize(items, window.max_tokens)
        
        # Limpiar ventana
        window.clear()
        
        # Agregar ítems priorizados
        for item in prioritized:
            if not window.add_item(item):
                break
        
        return window

    def get_items_to_remove(
        self,
        window: ContextWindow,
        tokens_to_free: int,
    ) -> list[ContextItem]:
        """
        Identifica ítems a remover para liberar espacio.
        
        Args:
            window: Ventana actual
            tokens_to_free: Tokens a liberar
            
        Returns:
            Lista de ítems a remover (ordenados por menor importancia)
        """
        # Items removibles (no críticos)
        removable = [
            item for item in window.items
            if item.priority != ContextPriority.CRITICAL
        ]
        
        # Ordenar por score (menor primero)
        scored = [
            (item, self._calculate_score(item))
            for item in removable
        ]
        scored.sort(key=lambda x: x[1])
        
        # Seleccionar ítems hasta liberar suficiente espacio
        to_remove = []
        freed_tokens = 0
        
        for item, score in scored:
            if freed_tokens >= tokens_to_free:
                break
            to_remove.append(item)
            freed_tokens += item.token_count
        
        return to_remove


class RelevanceCalculator:
    """
    Calculador de relevancia de contexto.
    
    Usa diferentes estrategias para calcular
    qué tan relevante es un ítem de contexto.
    """

    def __init__(self) -> None:
        self.strategies: list[RelevanceStrategy] = []

    def add_strategy(self, strategy: RelevanceStrategy) -> None:
        """Agrega una estrategia de relevancia."""
        self.strategies.append(strategy)

    def calculate(
        self,
        item: ContextItem,
        query: str | None = None,
    ) -> float:
        """Calcula la relevancia de un ítem."""
        if not self.strategies:
            return item.relevance_score
        
        scores = [strategy.calculate(item, query) for strategy in self.strategies]
        return sum(scores) / len(scores)


class RelevanceStrategy:
    """Estrategia base para cálculo de relevancia."""
    
    def calculate(
        self,
        item: ContextItem,
        query: str | None,
    ) -> float:
        raise NotImplementedError


class KeywordRelevance(RelevanceStrategy):
    """Estrategia basada en palabras clave."""
    
    def __init__(self, keywords: list[str], weight: float = 1.0) -> None:
        self.keywords = [k.lower() for k in keywords]
        self.weight = weight
    
    def calculate(
        self,
        item: ContextItem,
        query: str | None,
    ) -> float:
        content_lower = item.content.lower()
        matches = sum(1 for kw in self.keywords if kw in content_lower)
        return min(1.0, matches * self.weight / len(self.keywords))


class SemanticRelevance(RelevanceStrategy):
    """Estrategia basada en similitud semántica."""
    
    def __init__(self, embeddings: Any | None = None) -> None:
        self.embeddings = embeddings
    
    def calculate(
        self,
        item: ContextItem,
        query: str | None,
    ) -> float:
        if not query or not self.embeddings:
            return item.relevance_score
        
        # Placeholder: En producción usar embeddings reales
        # Por ahora retornar score existente
        return item.relevance_score


class RecencyRelevance(RelevanceStrategy):
    """Estrategia basada en recencia."""
    
    def __init__(
        self,
        max_age_hours: float = 24.0,
        half_life_hours: float = 6.0,
    ) -> None:
        self.max_age_hours = max_age_hours
        self.half_life_hours = half_life_hours
    
    def calculate(
        self,
        item: ContextItem,
        query: str | None,
    ) -> float:
        from datetime import datetime, timedelta
        
        age = datetime.now() - item.created_at
        age_hours = age.total_seconds() / 3600
        
        if age_hours > self.max_age_hours:
            return 0.0
        
        # Decaimiento exponencial
        return 0.5 ** (age_hours / self.half_life_hours)
