"""
Reasoning Module Exceptions

Exception hierarchy for the Reasoning Engine.
"""

from typing import Optional


class ReasoningError(Exception):
    """Base exception for reasoning module."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "REASONING_ERROR"
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# Hypothesis Errors
class HypothesisError(ReasoningError):
    """Base exception for hypothesis operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="HYPOTHESIS_ERROR", **kwargs)


class HypothesisNotFoundError(HypothesisError):
    """Hypothesis not found."""
    
    def __init__(self, hypothesis_id: str):
        super().__init__(
            message=f"Hypothesis not found: {hypothesis_id}",
            error_code="HYPOTHESIS_NOT_FOUND",
            details={"hypothesis_id": hypothesis_id},
        )
        self.hypothesis_id = hypothesis_id


class HypothesisGenerationError(HypothesisError):
    """Error generating hypotheses."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Failed to generate hypotheses: {reason}",
            error_code="HYPOTHESIS_GENERATION_ERROR",
            details={"reason": reason},
        )


# Inference Errors
class InferenceError(ReasoningError):
    """Base exception for inference operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="INFERENCE_ERROR", **kwargs)


class CircularReasoningError(InferenceError):
    """Circular reasoning detected."""
    
    def __init__(self, chain_id: str):
        super().__init__(
            message=f"Circular reasoning detected in chain: {chain_id}",
            error_code="CIRCULAR_REASONING",
            details={"chain_id": chain_id},
        )


class InsufficientEvidenceError(InferenceError):
    """Insufficient evidence for inference."""
    
    def __init__(self, required: int, available: int):
        super().__init__(
            message=f"Insufficient evidence: required {required}, available {available}",
            error_code="INSUFFICIENT_EVIDENCE",
            details={"required": required, "available": available},
        )


class RuleNotFoundError(InferenceError):
    """Inference rule not found."""
    
    def __init__(self, rule_id: str):
        super().__init__(
            message=f"Inference rule not found: {rule_id}",
            error_code="RULE_NOT_FOUND",
            details={"rule_id": rule_id},
        )


# Diagnostic Errors
class DiagnosticError(ReasoningError):
    """Base exception for diagnostic operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="DIAGNOSTIC_ERROR", **kwargs)


class DiagnosisNotFoundError(DiagnosticError):
    """Diagnosis not found."""
    
    def __init__(self, diagnosis_id: str):
        super().__init__(
            message=f"Diagnosis not found: {diagnosis_id}",
            error_code="DIAGNOSIS_NOT_FOUND",
            details={"diagnosis_id": diagnosis_id},
        )


class AmbiguousDiagnosisError(DiagnosticError):
    """Ambiguous diagnosis - multiple equally likely conditions."""
    
    def __init__(self, conditions: list[str]):
        super().__init__(
            message=f"Ambiguous diagnosis: {conditions}",
            error_code="AMBIGUOUS_DIAGNOSIS",
            details={"conditions": conditions},
        )


class RootCauseAnalysisError(DiagnosticError):
    """Error in root cause analysis."""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Root cause analysis failed: {reason}",
            error_code="RCA_ERROR",
            details={"reason": reason},
        )


# Causal Graph Errors
class CausalGraphError(ReasoningError):
    """Base exception for causal graph operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CAUSAL_GRAPH_ERROR", **kwargs)


class CausalNodeNotFoundError(CausalGraphError):
    """Causal node not found."""
    
    def __init__(self, node_id: str):
        super().__init__(
            message=f"Causal node not found: {node_id}",
            error_code="CAUSAL_NODE_NOT_FOUND",
            details={"node_id": node_id},
        )


class CausalCycleError(CausalGraphError):
    """Cycle detected in causal graph."""
    
    def __init__(self, cycle_path: list[str]):
        super().__init__(
            message=f"Cycle detected in causal graph: {cycle_path}",
            error_code="CAUSAL_CYCLE",
            details={"cycle_path": cycle_path},
        )


# Chain Errors
class ChainError(ReasoningError):
    """Base exception for reasoning chain operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CHAIN_ERROR", **kwargs)


class ChainValidationError(ChainError):
    """Chain validation failed."""
    
    def __init__(self, chain_id: str, errors: list[str]):
        super().__init__(
            message=f"Chain validation failed for {chain_id}: {errors}",
            error_code="CHAIN_VALIDATION_ERROR",
            details={"chain_id": chain_id, "errors": errors},
        )


class UnsupportedConclusionError(ChainError):
    """Conclusion without supporting premises."""
    
    def __init__(self, conclusion: str, missing_premises: list[str]):
        super().__init__(
            message=f"Conclusion '{conclusion}' lacks supporting premises: {missing_premises}",
            error_code="UNSUPPORTED_CONCLUSION",
            details={"conclusion": conclusion, "missing_premises": missing_premises},
        )


# Context Errors
class ContextError(ReasoningError):
    """Base exception for context operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CONTEXT_ERROR", **kwargs)


class InsufficientContextError(ContextError):
    """Insufficient context for reasoning."""
    
    def __init__(self, missing_components: list[str]):
        super().__init__(
            message=f"Insufficient context. Missing: {missing_components}",
            error_code="INSUFFICIENT_CONTEXT",
            details={"missing_components": missing_components},
        )


# Pipeline Errors
class PipelineError(ReasoningError):
    """Base exception for pipeline operations."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="PIPELINE_ERROR", **kwargs)


class PipelineStageError(PipelineError):
    """Error in a specific pipeline stage."""
    
    def __init__(self, stage: str, reason: str):
        super().__init__(
            message=f"Pipeline stage '{stage}' failed: {reason}",
            error_code="PIPELINE_STAGE_ERROR",
            details={"stage": stage, "reason": reason},
        )


class ConfidenceThresholdError(PipelineError):
    """Confidence below threshold."""
    
    def __init__(self, confidence: float, threshold: float):
        super().__init__(
            message=f"Confidence {confidence:.2f} below threshold {threshold:.2f}",
            error_code="CONFIDENCE_THRESHOLD",
            details={"confidence": confidence, "threshold": threshold},
        )


__all__ = [
    # Base
    "ReasoningError",
    # Hypothesis
    "HypothesisError",
    "HypothesisNotFoundError",
    "HypothesisGenerationError",
    # Inference
    "InferenceError",
    "CircularReasoningError",
    "InsufficientEvidenceError",
    "RuleNotFoundError",
    # Diagnostic
    "DiagnosticError",
    "DiagnosisNotFoundError",
    "AmbiguousDiagnosisError",
    "RootCauseAnalysisError",
    # Causal
    "CausalGraphError",
    "CausalNodeNotFoundError",
    "CausalCycleError",
    # Chain
    "ChainError",
    "ChainValidationError",
    "UnsupportedConclusionError",
    # Context
    "ContextError",
    "InsufficientContextError",
    # Pipeline
    "PipelineError",
    "PipelineStageError",
    "ConfidenceThresholdError",
]
