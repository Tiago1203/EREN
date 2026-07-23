"""
PHASE 4 - EPIC 8: Quality Module

Análisis de calidad:
- Quality Analyzer
- Quality Score
- Quality Report
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

# Import unified QualityDimension from PHASE_3 (IMP-001 fix)
from core.PHASE_3.intelligence.foundation.enums import QualityDimension


class QualityLevel(str, Enum):
    """Niveles de calidad."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class QualityScore:
    """Score de calidad."""
    overall: float
    accuracy: float = 0.0
    completeness: float = 0.0
    consistency: float = 0.0
    currency: float = 0.0
    relevance: float = 0.0
    
    level: QualityLevel = QualityLevel.FAIR
    
    def __post_init__(self):
        if self.overall >= 0.9:
            self.level = QualityLevel.EXCELLENT
        elif self.overall >= 0.75:
            self.level = QualityLevel.GOOD
        elif self.overall >= 0.5:
            self.level = QualityLevel.FAIR
        elif self.overall >= 0.25:
            self.level = QualityLevel.POOR
        else:
            self.level = QualityLevel.UNACCEPTABLE


@dataclass
class QualityReport:
    """Reporte de calidad."""
    source_id: str
    score: QualityScore
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    
    created_at: str = ""
    is_acceptable: bool = True
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.is_acceptable = self.score.level not in (
            QualityLevel.POOR,
            QualityLevel.UNACCEPTABLE,
        )


class BaseQualityAnalyzer(ABC):
    """Clase base para analizadores de calidad."""
    
    @abstractmethod
    def analyze(self, evidence_item: dict) -> QualityReport:
        """Analiza calidad de evidencia."""
        ...


class ClinicalQualityAnalyzer(BaseQualityAnalyzer):
    """Analizador de calidad clínica."""
    
    def __init__(self):
        self._quality_thresholds = {
            QualityDimension.ACCURACY: 0.7,
            QualityDimension.COMPLETENESS: 0.6,
            QualityDimension.CONSISTENCY: 0.7,
            QualityDimension.CURRENCY: 0.5,
            QualityDimension.RELEVANCE: 0.6,
        }
    
    def analyze(self, evidence_item: dict) -> QualityReport:
        """Analiza calidad de evidencia clínica."""
        source_id = evidence_item.get("id", "unknown")
        
        # Calculate dimension scores
        accuracy = self._assess_accuracy(evidence_item)
        completeness = self._assess_completeness(evidence_item)
        consistency = self._assess_consistency(evidence_item)
        currency = self._assess_currency(evidence_item)
        relevance = self._assess_relevance(evidence_item)
        
        # Calculate overall
        overall = (
            accuracy * 0.3 +
            completeness * 0.2 +
            consistency * 0.2 +
            currency * 0.1 +
            relevance * 0.2
        )
        
        score = QualityScore(
            overall=overall,
            accuracy=accuracy,
            completeness=completeness,
            consistency=consistency,
            currency=currency,
            relevance=relevance,
        )
        
        # Generate issues and warnings
        issues, warnings = self._identify_issues(evidence_item, score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(score)
        
        return QualityReport(
            source_id=source_id,
            score=score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
        )
    
    def _assess_accuracy(self, evidence: dict) -> float:
        """Evalúa exactitud."""
        metadata = evidence.get("metadata", {})
        
        # Peer-reviewed sources are more accurate
        if metadata.get("peer_reviewed"):
            return 0.9
        
        # Manufacturer docs
        if metadata.get("manufacturer_doc"):
            return 0.6
        
        # General content
        return 0.5
    
    def _assess_completeness(self, evidence: dict) -> float:
        """Evalúa completitud."""
        metadata = evidence.get("metadata", {})
        
        score = 0.5
        
        # Check for required fields
        if metadata.get("title"):
            score += 0.1
        if metadata.get("authors"):
            score += 0.1
        if metadata.get("date"):
            score += 0.1
        if metadata.get("doi") or metadata.get("pmid"):
            score += 0.1
        if metadata.get("journal"):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_consistency(self, evidence: dict) -> float:
        """Evalúa consistencia."""
        # Check for contradictory information
        text = evidence.get("text", "")
        
        # Simple heuristic: check for negation words
        negations = ["but", "however", "although", "despite"]
        if any(neg in text.lower() for neg in negations):
            return 0.7
        
        return 0.8
    
    def _assess_currency(self, evidence: dict) -> float:
        """Evalúa actualidad."""
        metadata = evidence.get("metadata", {})
        date = metadata.get("date", metadata.get("publication_date", ""))
        
        if not date:
            return 0.4
        
        try:
            year = int(date[:4])
            current_year = datetime.now().year
            
            if current_year - year <= 2:
                return 0.95
            elif current_year - year <= 5:
                return 0.8
            elif current_year - year <= 10:
                return 0.6
            else:
                return 0.3
        except (ValueError, IndexError):
            return 0.5
    
    def _assess_relevance(self, evidence: dict) -> float:
        """Evalúa relevancia."""
        return evidence.get("score", 0.5)
    
    def _identify_issues(
        self,
        evidence: dict,
        score: QualityScore,
    ) -> tuple[list[str], list[str]]:
        """Identifica problemas."""
        issues = []
        warnings = []
        
        if score.accuracy < self._quality_thresholds[QualityDimension.ACCURACY]:
            issues.append("Low accuracy score")
        
        if score.completeness < 0.5:
            issues.append("Incomplete metadata")
        
        if score.currency < 0.5:
            warnings.append("Outdated source")
        
        metadata = evidence.get("metadata", {})
        if not metadata.get("doi") and not metadata.get("pmid"):
            warnings.append("Missing DOI or PMID")
        
        return issues, warnings
    
    def _generate_recommendations(self, score: QualityScore) -> list[str]:
        """Genera recomendaciones."""
        recommendations = []
        
        if score.accuracy < 0.7:
            recommendations.append("Consider using peer-reviewed sources")
        
        if score.completeness < 0.7:
            recommendations.append("Include more complete citations")
        
        if score.currency < 0.6:
            recommendations.append("Prioritize recent publications")
        
        return recommendations


__all__ = [
    "QualityLevel",
    "QualityDimension",
    "QualityScore",
    "QualityReport",
    "BaseQualityAnalyzer",
    "ClinicalQualityAnalyzer",
]
