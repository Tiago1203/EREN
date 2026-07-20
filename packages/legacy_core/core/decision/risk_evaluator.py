"""Risk Evaluator for EREN Cognitive Decision Engine.

Evaluates risk for decisions and plans.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.decision.types import (
    DecisionPlan,
    DecisionTask,
    RiskAssessment,
    RiskLevel,
)

if TYPE_CHECKING:
    pass


class RiskEvaluator:
    """Evaluates risk for decisions.

    The Risk Evaluator does NOT:
    - Execute tasks
    - Make decisions

    It ONLY:
    - Assesses risk levels
    - Identifies risk factors
    - Recommends mitigation
    """

    def __init__(self):
        """Initialize risk evaluator."""
        self._risk_weights = {
            "critical_activity": 0.5,
            "medical_procedure": 0.4,
            "data_modification": 0.3,
            "external_call": 0.2,
            "long_duration": 0.1,
            "complex_dependency": 0.15,
        }

    def evaluate_plan(
        self,
        plan: DecisionPlan,
        tasks: list[DecisionTask],
    ) -> RiskAssessment:
        """Evaluate overall plan risk.

        Args:
            plan: Decision plan.
            tasks: Tasks in plan.

        Returns:
            Risk assessment.
        """
        risk_factors = []
        total_risk_score = 0.0
        weight_sum = 0.0

        # Check each task for risk factors
        for task in tasks:
            factor = self._evaluate_task_risk(task)
            if factor:
                risk_factors.append(factor)
                risk_score = self._get_risk_score(factor["type"])
                weight = self._risk_weights.get(factor["type"], 0.1)
                total_risk_score += risk_score * weight
                weight_sum += weight

        # Calculate overall risk
        if weight_sum > 0:
            normalized_score = total_risk_score / weight_sum
        else:
            normalized_score = 0.0

        # Determine risk level
        risk_level = self._score_to_level(normalized_score)

        # Generate mitigation strategies
        mitigation = self._generate_mitigation(risk_level, risk_factors)

        # Check if escalation required
        requires_escalation = (
            risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] or
            any(f["type"] == "medical_procedure" for f in risk_factors)
        )

        return RiskAssessment(
            overall_risk=risk_level,
            risk_score=normalized_score,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation,
            requires_escalation=requires_escalation,
            escalation_reason="High-risk decision requires human approval" if requires_escalation else "",
        )

    def evaluate_task(self, task: DecisionTask) -> RiskLevel:
        """Evaluate single task risk.

        Args:
            task: Task to evaluate.

        Returns:
            Risk level.
        """
        factor = self._evaluate_task_risk(task)
        if factor:
            return self._get_risk_level(factor["score"])
        return RiskLevel.LOW

    def _evaluate_task_risk(self, task: DecisionTask) -> dict | None:
        """Evaluate a single task's risk."""
        risk_indicators = []

        # Check task type
        high_risk_types = ["medical", "procedure", "treatment", "surgery"]
        if any(t in task.task_type.lower() for t in high_risk_types):
            risk_indicators.append("medical_procedure")

        # Check task name
        critical_keywords = ["critical", "emergency", "urgent", "life"]
        if any(kw in task.name.lower() for kw in critical_keywords):
            risk_indicators.append("critical_activity")

        # Check modification actions
        modify_keywords = ["delete", "update", "modify", "create", "write"]
        if any(kw in task.name.lower() for kw in modify_keywords):
            risk_indicators.append("data_modification")

        # Check external calls
        external_keywords = ["api", "call", "request", "fetch", "http"]
        if any(kw in task.name.lower() for kw in external_keywords):
            risk_indicators.append("external_call")

        # Check duration
        if task.estimated_time_seconds > 300:  # > 5 minutes
            risk_indicators.append("long_duration")

        # Check dependencies
        if len(task.depends_on) > 3:
            risk_indicators.append("complex_dependency")

        if not risk_indicators:
            return None

        # Calculate score
        score = sum(self._risk_weights.get(ind, 0.1) for ind in risk_indicators)
        score = min(score, 1.0)

        return {
            "type": risk_indicators[0],  # Primary risk type
            "all_types": risk_indicators,
            "score": score,
            "task_id": task.task_id,
            "task_name": task.name,
        }

    def _get_risk_score(self, risk_type: str) -> float:
        """Get risk score for type."""
        return self._risk_weights.get(risk_type, 0.1)

    def _get_risk_level(self, score: float) -> RiskLevel:
        """Convert score to risk level."""
        if score >= 0.7:
            return RiskLevel.CRITICAL
        elif score >= 0.5:
            return RiskLevel.HIGH
        elif score >= 0.3:
            return RiskLevel.MEDIUM
        elif score >= 0.1:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL

    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert score to risk level."""
        return self._get_risk_level(score)

    def _generate_mitigation(
        self,
        risk_level: RiskLevel,
        risk_factors: list[dict],
    ) -> list[str]:
        """Generate mitigation strategies."""
        strategies = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            strategies.append("Enable human approval for high-risk decisions")
            strategies.append("Implement failfast policy")
            strategies.append("Add checkpoints for verification")

        if risk_level == RiskLevel.MEDIUM:
            strategies.append("Enable conservative execution policy")
            strategies.append("Add progress monitoring")

        if any("medical_procedure" in f.get("type", "") for f in risk_factors):
            strategies.append("Require clinical verification")
            strategies.append("Enable rollback capability")

        if any("external_call" in f.get("type", "") for f in risk_factors):
            strategies.append("Add timeout and retry limits")
            strategies.append("Enable circuit breaker pattern")

        if any("data_modification" in f.get("type", "") for f in risk_factors):
            strategies.append("Enable audit logging")
            strategies.append("Require confirmation for modifications")

        if not strategies:
            strategies.append("Standard execution with monitoring")

        return strategies

    def should_escalate(
        self,
        plan: DecisionPlan,
        assessment: RiskAssessment,
    ) -> bool:
        """Determine if decision should escalate to human.

        Args:
            plan: Decision plan.
            assessment: Risk assessment.

        Returns:
            True if escalation required.
        """
        # High or critical risk
        if assessment.overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True

        # Medical procedures
        if any("medical_procedure" in f.get("type", "") for f in assessment.risk_factors):
            return True

        # Failed tasks
        if plan.failed_tasks > 0 and plan.tasks:
            failure_rate = plan.failed_tasks / len(plan.tasks)
            if failure_rate > 0.2:  # > 20% failure rate
                return True

        return False
