"""
EREN Cognitive Runtime

The Cognitive Runtime orchestrates all AI capabilities to process user messages
and generate intelligent responses.

Architecture:
    Safety → Context → RAG → Reasoning → Confidence → Explainability → Response

See docs/epic4/README.md for architecture overview.
See docs/adr/epic4/ADR-0402.md for implementation details.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator
from uuid import UUID

if TYPE_CHECKING:
    from core.cognitive.safety.domain.entities import SafetyCheckResult
    from core.cognitive.rag.domain.entities import Evidence
    from core.cognitive.reasoning.domain.entities import ReasoningResult
    from core.cognitive.conversation.domain.value_objects import ConfidenceScore


@dataclass
class CognitiveResult:
    """Result from cognitive processing."""
    success: bool
    response: str | None = None
    confidence: float | None = None
    error: str | None = None
    blocked: bool = False
    block_reason: str | None = None
    
    @classmethod
    def success_response(
        cls,
        response: str,
        confidence: float,
    ) -> "CognitiveResult":
        return cls(success=True, response=response, confidence=confidence)
    
    @classmethod
    def blocked(cls, reason: str) -> "CognitiveResult":
        return cls(success=False, blocked=True, block_reason=reason)
    
    @classmethod
    def error_response(cls, error: str) -> "CognitiveResult":
        return cls(success=False, error=error)


@dataclass
class ProcessingContext:
    """Context for message processing."""
    conversation_id: UUID
    user_id: UUID
    tenant_id: UUID
    message: str
    domain: str = "biomedical"
    metadata: dict | None = None


class CognitiveRuntime:
    """
    Main entry point for AI operations.
    
    Coordinates the complete cognitive pipeline:
    1. Safety validation (pre-check)
    2. Context building
    3. RAG retrieval
    4. Reasoning
    5. Confidence calculation
    6. Response composition
    7. Safety validation (post-check)
    """
    
    def __init__(
        self,
        safety_engine,  # SafetyEngine
        context_builder,  # ContextBuilder
        rag_orchestrator,  # RAGOrchestrator
        reasoning_service,  # ReasoningService
        confidence_engine,  # ConfidenceEngine
        response_composer,  # ResponseComposer
        memory_manager,  # MemoryManager
    ):
        self.safety_engine = safety_engine
        self.context_builder = context_builder
        self.rag_orchestrator = rag_orchestrator
        self.reasoning_service = reasoning_service
        self.confidence_engine = confidence_engine
        self.response_composer = response_composer
        self.memory_manager = memory_manager
    
    async def process_message(
        self,
        context: ProcessingContext,
    ) -> CognitiveResult:
        """
        Process a user message and return a cognitive response.
        
        Pipeline:
        1. Pre-safety check
        2. Build context
        3. RAG retrieval
        4. Reasoning
        5. Confidence
        6. Post-safety check
        7. Compose response
        """
        # 1. Pre-safety check
        safety_result = await self.safety_engine.validate_input(
            context.message,
            context.user_id,
        )
        
        if not safety_result.is_safe:
            return CognitiveResult.blocked(
                safety_result.violations[0].details 
                if safety_result.violations 
                else "Safety check failed"
            )
        
        # 2. Build context
        enriched_context = await self.context_builder.build(context)
        
        # 3. RAG retrieval
        evidence = await self.rag_orchestrator.retrieve(
            context.message,
            context.tenant_id,
        )
        
        # 4. Reasoning
        reasoning_result = await self.reasoning_service.reason(
            enriched_context,
            evidence,
        )
        
        # 5. Confidence calculation
        confidence = await self.confidence_engine.calculate(
            reasoning_result,
            evidence,
        )
        
        # 6. Post-safety check
        output_safety = await self.safety_engine.validate_output(
            reasoning_result.final_answer,
            context.user_id,
        )
        
        if not output_safety.is_safe:
            return CognitiveResult.blocked(
                output_safety.violations[0].details
                if output_safety.violations
                else "Output safety check failed"
            )
        
        # 7. Compose response
        response = await self.response_composer.compose(
            reasoning_result=reasoning_result,
            confidence=confidence,
            evidence=evidence,
        )
        
        return CognitiveResult.success_response(
            response=response,
            confidence=confidence.overall,
        )
    
    async def process_message_stream(
        self,
        context: ProcessingContext,
    ) -> AsyncIterator[str]:
        """
        Process a message with streaming response.
        
        Yields response chunks as they become available.
        """
        # Start with safety check
        safety_result = await self.safety_engine.validate_input(
            context.message,
            context.user_id,
        )
        
        if not safety_result.is_safe:
            yield f"[BLOCKED] {safety_result.violations[0].details}"
            return
        
        # Process and stream
        result = await self.process_message(context)
        
        if result.blocked:
            yield f"[BLOCKED] {result.block_reason}"
        elif result.success:
            yield result.response or ""
        else:
            yield f"[ERROR] {result.error}"


# Factory function for creating CognitiveRuntime
def create_cognitive_runtime(
    config: dict,
) -> CognitiveRuntime:
    """
    Create a CognitiveRuntime instance with all dependencies.
    
    Args:
        config: Configuration dictionary with LLM, storage, etc.
    
    Returns:
        Configured CognitiveRuntime instance.
    """
    # This would wire up all dependencies in production
    # For now, return a placeholder
    return CognitiveRuntime(
        safety_engine=None,
        context_builder=None,
        rag_orchestrator=None,
        reasoning_service=None,
        confidence_engine=None,
        response_composer=None,
        memory_manager=None,
    )
