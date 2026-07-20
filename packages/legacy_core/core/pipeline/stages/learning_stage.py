"""Learning Stage for EREN OS Cognitive Pipeline.

Learns from the execution results to improve future performance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.pipeline.stages.cognitive_stage import CognitiveStage
from core.pipeline.context import PipelineContext

if TYPE_CHECKING:
    from core.pipeline.cognitive_events import CognitiveEventPublisher


class CognitiveLearningStage(CognitiveStage):
    """Stage for learning from execution.
    
    Responsibilities:
    - Analyze execution results
    - Update memory
    - Adjust confidence
    - Generate lessons learned
    """
    
    def __init__(
        self,
        event_publisher: CognitiveEventPublisher | None = None,
    ):
        """Initialize the learning stage."""
        super().__init__(
            name="learning",
            event_publisher=event_publisher,
        )
    
    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "Learning"
    
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Execute learning from execution.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Learning result.
        """
        execution = context.get("execution_result", {})
        reasoning = context.get("reasoning", {})
        memories = context.get("memories", [])
        
        # Learn from execution
        learning_result = self._learn(execution, reasoning, memories)
        
        # Record telemetry
        self._record_telemetry(
            lessons_learned=learning_result["lessons_learned"],
            memory_updates=learning_result["memory_updates"],
            confidence_delta=learning_result["confidence_delta"],
        )
        
        # Store in context
        context["learning"] = learning_result
        
        return learning_result
    
    def _learn(
        self,
        execution: dict,
        reasoning: dict,
        memories: list,
    ) -> dict[str, Any]:
        """Learn from execution results.
        
        Args:
            execution: Execution results.
            reasoning: Reasoning results.
            memories: Retrieved memories.
            
        Returns:
            Learning result.
        """
        success_rate = (
            execution.get("success", 0) / max(1, execution.get("executed", 1))
        )
        
        # Generate lessons
        lessons = []
        
        if success_rate == 1.0:
            lessons.append("All tasks completed successfully")
        elif success_rate < 0.5:
            lessons.append("Execution had significant failures - review approach")
        
        # Calculate confidence adjustment
        confidence_delta = 0.0
        if success_rate == 1.0:
            confidence_delta = 0.05
        elif success_rate < 0.5:
            confidence_delta = -0.1
        
        # Memory updates
        memory_updates = len(memories) if memories else 0
        
        return {
            "lessons_learned": len(lessons),
            "lessons": lessons,
            "memory_updates": memory_updates,
            "confidence_delta": confidence_delta,
            "success_rate": success_rate,
            "reinforcement": success_rate == 1.0,
        }
    
    def _create_event(self, context, success=True, error=""):
        """Create learning completed event."""
        from core.pipeline.cognitive_events import LearningCompletedEvent, CognitiveEventType
        
        learning = context.get("learning", {})
        
        return LearningCompletedEvent(
            event_type=CognitiveEventType.LEARNING_COMPLETED,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            lessons_learned=learning.get("lessons_learned", 0),
            memory_updates=learning.get("memory_updates", 0),
            confidence_delta=learning.get("confidence_delta", 0.0),
            data=self._telemetry.metadata,
        )
