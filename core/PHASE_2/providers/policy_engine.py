"""Policy Engine for EREN OS Multi-Provider Layer.

Manages provider selection policies and rules.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from core.PHASE_2.providers.types import ProviderCapabilities, SelectionCriteria


class PolicyType(str, Enum):
    """Types of selection policies."""

    COST_OPTIMIZED = "cost_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    RELIABILITY_OPTIMIZED = "reliability_optimized"
    CAPABILITY_MATCHED = "capability_matched"
    FALLBACK = "fallback"
    LOAD_BALANCED = "load_balanced"
    CUSTOM = "custom"


class PolicyPriority(str, Enum):
    """Priority levels for policies."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PolicyRule:
    """A policy rule for provider selection."""

    rule_id: str
    name: str
    policy_type: PolicyType
    priority: PolicyPriority = PolicyPriority.MEDIUM
    enabled: bool = True

    # Conditions
    conditions: dict = field(default_factory=dict)
    # e.g., {"task_type": "code", "max_cost": 0.001}

    # Actions
    actions: dict = field(default_factory=dict)
    # e.g., {"select_provider": "ollama", "model": "codellama"}

    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def matches(self, criteria: SelectionCriteria, context: dict | None = None) -> bool:
        """Check if rule matches the criteria.

        Args:
            criteria: Selection criteria.
            context: Optional context data.

        Returns:
            True if rule matches.
        """
        context = context or {}

        # Check task type
        if "task_type" in self.conditions:
            if criteria.task_type.value != self.conditions["task_type"]:
                return False

        # Check max cost
        if "max_cost" in self.conditions:
            if criteria.max_cost > 0 and criteria.max_cost < self.conditions["max_cost"]:
                return False

        # Check privacy requirement
        if "privacy_required" in self.conditions:
            if criteria.privacy_required != self.conditions["privacy_required"]:
                return False

        # Check preferred providers
        if "preferred_providers" in self.conditions:
            if not any(p in criteria.preferred_providers for p in self.conditions["preferred_providers"]):
                return False

        # Check custom condition function
        if "condition_fn" in self.conditions:
            fn = self.conditions["condition_fn"]
            if not fn(criteria, context):
                return False

        return True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "policy_type": self.policy_type.value,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "conditions": self.conditions,
            "actions": self.actions,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class PolicyConfig:
    """Configuration for a policy."""

    policy_type: PolicyType
    enabled: bool = True
    priority: PolicyPriority = PolicyPriority.MEDIUM
    rules: list[PolicyRule] = field(default_factory=list)

    # Policy-specific settings
    settings: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "policy_type": self.policy_type.value,
            "enabled": self.enabled,
            "priority": self.priority.value,
            "rules": [r.to_dict() for r in self.rules],
            "settings": self.settings,
        }


