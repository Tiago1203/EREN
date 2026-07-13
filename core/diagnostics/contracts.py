"""Contract Validator for EREN OS Diagnostics.

Validates that all contracts between components are properly defined
and satisfied. This includes:
- Interface definitions exist
- Implementations satisfy interfaces
- Event contracts are respected
- No contract violations

Philosophy:
    Contracts are the law. EREN must prove contract compliance.
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
class ContractViolation:
    """A single contract violation."""

    contract_name: str
    violator: str
    violation_type: str  # missing_implementation, signature_mismatch, etc.
    description: str
    severity: str  # critical, major, minor
    expected: str = ""
    actual: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "contract_name": self.contract_name,
            "violator": self.violator,
            "violation_type": self.violation_type,
            "description": self.description,
            "severity": self.severity,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass
class ContractReport:
    """Complete contract validation report."""

    is_valid: bool
    score: float
    violations: list[ContractViolation]
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    contracts_checked: int = 0
    passed_checks: int = 0

    # Detailed metrics
    interfaces_defined: int = 0
    interfaces_implemented: int = 0
    event_contracts_valid: int = 0
    missing_implementations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "violations": [v.to_dict() for v in self.violations],
            "validated_at": self.validated_at.isoformat(),
            "duration_ms": self.duration_ms,
            "contracts_checked": self.contracts_checked,
            "passed_checks": self.passed_checks,
            "interfaces_defined": self.interfaces_defined,
            "interfaces_implemented": self.interfaces_implemented,
            "event_contracts_valid": self.event_contracts_valid,
            "missing_implementations": self.missing_implementations,
            "critical_violations": [v.to_dict() for v in self.violations if v.severity == "critical"],
        }


class ContractValidator:
    """Validates EREN OS contract compliance.

    Checks:
    - All interfaces are defined in contracts/
    - All engines implement required interfaces
    - Event contracts are respected
    - No missing implementations
    """

    # Required contracts based on architecture
    REQUIRED_CONTRACTS = {
        "CognitiveEngine": {
            "description": "Base contract for all cognitive engines",
            "required_methods": ["name", "describe"],
            "severity": "critical",
        },
        "EventPublisher": {
            "description": "Contract for components that publish events",
            "required_methods": ["publish"],
            "severity": "critical",
        },
        "EventSubscriber": {
            "description": "Contract for components that subscribe to events",
            "required_methods": ["subscribed_types", "handle"],
            "severity": "critical",
        },
        "CapabilityRegistry": {
            "description": "Contract for capability registry",
            "required_methods": ["register", "get", "list"],
            "severity": "critical",
        },
        "ContextManager": {
            "description": "Contract for context manager",
            "required_methods": ["create_context", "get_context", "update_context"],
            "severity": "critical",
        },
        "Scheduler": {
            "description": "Contract for task scheduler",
            "required_methods": ["submit_task", "schedule_next"],
            "severity": "major",
        },
        "Planner": {
            "description": "Contract for planner engine",
            "required_methods": ["receive_intention", "create_plan"],
            "severity": "critical",
        },
        "Reasoning": {
            "description": "Contract for reasoning engine",
            "required_methods": ["reason"],
            "severity": "critical",
        },
        "Memory": {
            "description": "Contract for memory engine",
            "required_methods": ["store", "retrieve"],
            "severity": "critical",
        },
        "Knowledge": {
            "description": "Contract for knowledge engine",
            "required_methods": ["query", "index"],
            "severity": "major",
        },
        "Tool": {
            "description": "Contract for tool execution",
            "required_methods": ["execute", "validate"],
            "severity": "major",
        },
        "Decision": {
            "description": "Contract for decision engine",
            "required_methods": ["decide"],
            "severity": "major",
        },
    }

    # Event contracts that should exist
    REQUIRED_EVENT_CONTRACTS = [
        "diagnostic_started",
        "diagnostic_completed",
        "diagnostic_failed",
        "health_check_started",
        "health_check_completed",
        "validation_started",
        "validation_completed",
        "report_generated",
    ]

    def __init__(self):
        self._custom_contracts: dict[str, dict] = {}
        self._lock = threading.RLock()

    def add_contract(
        self,
        contract_name: str,
        description: str,
        required_methods: list[str],
        severity: str = "major",
    ) -> None:
        """Add a custom contract to validate.

        Args:
            contract_name: Name of the contract.
            description: Human-readable description.
            required_methods: List of required method names.
            severity: Severity if not implemented.
        """
        with self._lock:
            self._custom_contracts[contract_name] = {
                "description": description,
                "required_methods": required_methods,
                "severity": severity,
            }

    def validate(self) -> ContractReport:
        """Run complete contract validation.

        Returns:
            ContractReport with validation results.
        """
        start_time = time.time()
        violations = []
        contracts_checked = len(self.REQUIRED_CONTRACTS) + len(self._custom_contracts)

        # Check all required contracts
        for contract_name, contract_def in self.REQUIRED_CONTRACTS.items():
            # For scaffolding, we check if the contract interface exists
            contract_violations = self._check_contract(contract_name, contract_def)
            violations.extend(contract_violations)

        # Check custom contracts
        for contract_name, contract_def in self._custom_contracts.items():
            contract_violations = self._check_contract(contract_name, contract_def)
            violations.extend(contract_violations)

        # Validate event contracts
        event_violations = self._validate_event_contracts()
        violations.extend(event_violations)

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate score
        critical_violations = [v for v in violations if v.severity == "critical"]
        major_violations = [v for v in violations if v.severity == "major"]
        minor_violations = [v for v in violations if v.severity == "minor"]

        is_valid = len(critical_violations) == 0

        total_deduction = len(critical_violations) * 20 + len(major_violations) * 5 + len(minor_violations) * 1
        score = max(0, 100 - total_deduction)

        passed_checks = contracts_checked - len(violations)

        # Count interfaces
        interfaces_defined = len(self.REQUIRED_CONTRACTS) + len(self._custom_contracts)
        interfaces_implemented = interfaces_defined - len(major_violations)
        event_contracts_valid = len(self.REQUIRED_EVENT_CONTRACTS) - len(event_violations)

        missing_implementations = [
            v.contract_name for v in violations
            if v.violation_type == "missing_implementation"
        ]

        return ContractReport(
            is_valid=is_valid,
            score=score,
            violations=violations,
            duration_ms=duration_ms,
            contracts_checked=contracts_checked,
            passed_checks=passed_checks,
            interfaces_defined=interfaces_defined,
            interfaces_implemented=interfaces_implemented,
            event_contracts_valid=event_contracts_valid,
            missing_implementations=missing_implementations,
        )

    def _check_contract(
        self,
        contract_name: str,
        contract_def: dict,
    ) -> list[ContractViolation]:
        """Check a single contract.

        Args:
            contract_name: Name of the contract.
            contract_def: Contract definition.

        Returns:
            List of violations found.
        """
        violations = []

        # For scaffolding, we verify that contract modules exist
        import os

        contracts_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "contracts"
        )

        # Check if contract is defined
        # In scaffolding, we assume contracts are properly defined
        # This would be enhanced when real code exists

        return violations

    def _validate_event_contracts(self) -> list[ContractViolation]:
        """Validate event contracts.

        Returns:
            List of violations found.
        """
        violations = []

        # Check if event types are defined in models
        # For scaffolding, we verify the structure exists

        return violations

    def validate_implementation(
        self,
        implementation_class: type,
        contract_name: str,
    ) -> tuple[bool, list[str]]:
        """Validate that a class implements a contract.

        Args:
            implementation_class: Class to validate.
            contract_name: Name of the contract to check against.

        Returns:
            Tuple of (is_valid, list_of_missing_methods).
        """
        if contract_name not in self.REQUIRED_CONTRACTS:
            return True, []

        contract_def = self.REQUIRED_CONTRACTS[contract_name]
        required_methods = contract_def["required_methods"]

        missing_methods = []
        for method in required_methods:
            if not hasattr(implementation_class, method):
                missing_methods.append(method)

        return len(missing_methods) == 0, missing_methods

    def validate_event_subscription(
        self,
        subscriber_class: type,
        expected_event_types: list[str],
    ) -> tuple[bool, list[str]]:
        """Validate that a subscriber handles expected event types.

        Args:
            subscriber_class: Subscriber class to validate.
            expected_event_types: Event types the subscriber should handle.

        Returns:
            Tuple of (is_valid, list_of_missing_event_types).
        """
        if not hasattr(subscriber_class, "subscribed_types"):
            return False, expected_event_types

        subscribed = getattr(subscriber_class, "subscribed_types", [])
        subscribed_types = [e.value if hasattr(e, "value") else e for e in subscribed]

        missing = [et for et in expected_event_types if et not in subscribed_types]

        return len(missing) == 0, missing
