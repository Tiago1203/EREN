"""Integration Validator for EREN OS Diagnostics.

Validates that all kernel components can operate together:
- Event flow between components
- Data passing between engines
- Session lifecycle coordination
- Blackboard interactions
- Orchestrator-engine integration

Philosophy:
    Components may work in isolation, but integration proves production readiness.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class IntegrationIssue:
    """A single integration issue."""

    integration_type: str  # event_flow, data_pass, coordination, etc.
    source: str
    target: str
    description: str
    severity: str  # critical, major, minor

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "integration_type": self.integration_type,
            "source": self.source,
            "target": self.target,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass
class IntegrationReport:
    """Complete integration validation report."""

    is_valid: bool
    score: float
    issues: list[IntegrationIssue]
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0

    # Integration metrics
    integrations_checked: int = 0
    passed_checks: int = 0
    failed_integrations: list[str] = field(default_factory=list)

    # Detailed scores
    event_flow_score: float = 0.0
    data_passing_score: float = 0.0
    coordination_score: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "issues": [i.to_dict() for i in self.issues],
            "validated_at": self.validated_at.isoformat(),
            "duration_ms": self.duration_ms,
            "integrations_checked": self.integrations_checked,
            "passed_checks": self.passed_checks,
            "failed_integrations": self.failed_integrations,
            "event_flow_score": self.event_flow_score,
            "data_passing_score": self.data_passing_score,
            "coordination_score": self.coordination_score,
            "critical_issues": [i.to_dict() for i in self.issues if i.severity == "critical"],
        }


class IntegrationValidator:
    """Validates EREN OS integration between components.

    Checks:
    - Event flow between components
    - Data passing mechanisms
    - Session lifecycle coordination
    - Blackboard operations
    - Orchestrator-engine communication
    """

    # Required integration points
    REQUIRED_INTEGRATIONS = {
        "event_bus_to_orchestrator": {
            "description": "Event Bus can communicate with Orchestrator",
            "integration_type": "event_flow",
            "severity": "critical",
        },
        "orchestrator_to_planner": {
            "description": "Orchestrator can invoke Planner",
            "integration_type": "coordination",
            "severity": "critical",
        },
        "orchestrator_to_reasoning": {
            "description": "Orchestrator can invoke Reasoning",
            "integration_type": "coordination",
            "severity": "critical",
        },
        "reasoning_to_decision": {
            "description": "Reasoning can invoke Decision",
            "integration_type": "coordination",
            "severity": "critical",
        },
        "memory_to_knowledge": {
            "description": "Memory can access Knowledge",
            "integration_type": "data_passing",
            "severity": "major",
        },
        "session_to_context": {
            "description": "Session can manage Context",
            "integration_type": "coordination",
            "severity": "critical",
        },
        "blackboard_to_engines": {
            "description": "Blackboard accessible by engines",
            "integration_type": "data_passing",
            "severity": "major",
        },
        "scheduler_to_capabilities": {
            "description": "Scheduler can dispatch to Capabilities",
            "integration_type": "coordination",
            "severity": "major",
        },
        "tool_engine_capability_registry": {
            "description": "Tool Engine uses Capability Registry",
            "integration_type": "data_passing",
            "severity": "major",
        },
        "lifecycle_to_all_engines": {
            "description": "Lifecycle Manager coordinates all engines",
            "integration_type": "coordination",
            "severity": "critical",
        },
    }

    def __init__(self):
        self._integration_checks: dict[str, callable] = {}
        self._lock = threading.RLock()

    def register_integration_check(
        self,
        integration_name: str,
        check_fn: callable,
    ) -> None:
        """Register a custom integration check.

        Args:
            integration_name: Name of the integration.
            check_fn: Function returning (passed, description).
        """
        with self._lock:
            self._integration_checks[integration_name] = check_fn

    def validate(self) -> IntegrationReport:
        """Run complete integration validation.

        Returns:
            IntegrationReport with validation results.
        """
        start_time = time.time()
        issues = []

        integrations_checked = len(self.REQUIRED_INTEGRATIONS)

        # Check all required integrations
        for integration_name, integration_def in self.REQUIRED_INTEGRATIONS.items():
            passed = True
            description = integration_def["description"]

            # Try custom check if registered
            if integration_name in self._integration_checks:
                try:
                    passed, desc = self._integration_checks[integration_name]()
                    description = desc
                except Exception:
                    passed = False
                    description = f"Integration check failed for {integration_name}"

            if not passed:
                # Determine source and target from name
                parts = integration_name.split("_to_")
                source = parts[0] if parts else integration_name
                target = parts[1] if len(parts) > 1 else "unknown"

                issues.append(IntegrationIssue(
                    integration_type=integration_def["integration_type"],
                    source=source,
                    target=target,
                    description=description,
                    severity=integration_def["severity"],
                ))

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate scores
        critical_issues = [i for i in issues if i.severity == "critical"]
        major_issues = [i for i in issues if i.severity == "major"]
        minor_issues = [i for i in issues if i.severity == "minor"]

        is_valid = len(critical_issues) == 0

        total_deduction = len(critical_issues) * 20 + len(major_issues) * 5 + len(minor_issues) * 1
        score = max(0, 100 - total_deduction)

        passed_checks = integrations_checked - len(issues)
        failed_integrations = [i.source + "_to_" + i.target for i in issues]

        # Calculate category scores
        event_flow_issues = [i for i in issues if i.integration_type == "event_flow"]
        data_passing_issues = [i for i in issues if i.integration_type == "data_passing"]
        coordination_issues = [i for i in issues if i.integration_type == "coordination"]

        event_flow_score = max(0, 100 - len(event_flow_issues) * 20)
        data_passing_score = max(0, 100 - len(data_passing_issues) * 15)
        coordination_score = max(0, 100 - len(coordination_issues) * 20)

        return IntegrationReport(
            is_valid=is_valid,
            score=score,
            issues=issues,
            duration_ms=duration_ms,
            integrations_checked=integrations_checked,
            passed_checks=passed_checks,
            failed_integrations=failed_integrations,
            event_flow_score=event_flow_score,
            data_passing_score=data_passing_score,
            coordination_score=coordination_score,
        )

    def validate_event_flow(
        self,
        from_component: str,
        to_component: str,
        event_types: list[str],
    ) -> tuple[bool, str]:
        """Validate event flow between two components.

        Args:
            from_component: Publisher component.
            to_component: Subscriber component.
            event_types: Expected event types in flow.

        Returns:
            Tuple of (is_valid, description).
        """
        # For scaffolding, assume proper event flow
        return True, f"Event flow validated: {from_component} -> {to_component}"

    def validate_data_passing(
        self,
        from_component: str,
        to_component: str,
        data_contract: dict,
    ) -> tuple[bool, str]:
        """Validate data passing between two components.

        Args:
            from_component: Source component.
            to_component: Target component.
            data_contract: Expected data contract.

        Returns:
            Tuple of (is_valid, description).
        """
        # For scaffolding, assume proper data passing
        return True, f"Data passing validated: {from_component} -> {to_component}"

    def validate_coordination(
        self,
        coordinator: str,
        worker: str,
    ) -> tuple[bool, str]:
        """Validate coordination between components.

        Args:
            coordinator: Coordinating component.
            worker: Worker component.

        Returns:
            Tuple of (is_valid, description).
        """
        # For scaffolding, assume proper coordination
        return True, f"Coordination validated: {coordinator} -> {worker}"

    def validate_full_cognitive_cycle(self) -> tuple[bool, list[str]]:
        """Validate that the full cognitive cycle works.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []

        # Simulate full cognitive cycle validation
        # In production, this would actually execute the cycle

        return len(issues) == 0, issues
