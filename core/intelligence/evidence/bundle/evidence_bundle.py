"""
Evidence Bundle Module

Complete implementation for bundling evidence with supporting
and contradicting evidence for clinical reasoning.

ARCHITECTURE NOTE:
ComplianceStatus is imported from core.intelligence.foundation.enums to ensure consistency.
EvidencePriority is a local enum specific to evidence bundling (different from foundation.Priority).
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# Import shared enum from SINGLE SOURCE OF TRUTH
from core.intelligence.foundation.enums import ComplianceStatus


class EvidencePriority(Enum):
    """Priority levels for evidence bundles (local - different from foundation.Priority)."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass(frozen=True)
class RuleMatch:
    """Match with a rule."""
    rule_id: str
    rule_name: str
    matched: bool
    conditions_met: list[str] = field(default_factory=list)
    conditions_not_met: list[str] = field(default_factory=list)
    action: Optional[str] = None
    priority: EvidencePriority = EvidencePriority.MEDIUM
    compliance_status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW


@dataclass(frozen=True)
class EvidenceSummary:
    """Summary of evidence bundle."""
    overall_confidence: float
    evidence_count: int
    supporting_count: int
    contradicting_count: int
    source_diversity: float
    recommendation: str
    compliance_status: ComplianceStatus


@dataclass(frozen=True)
class EvidenceBundle:
    """
    Complete evidence bundle for a hypothesis.
    """
    bundle_id: str
    hypothesis_id: str
    hypothesis_name: str
    supporting_evidence: list
    contradicting_evidence: list
    summary: EvidenceSummary
    rule_matches: list[RuleMatch]
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def overall_confidence(self) -> float:
        """Calculate overall confidence from evidence."""
        supporting_strength = sum(
            e.relevance_score * e.quality_score 
            for e in self.supporting_evidence
        ) if self.supporting_evidence else 0
        
        contradicting_strength = sum(
            e.relevance_score * e.quality_score 
            for e in self.contradicting_evidence
        ) if self.contradicting_evidence else 0
        
        total = supporting_strength + contradicting_strength
        if total == 0:
            return 0.5
        
        return supporting_strength / total
    
    @property
    def is_supportive(self) -> bool:
        """Check if evidence is mostly supportive."""
        return self.overall_confidence > 0.6


