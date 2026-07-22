"""Context Building Stage for EREN OS Cognitive Pipeline.

Builds context from user input and available sources.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.PHASE_2.pipeline.stages.cognitive_stage import CognitiveStage
from core.PHASE_2.pipeline.context import PipelineContext

if TYPE_CHECKING:
    from core.PHASE_2.pipeline.cognitive_events import CognitiveEventPublisher


class ContextBuildingStage(CognitiveStage):
    """Stage for building processing context.
    
    Responsibilities:
    - Gather context from multiple sources
    - Build context object
    - Prioritize context items
    """
    
    def __init__(
        self,
        event_publisher: CognitiveEventPublisher | None = None,
        max_context_items: int = 10,
    ):
        """Initialize the context stage.
        
        Args:
            event_publisher: Event publisher.
            max_context_items: Maximum context items.
        """
        super().__init__(
            name="context",
            event_publisher=event_publisher,
        )
        self._max_context_items = max_context_items
    
    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "Context Building"
    
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Execute context building.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Context building result.
        """
        # Gather context from sources
        context_items = []
        sources = []
        
        # User input context
        if context.get("user_input"):
            context_items.append({
                "type": "user_input",
                "content": context["user_input"],
                "priority": 10,
            })
            sources.append("user_input")
        
        # Session context
        if context.get("session_id"):
            context_items.append({
                "type": "session",
                "content": f"Session: {context['session_id']}",
                "priority": 5,
            })
            sources.append("session")
        
        # Intent context
        if context.get("intent"):
            context_items.append({
                "type": "intent",
                "content": f"Intent: {context['intent']}",
                "priority": 8,
            })
            sources.append("intent")
        
        # Sort by priority and limit
        context_items.sort(key=lambda x: x["priority"], reverse=True)
        context_items = context_items[:self._max_context_items]
        
        # Record telemetry
        self._record_telemetry(
            context_items=len(context_items),
            sources=sources,
        )
        
        # Store in context
        context["context_items"] = context_items
        context["context_sources"] = sources
        
        return {
            "context_items": len(context_items),
            "context_sources": sources,
            "items": context_items,
        }
    
    def _create_event(self, context, success=True, error=""):
        """Create context built event."""
        from core.PHASE_2.pipeline.cognitive_events import ContextBuiltEvent, CognitiveEventType
        
        return ContextBuiltEvent(
            event_type=CognitiveEventType.CONTEXT_BUILT,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            context_items=len(context.get("context_items", [])),
            context_sources=context.get("context_sources", []),
            data=self._telemetry.metadata,
        )
