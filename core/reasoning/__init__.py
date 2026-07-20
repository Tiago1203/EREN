"""Cognitive Reasoning Platform (CRP).

The logical brain of EREN. Transforms evidence into hypotheses
and then into justified decisions.

Philosophy:
    Reasoning is not a single algorithm.
    It is a collection of independent cognitive processes.
    Each process can evolve without affecting others.

Architecture:
    Reasoning Platform
        ├── Inference Engine
        ├── Evidence Engine
        ├── Hypothesis Manager
        ├── Reflection Engine
        ├── Confidence Engine
        ├── Explanation Engine
        ├── Validation Engine
        └── Decision Composer

EREN NO uses AI. EREN NO generates text. EREN NO calls LLM.
EREN only organizes reasoning.

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

from core.reasoning.adapters import (
    ReasoningContextAdapter,
    ReasoningMemoryAdapter,
)
from core.reasoning.capabilities import get_reasoning_capabilities
from core.reasoning.confidence_engine import (
    ConfidenceEngine,
    get_confidence_engine,
    reset_confidence_engine,
)
from core.reasoning.confidence_model import (
    BayesianConfidenceCalculator,
    ConfidenceCalculator,
    ConfidenceCalculatorFactory,
    DefaultConfidenceCalculator,
    DempsterShaferCalculator,
    probability_to_level,
)
from core.reasoning.decision_composer import (
    DecisionComposer,
    get_decision_composer,
    reset_decision_composer,
)
from core.reasoning.evidence_engine import (
    EvidenceEngine,
    get_evidence_engine,
    reset_evidence_engine,
)
from core.reasoning.evidence_manager import EvidenceManager
from core.reasoning.exceptions import (
    ChainNotFoundError,
    ChainValidationError,
    DecisionNotFoundError,
    EvidenceNotFoundError,
    HypothesisLimitExceededError,
    HypothesisNotFoundError,
    InsufficientEvidenceError,
    InvalidConfidenceError,
    ReasoningError,
    ReasoningStageError,
    SessionAlreadyActiveError,
    SessionNotFoundError,
    StrategyNotSupportedError,
)
from core.reasoning.explanation_engine import (
    ExplanationEngine,
    get_explanation_engine,
    reset_explanation_engine,
)
from core.reasoning.hypothesis_manager import HypothesisManager

# Reasoning Platform Components
from core.reasoning.inference import (
    InferenceEngine,
    get_inference_engine,
    reset_inference_engine,
)
from core.reasoning.reasoning_chain import (
    ReasoningChain,
    ReasoningChainBuilder,
    ReasoningChainManager,
)
from core.reasoning.reasoning_engine import (
    CognitiveReasoningEngine,
    ReasoningCapabilityRegistrar,
    ReasoningEventPublisher,
    ReasoningSession,
)
from core.reasoning.reasoning_events import ReasoningEvent
from core.reasoning.reasoning_events import ReasoningEventPublisher as LegacyEventPublisher
from core.reasoning.reasoning_metrics import (
    ReasoningHealthCheck,
    ReasoningMetrics,
    ReasoningMetricsCollector,
)
from core.reasoning.reasoning_strategy import (
    EvidenceFirstStrategyExecutor,
    ExhaustiveStrategyExecutor,
    FocusedStrategyExecutor,
    HypothesisFirstStrategyExecutor,
    ReasoningStrategyExecutor,
)
from core.reasoning.reasoning_trace import ReasoningTrace, ReasoningTraceBuilder
from core.reasoning.reasoning_types import (
    ConfidenceLevel,
    ConfidenceScore,
    Decision,
    DecisionStatus,
    DecisionType,
    Evidence,
    EvidenceRelation,
    EvidenceSource,
    EvidenceType,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    InferenceType,
    ReasoningStage,
    ReasoningState,
    ReasoningStrategy,
    StrategyConfig,
)
from core.reasoning.reflection_engine import (
    ReflectionEngine,
    get_reflection_engine,
    reset_reflection_engine,
)
from core.reasoning.validation_engine import (
    ValidationEngine,
    get_validation_engine,
    reset_validation_engine,
)

# Aliases for backwards compatibility
ReasoningEngine = CognitiveReasoningEngine


__all__ = [
    # Core Engine
    "CognitiveReasoningEngine",
    "ReasoningEngine",  # Alias for backwards compatibility
    "ReasoningSession",
    "ReasoningCapabilityRegistrar",
    "ReasoningEventPublisher",
    # Legacy (for backwards compatibility)
    "LegacyEventPublisher",
    # Adapters
    "ReasoningContextAdapter",
    "ReasoningMemoryAdapter",
    # Capabilities
    "get_reasoning_capabilities",
    # Hypothesis Management
    "HypothesisManager",
    "Hypothesis",
    "HypothesisStatus",
    "HypothesisPriority",
    # Evidence Management
    "EvidenceManager",
    "Evidence",
    "EvidenceType",
    "EvidenceSource",
    "EvidenceRelation",
    # Confidence
    "ConfidenceScore",
    "ConfidenceLevel",
    "ConfidenceCalculator",
    "ConfidenceCalculatorFactory",
    "DefaultConfidenceCalculator",
    "BayesianConfidenceCalculator",
    "DempsterShaferCalculator",
    "probability_to_level",
    # Decision
    "Decision",
    "DecisionType",
    "DecisionStatus",
    # Reasoning Chain
    "ReasoningChain",
    "ReasoningChainBuilder",
    "ReasoningChainManager",
    "ReasoningStep",
    "InferenceType",
    # Trace
    "ReasoningTrace",
    "ReasoningTraceBuilder",
    "ReasoningEvent",
    # Metrics
    "ReasoningMetrics",
    "ReasoningMetricsCollector",
    "ReasoningHealthCheck",
    # Strategy
    "ReasoningStrategy",
    "ReasoningStrategyExecutor",
    "StrategyConfig",
    "ExhaustiveStrategyExecutor",
    "FocusedStrategyExecutor",
    "EvidenceFirstStrategyExecutor",
    "HypothesisFirstStrategyExecutor",
    # State
    "ReasoningState",
    "ReasoningStage",
    # Reasoning Platform Components
    "InferenceEngine",
    "get_inference_engine",
    "reset_inference_engine",
    "EvidenceEngine",
    "get_evidence_engine",
    "reset_evidence_engine",
    "ReflectionEngine",
    "get_reflection_engine",
    "reset_reflection_engine",
    "ConfidenceEngine",
    "get_confidence_engine",
    "reset_confidence_engine",
    "ExplanationEngine",
    "get_explanation_engine",
    "reset_explanation_engine",
    "ValidationEngine",
    "get_validation_engine",
    "reset_validation_engine",
    "DecisionComposer",
    "get_decision_composer",
    "reset_decision_composer",
    # Exceptions
    "ReasoningError",
    "SessionNotFoundError",
    "SessionAlreadyActiveError",
    "HypothesisNotFoundError",
    "EvidenceNotFoundError",
    "DecisionNotFoundError",
    "ChainNotFoundError",
    "InvalidConfidenceError",
    "HypothesisLimitExceededError",
    "ChainValidationError",
    "StrategyNotSupportedError",
    "InsufficientEvidenceError",
    "ReasoningStageError",
]
