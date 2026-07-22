"""
Ambiguity Detector Module

Exports for ambiguity detection.
"""

from dataclasses import dataclass
from enum import Enum


class AmbiguityType(Enum):
    """Types of ambiguity."""
    SEMANTIC = "semantic"
    EVIDENTIAL = "evidential"
    REASONING = "reasoning"


@dataclass
class AmbiguityReport:
    """Ambiguity detection result."""
    is_ambiguous: bool
    ambiguity_types: list[str]
    conflicting_interpretations: list[str]
    clarification_needed: list[str]
    confidence_impact: float
    
    @property
    def needs_human_review(self) -> bool:
        """Check if human review is needed."""
        return self.is_ambiguous and self.confidence_impact > 0.2


class AmbiguityDetector:
    """Detects ambiguity in reasoning and evidence."""
    
    def __init__(self):
        self._vague_terms = {
            "maybe", "perhaps", "possibly", "might", "could",
            "unclear", "unclear", "unusual", "abnormal", "odd"
        }
        self._comparison_terms = {"more", "less", "higher", "lower", "better", "worse"}
    
    def detect(
        self,
        hypothesis: dict,
        evidence_bundle: dict,
        reasoning_chain: dict,
    ) -> AmbiguityReport:
        """Detect ambiguity in the analysis."""
        
        ambiguity_types = []
        conflicting_interpretations = []
        clarification_needed = []
        
        # Semantic ambiguity
        semantic_ambiguity = self._detect_semantic_ambiguity(hypothesis)
        if semantic_ambiguity:
            ambiguity_types.append(AmbiguityType.SEMANTIC.value)
            clarification_needed.extend(semantic_ambiguity)
        
        # Evidential ambiguity
        evidential_ambiguity = self._detect_evidential_ambiguity(evidence_bundle)
        if evidential_ambiguity:
            ambiguity_types.append(AmbiguityType.EVIDENTIAL.value)
            conflicting_interpretations.extend(evidential_ambiguity)
        
        # Reasoning ambiguity
        reasoning_ambiguity = self._detect_reasoning_ambiguity(reasoning_chain)
        if reasoning_ambiguity:
            ambiguity_types.append(AmbiguityType.REASONING.value)
            clarification_needed.extend(reasoning_ambiguity)
        
        # Calculate confidence impact
        confidence_impact = self._calculate_confidence_impact(
            ambiguity_types, conflicting_interpretations, clarification_needed
        )
        
        is_ambiguous = len(ambiguity_types) > 0
        
        return AmbiguityReport(
            is_ambiguous=is_ambiguous,
            ambiguity_types=ambiguity_types,
            conflicting_interpretations=conflicting_interpretations,
            clarification_needed=clarification_needed,
            confidence_impact=confidence_impact,
        )
    
    def _detect_semantic_ambiguity(self, hypothesis: dict) -> list[str]:
        """Detect semantic ambiguity in hypothesis."""
        issues = []
        
        description = hypothesis.get("description", "").lower()
        name = hypothesis.get("name", "").lower()
        combined = description + " " + name
        
        # Check for vague terms
        vague_found = [term for term in self._vague_terms if term in combined]
        if vague_found:
            issues.append(
                f"Vague terminology detected: {', '.join(vague_found)}"
            )
        
        # Check for relative comparisons
        comparisons_found = [
            term for term in self._comparison_terms 
            if term in combined
        ]
        if comparisons_found and not hypothesis.get("specific_value"):
            issues.append(
                f"Relative comparisons without specifics: {', '.join(comparisons_found)}"
            )
        
        return issues
    
    def _detect_evidential_ambiguity(
        self,
        evidence_bundle: dict,
    ) -> list[str]:
        """Detect evidential ambiguity (conflicting evidence)."""
        conflicts = []
        
        supporting = evidence_bundle.get("supporting", [])
        contradicting = evidence_bundle.get("contradicting", [])
        
        # Significant contradicting evidence
        if len(contradicting) > 0 and len(contradicting) >= len(supporting) * 0.3:
            conflicts.append(
                f"Contradicting evidence: {len(contradicting)} items "
                f"vs {len(supporting)} supporting"
            )
        
        # Conflicting sources
        if supporting:
            sources = [e.get("source_type") for e in supporting]
            if len(set(sources)) > 3:
                conflicts.append(
                    "Multiple conflicting source types detected"
                )
        
        return conflicts
    
    def _detect_reasoning_ambiguity(self, reasoning_chain: dict) -> list[str]:
        """Detect ambiguity in reasoning chain."""
        issues = []
        
        steps = reasoning_chain.get("steps", [])
        
        # Check for gaps in reasoning
        if len(steps) < 2:
            issues.append(
                "Limited reasoning chain - may be missing steps"
            )
        
        # Check for alternative paths not explored
        alternatives = reasoning_chain.get("alternatives", [])
        if not alternatives and len(steps) > 1:
            issues.append(
                "No alternative explanations considered"
            )
        
        # Check for unsupported conclusions
        for i, step in enumerate(steps):
            if step.get("type") == "conclusion" and not step.get("supported"):
                issues.append(
                    f"Step {i+1}: Conclusion lacks supporting premises"
                )
        
        return issues
    
    def _calculate_confidence_impact(
        self,
        types: list[str],
        conflicts: list[str],
        clarifications: list[str],
    ) -> float:
        """Calculate how much ambiguity impacts confidence."""
        impact = 0.0
        
        # Type-based impact
        type_impact = {
            AmbiguityType.SEMANTIC.value: 0.1,
            AmbiguityType.EVIDENTIAL.value: 0.15,
            AmbiguityType.REASONING.value: 0.1,
        }
        
        for t in types:
            impact += type_impact.get(t, 0.1)
        
        # Conflict-based impact
        impact += len(conflicts) * 0.1
        
        # Clarification-based impact
        impact += len(clarifications) * 0.05
        
        return min(impact, 0.5)
    
    def generate_clarification_questions(
        self,
        report: AmbiguityReport,
    ) -> list[str]:
        """Generate questions to clarify ambiguity."""
        questions = []
        
        for clarification in report.clarification_needed:
            if "vague" in clarification.lower():
                questions.append(
                    "Can you provide more specific details about the symptom?"
                )
            elif "relative" in clarification.lower():
                questions.append(
                    "What are the specific values or measurements?"
                )
            elif "missing steps" in clarification.lower():
                questions.append(
                    "What intermediate steps lead to this conclusion?"
                )
            elif "alternative" in clarification.lower():
                questions.append(
                    "What other possible explanations should be considered?"
                )
        
        for conflict in report.conflicting_interpretations:
            questions.append(
                f"How should we resolve: {conflict}"
            )
        
        return questions


__all__ = [
    "AmbiguityType",
    "AmbiguityReport",
    "AmbiguityDetector",
]
