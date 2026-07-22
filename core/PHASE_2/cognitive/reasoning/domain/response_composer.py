"""Response Composer - composes final AI responses."""
from dataclasses import dataclass

from core.PHASE_2.cognitive.reasoning.domain.entities import ReasoningResult
from core.PHASE_2.cognitive.reasoning.domain.explainability import ExplainabilityEngine, Explanation
from core.PHASE_2.cognitive.rag.domain.entities import Evidence
from core.PHASE_2.cognitive.conversation.domain.value_objects import ConfidenceScore, MessageContent


@dataclass
class ResponseComposerConfig:
    """Configuration for response composition."""
    include_reasoning: bool = True
    include_citations: bool = True
    include_confidence: bool = True
    max_citations: int = 3
    format: str = "markdown"  # markdown, text, html


class ResponseComposer:
    """
    Composes final AI responses with all components.
    
    Combines:
    - Reasoning result
    - Confidence score
    - Evidence/Citations
    - Explanations
    
    Into a user-friendly response.
    """
    
    def __init__(
        self,
        explainability_engine: ExplainabilityEngine,
        config: ResponseComposerConfig | None = None,
    ):
        self.explainability = explainability_engine
        self.config = config or ResponseComposerConfig()
    
    async def compose(
        self,
        reasoning_result: ReasoningResult,
        confidence: ConfidenceScore,
        evidence: Evidence,
    ) -> str:
        """
        Compose final response.
        
        Args:
            reasoning_result: Result from reasoning engine
            confidence: Calculated confidence
            evidence: Evidence used
        
        Returns:
            Composed response string
        """
        # Generate explanation
        explanation = self.explainability.explain(
            reasoning_result, evidence, confidence
        )
        
        # Build response parts
        parts = []
        
        # 1. Main response content
        parts.append(reasoning_result.final_answer)
        
        # 2. Confidence warning if needed
        if self.config.include_confidence and self._should_show_confidence(confidence):
            parts.append("")
            parts.append(self._format_confidence_warning(confidence))
        
        # 3. Citations if available and requested
        if self.config.include_citations and evidence.citations:
            parts.append("")
            parts.append(self._format_citations(evidence))
        
        # 4. Reasoning trace if requested and available
        if self.config.include_reasoning and reasoning_result.trace.steps:
            parts.append("")
            parts.append(self._format_reasoning(reasoning_result))
        
        return "\n".join(parts)
    
    def compose_with_explanation(
        self,
        reasoning_result: ReasoningResult,
        confidence: ConfidenceScore,
        evidence: Evidence,
    ) -> tuple[str, Explanation]:
        """
        Compose response with full explanation.
        
        Returns:
            Tuple of (response, explanation)
        """
        explanation = self.explainability.explain(
            reasoning_result, evidence, confidence
        )
        
        response = self.explainability.to_user_friendly(explanation)
        
        return response, explanation
    
    def _should_show_confidence(self, confidence: ConfidenceScore) -> bool:
        """Determine if confidence warning should be shown."""
        return (
            confidence.level.value in ["low", "very_low"]
            or confidence.low_evidence
            or confidence.conflicting_sources
            or confidence.outdated_information
        )
    
    def _format_confidence_warning(self, confidence: ConfidenceScore) -> str:
        """Format confidence warning."""
        lines = []
        
        level = confidence.level.value
        
        if level == "very_low":
            lines.append("⚠️ **Importante:** Esta respuesta tiene baja confianza. ")
            lines.append("Por favor consulta con un profesional antes de tomar decisiones.")
        
        elif level == "low":
            lines.append("ℹ️ **Nota:** Esta respuesta tiene confianza moderada.")
            lines.append("Te recomiendo verificar con fuentes adicionales.")
        
        elif confidence.low_evidence:
            lines.append("📚 **Evidencia limitada:** La información disponible es limitada.")
        
        elif confidence.conflicting_sources:
            lines.append("⚡ **Fuentes conflictivas:** Diferentes fuentes dan información diferente.")
        
        if confidence.summary:
            lines.append(f"\n_{confidence.summary}_")
        
        return "\n".join(lines)
    
    def _format_citations(self, evidence: Evidence) -> str:
        """Format citations section."""
        if not evidence.citations:
            return ""
        
        lines = []
        lines.append("**Fuentes consultadas:**")
        
        citations = evidence.citations[:self.config.max_citations]
        for i, citation in enumerate(citations, 1):
            if citation.citation_url:
                lines.append(f"{i}. [{citation.source_type.value.title()}]({citation.citation_url})")
            else:
                lines.append(f"{i}. {citation.source_type.value.title()}")
        
        return "\n".join(lines)
    
    def _format_reasoning(self, reasoning_result: ReasoningResult) -> str:
        """Format reasoning trace section."""
        lines = []
        lines.append("**Cómo llegué a esta respuesta:**")
        
        for step in reasoning_result.trace.steps[:5]:  # Top 5 steps
            lines.append(f"- {step.description}")
        
        return "\n".join(lines)
    
    def to_message_content(self, response: str) -> MessageContent:
        """Convert response to MessageContent."""
        return MessageContent(
            text=response,
            format=self.config.format,
        )


def create_response_composer(
    explainability_engine: ExplainabilityEngine | None = None,
) -> ResponseComposer:
    """Create a response composer."""
    if not explainability_engine:
        explainability_engine = ExplainabilityEngine()
    
    return ResponseComposer(explainability_engine=explainability_engine)
