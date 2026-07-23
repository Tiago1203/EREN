"""
PHASE 4 - EPIC 8: Ranking Module

Ranking de evidencia:
- Evidence Rank
- Ranking Engine
- Quality-Based Ranking
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EvidenceRank(str, Enum):
    """Rank de evidencia."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EXCLUDED = "excluded"


@dataclass
class RankedEvidence:
    """Evidencia con ranking."""
    source_id: str
    text: str
    
    # Scores
    original_score: float = 0.0
    quality_score: float = 0.0
    bias_score: float = 0.0
    relevance_score: float = 0.0
    final_score: float = 0.0
    
    # Rank
    rank: EvidenceRank = EvidenceRank.MEDIUM
    rank_position: int = 0
    
    # Metadata
    quality_report: dict | None = None
    bias_report: dict | None = None


class BaseRankingEngine(ABC):
    """Clase base para motores de ranking."""
    
    @abstractmethod
    def rank(self, evidence_items: list[dict]) -> list[RankedEvidence]:
        """Rankea evidencia."""
        ...


class QualityRankingEngine(BaseRankingEngine):
    """Motor de ranking basado en calidad."""
    
    def __init__(self):
        self._quality_weight = 0.4
        self._relevance_weight = 0.3
        self._bias_weight = 0.3
    
    def rank(self, evidence_items: list[dict]) -> list[RankedEvidence]:
        """Rankea evidencia."""
        ranked_list = []
        
        for item in evidence_items:
            # Get scores
            original_score = item.get("score", 0.5)
            quality_score = item.get("quality_score", 0.5)
            bias_score = 1.0 - item.get("bias_score", 0.0)  # Invert bias
            relevance_score = item.get("relevance_score", original_score)
            
            # Calculate final score
            final_score = (
                self._quality_weight * quality_score +
                self._relevance_weight * relevance_score +
                self._bias_weight * bias_score
            )
            
            # Determine rank
            rank = self._determine_rank(final_score)
            
            ranked = RankedEvidence(
                source_id=item.get("id", "unknown"),
                text=item.get("text", ""),
                original_score=original_score,
                quality_score=quality_score,
                bias_score=bias_score,
                relevance_score=relevance_score,
                final_score=final_score,
                rank=rank,
                quality_report=item.get("quality_report"),
                bias_report=item.get("bias_report"),
            )
            
            ranked_list.append(ranked)
        
        # Sort by final score
        ranked_list.sort(key=lambda x: x.final_score, reverse=True)
        
        # Assign positions
        for i, ranked in enumerate(ranked_list):
            ranked.rank_position = i + 1
        
        return ranked_list
    
    def _determine_rank(self, score: float) -> EvidenceRank:
        """Determina rank basado en score."""
        if score >= 0.75:
            return EvidenceRank.HIGH
        elif score >= 0.5:
            return EvidenceRank.MEDIUM
        elif score >= 0.25:
            return EvidenceRank.LOW
        else:
            return EvidenceRank.EXCLUDED


class ClinicalRankingEngine(BaseRankingEngine):
    """Motor de ranking clínico específico."""
    
    def __init__(self):
        self._quality_weight = 0.35
        self._evidence_level_weight = 0.25
        self._relevance_weight = 0.25
        self._bias_weight = 0.15
    
    def rank(self, evidence_items: list[dict]) -> list[RankedEvidence]:
        """Rankea evidencia clínica."""
        ranked_list = []
        
        for item in evidence_items:
            metadata = item.get("metadata", {})
            
            # Get scores
            original_score = item.get("score", 0.5)
            quality_score = item.get("quality_score", 0.5)
            bias_score = 1.0 - item.get("bias_score", 0.0)
            relevance_score = item.get("relevance_score", original_score)
            
            # Evidence level score (1-5 scale to 0-1)
            evidence_level = metadata.get("evidence_level", "3")
            try:
                level_num = int(evidence_level)
                evidence_level_score = max(0, 1 - (level_num - 1) / 4)
            except (ValueError, TypeError):
                evidence_level_score = 0.5
            
            # Calculate final score
            final_score = (
                self._quality_weight * quality_score +
                self._evidence_level_weight * evidence_level_score +
                self._relevance_weight * relevance_score +
                self._bias_weight * bias_score
            )
            
            # Clinical-specific rank
            rank = self._determine_clinical_rank(final_score, evidence_level_score)
            
            ranked = RankedEvidence(
                source_id=item.get("id", "unknown"),
                text=item.get("text", ""),
                original_score=original_score,
                quality_score=quality_score,
                bias_score=bias_score,
                relevance_score=relevance_score,
                final_score=final_score,
                rank=rank,
            )
            
            ranked_list.append(ranked)
        
        # Sort
        ranked_list.sort(key=lambda x: x.final_score, reverse=True)
        
        # Assign positions
        for i, ranked in enumerate(ranked_list):
            ranked.rank_position = i + 1
        
        return ranked_list
    
    def _determine_clinical_rank(
        self,
        score: float,
        evidence_level_score: float,
    ) -> EvidenceRank:
        """Determina rank clínico."""
        # Combine score and evidence level
        combined = (score + evidence_level_score) / 2
        
        if combined >= 0.7:
            return EvidenceRank.HIGH
        elif combined >= 0.5:
            return EvidenceRank.MEDIUM
        elif combined >= 0.3:
            return EvidenceRank.LOW
        else:
            return EvidenceRank.EXCLUDED


class DuplicateDetector:
    """Detector de duplicados."""
    
    def __init__(self, similarity_threshold: float = 0.9):
        self._threshold = similarity_threshold
    
    def find_duplicates(
        self,
        evidence_items: list[dict],
    ) -> list[tuple[str, str]]:
        """Encuentra duplicados."""
        duplicates = []
        processed = set()
        
        for i, item1 in enumerate(evidence_items):
            if item1["id"] in processed:
                continue
            
            for j, item2 in enumerate(evidence_items[i + 1:], i + 1):
                if item2["id"] in processed:
                    continue
                
                similarity = self._calculate_similarity(item1, item2)
                
                if similarity >= self._threshold:
                    duplicates.append((item1["id"], item2["id"]))
                    processed.add(item2["id"])
        
        return duplicates
    
    def _calculate_similarity(
        self,
        item1: dict,
        item2: dict,
    ) -> float:
        """Calcula similitud."""
        # Check same DOI or PMID
        meta1 = item1.get("metadata", {})
        meta2 = item2.get("metadata", {})
        
        if meta1.get("doi") and meta1.get("doi") == meta2.get("doi"):
            return 1.0
        
        if meta1.get("pmid") and meta1.get("pmid") == meta2.get("pmid"):
            return 1.0
        
        # Text similarity
        text1 = item1.get("text", "")[:500].lower()
        text2 = item2.get("text", "")[:500].lower()
        
        if text1 == text2:
            return 1.0
        
        # Word overlap
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


__all__ = [
    "EvidenceRank",
    "RankedEvidence",
    "BaseRankingEngine",
    "QualityRankingEngine",
    "ClinicalRankingEngine",
    "DuplicateDetector",
]
