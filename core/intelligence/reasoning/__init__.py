"""
Reasoning Engine Module

Complete implementation of EPIC 2 for EREN PHASE 3.

This module provides the reasoning capabilities of EREN including:
- Hypothesis Engine
- Inference Engine
- Diagnostic Engine
- Reasoning Chains
- Causal Graph
- Context Builder
- Reasoning Pipeline
"""

# Version
__version__ = "1.0.0"

# Hypothesis Engine
from core.intelligence.reasoning.hypothesis import (
    SeverityLevel,
    HypothesisStatus,
    Symptom,
    Evidence,
    Hypothesis,
    HypothesisSet,
    HypothesisEvaluation,
    HypothesisGenerator,
    HypothesisEvaluator,
    HypothesisPrioritizer,
    HypothesisEngine,
)

# Inference Engine
from core.intelligence.reasoning.inference import (
    InferenceType,
    Fact,
    InferenceRule,
    InferenceStep,
    InferenceResult,
    ProofTree,
    ForwardChaining,
    BackwardChaining,
    AbductiveReasoning,
    BayesianInference,
    InferenceEngine,
)

# Diagnostic Engine
from core.intelligence.reasoning.diagnostic import (
    UrgencyLevel,
    DiagnosticStatus,
    Recommendation,
    Diagnosis,
    DifferentialDiagnosis,
    RootCauseAnalysis,
    SymptomAnalysis,
    SymptomAnalyzer,
    DifferentialDiagnosisEngine,
    RootCauseAnalyzer,
    DiagnosticEngine,
)

# Causal Graph
from core.intelligence.reasoning.causal import (
    CausalType,
    CausalNodeType,
    TemporalRelation,
    CausalNode,
    CausalEdge,
    CausalPath,
    CausalAnalysis,
    CausalGraph,
    CausalReasoner,
)

# Reasoning Chains
from core.intelligence.reasoning.chains import (
    ChainType,
    StepType,
    ReasoningStep,
    ReasoningChain,
    ChainBuilder,
    ChainValidator,
    ChainExporter,
)

# Context Builder
from core.intelligence.reasoning.context import (
    MemoryContext,
    KnowledgeContext,
    DomainContext,
    ConversationContext,
    ReasoningContext,
    ContextBuilder,
)

# Pipeline
from core.intelligence.reasoning.pipeline import (
    ReasoningInput,
    ReasoningOutput,
    ReasoningPipeline,
    ReasoningEngine,
)

# Exceptions
from core.intelligence.reasoning.exceptions import (
    ReasoningError,
    HypothesisError,
    HypothesisNotFoundError,
    HypothesisGenerationError,
    InferenceError,
    CircularReasoningError,
    InsufficientEvidenceError,
    RuleNotFoundError,
    DiagnosticError,
    DiagnosisNotFoundError,
    AmbiguousDiagnosisError,
    RootCauseAnalysisError,
    CausalGraphError,
    CausalNodeNotFoundError,
    CausalCycleError,
    ChainError,
    ChainValidationError,
    UnsupportedConclusionError,
    ContextError,
    InsufficientContextError,
    PipelineError,
    PipelineStageError,
    ConfidenceThresholdError,
)

__all__ = [
    # Version
    "__version__",
    # Hypothesis
    "SeverityLevel",
    "HypothesisStatus",
    "Symptom",
    "Evidence",
    "Hypothesis",
    "HypothesisSet",
    "HypothesisEvaluation",
    "HypothesisGenerator",
    "HypothesisEvaluator",
    "HypothesisPrioritizer",
    "HypothesisEngine",
    # Inference
    "InferenceType",
    "Fact",
    "InferenceRule",
    "InferenceStep",
    "InferenceResult",
    "ProofTree",
    "ForwardChaining",
    "BackwardChaining",
    "AbductiveReasoning",
    "BayesianInference",
    "InferenceEngine",
    # Diagnostic
    "UrgencyLevel",
    "DiagnosticStatus",
    "Recommendation",
    "Diagnosis",
    "DifferentialDiagnosis",
    "RootCauseAnalysis",
    "SymptomAnalysis",
    "SymptomAnalyzer",
    "DifferentialDiagnosisEngine",
    "RootCauseAnalyzer",
    "DiagnosticEngine",
    # Causal
    "CausalType",
    "CausalNodeType",
    "TemporalRelation",
    "CausalNode",
    "CausalEdge",
    "CausalPath",
    "CausalAnalysis",
    "CausalGraph",
    "CausalReasoner",
    # Chains
    "ChainType",
    "StepType",
    "ReasoningStep",
    "ReasoningChain",
    "ChainBuilder",
    "ChainValidator",
    "ChainExporter",
    # Context
    "MemoryContext",
    "KnowledgeContext",
    "DomainContext",
    "ConversationContext",
    "ReasoningContext",
    "ContextBuilder",
    # Pipeline
    "ReasoningInput",
    "ReasoningOutput",
    "ReasoningPipeline",
    "ReasoningEngine",
    # Exceptions
    "ReasoningError",
    "HypothesisError",
    "HypothesisNotFoundError",
    "HypothesisGenerationError",
    "InferenceError",
    "CircularReasoningError",
    "InsufficientEvidenceError",
    "RuleNotFoundError",
    "DiagnosticError",
    "DiagnosisNotFoundError",
    "AmbiguousDiagnosisError",
    "RootCauseAnalysisError",
    "CausalGraphError",
    "CausalNodeNotFoundError",
    "CausalCycleError",
    "ChainError",
    "ChainValidationError",
    "UnsupportedConclusionError",
    "ContextError",
    "InsufficientContextError",
    "PipelineError",
    "PipelineStageError",
    "ConfidenceThresholdError",
]
