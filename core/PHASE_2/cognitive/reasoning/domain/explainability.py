"""Explainability Engine - generates explanations for AI responses."""
from dataclasses import dataclass

from core.PHASE_2.cognitive.reasoning.domain.entities import ReasoningResult, ReasoningTrace
from core.PHASE_2.cognitive.rag.domain.entities import Evidence, RetrievedChunk
from core.PHASE_2.cognitive.conversation.domain.value_objects import ConfidenceScore


@dataclass
class Explanation:
    """A generated explanation for an AI response."""
    summary: str
    reasoning_steps: list[str]
    sources_used: list[str]
    confidence_explanation: str
    suggestions: list[str]


class ExplainabilityEngine:
    """
    Generates human-readable explanations for AI responses.
    
    Provides transparency by explaining:
    - How the AI arrived at the response
    - What evidence was used
    - How confident the AI is
    - What limitations exist
    """
    
    def explain(
        self,
        reasoning_result: ReasoningResult,
        evidence: Evidence,
        confidence: ConfidenceScore,
    ) -> Explanation:
        """
        Generate a comprehensive explanation.
        
        Args:
            reasoning_result: Result from reasoning engine
            evidence: Evidence used
            confidence: Calculated confidence
        
        Returns:
            Explanation with all relevant details
        """
        # Extract reasoning steps from trace
        reasoning_steps = self._extract_reasoning_steps(reasoning_result.trace)
        
        # Get sources used
        sources_used = self._get_sources_used(evidence)
        
        # Generate confidence explanation
        confidence_explanation = self._explain_confidence(confidence)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            reasoning_result, evidence, confidence
        )
        
        # Generate summary
        summary = self._generate_summary(
            reasoning_steps, sources_used, confidence
        )
        
        return Explanation(
            summary=summary,
            reasoning_steps=reasoning_steps,
            sources_used=sources_used,
            confidence_explanation=confidence_explanation,
            suggestions=suggestions,
        )
    
    def _extract_reasoning_steps(self, trace: ReasoningTrace) -> list[str]:
        """Extract human-readable reasoning steps."""
        steps = []
        
        for step in trace.steps:
            description = f"Step {step.step_number}: {step.description}"
            
            if step.alternatives_considered:
                description += f" (considered {len(step.alternatives_considered)} alternatives)"
            
            steps.append(description)
        
        if not steps:
            # Fallback if no trace
            steps = ["1. Analyzed the question", "2. Retrieved relevant evidence", "3. Generated response"]
        
        return steps
    
    def _get_sources_used(self, evidence: Evidence) -> list[str]:
        """Get list of sources used in response."""
        sources = []
        
        for chunk in evidence.chunks:
            if chunk.metadata.get("title"):
                sources.append(chunk.metadata["title"])
            elif chunk.metadata.get("source"):
                sources.append(chunk.metadata["source"])
            else:
                sources.append(f"Source: {chunk.source_type.value}")
        
        # Deduplicate
        return list(dict.fromkeys(sources))[:5]  # Top 5
    
    def _explain_confidence(self, confidence: ConfidenceScore) -> str:
        """Generate explanation of confidence score."""
        if confidence.level.value == "high":
            return (
                f"I'm highly confident in this response ({confidence.overall:.0%}). "
                f"This is based on strong evidence ({confidence.evidence_score:.0%}) "
                f"and consistent information from multiple sources."
            )
        
        elif confidence.level.value == "medium":
            return (
                f"I'm moderately confident in this response ({confidence.overall:.0%}). "
                f"The evidence quality is {confidence.evidence_score:.0%}. "
                f"{confidence.summary}"
            )
        
        elif confidence.level.value == "low":
            return (
                f"This response has lower confidence ({confidence.overall:.0%}). "
                f"While the information may be helpful, please verify with additional sources. "
                f"{confidence.summary}"
            )
        
        else:  # very_low
            return (
                f"⚠️ This response has low confidence ({confidence.overall:.0%}). "
                f"I recommend consulting a specialist or additional documentation "
                f"before making decisions based on this response. "
                f"{confidence.summary}"
            )
    
    def _generate_suggestions(
        self,
        reasoning_result: ReasoningResult,
        evidence: Evidence,
        confidence: ConfidenceScore,
    ) -> list[str]:
        """Generate suggestions for the user."""
        suggestions = []
        
        # If low confidence, suggest verification
        if confidence.level.value in ["low", "very_low"]:
            suggestions.append(
                "Consider verifying this information with a supervisor or additional documentation."
            )
        
        # If conflicting sources, suggest checking multiple
        if confidence.conflicting_sources:
            suggestions.append(
                "Different sources provided conflicting information. Review both perspectives."
            )
        
        # If outdated information, suggest checking for updates
        if confidence.outdated_information:
            suggestions.append(
                "The information may be outdated. Check for newer documentation."
            )
        
        # Always suggest for critical topics
        critical_keywords = ["safety", "critical", "emergency", "faulty", "recall"]
        if any(kw in reasoning_result.final_answer.lower() for kw in critical_keywords):
            suggestions.append(
                "For critical safety issues, always follow established protocols and notify supervisors."
            )
        
        return suggestions
    
    def _generate_summary(
        self,
        reasoning_steps: list[str],
        sources_used: list[str],
        confidence: ConfidenceScore,
    ) -> str:
        """Generate overall summary."""
        parts = []
        
        # How we arrived at this
        if reasoning_steps:
            parts.append(f"I analyzed your question using {len(reasoning_steps)} reasoning steps.")
        
        # What sources
        if sources_used:
            parts.append(f"I referenced {len(sources_used)} information sources.")
        else:
            parts.append("I didn't find specific information sources for this query.")
        
        # Confidence
        parts.append(f"My confidence level is {confidence.level.value} ({confidence.overall:.0%}).")
        
        return " ".join(parts)
    
    def to_user_friendly(
        self,
        explanation: Explanation,
        include_details: bool = False,
    ) -> str:
        """Format explanation for user display."""
        lines = []
        
        # Main summary
        lines.append(explanation.summary)
        lines.append("")
        
        # Confidence explanation
        lines.append(explanation.confidence_explanation)
        
        # Show details if requested
        if include_details:
            if explanation.reasoning_steps:
                lines.append("")
                lines.append("### How I reasoned:")
                for step in explanation.reasoning_steps[:5]:
                    lines.append(f"- {step}")
            
            if explanation.sources_used:
                lines.append("")
                lines.append("### Sources:")
                for source in explanation.sources_used:
                    lines.append(f"- {source}")
        
        # Suggestions
        if explanation.suggestions:
            lines.append("")
            lines.append("### Suggestions:")
            for suggestion in explanation.suggestions:
                lines.append(f"- {suggestion}")
        
        return "\n".join(lines)


def create_explainability_engine() -> ExplainabilityEngine:
    """Create an explainability engine."""
    return ExplainabilityEngine()
