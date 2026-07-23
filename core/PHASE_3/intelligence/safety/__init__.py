"""
Safety Engine Module

Complete implementation of EPIC 7 for EREN PHASE 3.

This module provides safety validation:
- Safety Validator
- Hazard Detector
- Critical Alerts
- Human Override

ARCHITECTURE NOTE:
- Severity and RiskLevel are imported from Foundation (single source of truth)
- Safety-specific enums (SafetyCategory, SafetyDecision, AlertLevel) remain local
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import re

# Import shared enums from Foundation (SINGLE SOURCE OF TRUTH)
from core.PHASE_3.intelligence.foundation import Severity, RiskLevel


# Version
__version__ = "1.0.0"


class SafetyCategory(Enum):
    """Safety categories. (Engine-specific enum)"""
    PATIENT_SAFETY = "patient_safety"
    ELECTRICAL_SAFETY = "electrical_safety"
    RADIATION_SAFETY = "radiation_safety"
    BIOLOGICAL_SAFETY = "biological_safety"
    MECHANICAL_SAFETY = "mechanical_safety"
    CHEMICAL_SAFETY = "chemical_safety"
    EQUIPMENT = "equipment"
    SAFETY_SYSTEM = "safety_system"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class SafetyDecision(Enum):
    """Safety decision outcomes. (Engine-specific enum)"""
    ALLOW = "allow"
    ALLOW_WITH_WARNING = "allow_with_warning"
    BLOCK = "block"
    ESCALATE = "escalate"


class AlertLevel(Enum):
    """Alert escalation levels. (Engine-specific enum)"""
    LEVEL_1_SYSTEM = "level_1_system"
    LEVEL_2_SUPERVISOR = "level_2_supervisor"
    LEVEL_3_MANAGEMENT = "level_3_management"
    LEVEL_4_EMERGENCY = "level_4_emergency"


@dataclass
class SafetyBlocker:
    """Safety blocker for dangerous actions."""
    blocker_id: str
    category: SafetyCategory
    reason: str
    severity: Severity  # From Foundation
    action: str
    alternative: str | None = None


@dataclass
class SafetyWarning:
    """Safety warning."""
    warning_id: str
    category: SafetyCategory
    description: str
    recommendation: str


@dataclass
class SafetyResult:
    """Result of safety validation."""
    decision: SafetyDecision
    is_safe: bool
    blockers: list[SafetyBlocker]
    warnings: list[SafetyWarning]
    risk_score: float
    risk_level: RiskLevel  # From Foundation
    recommendations: list[str]
    requires_human_review: bool
    critical_alert_triggered: bool


@dataclass
class CriticalAlert:
    """Critical alert definition."""
    alert_id: str
    level: AlertLevel
    title: str
    description: str
    affected_equipment: list[str]
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.now)


# Blocked actions (hard-coded safety rules)
BLOCKED_PATTERNS = [
    (r"open.*defibrillator", "Opening defibrillator while charged can cause lethal shock"),
    (r"disable.*alarm", "Disabling alarms can cause missed critical events"),
    (r"bypass.*isolation", "Bypassing isolation can cause shock hazard"),
    (r"override.*safety", "Safety system override can cause equipment damage"),
    (r"disable.*ground", "Disabling ground can cause shock hazard"),
    (r"disable.*grounding", "Disabling grounding can cause shock hazard"),
    (r"bypass.*authentication", "Authentication bypass violates security policy"),
    (r"disable.*audit", "Disabling audit violates compliance requirements"),
    (r"remove.*safety", "Removing safety features can cause harm"),
    (r"force.*override", "Forcing override bypasses safety controls"),
]


class SafetyValidator:
    """Validates safety of recommendations."""
    
    def check_blocked_actions(self, action_text: str) -> list[SafetyBlocker]:
        """Check if action is blocked."""
        blockers = []
        action_lower = action_text.lower()
        
        for pattern, reason in BLOCKED_PATTERNS:
            if re.search(pattern, action_lower, re.IGNORECASE):
                blockers.append(SafetyBlocker(
                    blocker_id=f"blocked_{hash(pattern)}",
                    category=SafetyCategory.SAFETY_SYSTEM,
                    reason=reason,
                    severity=Severity.CRITICAL,
                    action=f"Blocked action: {action_text}",
                    alternative="Consult supervisor for authorized procedure",
                ))
        
        return blockers
    
    def check_clinical_safety(self, context: dict) -> list[SafetyWarning]:
        """Check clinical safety constraints."""
        warnings = []
        
        if context.get("alarms_disabled"):
            warnings.append(SafetyWarning(
                warning_id="clinical_alarm_disabled",
                category=SafetyCategory.PATIENT_SAFETY,
                description="Alarms are currently disabled",
                recommendation="Enable alarms or configure appropriate limits",
            ))
        
        return warnings


class HazardDetector:
    """Detects hazards in equipment/context."""
    
    def detect(self, context: dict) -> list[SafetyBlocker]:
        """Detect all hazards."""
        blockers = []
        
        # Check leakage current
        leakage = context.get("leakage_current_ma", 0)
        if leakage > 0.5:
            blockers.append(SafetyBlocker(
                blocker_id="hazard_electrical_shock",
                category=SafetyCategory.ELECTRICAL_SAFETY,
                reason=f"Leakage current {leakage}mA exceeds safe limit of 0.5mA",
                severity=Severity.CRITICAL,
                action="IMMEDIATE REMOVAL FROM SERVICE",
            ))
        
        # Check for damaged insulation
        if context.get("insulation_damaged", False):
            blockers.append(SafetyBlocker(
                blocker_id="hazard_insulation",
                category=SafetyCategory.ELECTRICAL_SAFETY,
                reason="Damaged insulation creates shock hazard",
                severity=Severity.CRITICAL,
                action="IMMEDIATE REMOVAL FROM SERVICE",
            ))
        
        # Check for missing ground
        if context.get("ground_missing", False):
            blockers.append(SafetyBlocker(
                blocker_id="hazard_ground",
                category=SafetyCategory.ELECTRICAL_SAFETY,
                reason="Missing protective ground creates shock hazard",
                severity=Severity.CRITICAL,
                action="IMMEDIATE REMOVAL FROM SERVICE",
            ))
        
        # Check for contaminated equipment
        if context.get("equipment_contaminated", False):
            blockers.append(SafetyBlocker(
                blocker_id="hazard_biohazard",
                category=SafetyCategory.BIOLOGICAL_SAFETY,
                reason="Equipment is contaminated",
                severity=Severity.CRITICAL,
                action="Decontaminate before use",
            ))
        
        return blockers


class RiskAnalyzer:
    """Analyzes risk of recommendations."""
    
    def calculate_risk(
        self,
        blockers: list[SafetyBlocker],
        context: dict,
    ) -> tuple[float, RiskLevel]:
        """Calculate risk score and level."""
        if not blockers:
            return 0.0, RiskLevel.LOW
        
        # Check for critical severity
        if any(b.severity == Severity.CRITICAL for b in blockers):
            return 0.95, RiskLevel.CRITICAL
        
        # Calculate based on severity distribution
        high_count = sum(1 for b in blockers if b.severity == Severity.HIGH)
        medium_count = sum(1 for b in blockers if b.severity == Severity.MEDIUM)
        
        score = min(1.0, (high_count * 0.3) + (medium_count * 0.15))
        
        if score >= 0.7:
            level = RiskLevel.HIGH
        elif score >= 0.4:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return score, level


class CriticalAlertSystem:
    """System for generating critical alerts."""
    
    def should_alert(self, result: SafetyResult) -> bool:
        """Determine if alert should be triggered."""
        if any(b.severity == Severity.CRITICAL for b in result.blockers):
            return True
        if result.risk_score >= 0.8:
            return True
        return False
    
    def determine_alert_level(self, result: SafetyResult) -> AlertLevel:
        """Determine alert level."""
        if any(b.severity == Severity.CRITICAL for b in result.blockers):
            return AlertLevel.LEVEL_4_EMERGENCY
        if result.risk_score >= 0.7:
            return AlertLevel.LEVEL_3_MANAGEMENT
        if result.risk_score >= 0.5:
            return AlertLevel.LEVEL_2_SUPERVISOR
        return AlertLevel.LEVEL_1_SYSTEM
    
    def generate_alert(
        self,
        result: SafetyResult,
        context: dict,
    ) -> CriticalAlert | None:
        """Generate critical alert if needed."""
        if not self.should_alert(result):
            return None
        
        level = self.determine_alert_level(result)
        
        return CriticalAlert(
            alert_id=f"alert_{datetime.now().timestamp()}",
            level=level,
            title=self._generate_title(result),
            description=self._generate_description(result),
            affected_equipment=[context.get("equipment_id", "unknown")],
            recommended_action=result.blockers[0].action if result.blockers else "Review required",
        )
    
    def _generate_title(self, result: SafetyResult) -> str:
        """Generate alert title."""
        return "SAFETY ALERT: " + result.blockers[0].reason[:50] if result.blockers else "Safety Review Required"
    
    def _generate_description(self, result: SafetyResult) -> str:
        """Generate alert description."""
        reasons = [b.reason for b in result.blockers[:3]]
        return "; ".join(reasons)


class SafetyEngine:
    """
    Main safety engine that validates ALL recommendations.
    This is the final gate before any response is issued.
    """
    
    def __init__(self):
        self.validator = SafetyValidator()
        self.hazard_detector = HazardDetector()
        self.risk_analyzer = RiskAnalyzer()
        self.alert_system = CriticalAlertSystem()
    
    async def validate(
        self,
        recommendation: dict,
        context: dict,
    ) -> SafetyResult:
        """
        Validate a recommendation for safety.
        Returns SafetyResult with decision.
        """
        
        action_text = recommendation.get("action", "")
        blockers = []
        warnings = []
        
        # Step 1: Check blocked actions
        blocked = self.validator.check_blocked_actions(action_text)
        blockers.extend(blocked)
        
        # Step 2: Check clinical safety
        clinical_warnings = self.validator.check_clinical_safety(context)
        warnings.extend(clinical_warnings)
        
        # Step 3: Detect hazards
        hazards = self.hazard_detector.detect(context)
        blockers.extend(hazards)
        
        # Step 4: Calculate risk
        risk_score, risk_level = self.risk_analyzer.calculate_risk(blockers, context)
        
        # Step 5: Determine decision
        if blockers:
            decision = SafetyDecision.BLOCK
        elif warnings:
            decision = SafetyDecision.ALLOW_WITH_WARNING
        else:
            decision = SafetyDecision.ALLOW
        
        # Step 6: Determine if human review required
        requires_review = decision == SafetyDecision.ESCALATE or risk_score >= 0.7
        
        # Step 7: Generate recommendations
        recommendations = self._generate_recommendations(decision, blockers, warnings)
        
        return SafetyResult(
            decision=decision,
            is_safe=decision in [SafetyDecision.ALLOW, SafetyDecision.ALLOW_WITH_WARNING],
            blockers=blockers,
            warnings=warnings,
            risk_score=risk_score,
            risk_level=risk_level,
            recommendations=recommendations,
            requires_human_review=requires_review,
            critical_alert_triggered=self.alert_system.should_alert(
                SafetyResult(
                    decision=decision,
                    is_safe=False,
                    blockers=blockers,
                    warnings=warnings,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    recommendations=[],
                    requires_human_review=False,
                    critical_alert_triggered=False,
                )
            ),
        )
    
    def _generate_recommendations(
        self,
        decision: SafetyDecision,
        blockers: list[SafetyBlocker],
        warnings: list[SafetyWarning],
    ) -> list[str]:
        """Generate recommendations based on decision."""
        recommendations = []
        
        if decision == SafetyDecision.BLOCK:
            recommendations.append("Action blocked for safety reasons")
            if blockers and blockers[0].alternative:
                recommendations.append(f"Alternative: {blockers[0].alternative}")
            recommendations.append("Consult supervisor for authorization")
        
        elif decision == SafetyDecision.ALLOW_WITH_WARNING:
            for w in warnings:
                recommendations.append(w.recommendation)
        
        return recommendations
    
    def generate_alert(
        self,
        result: SafetyResult,
        context: dict,
    ) -> CriticalAlert | None:
        """Generate critical alert if needed."""
        return self.alert_system.generate_alert(result, context)


__all__ = [
    # Version
    "__version__",
    # Enums
    "SafetyCategory",
    "Severity",
    "RiskLevel",
    "SafetyDecision",
    "AlertLevel",
    # Data Classes
    "SafetyBlocker",
    "SafetyWarning",
    "SafetyResult",
    "CriticalAlert",
    # Validators
    "SafetyValidator",
    "HazardDetector",
    "RiskAnalyzer",
    "CriticalAlertSystem",
    "SafetyEngine",
]
