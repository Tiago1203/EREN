"""Cognitive Pipeline for EREN OS.

Main cognitive pipeline that orchestrates the complete cognitive processing cycle.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.PHASE_2.pipeline.context import PipelineContext
from core.PHASE_2.pipeline.pipeline import CognitivePipeline as BasePipeline
from core.PHASE_2.pipeline.types import PipelineConfig, PipelineResult, PipelineState
from core.PHASE_2.pipeline.cognitive_events import (
    CognitiveEventPublisher,
    CognitiveEventType,
    CognitiveEvent,
)

if TYPE_CHECKING:
    from core.PHASE_2.pipeline.stages import (
        IntentStage,
        ContextStage,
        MemoryStage,
        KnowledgeStage,
        ReasoningStage,
        PlanningStage,
        DecisionStage,
        ExecutionStage,
        LearningStage,
        ResponseStage,
    )


@dataclass
class CognitivePipelineResult:
    """Result from cognitive pipeline execution."""
    
    pipeline_id: str
    session_id: str
    correlation_id: str
    success: bool
    response: dict
    stages: list[dict]
    total_duration_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    error: str = ""
    metrics: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "success": self.success,
            "response": self.response,
            "stages": self.stages,
            "total_duration_ms": self.total_duration_ms,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "metrics": self.metrics,
        }


def create_cognitive_pipeline(
    event_publisher: CognitiveEventPublisher | None = None,
    enable_telemetry: bool = True,
) -> CognitivePipeline:
    """Create a configured cognitive pipeline.
    
    Args:
        event_publisher: Optional event publisher.
        enable_telemetry: Enable telemetry collection.
        
    Returns:
        Configured cognitive pipeline.
    """
    from core.PHASE_2.pipeline.stages.cognitive_stage import CognitiveStage
    from core.PHASE_2.pipeline.stages.intent_stage import IntentDetectionStage
    from core.PHASE_2.pipeline.stages.context_stage import ContextBuildingStage
    from core.PHASE_2.pipeline.stages.memory_stage import MemoryRetrievalStage
    from core.PHASE_2.pipeline.stages.knowledge_stage import KnowledgeRetrievalStage
    from core.PHASE_2.pipeline.stages.reasoning_stage import CognitiveReasoningStage
    from core.PHASE_2.pipeline.stages.planning_stage import CognitivePlanningStage
    from core.PHASE_2.pipeline.stages.decision_stage import CognitiveDecisionStage
    from core.PHASE_2.pipeline.stages.execution_stage import TaskExecutionStage
    from core.PHASE_2.pipeline.stages.learning_stage import CognitiveLearningStage
    from core.PHASE_2.pipeline.stages.response_stage import ResponseGenerationStage
    
    # Create stages
    intent_stage = IntentDetectionStage(event_publisher=event_publisher)
    context_stage = ContextBuildingStage(event_publisher=event_publisher)
    memory_stage = MemoryRetrievalStage(event_publisher=event_publisher)
    knowledge_stage = KnowledgeRetrievalStage(event_publisher=event_publisher)
    reasoning_stage = CognitiveReasoningStage(event_publisher=event_publisher)
    planning_stage = CognitivePlanningStage(event_publisher=event_publisher)
    decision_stage = CognitiveDecisionStage(event_publisher=event_publisher)
    execution_stage = TaskExecutionStage(event_publisher=event_publisher)
    learning_stage = CognitiveLearningStage(event_publisher=event_publisher)
    response_stage = ResponseGenerationStage(event_publisher=event_publisher)
    
    # Create pipeline
    pipeline = CognitivePipeline(
        name="cognitive_pipeline",
        stages=[
            intent_stage,
            context_stage,
            memory_stage,
            knowledge_stage,
            reasoning_stage,
            planning_stage,
            decision_stage,
            execution_stage,
            learning_stage,
            response_stage,
        ],
        event_publisher=event_publisher,
    )
    
    return pipeline


class CognitivePipeline:
    """Cognitive Pipeline for EREN OS.
    
    Orchestrates the complete cognitive processing cycle:
    1. Intent Detection
    2. Context Building
    3. Memory Retrieval
    4. Knowledge Retrieval
    5. Reasoning
    6. Planning
    7. Decision Making
    8. Execution
    9. Learning
    10. Response Generation
    
    Each stage emits events and collects telemetry.
    """
    
    def __init__(
        self,
        name: str = "cognitive_pipeline",
        stages: list | None = None,
        event_publisher: CognitiveEventPublisher | None = None,
    ):
        """Initialize the cognitive pipeline.
        
        Args:
            name: Pipeline name.
            stages: List of cognitive stages.
            event_publisher: Event publisher.
        """
        self._name = name
        self._stages = stages or []
        self._event_publisher = event_publisher or CognitiveEventPublisher()
        self._lock = threading.RLock()
        self._pipeline_id = str(uuid.uuid4())
        self._state = PipelineState.CREATED
    
    @property
    def name(self) -> str:
        """Get pipeline name."""
        return self._name
    
    @property
    def pipeline_id(self) -> str:
        """Get pipeline ID."""
        return self._pipeline_id
    
    @property
    def stages(self) -> list:
        """Get pipeline stages."""
        return self._stages
    
    @property
    def event_publisher(self) -> CognitiveEventPublisher:
        """Get event publisher."""
        return self._event_publisher
    
    def add_stage(self, stage) -> None:
        """Add a stage to the pipeline.
        
        Args:
            stage: Stage to add.
        """
        with self._lock:
            self._stages.append(stage)
    
    def execute(
        self,
        user_input: str,
        session_id: str | None = None,
        metadata: dict | None = None,
    ) -> CognitivePipelineResult:
        """Execute the cognitive pipeline.
        
        Args:
            user_input: User input text.
            session_id: Optional session ID.
            metadata: Optional metadata.
            
        Returns:
            Pipeline execution result.
        """
        import time
        
        start_time = time.perf_counter()
        correlation_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())
        
        # Create context
        context = PipelineContext(
            correlation_id=correlation_id,
            session_id=session_id,
            pipeline_id=self._pipeline_id,
        )
        context.set("user_input", user_input)
        context.set("metadata", metadata or {})
        
        # Publish start event
        self._publish_event(
            event_type=CognitiveEventType.PIPELINE_STARTED,
            context=context,
        )
        
        # Execute stages
        stage_results = []
        total_duration = 0.0
        
        try:
            for stage in self._stages:
                # Set event publisher on stage
                if hasattr(stage, 'event_publisher'):
                    stage.event_publisher = self._event_publisher
                
                # Execute stage
                result = stage.execute(context)
                stage_results.append({
                    "stage": result.stage_name,
                    "success": result.status.value == "completed",
                    "duration_ms": result.duration_ms,
                    "data": result.output,
                })
                total_duration += result.duration_ms
                
                # Check for failure
                if result.status.value != "completed":
                    raise Exception(result.errors[0] if result.errors else "Stage failed")
            
            # Get response from context
            response = context.get("response", {})
            
            # Publish completion event
            self._publish_event(
                event_type=CognitiveEventType.PIPELINE_COMPLETED,
                context=context,
            )
            
            return CognitivePipelineResult(
                pipeline_id=self._pipeline_id,
                session_id=session_id,
                correlation_id=correlation_id,
                success=True,
                response=response,
                stages=stage_results,
                total_duration_ms=total_duration,
            )
            
        except Exception as e:
            # Publish failure event
            self._publish_event(
                event_type=CognitiveEventType.PIPELINE_FAILED,
                context=context,
                error=str(e),
            )
            
            return CognitivePipelineResult(
                pipeline_id=self._pipeline_id,
                session_id=session_id,
                correlation_id=correlation_id,
                success=False,
                response=context.get("response", {}),
                stages=stage_results,
                total_duration_ms=total_duration,
                error=str(e),
            )
    
    def _publish_event(
        self,
        event_type: CognitiveEventType,
        context: PipelineContext,
        success: bool = True,
        error: str = "",
        **kwargs,
    ) -> None:
        """Publish a cognitive event.
        
        Args:
            event_type: Type of event.
            context: Pipeline context.
            success: Whether operation succeeded.
            error: Error message if failed.
            **kwargs: Additional event data.
        """
        event = CognitiveEvent(
            event_type=event_type,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=self._pipeline_id,
            success=success,
            error=error,
            data=kwargs,
        )
        self._event_publisher.publish(event)
    
    def get_stages_summary(self) -> list[dict]:
        """Get summary of all stages.
        
        Returns:
            List of stage summaries.
        """
        return [
            {
                "name": stage.name,
                "stage_type": getattr(stage, 'stage_name', lambda: stage.name)(),
            }
            for stage in self._stages
        ]
