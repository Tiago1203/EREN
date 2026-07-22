"""Safety domain services."""
from dataclasses import dataclass
from typing import Protocol, Any

from core.PHASE_2.cognitive.safety.domain.entities import (
    SafetyCheckResult,
    SafetyViolation,
    ViolationType,
    Severity,
    RiskLevel,
)


class ContentFilter(Protocol):
    """Protocol for content filtering."""
    async def check(self, content: str) -> SafetyCheckResult:
        ...


class PHIDetector(Protocol):
    """Protocol for PHI detection."""
    async def detect(self, content: str) -> Any:
        ...


class RateLimiter(Protocol):
    """Protocol for rate limiting."""
    async def check(self, user_id: str) -> Any:
        ...


@dataclass
class SafetyContext:
    """Context for safety checks."""
    user_id: str
    tenant_id: str
    conversation_id: str
    domain: str = "biomedical"


class SafetyEngine:
    """Main safety validation engine."""
    
    def __init__(
        self,
        content_filter: ContentFilter | None = None,
        phi_detector: PHIDetector | None = None,
        rate_limiter: RateLimiter | None = None,
    ):
        self.content_filter = content_filter
        self.phi_detector = phi_detector
        self.rate_limiter = rate_limiter
    
    async def validate_input(
        self,
        message: str,
        context: SafetyContext,
    ) -> SafetyCheckResult:
        """Pre-processing safety checks."""
        violations = []
        
        # Basic validation - all inputs must be non-empty
        if not message or not message.strip():
            violations.append(SafetyViolation(
                type=ViolationType.INAPPROPRIATE_CONTENT,
                severity=Severity.HIGH,
                details="Empty message",
            ))
        
        # Basic length check
        if len(message) > 10000:
            violations.append(SafetyViolation(
                type=ViolationType.INAPPROPRIATE_CONTENT,
                severity=Severity.MEDIUM,
                details="Message too long (max 10000 chars)",
            ))
        
        # Check rate limit if available
        if self.rate_limiter:
            rate_result = await self.rate_limiter.check(context.user_id)
            if rate_result.exceeded:
                violations.append(SafetyViolation(
                    type=ViolationType.RATE_LIMIT_EXCEEDED,
                    severity=Severity.LOW,
                    details=f"Rate limit exceeded",
                ))
        
        is_safe = not any(v.severity == Severity.CRITICAL for v in violations)
        risk_level = self._calculate_risk_level(violations)
        
        return SafetyCheckResult(
            is_safe=is_safe,
            risk_level=risk_level,
            violations=violations,
        )
    
    async def validate_output(
        self,
        response: str,
        context: SafetyContext,
    ) -> SafetyCheckResult:
        """Post-processing safety checks."""
        violations = []
        
        # Basic validation
        if not response:
            violations.append(SafetyViolation(
                type=ViolationType.HALLUCINATION,
                severity=Severity.HIGH,
                details="Empty response",
            ))
        
        is_safe = not any(
            v.severity in [Severity.CRITICAL, Severity.HIGH] 
            for v in violations
        )
        risk_level = self._calculate_risk_level(violations)
        
        return SafetyCheckResult(
            is_safe=is_safe,
            risk_level=risk_level,
            violations=violations,
        )
    
    def _calculate_risk_level(self, violations: list[SafetyViolation]) -> RiskLevel:
        """Calculate overall risk level from violations."""
        if any(v.severity == Severity.CRITICAL for v in violations):
            return RiskLevel.CRITICAL
        elif any(v.severity == Severity.HIGH for v in violations):
            return RiskLevel.HIGH
        elif any(v.severity == Severity.MEDIUM for v in violations):
            return RiskLevel.MEDIUM
        elif any(v.severity == Severity.LOW for v in violations):
            return RiskLevel.LOW
        return RiskLevel.LOW
