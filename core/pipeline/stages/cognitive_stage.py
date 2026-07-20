"""Cognitive Stage Base for EREN OS Cognitive Pipeline.

Abstract base class for all cognitive pipeline stages.
Each stage handles a specific step in the cognitive processing pipeline.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.pipeline.stage import PipelineStage
from core.pipeline.context import PipelineContext
from core.pipeline.types import StageMetadata, StageResult, StageState

if TYPE_CHECKING:
    from core.pipeline.cognitive_events import (
        CognitiveEventPublisher,
        CognitiveEvent,
    )


@dataclass
class CognitiveTelemetry:
    """Telemetry data collected during stage execution."""
    
    duration_ms: float = 0.0
    tokens_used: int = 0
    provider: str = ""
    estimated_cost: float = 0.0
    errors: int = 0
    retries: int = 0
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "provider": self.provider,
            "estimated_cost": self.estimated_cost,
            "errors": self.errors,
            "retries": self.retries,
            "metadata": self.metadata,
        }


class CognitiveStage(PipelineStage, ABC):
    """Abstract base class for cognitive pipeline stages.
    
    All cognitive stages follow a common pattern:
    1. Execute the stage logic
    2. Collect telemetry
    3. Emit events
    
    Subclasses must implement:
    - _execute_impl(): Core stage logic
    - _get_stage_name(): Stage identifier
    - _create_event(): Stage-specific event
    """
    
    def __init__(
        self,
        name: str,
        event_publisher: CognitiveEventPublisher | None = None,
        timeout_seconds: float = 30.0,
        stage_type=None,
    ):
        """Initialize the cognitive stage.
        
        Args:
            name: Stage name.
            event_publisher: Optional event publisher.
            timeout_seconds: Stage timeout.
            stage_type: Optional stage type.
        """
        from core.pipeline.types import StageType
        super().__init__(name=name)
        self._event_publisher = event_publisher
        self._timeout_seconds = timeout_seconds
        self._stage_type = stage_type or StageType.CUSTOM
        self._telemetry = CognitiveTelemetry()
    
    @property
    def stage_type(self):
        """Get stage type."""
        return self._stage_type
    
    @property
    def event_publisher(self) -> CognitiveEventPublisher | None:
        """Get the event publisher."""
        return self._event_publisher
    
    @event_publisher.setter
    def event_publisher(self, publisher: CognitiveEventPublisher) -> None:
        """Set the event publisher."""
        self._event_publisher = publisher
    
    @property
    def telemetry(self) -> CognitiveTelemetry:
        """Get stage telemetry."""
        return self._telemetry
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute the stage with telemetry and event publishing.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Stage execution result.
        """
        from core.pipeline.types import StageState
        
        # Reset telemetry
        self._telemetry = CognitiveTelemetry()
        start_time = time.perf_counter()
        
        try:
            # Execute stage logic
            result = self._execute_impl(context)
            
            # Calculate duration
            self._telemetry.duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Publish event on success
            if self._event_publisher:
                event = self._create_event(context, success=True)
                self._event_publisher.publish(event)
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                status=StageState.COMPLETED,
                duration_ms=int(self._telemetry.duration_ms),
                output=result,
            )
            
        except Exception as e:
            # Calculate duration
            self._telemetry.duration_ms = (time.perf_counter() - start_time) * 1000
            self._telemetry.errors += 1
            
            # Publish event on failure
            if self._event_publisher:
                event = self._create_event(context, success=False, error=str(e))
                self._event_publisher.publish(event)
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                status=StageState.FAILED,
                duration_ms=int(self._telemetry.duration_ms),
                output={"error": str(e)},
                errors=[str(e)],
            )
    
    @abstractmethod
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Execute stage-specific logic.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Stage result data.
        """
        ...
    
    def describe(self) -> str:
        """Return human-readable description of this stage.
        
        Returns:
            Description of the stage.
        """
        return f"Cognitive Stage: {self._name}"
    
    def _create_event(
        self, 
        context: PipelineContext, 
        success: bool = True,
        error: str = "",
    ) -> CognitiveEvent:
        """Create a cognitive event for this stage.
        
        Args:
            context: Pipeline context.
            success: Whether stage succeeded.
            error: Error message if failed.
            
        Returns:
            Cognitive event.
        """
        from core.pipeline.cognitive_events import CognitiveEvent
        
        # Import stage name dynamically
        event_type = f"{self.name}_completed" if success else f"{self.name}_failed"
        
        return CognitiveEvent(
            event_type=event_type,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            tokens_used=self._telemetry.tokens_used,
            provider=self._telemetry.provider,
            estimated_cost=self._telemetry.estimated_cost,
            data=self._telemetry.metadata,
        )
    
    def _record_telemetry(
        self,
        tokens: int = 0,
        provider: str = "",
        cost: float = 0.0,
        **metadata,
    ) -> None:
        """Record telemetry data for the stage.
        
        Args:
            tokens: Tokens used.
            provider: LLM provider used.
            cost: Estimated cost.
            **metadata: Additional metadata.
        """
        self._telemetry.tokens_used = tokens
        self._telemetry.provider = provider
        self._telemetry.estimated_cost = cost
        self._telemetry.metadata.update(metadata)
