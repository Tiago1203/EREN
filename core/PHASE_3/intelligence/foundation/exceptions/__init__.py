"""
Clinical Intelligence Exceptions

Custom exceptions for clinical intelligence components.
"""

from typing import Optional


class ClinicalIntelligenceError(Exception):
    """Error base para Clinical Intelligence."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "CI_UNKNOWN"
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class EvidenceError(ClinicalIntelligenceError):
    """Error relacionado con evidencia."""
    
    def __init__(
        self,
        message: str,
        evidence_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="EVIDENCE_ERROR", **kwargs)
        self.evidence_id = evidence_id


class EvidenceNotFoundError(EvidenceError):
    """Evidencia no encontrada."""
    
    def __init__(self, evidence_id: str):
        super().__init__(
            message=f"Evidence not found: {evidence_id}",
            evidence_id=evidence_id,
        )
        self.error_code = "EVIDENCE_NOT_FOUND"


class EvidenceExpiredError(EvidenceError):
    """Evidencia ha expirado."""
    
    def __init__(self, evidence_id: str, expired_at: str):
        super().__init__(
            message=f"Evidence {evidence_id} expired at {expired_at}",
            evidence_id=evidence_id,
        )
        self.error_code = "EVIDENCE_EXPIRED"
        self.expired_at = expired_at


class SafetyError(ClinicalIntelligenceError):
    """Error relacionado con seguridad."""
    
    def __init__(
        self,
        message: str,
        safety_level: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="SAFETY_ERROR", **kwargs)
        self.safety_level = safety_level


class SafetyViolationError(SafetyError):
    """Violación de seguridad detectada."""
    
    def __init__(
        self,
        message: str,
        safety_level: str,
        check_id: str,
    ):
        super().__init__(message, safety_level=safety_level)
        self.error_code = "SAFETY_VIOLATION"
        self.check_id = check_id


class ValidationError(ClinicalIntelligenceError):
    """Error de validación."""
    
    def __init__(
        self,
        message: str,
        validation_id: Optional[str] = None,
        rule_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.validation_id = validation_id
        self.rule_id = rule_id


class ValidationBlockingError(ValidationError):
    """Error de validación bloqueante."""
    
    def __init__(
        self,
        message: str,
        validation_id: str,
        rule_id: str,
    ):
        super().__init__(
            message=message,
            validation_id=validation_id,
            rule_id=rule_id,
        )
        self.error_code = "VALIDATION_BLOCKING"


class ConfidenceError(ClinicalIntelligenceError):
    """Error relacionado con confianza."""
    
    def __init__(
        self,
        message: str,
        confidence_score: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="CONFIDENCE_ERROR", **kwargs)
        self.confidence_score = confidence_score


class ConfidenceTooLowError(ConfidenceError):
    """Confianza demasiado baja para proporcionar recomendación."""
    
    def __init__(
        self,
        message: str,
        confidence_score: float,
        threshold: float,
    ):
        super().__init__(message, confidence_score=confidence_score)
        self.error_code = "CONFIDENCE_TOO_LOW"
        self.threshold = threshold


class KnowledgeError(ClinicalIntelligenceError):
    """Error relacionado con conocimiento."""
    
    def __init__(self, message: str, concept_id: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="KNOWLEDGE_ERROR", **kwargs)
        self.concept_id = concept_id


class ConceptNotFoundError(KnowledgeError):
    """Concepto médico no encontrado."""
    
    def __init__(self, concept_id: str):
        super().__init__(
            message=f"Concept not found: {concept_id}",
            concept_id=concept_id,
        )
        self.error_code = "CONCEPT_NOT_FOUND"


class ReasoningError(ClinicalIntelligenceError):
    """Error en razonamiento clínico."""
    
    def __init__(
        self,
        message: str,
        reasoning_type: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, error_code="REASONING_ERROR", **kwargs)
        self.reasoning_type = reasoning_type