class PolicyEngine:
    """Manages provider selection policies and rules.

    Features:
    - Multiple policy types
    - Policy rules with conditions and actions
    - Policy chaining and priority
    - Custom policy support
    """

    def __init__(self):
        """Initialize policy engine."""
        self._policies: dict[PolicyType, PolicyConfig] = {}
        self._rules: list[PolicyRule] = []
        self._custom_selectors: dict[str, Callable] = {}
        self._lock = threading.RLock()

        # Initialize default policies
        self._initialize_default_policies()

    def _initialize_default_policies(self) -> None:
        """Initialize default policies."""
        # Cost optimized policy
        self.add_policy(
            PolicyConfig(
                policy_type=PolicyType.COST_OPTIMIZED,
                settings={"weight_cost": 0.5, "weight_latency": 0.3, "weight_reliability": 0.2},
            )
        )

        # Latency optimized policy
        self.add_policy(
            PolicyConfig(
                policy_type=PolicyType.LATENCY_OPTIMIZED,
                settings={"weight_latency": 0.5, "weight_reliability": 0.3, "weight_cost": 0.2},
            )
        )

        # Reliability optimized policy
        self.add_policy(
            PolicyConfig(
                policy_type=PolicyType.RELIABILITY_OPTIMIZED,
                settings={"weight_reliability": 0.5, "weight_latency": 0.25, "weight_cost": 0.25},
            )
        )

        # Capability matched policy
        self.add_policy(
            PolicyConfig(
                policy_type=PolicyType.CAPABILITY_MATCHED,
                settings={"weight_capabilities": 0.5, "weight_reliability": 0.3, "weight_cost": 0.2},
            )
        )

        # Fallback policy
        self.add_policy(
            PolicyConfig(
                policy_type=PolicyType.FALLBACK,
                settings={"primary_priority": 1, "fallback_priority": 10},
            )
        )

        # Load balanced policy
        self.add_policy(
            PolicyConfig(
                policy_type=PolicyType.LOAD_BALANCED,
                settings={"strategy": "round_robin", "health_check": True},
            )
        )

    def add_policy(self, policy: PolicyConfig) -> None:
        """Add a policy.

        Args:
            policy: Policy configuration.
        """
        with self._lock:
            self._policies[policy.policy_type] = policy

    def get_policy(self, policy_type: PolicyType) -> PolicyConfig | None:
        """Get a policy.

        Args:
            policy_type: Type of policy.

        Returns:
            Policy configuration or None.
        """
        with self._lock:
            return self._policies.get(policy_type)

    def remove_policy(self, policy_type: PolicyType) -> bool:
        """Remove a policy.

        Args:
            policy_type: Type of policy.

        Returns:
            True if removed.
        """
        with self._lock:
            if policy_type in self._policies:
                del self._policies[policy_type]
                return True
            return False

    def enable_policy(self, policy_type: PolicyType) -> bool:
        """Enable a policy.

        Args:
            policy_type: Type of policy.

        Returns:
            True if enabled.
        """
        with self._lock:
            if policy_type in self._policies:
                self._policies[policy_type].enabled = True
                return True
            return False

    def disable_policy(self, policy_type: PolicyType) -> bool:
        """Disable a policy.

        Args:
            policy_type: Type of policy.

        Returns:
            True if disabled.
        """
        with self._lock:
            if policy_type in self._policies:
                self._policies[policy_type].enabled = False
                return True
            return False

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a policy rule.

        Args:
            rule: Policy rule to add.
        """
        with self._lock:
            self._rules.append(rule)
            rule.created_at = datetime.now(UTC)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a policy rule.

        Args:
            rule_id: Rule identifier.

        Returns:
            True if removed.
        """
        with self._lock:
            for i, rule in enumerate(self._rules):
                if rule.rule_id == rule_id:
                    del self._rules[i]
                    return True
            return False

    def get_rule(self, rule_id: str) -> PolicyRule | None:
        """Get a policy rule.

        Args:
            rule_id: Rule identifier.

        Returns:
            Policy rule or None.
        """
        with self._lock:
            for rule in self._rules:
                if rule.rule_id == rule_id:
                    return rule
            return None

    def update_rule(self, rule_id: str, updates: dict) -> bool:
        """Update a policy rule.

        Args:
            rule_id: Rule identifier.
            updates: Fields to update.

        Returns:
            True if updated.
        """
        with self._lock:
            for rule in self._rules:
                if rule.rule_id == rule_id:
                    if "name" in updates:
                        rule.name = updates["name"]
                    if "enabled" in updates:
                        rule.enabled = updates["enabled"]
                    if "conditions" in updates:
                        rule.conditions.update(updates["conditions"])
                    if "actions" in updates:
                        rule.actions.update(updates["actions"])
                    if "description" in updates:
                        rule.description = updates["description"]
                    rule.updated_at = datetime.now(UTC)
                    return True
            return False

    def register_custom_selector(
        self,
        name: str,
        selector: Callable[[list, SelectionCriteria, dict], str],
    ) -> None:
        """Register a custom provider selector.

        Args:
            name: Selector name.
            selector: Selector function(providers, criteria, context) -> provider_id.
        """
        with self._lock:
            self._custom_selectors[name] = selector

    def unregister_custom_selector(self, name: str) -> bool:
        """Unregister a custom selector.

        Args:
            name: Selector name.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if name in self._custom_selectors:
                del self._custom_selectors[name]
                return True
            return False

    def evaluate_criteria(
        self,
        criteria: SelectionCriteria,
        context: dict | None = None,
    ) -> PolicyType:
        """Evaluate criteria and determine best policy type.

        Args:
            criteria: Selection criteria.
            context: Optional context.

        Returns:
            Recommended policy type.
        """
        context = context or {}

        # Check rules first (highest priority)
        for rule in self._get_sorted_rules():
            if rule.enabled and rule.matches(criteria, context):
                # Return policy type from rule
                return rule.policy_type

        # Determine based on criteria
        if criteria.max_cost > 0 and criteria.max_cost < 0.001:
            return PolicyType.COST_OPTIMIZED

        if criteria.max_latency_ms > 0 and criteria.max_latency_ms < 1000:
            return PolicyType.LATENCY_OPTIMIZED

        if criteria.required_capabilities:
            return PolicyType.CAPABILITY_MATCHED

        if criteria.privacy_required:
            return PolicyType.RELIABILITY_OPTIMIZED

        # Default
        return PolicyType.FALLBACK

    def _get_sorted_rules(self) -> list[PolicyRule]:
        """Get rules sorted by priority.

        Returns:
            Sorted list of rules.
        """
        priority_order = {
            PolicyPriority.CRITICAL: 0,
            PolicyPriority.HIGH: 1,
            PolicyPriority.MEDIUM: 2,
            PolicyPriority.LOW: 3,
        }

        return sorted(self._rules, key=lambda r: priority_order.get(r.priority, 99))

    def get_applicable_rules(
        self,
        criteria: SelectionCriteria,
        context: dict | None = None,
    ) -> list[PolicyRule]:
        """Get all rules that match the criteria.

        Args:
            criteria: Selection criteria.
            context: Optional context.

        Returns:
            List of matching rules.
        """
        with self._lock:
            return [r for r in self._rules if r.enabled and r.matches(criteria, context)]

    def get_all_policies(self) -> dict[PolicyType, PolicyConfig]:
        """Get all policies.

        Returns:
            Dictionary of policies.
        """
        with self._lock:
            return dict(self._policies)

    def get_all_rules(self) -> list[PolicyRule]:
        """Get all rules.

        Returns:
            List of rules.
        """
        with self._lock:
            return list(self._rules)

    def clear_rules(self) -> None:
        """Clear all rules."""
        with self._lock:
            self._rules.clear()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        with self._lock:
            return {
                "policies": {k.value: v.to_dict() for k, v in self._policies.items()},
                "rules": [r.to_dict() for r in self._rules],
                "custom_selectors": list(self._custom_selectors.keys()),
            }