class EvidenceBundleGenerator:
    """Generates evidence bundles from evidence items."""
    
    def __init__(self):
        self._support_keywords = {
            "confirm", "support", "consistent", "matches", "agree",
            "corroborate", "validate", "verify", "confirm"
        }
        self._contradict_keywords = {
            "contradict", "refute", "disagree", "inconsistent", "oppose",
            "contrary", "different", "conflict"
        }
    
    async def generate(
        self,
        hypothesis_id: str,
        hypothesis_name: str,
        hypothesis_description: str,
        evidence_items: list,
    ) -> EvidenceBundle:
        """Generate an evidence bundle for a hypothesis."""
        # Separate supporting and contradicting
        supporting = []
        contradicting = []
        
        for evidence in evidence_items:
            if self._supports_hypothesis(
                evidence.content, hypothesis_name, hypothesis_description
            ):
                supporting.append(evidence)
            else:
                contradicting.append(evidence)
        
        # Calculate summary
        summary = self._calculate_summary(
            supporting, contradicting, hypothesis_name
        )
        
        return EvidenceBundle(
            bundle_id=f"bundle_{hypothesis_id}",
            hypothesis_id=hypothesis_id,
            hypothesis_name=hypothesis_name,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            summary=summary,
            rule_matches=[],
        )
    
    def _supports_hypothesis(
        self,
        evidence_content: str,
        hypothesis_name: str,
        hypothesis_description: str,
    ) -> bool:
        """Determine if evidence supports the hypothesis."""
        content_lower = evidence_content.lower()
        hypothesis_lower = hypothesis_name.lower()
        
        # Check for contradiction keywords
        for keyword in self._contradict_keywords:
            if keyword in content_lower:
                # Check if hypothesis keywords are present (might be clarification)
                if any(kw in hypothesis_lower for kw in ["sensor", "malfunction", "issue"]):
                    if "no" in content_lower or "not" in content_lower or "without" in content_lower:
                        return True
                return False
        
        # Check for support keywords
        for keyword in self._support_keywords:
            if keyword in content_lower:
                return True
        
        # Check for keyword overlap
        hypothesis_words = set(hypothesis_lower.split())
        evidence_words = set(content_lower.split())
        overlap = hypothesis_words & evidence_words
        
        return len(overlap) >= 2
    
    def _calculate_summary(
        self,
        supporting: list,
        contradicting: list,
        hypothesis_name: str,
    ) -> EvidenceSummary:
        """Calculate evidence summary."""
        evidence_count = len(supporting) + len(contradicting)
        
        # Source diversity
        sources = set()
        for e in supporting + contradicting:
            if hasattr(e, 'source_type'):
                sources.add(e.source_type.value)
        source_diversity = min(len(sources) / 5, 1.0)  # Normalize to 0-1
        
        # Recommendation
        if len(supporting) > len(contradicting) * 2:
            recommendation = f"Proceed with: {hypothesis_name}"
        elif len(contradicting) > len(supporting) * 2:
            recommendation = f"Reconsider: {hypothesis_name}"
        else:
            recommendation = f"Further investigation needed for: {hypothesis_name}"
        
        # Compliance status (using Foundation ComplianceStatus values)
        if not supporting:
            compliance = ComplianceStatus.NON_COMPLIANT  # WARNING -> NON_COMPLIANT
        elif not contradicting:
            compliance = ComplianceStatus.COMPLIANT
        else:
            compliance = ComplianceStatus.PENDING_REVIEW  # PENDING -> PENDING_REVIEW
        
        # Calculate confidence
        overall_confidence = self._calculate_confidence(supporting, contradicting)
        
        return EvidenceSummary(
            overall_confidence=overall_confidence,
            evidence_count=evidence_count,
            supporting_count=len(supporting),
            contradicting_count=len(contradicting),
            source_diversity=source_diversity,
            recommendation=recommendation,
            compliance_status=compliance,
        )
    
    def _calculate_confidence(
        self,
        supporting: list,
        contradicting: list,
    ) -> float:
        """Calculate confidence score."""
        supporting_strength = sum(
            e.relevance_score * e.quality_score 
            for e in supporting
        ) if supporting else 0
        
        contradicting_strength = sum(
            e.relevance_score * e.quality_score 
            for e in contradicting
        ) if contradicting else 0
        
        total = supporting_strength + contradicting_strength
        if total == 0:
            return 0.5
        
        return supporting_strength / total


class EvidenceBundleManager:
    """Manages multiple evidence bundles."""
    
    def __init__(self):
        self._bundles: dict[str, EvidenceBundle] = {}
    
    async def create_bundle(
        self,
        hypothesis_id: str,
        hypothesis_name: str,
        hypothesis_description: str,
        evidence_items: list,
    ) -> EvidenceBundle:
        """Create and store a bundle."""
        generator = EvidenceBundleGenerator()
        bundle = await generator.generate(
            hypothesis_id=hypothesis_id,
            hypothesis_name=hypothesis_name,
            hypothesis_description=hypothesis_description,
            evidence_items=evidence_items,
        )
        
        self._bundles[bundle.bundle_id] = bundle
        return bundle
    
    def get_bundle(self, bundle_id: str) -> EvidenceBundle | None:
        """Get a bundle by ID."""
        return self._bundles.get(bundle_id)
    
    def get_all_bundles(self) -> list[EvidenceBundle]:
        """Get all stored bundles."""
        return list(self._bundles.values())


__all__ = [
    # Imported from Foundation
    "ComplianceStatus",
    # Local enums
    "EvidencePriority",
    # Data classes
    "RuleMatch",
    "EvidenceSummary",
    "EvidenceBundle",
    "EvidenceBundleGenerator",
    "EvidenceBundleManager",
]
