"""Decision Stage for EREN OS Cognitive Pipeline.

Makes decisions based on reasoning and planning.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.pipeline.stages.cognitive_stage import CognitiveStage
from core.pipeline.context import PipelineContext

if TYPE_CHECKING:
    from core.pipeline.cognitive_events import CognitiveEventPublisher


class CognitiveDecisionStage(CognitiveStage):
    """Stage for making decisions.
    
    Responsibilities:
    - Evaluate alternatives
    - Select best action
    - Calculate confidence
    """
    
    def __init__(
        self,
        event_publisher: CognitiveEventPublisher | None = None,
    ):
        """Initialize the decision stage."""
        super().__init__(
            name="decision",
            event_publisher=event_publisher,
        )
    
    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "Decision Making"
    
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Execute decision making.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Decision result.
        """
        reasoning = context.get("reasoning", {})
        plan = context.get("plan", {})
        
        # Make decision
        decision = self._make_decision(reasoning, plan)
        
        # Record telemetry
        self._record_telemetry(
            decision=decision["decision"],
            confidence=decision["confidence"],
        )
        
        # Store in context
        context["decision"] = decision
        
        return decision
    
    def _make_decision(
        self,
        reasoning: dict,
        plan: dict,
    ) -> dict[str, Any]:
        """Make decision based on reasoning and plan.
        
        Args:
            reasoning: Reasoning results.
            plan: Execution plan.
            
        Returns:
            Decision result.
        """
        reasoning_confidence = reasoning.get("confidence", 0.5)
        plan_risk = plan.get("risk_level", "low")
        
        # Calculate decision confidence
        if plan_risk == "high":
            confidence = reasoning_confidence * 0.7
        elif plan_risk == "medium":
            confidence = reasoning_confidence * 0.85
        else:
            confidence = reasoning_confidence
        
        # Determine decision
        decision_text = self._determine_decision(reasoning, plan)
        
        return {
            "decision": decision_text,
            "confidence": confidence,
            "alternatives_considered": 1,
            "reasoning_confidence": reasoning_confidence,
            "plan_risk": plan_risk,
        }
    
    def _determine_decision(
        self,
        reasoning: dict,
        plan: dict,
    ) -> str:
        """Determine the final decision.
        
        Args:
            reasoning: Reasoning results.
            plan: Execution plan.
            
        Returns:
            Decision text.
        """
        intent = reasoning.get("reasoning_type", "query")
        task_count = plan.get("task_count", 0)
        
        if intent == "command":
            return f"Execute {task_count} tasks as planned"
        elif intent == "medical":
            return "Provide medical recommendation with caution"
        return "Provide response based on analysis"
    
    def _create_event(self, context, success=True, error=""):
        """Create decision made event."""
        from core.pipeline.cognitive_events import DecisionMadeEvent, CognitiveEventType
        
        decision = context.get("decision", {})
        
        return DecisionMadeEvent(
            event_type=CognitiveEventType.DECISION_MADE,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            decision=decision.get("decision", ""),
            confidence=decision.get("confidence", 0.0),
            alternatives_considered=decision.get("alternatives_considered", 0),
            data=self._telemetry.metadata,
        )
