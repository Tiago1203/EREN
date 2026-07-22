"""
Inference Engine Module

Exports for forward/backward chaining, abductive reasoning, and Bayesian inference.
"""

from core.PHASE_3.intelligence.reasoning.inference.inference_engine import (
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

__all__ = [
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
]
