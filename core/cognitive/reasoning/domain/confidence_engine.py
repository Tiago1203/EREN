"""Confidence Engine - calculates confidence scores for AI responses."""
from dataclasses import dataclass

from core.cognitive.reasoning.domain.entities import ReasoningResult
from core.cognitive.rag.domain.entities import Evidence
from core.cognitive.conversation.domain.value_objects import ConfidenceScore, ConfidenceLevel


@dataclass
class ConfidenceConfig:
    """Configuration for confidence calculation."""
    evidence_weight: float = 0.4
    consistency_weight: float = 0.2
    coverage_weight: float = 0.2
    recency_weight: float = 0.2
    
    low_evidence_threshold: float = 0.3
    conflicting_threshold: float = 0.2
    outdated_threshold_days: int = 365


class ConfidenceEngine:
    """
    Calculates confidence scores for AI responses.
    
    Uses multiple signals to determine how confident the AI should be
    in its response:
    - Evidence quality (relevance, source quality)
    - Consistency (internal consistency, citation alignment)
    - Coverage (query aspects covered by evidence)
    - Recency (information freshness)
    """
    
    def __init__(self, config: ConfidenceConfig | None = None):
        self.config = config or ConfidenceConfig()
    
    async def calculate(
        self,
        reasoning_result: ReasoningResult,
        evidence: Evidence,
    ) -> ConfidenceScore:
        """
        Calculate confidence score for a reasoning result.
        
        Args:
            reasoning_result: The result from the reasoning engine
            evidence: The evidence retrieved from RAG
        
        Returns:
            ConfidenceScore with overall and component scores
        """
        # Calculate component scores
        evidence_score = self._calculate_evidence_score(evidence)
        consistency_score = self._calculate_consistency_score(reasoning_result, evidence)
        coverage_score = self._calculate_coverage_score(reasoning_result, evidence)
        recency_score = self._calculate_recency_score(evidence)
        
        # Calculate overall score (weighted average)
        overall = (
            evidence_score * self.config.evidence_weight +
            consistency_score * self.config.consistency_weight +
            coverage_score * self.config.coverage_weight +
            recency_score * self.config.recency_weight
        )
        
        # Check for special conditions
        low_evidence = evidence_score < self.config.low_evidence_threshold
        conflicting_sources = self._has_conflicting_sources(evidence)
        outdated = recency_score < 0.5
        
        # Generate summary
        summary = self._generate_summary(
            evidence_score, consistency_score, coverage_score, recency_score,
            low_evidence, conflicting_sources, outdated
        )
        
        return ConfidenceScore(
            overall=overall,
            evidence_score=evidence_score,
            consistency_score=consistency_score,
            coverage_score=coverage_score,
            recency_score=recency_score,
            low_evidence=low_evidence,
            conflicting_sources=conflicting_sources,
            outdated_information=outdated,
            summary=summary,
        )
    
    def _calculate_evidence_score(self, evidence: Evidence) -> float:
        """Calculate evidence quality score."""
        if not evidence.chunks:
            return 0.0
        
        # Average relevance of top chunks
        top_chunks = sorted(
            evidence.chunks,
            key=lambda c: c.relevance_score,
            reverse=True
        )[:5]
        
        if not top_chunks:
            return 0.0
        
        avg_relevance = sum(c.relevance_score for c in top_chunks) / len(top_chunks)
        
        # Penalize for low number of sources
        source_count_factor = min(evidence.total_sources / 3, 1.0)
        
        return avg_relevance * source_count_factor
    
    def _calculate_consistency_score(
        self,
        reasoning_result: ReasoningResult,
        evidence: Evidence,
    ) -> float:
        """Calculate internal consistency score."""
        # Check if citations in response match evidence
        cited_sources = set(reasoning_result.citations)
        available_sources = set(c.source_id for c in evidence.chunks)
        
        if not cited_sources:
            # No citations = assume consistent
            return 0.8
        
        overlap = len(cited_sources & available_sources)
        total_cited = len(cited_sources)
        
        if total_cited == 0:
            return 0.8
        
        return overlap / total_cited
    
    def _calculate_coverage_score(
        self,
        reasoning_result: ReasoningResult,
        evidence: Evidence,
    ) -> float:
        """Calculate coverage score (how much of query is answered)."""
        # Simple heuristic: based on evidence chunks
        if not evidence.chunks:
            return 0.0
        
        # More chunks = better coverage (up to a point)
        chunk_count = len(evidence.chunks)
        if chunk_count >= 5:
            return 0.9
        elif chunk_count >= 3:
            return 0.7
        elif chunk_count >= 1:
            return 0.5
        return 0.2
    
    def _calculate_recency_score(self, evidence: Evidence) -> float:
        """Calculate recency score (information freshness)."""
        if not evidence.chunks:
            return 0.5
        
        # In production, would check metadata for timestamps
        # For now, assume reasonable freshness
        return 0.8
    
    def _has_conflicting_sources(self, evidence: Evidence) -> bool:
        """Check for conflicting information in sources."""
        # Simple check: very different relevance scores might indicate conflict
        if len(evidence.chunks) < 2:
            return False
        
        scores = [c.relevance_score for c in evidence.chunks]
        max_score = max(scores)
        min_score = min(scores)
        
        return (max_score - min_score) > 0.7
    
    def _generate_summary(
        self,
        evidence_score: float,
        consistency_score: float,
        coverage_score: float,
        recency_score: float,
        low_evidence: bool,
        conflicting_sources: bool,
        outdated: bool,
    ) -> str:
        """Generate human-readable summary."""
        issues = []
        
        if low_evidence:
            issues.append("limited evidence available")
        if conflicting_sources:
            issues.append("sources provide conflicting information")
        if outdated:
            issues.append("information may be outdated")
        
        if not issues:
            return "High confidence in response quality."
        
        return f"Consider verifying: {'; '.join(issues)}."
    
    def should_include_warning(self, confidence: ConfidenceScore) -> bool:
        """Determine if confidence warning should be shown to user."""
        return (
            confidence.level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]
            or confidence.low_evidence
            or confidence.conflicting_sources
        )


def create_confidence_engine(config: ConfidenceConfig | None = None) -> ConfidenceEngine:
    """Create a confidence engine."""
    return ConfidenceEngine(config=config)
