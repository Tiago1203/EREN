"""
Biomedical Rules Engine Module

Complete implementation of a Drools-style rules engine for
biomedical validation and compliance checking.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Any
from collections import defaultdict


class RuleCategory(Enum):
    """Categories of rules."""
    CLINICAL = "clinical"
    ENGINEERING = "engineering"
    SAFETY = "safety"
    POLICY = "policy"
    REGULATORY = "regulatory"
    MANUFACTURER = "manufacturer"


class ConditionOperator(Enum):
    """Operators for condition evaluation."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    CONTAINS = "contains"
    IN = "in"
    BETWEEN = "between"
    MATCHES_PATTERN = "matches_pattern"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


class ConditionConnector(Enum):
    """Connectors between conditions."""
    AND = "and"
    OR = "or"


class ActionType(Enum):
    """Types of rule actions."""
    ALERT = "alert"
    RECOMMENDATION = "recommendation"
    COMPLIANCE_WARNING = "compliance_warning"
    SAFETY_STOP = "safety_stop"
    MAINTENANCE_REQUIRED = "maintenance_required"
    DOCUMENTATION_REQUIRED = "documentation_required"


@dataclass(frozen=True)
class Condition:
    """Condition in a rule."""
    attribute: str
    operator: ConditionOperator
    value: Any
    connector: ConditionConnector = ConditionConnector.AND
    
    def __post_init__(self):
        if isinstance(self.operator, str):
            object.__setattr__(self, 'operator', ConditionOperator(self.operator))
        if isinstance(self.connector, str):
            object.__setattr__(self, 'connector', ConditionConnector(self.connector))


@dataclass(frozen=True)
class RuleAction:
    """Action triggered by a rule."""
    action_type: ActionType
    message: str
    priority: int  # 1=highest, 4=lowest
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.action_type, str):
            object.__setattr__(self, 'action_type', ActionType(self.action_type))


@dataclass(frozen=True)
class Rule:
    """Biomedical rule."""
    rule_id: str
    name: str
    description: str
    category: RuleCategory
    priority: int  # 1=highest, 4=lowest
    conditions: list[Condition]
    actions: list[RuleAction]
    source: str
    effective_date: date
    expiration_date: Optional[date] = None
    enabled: bool = True
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.category, str):
            object.__setattr__(self, 'category', RuleCategory(self.category))
    
    def is_effective(self) -> bool:
        """Check if rule is currently effective."""
        today = date.today()
        if self.expiration_date and today > self.expiration_date:
            return False
        if today < self.effective_date:
            return False
        return self.enabled


@dataclass(frozen=True)
class RuleMatch:
    """Result of rule evaluation."""
    rule: Rule
    matched: bool
    conditions_met: list[Condition]
    conditions_not_met: list[Condition]
    triggered_actions: list[RuleAction]


class ConditionEvaluator:
    """Evaluates individual conditions."""
    
    def evaluate(self, condition: Condition, context: dict) -> bool:
        """Evaluate a condition against context."""
        value = context.get(condition.attribute)
        
        # Handle EXISTS/NOT_EXISTS
        if condition.operator == ConditionOperator.EXISTS:
            return value is not None
        if condition.operator == ConditionOperator.NOT_EXISTS:
            return value is None
        
        # If value doesn't exist, condition is not met
        if value is None:
            return False
        
        return self._evaluate_operator(condition.operator, value, condition.value)
    
    def _evaluate_operator(
        self,
        operator: ConditionOperator,
        actual: Any,
        expected: Any,
    ) -> bool:
        """Evaluate operator against values."""
        if operator == ConditionOperator.EQUALS:
            return actual == expected
        elif operator == ConditionOperator.NOT_EQUALS:
            return actual != expected
        elif operator == ConditionOperator.GREATER_THAN:
            return actual > expected
        elif operator == ConditionOperator.LESS_THAN:
            return actual < expected
        elif operator == ConditionOperator.GREATER_OR_EQUAL:
            return actual >= expected
        elif operator == ConditionOperator.LESS_OR_EQUAL:
            return actual <= expected
        elif operator == ConditionOperator.CONTAINS:
            return expected in actual if hasattr(actual, '__contains__') else False
        elif operator == ConditionOperator.IN:
            return actual in expected
        elif operator == ConditionOperator.MATCHES_PATTERN:
            import re
            return bool(re.match(expected, str(actual)))
        
        return False


