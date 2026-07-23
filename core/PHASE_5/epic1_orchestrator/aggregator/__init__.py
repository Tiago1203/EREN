"""
PHASE 5 - EPIC 1: Response Aggregator

Componente que agrega y fusiona resultados de múltiples agentes.
Gestiona la combinación de respuestas y el manejo de conflictos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM DOMAIN
# =============================================================================

from core.PHASE_5.epic1_orchestrator.domain import (
    AggregationMethod,
    ExecutionResult,
)


# =============================================================================
# AGGREGATION CONFIG
# =============================================================================

@dataclass
class AggregationConfig:
    """Configuración para agregación."""
    method: AggregationMethod = AggregationMethod.BEST
    min_confidence: float = 0.5
    max_results: int = 10
    
    # Para WEIGHTED
    weights: dict[str, float] = field(default_factory=dict)
    
    # Para MERGE
    merge_strategy: str = "deep"  # shallow, deep, union
    
    # Para VOTE
    vote_threshold: float = 0.5
    
    # Para confianza
    confidence_boost: float = 1.2  # Multiplicador para confianza
    citation_boost: float = 1.1   # Multiplicador por citación


# =============================================================================
# AGGREGATED RESULT
# =============================================================================

@dataclass
class AggregatedResult:
    """Resultado agregado de múltiples ejecuciones."""
    success: bool
    output: dict = field(default_factory=dict)
    
    # Métricas agregadas
    total_execution_time_ms: int = 0
    avg_confidence: float = 0.0
    total_citations: list[str] = field(default_factory=list)
    
    # Detalles
    method_used: AggregationMethod = AggregationMethod.BEST
    sources: list[str] = field(default_factory=list)  # step_ids de origen
    
    # Conflicto (si hay)
    conflicts: list[dict] = field(default_factory=list)
    
    # Errores
    errors: list[str] = field(default_factory=list)
    
    # Metadatos
    aggregated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# RESPONSE AGGREGATOR
# =============================================================================

class ResponseAggregator:
    """
    Agregador de respuestas.
    
    Responsabilidades:
    1. Seleccionar método de agregación
    2. Combinar resultados según método
    3. Resolver conflictos
    4. Generar resultado final
    """
    
    def __init__(
        self,
        config: AggregationConfig | None = None,
    ):
        self.config = config or AggregationConfig()
    
    async def aggregate(
        self,
        results: dict[str, dict],
        shared_context: dict,
        method: AggregationMethod | None = None,
    ) -> dict:
        """
        Agrega resultados de múltiples pasos.
        
        Args:
            results: Dict de step_id -> result
            shared_context: Contexto compartido del workflow
            method: Método de agregación
        
        Returns:
            Dict con resultado agregado
        """
        method = method or self.config.method
        
        # Convertir a ExecutionResult
        exec_results = []
        for step_id, result in results.items():
            exec_result = ExecutionResult(
                execution_id=step_id,
                success=result.get("success", False),
                output=result.get("output", {}),
                error=result.get("error"),
                confidence=result.get("confidence", 0.0),
                citations=result.get("citations", []),
                execution_time_ms=result.get("execution_time_ms", 0),
            )
            exec_results.append(exec_result)
        
        # Ejecutar agregación
        if method == AggregationMethod.FIRST:
            aggregated = self._aggregate_first(exec_results)
        elif method == AggregationMethod.BEST:
            aggregated = self._aggregate_best(exec_results)
        elif method == AggregationMethod.ALL:
            aggregated = self._aggregate_all(exec_results)
        elif method == AggregationMethod.MERGE:
            aggregated = await self._aggregate_merge(exec_results, shared_context)
        elif method == AggregationMethod.VOTE:
            aggregated = self._aggregate_vote(exec_results)
        elif method == AggregationMethod.WEIGHTED:
            aggregated = await self._aggregate_weighted(exec_results)
        else:
            aggregated = self._aggregate_best(exec_results)
        
        # Agregar contexto compartido
        if shared_context:
            aggregated.output["_shared_context"] = shared_context
        
        return {
            "success": aggregated.success,
            "output": aggregated.output,
            "total_execution_time_ms": aggregated.total_execution_time_ms,
            "avg_confidence": aggregated.avg_confidence,
            "citations": aggregated.total_citations,
            "method_used": aggregated.method_used.value,
            "sources": aggregated.sources,
            "conflicts": aggregated.conflicts,
            "errors": aggregated.errors,
        }
    
    def _aggregate_first(self, results: list[ExecutionResult]) -> AggregatedResult:
        """Retorna el primer resultado válido."""
        
        for result in results:
            if result.success:
                return AggregatedResult(
                    success=True,
                    output=result.output,
                    total_execution_time_ms=result.execution_time_ms,
                    avg_confidence=result.confidence,
                    total_citations=result.citations,
                    method_used=AggregationMethod.FIRST,
                    sources=[result.execution_id],
                )
        
        # Todos fallaron
        return AggregatedResult(
            success=False,
            errors=[r.error for r in results if r.error],
            method_used=AggregationMethod.FIRST,
        )
    
    def _aggregate_best(self, results: list[ExecutionResult]) -> AggregatedResult:
        """Retorna el resultado con mayor confianza."""
        
        valid_results = [r for r in results if r.success]
        
        if not valid_results:
            return AggregatedResult(
                success=False,
                errors=[r.error for r in results if r.error],
                method_used=AggregationMethod.BEST,
            )
        
        # Ordenar por confianza
        best = max(valid_results, key=lambda r: r.confidence)
        
        # Combinar citaciones
        all_citations = []
        for r in valid_results:
            all_citations.extend(r.citations)
        
        # Promedio de confianza
        avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
        
        return AggregatedResult(
            success=True,
            output=best.output,
            total_execution_time_ms=sum(r.execution_time_ms for r in results),
            avg_confidence=avg_confidence,
            total_citations=all_citations,
            method_used=AggregationMethod.BEST,
            sources=[best.execution_id],
        )
    
    def _aggregate_all(self, results: list[ExecutionResult]) -> AggregatedResult:
        """Retorna todos los resultados."""
        
        outputs = [r.output for r in results if r.success]
        errors = [r.error for r in results if r.error]
        
        return AggregatedResult(
            success=any(r.success for r in results),
            output={"_all_results": outputs},
            total_execution_time_ms=sum(r.execution_time_ms for r in results),
            avg_confidence=sum(r.confidence for r in results) / len(results) if results else 0,
            total_citations=[c for r in results for c in r.citations],
            method_used=AggregationMethod.ALL,
            sources=[r.execution_id for r in results],
            errors=errors,
        )
    
    async def _aggregate_merge(
        self,
        results: list[ExecutionResult],
        shared_context: dict,
    ) -> AggregatedResult:
        """Fusiona todos los resultados."""
        
        merged = {}
        all_citations = []
        total_time = 0
        total_confidence = 0.0
        success_count = 0
        
        for result in results:
            total_time += result.execution_time_ms
            total_confidence += result.confidence
            all_citations.extend(result.citations)
            
            if result.success:
                success_count += 1
                # Merge profundo
                merged = self._deep_merge(merged, result.output)
        
        return AggregatedResult(
            success=success_count > 0,
            output=merged,
            total_execution_time_ms=total_time,
            avg_confidence=total_confidence / len(results) if results else 0,
            total_citations=all_citations,
            method_used=AggregationMethod.MERGE,
            sources=[r.execution_id for r in results if r.success],
        )
    
    def _aggregate_vote(self, results: list[ExecutionResult]) -> AggregatedResult:
        """
        Votación entre resultados.
        
        Para campos discretos, cuenta votos.
        """
        
        # Agrupar por key
        votes: dict[str, dict[Any, int]] = {}
        
        for result in results:
            if not result.success:
                continue
            
            for key, value in result.output.items():
                if key.startswith("_"):
                    continue
                
                if key not in votes:
                    votes[key] = {}
                
                # Usar string del valor como key de votación
                value_str = str(value)
                votes[key][value_str] = votes[key].get(value_str, 0) + 1
        
        # Seleccionar valor con más votos
        final_output = {}
        conflicts = []
        
        for key, value_counts in votes.items():
            if not value_counts:
                continue
            
            winner = max(value_counts.items(), key=lambda x: x[1])
            final_output[key] = winner[0]
            
            # Detectar conflicto si hay empate o poca diferencia
            total_votes = sum(value_counts.values())
            if len(value_counts) > 1:
                top_votes = sorted(value_counts.values(), reverse=True)[:2]
                if top_votes[0] - top_votes[1] < total_votes * 0.2:
                    conflicts.append({
                        "field": key,
                        "options": list(value_counts.keys()),
                        "winning": winner[0],
                    })
        
        return AggregatedResult(
            success=len(final_output) > 0,
            output=final_output,
            total_execution_time_ms=sum(r.execution_time_ms for r in results),
            avg_confidence=sum(r.confidence for r in results) / len(results) if results else 0,
            method_used=AggregationMethod.VOTE,
            sources=[r.execution_id for r in results if r.success],
            conflicts=conflicts,
        )
    
    async def _aggregate_weighted(
        self,
        results: list[ExecutionResult],
    ) -> AggregatedResult:
        """Agregación ponderada."""
        
        weights = self.config.weights
        
        # Si no hay pesos, usar confianza como peso
        if not weights:
            weights = {
                r.execution_id: r.confidence
                for r in results if r.success
            }
        
        total_weight = sum(weights.values())
        
        if total_weight == 0:
            return self._aggregate_best(results)
        
        # Merge ponderado para valores numéricos
        merged = {}
        numeric_fields: dict[str, tuple[float, float]] = {}  # field -> (weighted_sum, weight_sum)
        
        for result in results:
            if not result.success:
                continue
            
            weight = weights.get(result.execution_id, 1.0)
            
            for key, value in result.output.items():
                if isinstance(value, (int, float)):
                    if key not in numeric_fields:
                        numeric_fields[key] = (0.0, 0.0)
                    current_sum, current_weight = numeric_fields[key]
                    numeric_fields[key] = (
                        current_sum + value * weight,
                        current_weight + weight,
                    )
                else:
                    # Para no numéricos, usar el de mayor peso
                    if key not in merged:
                        merged[key] = value
        
        # Calcular promedios ponderados
        for key, (weighted_sum, weight_sum) in numeric_fields.items():
            if weight_sum > 0:
                merged[key] = weighted_sum / weight_sum
        
        return AggregatedResult(
            success=len(merged) > 0,
            output=merged,
            total_execution_time_ms=sum(r.execution_time_ms for r in results),
            avg_confidence=sum(r.confidence for r in results) / len(results) if results else 0,
            total_citations=[c for r in results for c in r.citations],
            method_used=AggregationMethod.WEIGHTED,
            sources=[r.execution_id for r in results if r.success],
        )
    
    def _deep_merge(
        self,
        base: dict,
        update: dict,
    ) -> dict:
        """Merge profundo de diccionarios."""
        
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del aggregator."""
        
        return {
            "method_used": self.config.method.value,
            "min_confidence": self.config.min_confidence,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ResponseAggregator",
    "AggregationConfig",
    "AggregatedResult",
]
