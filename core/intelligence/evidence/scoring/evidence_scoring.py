"""
Evidence Scoring Module

Complete implementation for scoring and ranking evidence.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class ScoringMethod(Enum):
    """Methods for scoring evidence."""
    QUALITY_ONLY = "quality_only"
    RELEVANCE_ONLY = "relevance_only"
    WEIGHTED = "weighted"
    COMBINED = "combined"
    RECENCY_WEIGHTED = "recency_weighted"


@dataclass(frozen=True)
class EvidenceScore:
    """Scored evidence item."""
    evidence_id: str
    quality_score: float
    relevance_score: float
    recency_score: float
    combined_score: float
    breakdown: dict


class EvidenceScorer:
    """Scores evidence based on multiple factors."""
    
    def __init__(
        self,
        quality_weight: float = 0.4,
        relevance_weight: float = 0.4,
        recency_weight: float = 0.2,
    ):
        self.quality_weight = quality_weight
        self.relevance_weight = relevance_weight
        self.recency_weight = recency_weight
    
    def score(
        self,
        evidence_item,
        query: str | None = None,
    ) -> EvidenceScore:
        """Score a single evidence item."""
        # Quality score (based on source)
        quality_score = self._calculate_quality_score(evidence_item)
        
        # Relevance score (based on content match)
        relevance_score = self._calculate_relevance_score(evidence_item, query)
        
        # Recency score (based on timestamp)
        recency_score = self._calculate_recency_score(evidence_item)
        
        # Combined score
        combined_score = (
            quality_score * self.quality_weight +
            relevance_score * self.relevance_weight +
            recency_score * self.recency_weight
        )
        
        return EvidenceScore(
            evidence_id=evidence_item.evidence_id,
            quality_score=quality_score,
            relevance_score=relevance_score,
            recency_score=recency_score,
            combined_score=combined_score,
            breakdown={
                "quality_weight": self.quality_weight,
                "relevance_weight": self.relevance_weight,
                "recency_weight": self.recency_weight,
            },
        )
    
    def _calculate_quality_score(self, evidence_item) -> float:
        """Calculate quality score based on source type."""
        source_quality = {
            "knowledge_graph": 0.9,
            "standard": 1.0,
            "regulation": 1.0,
            "manual": 0.8,
            "guideline": 0.85,
            "literature": 0.9,
            "historical": 0.7,
            "incident_report": 0.75,
            "maintenance_log": 0.8,
        }
        
        source_type = evidence_item.source_type.value if hasattr(
            evidence_item.source_type, 'value'
        ) else str(evidence_item.source_type)
        
        base_score = source_quality.get(source_type, 0.5)
        
        # Adjust by explicit quality score if available
        if hasattr(evidence_item, 'quality_score'):
            base_score = (base_score + evidence_item.quality_score) / 2
        
        return min(base_score, 1.0)
    
    def _calculate_relevance_score(
        self,
        evidence_item,
        query: str | None,
    ) -> float:
        """Calculate relevance score based on content match."""
        if not query:
            return 0.5  # Neutral if no query
        
        query_words = set(query.lower().split())
        content_words = set(evidence_item.content.lower().split())
        
        # Jaccard similarity
        if not query_words or not content_words:
            return 0.5
        
        intersection = query_words & content_words
        union = query_words | content_words
        
        similarity = len(intersection) / len(union)
        
        return min(similarity * 2, 1.0)  # Scale up and cap at 1.0
    
    def _calculate_recency_score(self, evidence_item) -> float:
        """Calculate recency score based on timestamp."""
        if not evidence_item.timestamp:
            return 0.5  # Neutral if no timestamp
        
        # Days since evidence
        days_old = (datetime.now() - evidence_item.timestamp).days
        
        # Decay function
        if days_old < 30:
            return 1.0
        elif days_old < 180:
            return 0.8
        elif days_old < 365:
            return 0.6
        elif days_old < 730:
            return 0.4
        else:
            return 0.2


class EvidenceRanker:
    """Ranks evidence by score."""
    
    def __init__(self, scorer: EvidenceScorer | None = None):
        self.scorer = scorer or EvidenceScorer()
    
    def rank(
        self,
        evidence_items: list,
        query: str | None = None,
        method: ScoringMethod = ScoringMethod.COMBINED,
    ) -> list:
        """Rank evidence items by score."""
        scored = []
        
        for item in evidence_items:
            score = self.scorer.score(item, query)
            
            if method == ScoringMethod.QUALITY_ONLY:
                sort_score = score.quality_score
            elif method == ScoringMethod.RELEVANCE_ONLY:
                sort_score = score.relevance_score
            elif method == ScoringMethod.RECENCY_WEIGHTED:
                sort_score = score.recency_score
            else:
                sort_score = score.combined_score
            
            scored.append((item, score, sort_score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[2], reverse=True)
        
        return [item for item, _, _ in scored]
    
    def get_top_evidence(
        self,
        evidence_items: list,
        query: str | None = None,
        top_n: int = 10,
    ) -> list:
        """Get top N evidence items."""
        ranked = self.rank(evidence_items, query)
        return ranked[:top_n]


__all__ = [
    "ScoringMethod",
    "EvidenceScore",
    "EvidenceScorer",
    "EvidenceRanker",
]
