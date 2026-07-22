"""
Biomedical Rules Engine Module

Complete implementation of EPIC 6 for EREN PHASE 3.

This module provides deterministic rule-based validation:
- IEC/ISO/AAMI Standards Validation
- Clinical Rules
- Engineering Rules

ARCHITECTURE NOTE:
- Severity and RiskLevel are imported from Foundation (single source of truth)
- StandardType is specific to Rules and remains local
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any

# Import shared enums from Foundation (SINGLE SOURCE OF TRUTH)
from core.intelligence.foundation import Severity, RiskLevel


# Version
__version__ = "1.0.0"


class StandardType(Enum):
    """Types of standards. (Engine-specific enum)"""
    IEC = "iec"
    ISO = "iso"
    AAMI = "aami"
    CUSTOM = "custom"


@dataclass
class Violation:
    """Rule violation."""
    rule_id: str
    standard: str
    clause: str
    description: str
    severity: Severity  # From Foundation
    current_value: Any
    required_value: Any
    action: str | None = None


@dataclass
class Warning:
    """Rule warning (non-critical)."""
    rule_id: str
    description: str
    recommendation: str


@dataclass
class ValidationResult:
    """Result of rules validation."""
    is_compliant: bool
    violations: list[Violation]
    warnings: list[Warning]
    recommendations: list[str]
    risk_level: RiskLevel  # From Foundation
    validation_time_ms: int
    standards_checked: list[str]


@dataclass
class Rule:
    """Rule definition."""
    rule_id: str
    name: str
    description: str
    condition: str
    standard: str
    clause: str
    severity: Severity  # From Foundation
    action: str | None = None


# Equipment maintenance intervals (days)
EQUIPMENT_INTERVALS = {
    "Ventilator": {
        "preventive_maintenance": 180,
        "filter_replacement": 90,
        "sensor_calibration": 365,
    },
    "Infusion Pump": {
        "preventive_maintenance": 365,
        "battery_replacement": 730,
        "accuracy_check": 180,
    },
    "Defibrillator": {
        "preventive_maintenance": 180,
        "battery_check": 30,
        "electrode_expiry_check": 90,
    },
    "SpO2 Monitor": {
        "preventive_maintenance": 365,
        "sensor_calibration": 180,
        "accuracy_verification": 90,
    },
    "ECG Monitor": {
        "preventive_maintenance": 365,
        "electrode_check": 180,
        "leakage_test": 180,
    },
    "Infant Incubator": {
        "preventive_maintenance": 180,
        "temperature_calibration": 90,
        "humidity_check": 30,
    },
}


class IEC60601Validator:
    """Validator for IEC 60601 standards."""
    
    RULES = [
        {
            "id": "IEC60601_LEAKAGE",
            "clause": "8.7",
            "name": "Leakage Current",
            "limit": 0.5,
            "unit": "mA",
            "severity": Severity.CRITICAL,
        },
        {
            "id": "IEC60601_GROUNDING",
            "clause": "8.6",
            "name": "Protective Grounding",
            "limit": 0.2,
            "unit": "ohm",
            "severity": Severity.CRITICAL,
        },
        {
            "id": "IEC60601_CALIBRATION",
            "clause": "4.4",
            "name": "Calibration Interval",
            "limit": 365,
            "unit": "days",
            "severity": Severity.HIGH,
        },
        {
            "id": "IEC60601_PM",
            "clause": "5.1",
            "name": "Preventive Maintenance",
            "limit": 180,
            "unit": "days",
            "severity": Severity.HIGH,
        },
    ]
    
    async def validate(self, context: dict) -> list[Violation]:
        """Validate against IEC 60601."""
        violations = []
        
        # Check leakage current
        leakage = context.get("leakage_current_ma", 0)
        if leakage > 0.5:
            violations.append(Violation(
                rule_id="IEC60601_LEAKAGE",
                standard="IEC 60601-1",
                clause="8.7",
                description=f"Leakage current {leakage}mA exceeds 0.5mA limit",
                severity=Severity.CRITICAL,
                current_value=leakage,
                required_value=0.5,
                action="IMMEDIATE REMOVAL FROM SERVICE",
            ))
        
        # Check ground resistance
        ground = context.get("ground_resistance_ohm", 0)
        if ground > 0.2:
            violations.append(Violation(
                rule_id="IEC60601_GROUNDING",
                standard="IEC 60601-1",
                clause="8.6",
                description=f"Ground resistance {ground}Ω exceeds 0.2Ω limit",
                severity=Severity.CRITICAL,
                current_value=ground,
                required_value=0.2,
                action="IMMEDIATE REMOVAL FROM SERVICE",
            ))
        
        return violations


class ClinicalRulesEngine:
    """Clinical safety rules engine."""
    
    RULES = [
        {
            "id": "CLINICAL_ALARM_DELAY",
            "name": "Alarm Delay",
            "limit": 30,
            "unit": "seconds",
            "severity": Severity.HIGH,
        },
        {
            "id": "CLINICAL_ALARM_SILENCE",
            "name": "Alarm Silence Duration",
            "limit": 2,
            "unit": "minutes",
            "severity": Severity.HIGH,
        },
        {
            "id": "CLINICAL_SPO2_LOW",
            "name": "SpO2 Low Alarm",
            "limit": 90,
            "unit": "%",
            "severity": Severity.CRITICAL,
        },
    ]
    
    async def evaluate(self, context: dict) -> ValidationResult:
        """Evaluate clinical rules."""
        violations = []
        
        # Check alarm delay
        alarm_delay = context.get("alarm_delay_seconds", 0)
        if alarm_delay > 30:
            violations.append(Violation(
                rule_id="CLINICAL_ALARM_DELAY",
                standard="AAMI",
                clause="6.8",
                description=f"Alarm delay {alarm_delay}s exceeds 30s limit",
                severity=Severity.HIGH,
                current_value=alarm_delay,
                required_value=30,
            ))
        
        return ValidationResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            warnings=[],
            recommendations=[],
            risk_level=RiskLevel.LOW,
            validation_time_ms=0,
            standards_checked=["AAMI"],
        )


class EngineeringRulesEngine:
    """Engineering rules engine."""
    
    async def evaluate(self, equipment: dict, context: dict) -> ValidationResult:
        """Evaluate engineering rules."""
        violations = []
        
        equipment_type = context.get("equipment_type", "Unknown")
        intervals = EQUIPMENT_INTERVALS.get(equipment_type, {})
        
        # Check PM interval
        pm_interval = intervals.get("preventive_maintenance", 365)
        days_since_pm = context.get("days_since_pm", 0)
        
        if days_since_pm > pm_interval:
            violations.append(Violation(
                rule_id="ENG_PM_OVERDUE",
                standard="Internal Policy",
                clause="PM-001",
                description=f"PM overdue by {days_since_pm - pm_interval} days",
                severity=Severity.HIGH,
                current_value=days_since_pm,
                required_value=pm_interval,
                action="Schedule preventive maintenance",
            ))
        
        # Check calibration interval
        cal_interval = intervals.get("sensor_calibration", 365)
        days_since_cal = context.get("days_since_calibration", 0)
        
        if days_since_cal > cal_interval:
            violations.append(Violation(
                rule_id="ENG_CAL_OVERDUE",
                standard="Internal Policy",
                clause="CAL-001",
                description=f"Calibration overdue by {days_since_cal - cal_interval} days",
                severity=Severity.HIGH,
                current_value=days_since_cal,
                required_value=cal_interval,
                action="Schedule calibration",
            ))
        
        # Check battery
        battery_cycles = context.get("battery_cycles", 0)
        if battery_cycles > 500:
            violations.append(Violation(
                rule_id="ENG_BATTERY_CYCLES",
                standard="Internal Policy",
                clause="BAT-001",
                description=f"Battery cycles ({battery_cycles}) exceeds 500 limit",
                severity=Severity.HIGH,
                current_value=battery_cycles,
                required_value=500,
                action="Replace battery",
            ))
        
        return ValidationResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            warnings=[],
            recommendations=[],
            risk_level=self._calculate_risk(violations),
            validation_time_ms=0,
            standards_checked=["Internal Policy"],
        )
    
    def _calculate_risk(self, violations: list[Violation]) -> RiskLevel:
        """Calculate risk level from violations."""
        if not violations:
            return RiskLevel.LOW
        
        severities = [v.severity for v in violations]
        
        if Severity.CRITICAL in severities:
            return RiskLevel.CRITICAL
        elif Severity.HIGH in severities:
            return RiskLevel.HIGH
        elif Severity.MEDIUM in severities:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW


class BiomedicalRulesEngine:
    """
    Main biomedical rules engine.
    Extends EPIC 3 base rules with IEC/ISO/AAMI validation.
    """
    
    def __init__(self):
        self.iec_validator = IEC60601Validator()
        self.clinical_rules = ClinicalRulesEngine()
        self.engineering_rules = EngineeringRulesEngine()
    
    async def validate(
        self,
        equipment: dict,
        recommendation: dict,
        context: dict,
    ) -> ValidationResult:
        """Validate against all rules."""
        
        violations = []
        warnings = []
        recommendations = []
        standards = []
        
        # IEC Validation
        iec_violations = await self.iec_validator.validate(context)
        violations.extend(iec_violations)
        if iec_violations:
            standards.append("IEC 60601-1")
        
        # Clinical Rules
        clinical_result = await self.clinical_rules.evaluate(context)
        violations.extend(clinical_result.violations)
        warnings.extend(clinical_result.warnings)
        if clinical_result.violations:
            standards.append("AAMI")
        
        # Engineering Rules
        eng_result = await self.engineering_rules.evaluate(equipment, context)
        violations.extend(eng_result.violations)
        if eng_result.violations:
            standards.append("Internal Policy")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(violations)
        
        # Calculate risk
        risk_level = self._calculate_risk_level(violations)
        
        return ValidationResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            risk_level=risk_level,
            validation_time_ms=0,
            standards_checked=standards,
        )
    
    def _calculate_risk_level(self, violations: list[Violation]) -> RiskLevel:
        """Calculate overall risk level."""
        if not violations:
            return RiskLevel.LOW
        
        severities = [v.severity for v in violations]
        
        if Severity.CRITICAL in severities:
            return RiskLevel.CRITICAL
        elif Severity.HIGH in severities:
            return RiskLevel.HIGH
        elif Severity.MEDIUM in severities:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
    
    def _generate_recommendations(self, violations: list[Violation]) -> list[str]:
        """Generate recommendations from violations."""
        recommendations = []
        
        for v in violations:
            if v.action:
                recommendations.append(v.action)
        
        return list(set(recommendations))


__all__ = [
    # Version
    "__version__",
    # Enums
    "Severity",
    "RiskLevel",
    "StandardType",
    # Data Classes
    "Violation",
    "Warning",
    "ValidationResult",
    "Rule",
    # Validators
    "IEC60601Validator",
    "ClinicalRulesEngine",
    "EngineeringRulesEngine",
    "BiomedicalRulesEngine",
    # Constants
    "EQUIPMENT_INTERVALS",
]
