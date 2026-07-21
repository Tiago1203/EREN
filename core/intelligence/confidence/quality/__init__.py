"""
Quality Evaluator Module

Exports for quality evaluation.
"""

from enum import Enum
from dataclasses import dataclass


class QualityDimension(Enum):
    """Dimensions of quality."""
    EVIDENCE_QUALITY = "evidence_quality"
    REASONING_QUALITY = "reasoning_quality"
    OUTPUT_QUALITY = "output_quality"
    KNOWLEDGE_QUALITY = "knowledge_quality"
    COVERAGE_QUALITY = "coverage_quality"


@dataclass
class QualityScore:
    """Quality evaluation result."""
    overall_quality: float
    dimensions: dict[QualityDimension, float]
    issues: list[str]
    strengths: list[str]
    
    @property
    def is_acceptable(self) -> bool:
        """Check if quality is acceptable."""
        return self.overall_quality >= 0.6


@dataclass
class QualityIssue:
    """Individual quality issue."""
    issue_id: str
    dimension: QualityDimension
    severity: str
    description: str
    recommendation: str


class QualityEvaluator:
    """Evaluates quality of evidence and reasoning."""
    
    def evaluate(
        self,
        evidence_bundle: dict,
        reasoning_chain: dict,
        output: dict,
    ) -> QualityScore:
        """Evaluate overall quality."""
        
        # Evaluate dimensions
        evidence_quality = self._evaluate_evidence_quality(evidence_bundle)
        reasoning_quality = self._evaluate_reasoning_quality(reasoning_chain)
        output_quality = self._evaluate_output_quality(output)
        
        dimensions = {
            QualityDimension.EVIDENCE_QUALITY: evidence_quality,
            QualityDimension.REASONING_QUALITY: reasoning_quality,
            QualityDimension.OUTPUT_QUALITY: output_quality,
        }
        
        # Calculate overall
        overall = sum(dimensions.values()) / len(dimensions)
        
        # Identify issues and strengths
        issues = self._identify_issues(dimensions)
        strengths = self._identify_strengths(dimensions)
        
        return QualityScore(
            overall_quality=overall,
            dimensions=dimensions,
            issues=issues,
            strengths=strengths,
        )
    
    def _evaluate_evidence_quality(self, bundle: dict) -> float:
        """Evaluate evidence quality."""
        supporting = bundle.get("supporting", [])
        
        if not supporting:
            return 0.2
        
        # Source quality
        quality_scores = [e.get("quality_score", 0.5) for e in supporting]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Diversity bonus
        sources = set(e.get("source_type") for e in supporting)
        diversity_bonus = min(len(sources) / 3, 0.1)
        
        return min(avg_quality + diversity_bonus, 1.0)
    
    def _evaluate_reasoning_quality(self, chain: dict) -> float:
        """Evaluate reasoning quality."""
        steps = chain.get("steps", [])
        
        if not steps:
            return 0.3
        
        # Premise support
        supported = sum(1 for s in steps if s.get("supported", False))
        support_ratio = supported / len(steps)
        
        # Chain length penalty
        length_penalty = max(0, (len(steps) - 7) * 0.02)
        
        return max(0.0, min(support_ratio - length_penalty + 0.3, 1.0))
    
    def _evaluate_output_quality(self, output: dict) -> float:
        """Evaluate output quality."""
        # Completeness
        has_recommendation = bool(output.get("recommendation"))
        has_rationale = bool(output.get("rationale"))
        has_evidence = bool(output.get("evidence"))
        
        completeness = sum([has_recommendation, has_rationale, has_evidence]) / 3
        
        # Clarity (placeholder)
        clarity = 0.8
        
        return (completeness + clarity) / 2
    
    def _identify_issues(
        self,
        dimensions: dict[QualityDimension, float],
    ) -> list[str]:
        """Identify quality issues."""
        issues = []
        
        for dim, score in dimensions.items():
            if score < 0.5:
                issues.append(
                    f"{dim.value}: Score is {score:.0%} - below acceptable threshold"
                )
        
        return issues
    
    def _identify_strengths(
        self,
        dimensions: dict[QualityDimension, float],
    ) -> list[str]:
        """Identify quality strengths."""
        strengths = []
        
        for dim, score in dimensions.items():
            if score >= 0.8:
                strengths.append(f"{dim.value}: Strong at {score:.0%}")
        
        return strengths


__all__ = [
    "QualityDimension",
    "QualityScore",
    "QualityIssue",
    "QualityEvaluator",
]