class RulesEngine:
    """
    Drools-style rules engine for biomedical validation.
    """
    
    def __init__(self):
        self._rules: list[Rule] = []
        self._rules_by_category: dict[RuleCategory, list[Rule]] = defaultdict(list)
        self._evaluator = ConditionEvaluator()
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the engine."""
        self._rules.append(rule)
        self._rules_by_category[rule.category].append(rule)
    
    def add_rules(self, rules: list[Rule]) -> None:
        """Add multiple rules."""
        for rule in rules:
            self.add_rule(rule)
    
    async def evaluate(
        self,
        context: dict,
        categories: list[RuleCategory] | None = None,
    ) -> list[RuleMatch]:
        """Evaluate rules against context."""
        matches = []
        
        # Select rules to evaluate
        if categories:
            rules_to_evaluate = []
            for cat in categories:
                rules_to_evaluate.extend(self._rules_by_category.get(cat, []))
        else:
            rules_to_evaluate = self._rules
        
        for rule in rules_to_evaluate:
            if not rule.is_effective():
                continue
            
            match = await self._evaluate_rule(rule, context)
            matches.append(match)
        
        # Sort by priority
        matches.sort(key=lambda m: m.rule.priority)
        
        return matches
    
    async def _evaluate_rule(
        self,
        rule: Rule,
        context: dict,
    ) -> RuleMatch:
        """Evaluate a single rule."""
        conditions_met = []
        conditions_not_met = []
        
        for condition in rule.conditions:
            if self._evaluator.evaluate(condition, context):
                conditions_met.append(condition)
            else:
                conditions_not_met.append(condition)
        
        # Determine if rule matched
        matched = len(conditions_not_met) == 0
        
        # Get triggered actions
        triggered_actions = []
        if matched:
            triggered_actions = rule.actions
        
        return RuleMatch(
            rule=rule,
            matched=matched,
            conditions_met=conditions_met,
            conditions_not_met=conditions_not_met,
            triggered_actions=triggered_actions,
        )
    
    def get_rules_by_category(
        self,
        category: RuleCategory,
    ) -> list[Rule]:
        """Get all rules in a category."""
        return self._rules_by_category.get(category, [])
    
    def get_rule(self, rule_id: str) -> Rule | None:
        """Get a rule by ID."""
        for rule in self._rules:
            if rule.rule_id == rule_id:
                return rule
        return None


# Standard biomedical rules
def get_standard_rules() -> list[Rule]:
    """Get standard biomedical rules."""
    today = date.today()
    
    return [
        # Engineering Rules
        Rule(
            rule_id="IEC60601_CALIBRATION",
            name="Equipment Calibration Required",
            description="Equipment must be calibrated within specified intervals",
            category=RuleCategory.ENGINEERING,
            priority=2,
            conditions=[
                Condition("equipment_type", ConditionOperator.EQUALS, "Medical Device"),
                Condition("days_since_calibration", ConditionOperator.GREATER_THAN, 180),
            ],
            actions=[
                RuleAction(
                    ActionType.MAINTENANCE_REQUIRED,
                    "Schedule calibration within 30 days",
                    priority=2,
                ),
            ],
            source="IEC 60601-1 Clause 4.4",
            effective_date=today,
        ),
        Rule(
            rule_id="BATTERY_CYCLES",
            name="Battery Replacement Required",
            description="Battery must be replaced after max cycles",
            category=RuleCategory.ENGINEERING,
            priority=2,
            conditions=[
                Condition("battery_cycles", ConditionOperator.GREATER_THAN, 500),
            ],
            actions=[
                RuleAction(
                    ActionType.RECOMMENDATION,
                    "Replace battery immediately",
                    priority=2,
                ),
            ],
            source="Manufacturer Guidelines",
            effective_date=today,
        ),
        
        # Safety Rules
        Rule(
            rule_id="SAFETY_LEAKAGE_CURRENT",
            name="Critical Risk - Leakage Current",
            description="Equipment with excessive leakage current is unsafe",
            category=RuleCategory.SAFETY,
            priority=1,
            conditions=[
                Condition("leakage_current_ma", ConditionOperator.GREATER_THAN, 0.5),
            ],
            actions=[
                RuleAction(
                    ActionType.SAFETY_STOP,
                    "IMMEDIATELY REMOVE FROM SERVICE",
                    priority=1,
                ),
            ],
            source="IEC 60601-1 Clause 8.7",
            effective_date=today,
        ),
        Rule(
            rule_id="SAFETY_GROUNDING",
            name="Equipment Grounding Required",
            description="Equipment must have proper grounding",
            category=RuleCategory.SAFETY,
            priority=1,
            conditions=[
                Condition("ground_resistance_ohm", ConditionOperator.GREATER_THAN, 0.2),
            ],
            actions=[
                RuleAction(
                    ActionType.SAFETY_STOP,
                    "Equipment has unsafe grounding",
                    priority=1,
                ),
            ],
            source="IEC 60601-1 Clause 8.6",
            effective_date=today,
        ),
        
        # Clinical Rules
        Rule(
            rule_id="CLINICAL_ALARM_DELAY",
            name="Alarm Delay Exceeded",
            description="Alarm response time exceeds recommended threshold",
            category=RuleCategory.CLINICAL,
            priority=3,
            conditions=[
                Condition("alarm_delay_seconds", ConditionOperator.GREATER_THAN, 30),
            ],
            actions=[
                RuleAction(
                    ActionType.ALERT,
                    "Review alarm delays and response protocols",
                    priority=3,
                ),
            ],
            source="AAMI Alarm Safety Guidelines",
            effective_date=today,
        ),
        
        # Regulatory Rules
        Rule(
            rule_id="REG_MAINTENANCE_LOGS",
            name="Maintenance Documentation Required",
            description="Equipment must have complete maintenance records",
            category=RuleCategory.REGULATORY,
            priority=3,
            conditions=[
                Condition("maintenance_log_complete", ConditionOperator.EQUALS, False),
            ],
            actions=[
                RuleAction(
                    ActionType.DOCUMENTATION_REQUIRED,
                    "Complete maintenance documentation",
                    priority=3,
                ),
            ],
            source="FDA 21 CFR Part 820",
            effective_date=today,
        ),
    ]


__all__ = [
    "RuleCategory",
    "ConditionOperator",
    "ConditionConnector",
    "ActionType",
    "Condition",
    "RuleAction",
    "Rule",
    "RuleMatch",
    "ConditionEvaluator",
    "RulesEngine",
    "get_standard_rules",
]
