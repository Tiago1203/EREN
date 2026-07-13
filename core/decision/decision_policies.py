"""Decision policies for the Cognitive Decision Engine.

Provides policies for decision approval and escalation.

Architecture only -- no AI, no business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .decision_types import DecisionCandidate, DecisionContext, DecisionPolicyRule

if TYPE_CHECKING:
    pass


# =============================================================================
# Base Policy
# =============================================================================


class DecisionPolicyComponent(ABC):
    """Base class for decision policies."""

    @abstractmethod
    def should_approve(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check if decision should be approved.

        Args:
            candidate: The candidate.
            context: Decision context.

        Returns:
            True if should approve.
        """
        ...

    @abstractmethod
    def should_escalate(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check if decision should escalate to human.

        Args:
            candidate: The candidate.
            context: Decision context.

        Returns:
            True if should escalate.
        """
        ...

    @abstractmethod
    def get_rules(self) -> list[DecisionPolicyRule]:
        """Get policy rules."""
        ...


# =============================================================================
# Conservative Policy
# =============================================================================


class ConservativePolicy(DecisionPolicyComponent):
    """Conservative policy - requires strong evidence.

    Rules:
    - Require confidence >= 0.8 for approval
    - Escalate for risk >= HIGH
    - Require multiple evidence items
    """

    def should_approve(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check approval with conservative rules."""
        # High confidence required
        if candidate.confidence < 0.8:
            return False

        # Evidence required
        if not candidate.based_on_evidence:
            return False

        # Risk check
        if candidate.risk_level.value in ("HIGH", "CRITICAL"):
            return False

        return True

    def should_escalate(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check escalation with conservative rules."""
        # Always escalate for critical risk
        if candidate.risk_level.value == "CRITICAL":
            return True

        # Escalate for high risk with medium confidence
        if candidate.risk_level.value == "HIGH" and candidate.confidence < 0.9:
            return True

        # Escalate for moderate confidence in safety situations
        if candidate.metadata.get("affects_patient_safety"):
            if candidate.confidence < 0.95:
                return True

        return False

    def get_rules(self) -> list[DecisionPolicyRule]:
        """Get conservative policy rules."""
        return [
            DecisionPolicyRule(
                rule_id="conservative_1",
                name="High Confidence Required",
                description="Require confidence >= 0.8 for approval",
                condition="confidence < 0.8",
                action="reject",
                priority=100,
            ),
            DecisionPolicyRule(
                rule_id="conservative_2",
                name="Evidence Required",
                description="Require at least one evidence item",
                condition="no_evidence",
                action="reject",
                priority=90,
            ),
            DecisionPolicyRule(
                rule_id="conservative_3",
                name="Critical Risk Escalation",
                description="Always escalate critical risk",
                condition="risk_level == CRITICAL",
                action="escalate",
                priority=200,
            ),
        ]


# =============================================================================
# Balanced Policy
# =============================================================================


class BalancedPolicy(DecisionPolicyComponent):
    """Balanced policy - reasonable approval thresholds.

    Rules:
    - Require confidence >= 0.6 for approval
    - Escalate for risk >= HIGH
    - Consider context
    """

    def should_approve(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check approval with balanced rules."""
        # Moderate confidence required
        if candidate.confidence < 0.6:
            return False

        # Critical risk always escalated
        if candidate.risk_level.value == "CRITICAL":
            return False

        return True

    def should_escalate(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check escalation with balanced rules."""
        # High or critical risk
        if candidate.risk_level.value in ("HIGH", "CRITICAL"):
            return True

        # Safety-affecting decisions
        if candidate.metadata.get("affects_patient_safety"):
            return True

        # Low confidence with high priority
        if candidate.confidence < 0.7 and candidate.priority.value in ("HIGH", "CRITICAL"):
            return True

        return False

    def get_rules(self) -> list[DecisionPolicyRule]:
        """Get balanced policy rules."""
        return [
            DecisionPolicyRule(
                rule_id="balanced_1",
                name="Moderate Confidence Required",
                description="Require confidence >= 0.6 for approval",
                condition="confidence < 0.6",
                action="reject",
                priority=80,
            ),
            DecisionPolicyRule(
                rule_id="balanced_2",
                name="Risk Escalation",
                description="Escalate high and critical risk",
                condition="risk_level in [HIGH, CRITICAL]",
                action="escalate",
                priority=150,
            ),
        ]


# =============================================================================
# Permissive Policy
# =============================================================================


class PermissivePolicy(DecisionPolicyComponent):
    """Permissive policy - allows more autonomy.

    Rules:
    - Require confidence >= 0.4 for approval
    - Only escalate critical risk
    - Trust lower confidence decisions
    """

    def should_approve(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check approval with permissive rules."""
        # Low confidence threshold
        if candidate.confidence < 0.4:
            return False

        # Only critical risk blocked
        if candidate.risk_level.value == "CRITICAL":
            return False

        return True

    def should_escalate(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> bool:
        """Check escalation with permissive rules."""
        # Only critical risk
        return candidate.risk_level.value == "CRITICAL"

    def get_rules(self) -> list[DecisionPolicyRule]:
        """Get permissive policy rules."""
        return [
            DecisionPolicyRule(
                rule_id="permissive_1",
                name="Low Confidence Required",
                description="Require confidence >= 0.4 for approval",
                condition="confidence < 0.4",
                action="reject",
                priority=60,
            ),
            DecisionPolicyRule(
                rule_id="permissive_2",
                name="Critical Only Escalation",
                description="Only escalate critical risk",
                condition="risk_level == CRITICAL",
                action="escalate",
                priority=100,
            ),
        ]
