"""
PHASE 4 - EPIC 5: Fusion Module

Métodos de fusión para combinar resultados:
- Reciprocal Rank Fusion (RRF)
- Weighted Average
- Score Normalization
- CombSUM, CombMNZ
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import math


@dataclass
class FusionResult:
    """Resultado de fusión."""
    doc_id: str
    fused_score: float
    source_scores: dict[str, float] = field(default_factory=dict)
    source_ranks: dict[str, int] = field(default_factory=dict)
    source: str = ""  # Source of this result (e.g., "vector", "keyword")


class BaseFusionMethod(ABC):
    """Clase base para métodos de fusión."""
    
    @abstractmethod
    def fuse(
        self,
        result_lists: list[list[FusionResult]],
    ) -> list[FusionResult]:
        """Fusiona listas de resultados."""
        ...


class ReciprocalRankFusion(BaseFusionMethod):
    """Reciprocal Rank Fusion (RRF).
    
    RRF formula: score(d) = Σ 1 / (k + rank(d))
    
    donde k es un parámetro (típicamente 60).
    """
    
    def __init__(self, k: int = 60):
        self.k = k
    
    def fuse(
        self,
        result_lists: list[list[FusionResult]],
    ) -> list[FusionResult]:
        """Fusiona usando RRF."""
        # Combine all results
        combined: dict[str, dict] = {}
        
        for results in result_lists:
            for rank, result in enumerate(results, 1):
                doc_id = result.doc_id
                
                if doc_id not in combined:
                    combined[doc_id] = {
                        "source_scores": {},
                        "source_ranks": {},
                        "rrf_score": 0.0,
                    }
                
                # Add RRF contribution
                combined[doc_id]["rrf_score"] += 1 / (self.k + rank)
                combined[doc_id]["source_scores"][result.source] = result.fused_score
                combined[doc_id]["source_ranks"][result.source] = rank
        
        # Convert back to FusionResult
        fused = [
            FusionResult(
                doc_id=doc_id,
                fused_score=data["rrf_score"],
                source_scores=data["source_scores"],
                source_ranks=data["source_ranks"],
            )
            for doc_id, data in combined.items()
        ]
        
        # Sort by fused score
        fused.sort(key=lambda r: r.fused_score, reverse=True)
        
        return fused


class WeightedAverageFusion(BaseFusionMethod):
    """Fusión por promedio ponderado de scores."""
    
    def __init__(self, weights: dict[str, float] | None = None):
        """
        Args:
            weights: Diccionario de pesos por fuente.
                     Si es None, usa pesos uniformes.
        """
        self.weights = weights or {}
    
    def fuse(
        self,
        result_lists: list[list[FusionResult]],
    ) -> list[FusionResult]:
        """Fusiona usando promedio ponderado."""
        # Normalize weights
        total_weight = sum(self.weights.values()) if self.weights else len(result_lists)
        
        if total_weight == 0:
            return []
        
        # Normalize to 0-1 range
        normalized_weights = {
            source: w / total_weight
            for source, w in self.weights.items()
        }
        
        # If no weights, use uniform
        use_uniform = not self.weights
        
        # Combine all results
        combined: dict[str, dict] = {}
        
        for results in result_lists:
            for rank, result in enumerate(results, 1):
                doc_id = result.doc_id
                
                if doc_id not in combined:
                    combined[doc_id] = {
                        "source_scores": {},
                        "source_ranks": {},
                        "weighted_score": 0.0,
                        "count": 0,
                    }
                
                combined[doc_id]["source_scores"][result.source] = result.fused_score
                combined[doc_id]["source_ranks"][result.source] = rank
                
                # Apply weight
                if use_uniform:
                    weight = 1.0 / len(result_lists)
                else:
                    weight = normalized_weights.get(result.source, 0)
                
                combined[doc_id]["weighted_score"] += result.fused_score * weight
                combined[doc_id]["count"] += 1
        
        # Convert back to FusionResult
        fused = [
            FusionResult(
                doc_id=doc_id,
                fused_score=data["weighted_score"],
                source_scores=data["source_scores"],
                source_ranks=data["source_ranks"],
            )
            for doc_id, data in combined.items()
        ]
        
        # Sort by fused score
        fused.sort(key=lambda r: r.fused_score, reverse=True)
        
        return fused


class CombSUMFusion(BaseFusionMethod):
    """CombSUM - Suma de scores normalizados.
    
    Normaliza scores a rango [0, 1] y luego los suma.
    """
    
    def __init__(self, min_score: float = 0.0, max_score: float = 1.0):
        self.min_score = min_score
        self.max_score = max_score
    
    def fuse(
        self,
        result_lists: list[list[FusionResult]],
    ) -> list[FusionResult]:
        """Fusiona usando CombSUM."""
        # Combine all results
        combined: dict[str, dict] = {}
        
        for results in result_lists:
            if not results:
                continue
            
            # Find min/max for normalization
            scores = [r.fused_score for r in results]
            min_s = min(scores) if scores else 0
            max_s = max(scores) if scores else 1
            
            for result in results:
                doc_id = result.doc_id
                
                if doc_id not in combined:
                    combined[doc_id] = {
                        "source_scores": {},
                        "source_ranks": {},
                        "sum_score": 0.0,
                    }
                
                # Normalize to [0, 1]
                range_s = max_s - min_s if max_s != min_s else 1
                normalized = (result.fused_score - min_s) / range_s
                
                combined[doc_id]["source_scores"][result.source] = result.fused_score
                combined[doc_id]["sum_score"] += normalized
        
        # Convert back to FusionResult
        fused = [
            FusionResult(
                doc_id=doc_id,
                fused_score=data["sum_score"],
                source_scores=data["source_scores"],
                source_ranks={},  # Not tracked in CombSUM
            )
            for doc_id, data in combined.items()
        ]
        
        # Sort by fused score
        fused.sort(key=lambda r: r.fused_score, reverse=True)
        
        return fused


class CombMNZFusion(BaseFusionMethod):
    """CombMNZ - CombSUM con factor de cantidad.
    
    Multiplica la suma por el número de fuentes que recuperaron el documento.
    """
    
    def fuse(
        self,
        result_lists: list[list[FusionResult]],
    ) -> list[FusionResult]:
        """Fusiona usando CombMNZ."""
        # Combine all results
        combined: dict[str, dict] = {}
        
        for results in result_lists:
            if not results:
                continue
            
            scores = [r.fused_score for r in results]
            min_s = min(scores) if scores else 0
            max_s = max(scores) if scores else 1
            
            for result in results:
                doc_id = result.doc_id
                
                if doc_id not in combined:
                    combined[doc_id] = {
                        "source_scores": {},
                        "sum_score": 0.0,
                        "count": 0,
                    }
                
                range_s = max_s - min_s if max_s != min_s else 1
                normalized = (result.fused_score - min_s) / range_s
                
                combined[doc_id]["source_scores"][result.source] = result.fused_score
                combined[doc_id]["sum_score"] += normalized
                combined[doc_id]["count"] += 1
        
        # Apply MNZ factor
        for doc_id in combined:
            combined[doc_id]["sum_score"] *= combined[doc_id]["count"]
        
        # Convert back to FusionResult
        fused = [
            FusionResult(
                doc_id=doc_id,
                fused_score=data["sum_score"],
                source_scores=data["source_scores"],
                source_ranks={},
            )
            for doc_id, data in combined.items()
        ]
        
        # Sort by fused score
        fused.sort(key=lambda r: r.fused_score, reverse=True)
        
        return fused


class ScoreNormalizer:
    """Normalizador de scores a rango [0, 1]."""
    
    @staticmethod
    def min_max_normalize(scores: list[float]) -> list[float]:
        """Normaliza usando min-max."""
        if not scores:
            return []
        
        min_s = min(scores)
        max_s = max(scores)
        
        if max_s == min_s:
            return [0.5] * len(scores)
        
        return [(s - min_s) / (max_s - min_s) for s in scores]
    
    @staticmethod
    def z_score_normalize(scores: list[float]) -> list[float]:
        """Normaliza usando z-score."""
        if not scores:
            return []
        
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std = math.sqrt(variance)
        
        if std == 0:
            return [0.5] * len(scores)
        
        # Clamp to reasonable range
        normalized = [(s - mean) / std for s in scores]
        # Map to [0, 1] using sigmoid approximation
        return [max(0, min(1, (z + 3) / 6 + 0.5)) for z in normalized]


class HybridRanker:
    """Ranker híbrido que combina múltiples métodos."""
    
    def __init__(
        self,
        fusion_methods: list[BaseFusionMethod] | None = None,
    ):
        self.fusion_methods = fusion_methods or [
            ReciprocalRankFusion(k=60),
            WeightedAverageFusion(),
        ]
    
    def rank(
        self,
        result_lists: list[list[FusionResult]],
    ) -> dict[str, list[FusionResult]]:
        """Ranking usando múltiples métodos de fusión."""
        results = {}
        
        for method in self.fusion_methods:
            method_name = method.__class__.__name__
            results[method_name] = method.fuse(result_lists)
        
        return results


__all__ = [
    "FusionResult",
    "BaseFusionMethod",
    "ReciprocalRankFusion",
    "WeightedAverageFusion",
    "CombSUMFusion",
    "CombMNZFusion",
    "ScoreNormalizer",
    "HybridRanker",
]
