"""Safety domain entities."""
from dataclasses import dataclass, field
from enum import Enum


class ViolationType(str, Enum):
    """Type of safety violation."""
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    PHI_DETECTED = "phi_detected"
    PROMPT_INJECTION = "prompt_injection"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    HALLUCINATION = "hallucination"
    MEDICAL_UNSAFE = "medical_unsafe"
    INVALID_CITATION = "invalid_citation"


class Severity(str, Enum):
    """Violation severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Overall risk level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyViolation:
    """A safety violation."""
    type: ViolationType
    severity: Severity
    details: str
    timestamp: str | None = None


@dataclass
class SafetyCheckResult:
    """Result of safety check."""
    is_safe: bool
    risk_level: RiskLevel
    violations: list[SafetyViolation] = field(default_factory=list)
    sanitized_content: str | None = None
    audit_id: str | None = None
    
    @property
    def has_critical_violations(self) -> bool:
        return any(v.severity == Severity.CRITICAL for v in self.violations)
    
    @property
    def has_high_violations(self) -> bool:
        return any(v.severity == Severity.HIGH for v in self.violations)
