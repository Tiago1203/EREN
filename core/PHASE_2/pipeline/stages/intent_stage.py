"""Intent Detection Stage for EREN OS Cognitive Pipeline.

Detects user intent from input text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.PHASE_2.pipeline.stages.cognitive_stage import CognitiveStage, CognitiveTelemetry
from core.PHASE_2.pipeline.context import PipelineContext

if TYPE_CHECKING:
    from core.PHASE_2.pipeline.cognitive_events import (
        CognitiveEventPublisher,
        IntentDetectedEvent,
    )


class IntentDetectionStage(CognitiveStage):
    """Stage for detecting user intent.
    
    Responsibilities:
    - Parse user input
    - Extract entities
    - Determine intent
    - Calculate confidence
    """
    
    def __init__(
        self,
        event_publisher: CognitiveEventPublisher | None = None,
        min_confidence: float = 0.5,
    ):
        """Initialize the intent stage.
        
        Args:
            event_publisher: Event publisher.
            min_confidence: Minimum confidence threshold.
        """
        super().__init__(
            name="intent",
            event_publisher=event_publisher,
        )
        self._min_confidence = min_confidence
    
    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "Intent Detection"
    
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Execute intent detection.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Intent detection result.
        """
        user_input = context.get("user_input", "")
        
        if not user_input:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "entities": {},
            }
        
        # Extract intent patterns (simplified - real implementation would use ML/NLP)
        intent_result = self._detect_intent(user_input)
        
        # Record telemetry
        self._record_telemetry(
            input_length=len(user_input),
            intent_detected=intent_result["intent"],
            confidence=intent_result["confidence"],
        )
        
        # Store in context
        context["intent"] = intent_result["intent"]
        context["intent_confidence"] = intent_result["confidence"]
        context["entities"] = intent_result["entities"]
        
        return intent_result
    
    def _detect_intent(self, text: str) -> dict[str, Any]:
        """Detect intent from text.
        
        This is a simplified implementation. Real implementation
        would use ML models, rule-based systems, or LLM.
        
        Args:
            text: User input text.
            
        Returns:
            Intent detection result.
        """
        text_lower = text.lower()
        
        # Simple pattern matching (placeholder for real implementation)
        intent_patterns = {
            "query": ["what", "how", "why", "when", "where", "who", "?"],
            "command": ["do", "execute", "run", "start", "stop", "create", "delete"],
            "medical": ["patient", "diagnosis", "symptom", "treatment", "doctor", "medical"],
            "engineering": ["system", "device", "maintenance", "repair", "install"],
            "research": ["analyze", "investigate", "study", "compare", "evaluate"],
            "planning": ["plan", "schedule", "organize", "coordinate", "manage"],
        }
        
        detected_intent = "query"
        max_matches = 0
        
        for intent, patterns in intent_patterns.items():
            matches = sum(1 for p in patterns if p in text_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        
        # Calculate simple confidence based on pattern matches
        confidence = min(0.9, 0.3 + (max_matches * 0.15))
        
        # Extract entities (simplified)
        entities = self._extract_entities(text)
        
        return {
            "intent": detected_intent,
            "confidence": confidence,
            "entities": entities,
            "raw_input": text,
        }
    
    def _extract_entities(self, text: str) -> dict[str, list[str]]:
        """Extract entities from text.
        
        Args:
            text: Input text.
            
        Returns:
            Extracted entities.
        """
        # Simplified entity extraction
        entities = {
            "numbers": [],
            "dates": [],
            "medical_terms": [],
            "technical_terms": [],
        }
        
        import re
        
        # Extract numbers
        entities["numbers"] = re.findall(r'\d+(?:\.\d+)?', text)
        
        # Extract dates
        entities["dates"] = re.findall(
            r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\w+ \d{1,2},? \d{4}',
            text
        )
        
        return entities
    
    def _create_event(
        self,
        context: PipelineContext,
        success: bool = True,
        error: str = "",
    ) -> IntentDetectedEvent:
        """Create intent detected event."""
        from core.PHASE_2.pipeline.cognitive_events import IntentDetectedEvent, CognitiveEventType
        
        return IntentDetectedEvent(
            event_type=CognitiveEventType.INTENT_DETECTED,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            intent=context.get("intent", "unknown"),
            confidence=context.get("intent_confidence", 0.0),
            entities=context.get("entities", {}),
            data=self._telemetry.metadata,
        )
