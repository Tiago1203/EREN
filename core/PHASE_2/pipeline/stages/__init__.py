"""Cognitive Pipeline Stages for EREN OS.

This package contains the cognitive pipeline stages that implement
the cognitive processing pipeline.

Stages:
    - IntentStage: Detects user intent
    - ContextStage: Builds processing context
    - MemoryStage: Retrieves relevant memories
    - KnowledgeStage: Retrieves relevant knowledge
    - ReasoningStage: Performs reasoning
    - PlanningStage: Creates execution plans
    - DecisionStage: Makes decisions
    - ExecutionStage: Executes planned tasks
    - LearningStage: Learns from execution
    - ResponseStage: Generates responses

Usage:
    from core.PHASE_2.pipeline.stages import (
        CognitivePipeline,
        create_cognitive_pipeline,
    )
"""

from __future__ import annotations

from core.PHASE_2.pipeline.stages.cognitive_stage import CognitiveStage, CognitiveTelemetry
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

__all__ = [
    # Base
    "CognitiveStage",
    "CognitiveTelemetry",
    # Stages
    "IntentDetectionStage",
    "ContextBuildingStage",
    "MemoryRetrievalStage",
    "KnowledgeRetrievalStage",
    "CognitiveReasoningStage",
    "CognitivePlanningStage",
    "CognitiveDecisionStage",
    "TaskExecutionStage",
    "CognitiveLearningStage",
    "ResponseGenerationStage",
]