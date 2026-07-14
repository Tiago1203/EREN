"""Response Generation Stage for EREN OS Cognitive Pipeline.

Generates the final response based on all processing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.pipeline.stages.cognitive_stage import CognitiveStage
from core.pipeline.context import PipelineContext

if TYPE_CHECKING:
    from core.pipeline.cognitive_events import CognitiveEventPublisher


class ResponseGenerationStage(CognitiveStage):
    """Stage for generating responses.
    
    Responsibilities:
    - Compile all processing results
    - Generate response text
    - Add citations
    - Format output
    """
    
    def __init__(
        self,
        event_publisher: CognitiveEventPublisher | None = None,
    ):
        """Initialize the response stage."""
        super().__init__(
            name="response",
            event_publisher=event_publisher,
        )
    
    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "Response Generation"
    
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Generate response.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Response result.
        """
        decision = context.get("decision", {})
        execution = context.get("execution_result", {})
        reasoning = context.get("reasoning", {})
        memories = context.get("memories", [])
        knowledge = context.get("knowledge", [])
        
        # Generate response
        response = self._generate_response(
            decision=decision,
            execution=execution,
            reasoning=reasoning,
            memories=memories,
            knowledge=knowledge,
        )
        
        # Record telemetry
        self._record_telemetry(
            response_type=response["response_type"],
            includes_citations=response["includes_citations"],
        )
        
        # Store in context
        context["response"] = response
        
        return response
    
    def _generate_response(
        self,
        decision: dict,
        execution: dict,
        reasoning: dict,
        memories: list,
        knowledge: list,
    ) -> dict[str, Any]:
        """Generate the response text.
        
        Args:
            decision: Decision results.
            execution: Execution results.
            reasoning: Reasoning results.
            memories: Retrieved memories.
            knowledge: Retrieved knowledge.
            
        Returns:
            Generated response.
        """
        # Build response based on processing
        intent = reasoning.get("reasoning_type", "query")
        
        # Determine response type
        if intent == "command":
            response_type = "action_confirmation"
            text = self._generate_command_response(execution)
        elif intent == "medical":
            response_type = "medical_recommendation"
            text = self._generate_medical_response(reasoning, knowledge)
        else:
            response_type = "information"
            text = self._generate_information_response(reasoning, knowledge)
        
        # Check for citations
        includes_citations = len(knowledge) > 0
        
        return {
            "text": text,
            "response_type": response_type,
            "includes_citations": includes_citations,
            "confidence": decision.get("confidence", 0.0),
            "sources": [k.get("source", "unknown") for k in knowledge[:3]],
        }
    
    def _generate_command_response(self, execution: dict) -> str:
        """Generate response for command intent."""
        success = execution.get("success", 0)
        failed = execution.get("failed", 0)
        
        if failed == 0:
            return f"Successfully executed {success} action(s)."
        return f"Executed {success} action(s) with {failed} failure(s)."
    
    def _generate_medical_response(
        self,
        reasoning: dict,
        knowledge: list,
    ) -> str:
        """Generate response for medical intent."""
        conclusions = reasoning.get("conclusions", [])
        if conclusions:
            return f"Based on the analysis: {conclusions[0]}"
        return "Unable to provide medical recommendation. Please consult a professional."
    
    def _generate_information_response(
        self,
        reasoning: dict,
        knowledge: list,
    ) -> str:
        """Generate response for information intent."""
        conclusions = reasoning.get("conclusions", [])
        
        if conclusions:
            return f"Based on the analysis: {conclusions[0]}"
        elif knowledge:
            return f"Found relevant information: {knowledge[0].get('title', 'No results')}"
        return "Unable to find relevant information."
    
    def _create_event(self, context, success=True, error=""):
        """Create response generated event."""
        from core.pipeline.cognitive_events import ResponseGeneratedEvent, CognitiveEventType
        
        response = context.get("response", {})
        
        return ResponseGeneratedEvent(
            event_type=CognitiveEventType.RESPONSE_GENERATED,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            response_text=response.get("text", "")[:200],  # Truncate for event
            response_type=response.get("response_type", "unknown"),
            includes_citations=response.get("includes_citations", False),
            data=self._telemetry.metadata,
        )
