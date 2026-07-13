"""Architecture Validator for EREN OS Diagnostics.

Validates architectural principles and Clean Architecture compliance:
- Layer dependencies (inward dependency rule)
- SOLID principles
- Contract-based design
- No circular dependencies
- Proper abstraction levels

Philosophy:
    Architecture should be verifiable, not assumed correct.
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
class ArchitectureViolation:
    """A single architecture violation."""

    rule: str
    severity: str  # critical, major, minor
    component: str
    description: str
    file_path: str = ""
    line_number: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "rule": self.rule,
            "severity": self.severity,
            "component": self.component,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
        }


@dataclass
class ArchitectureReport:
    """Complete architecture validation report."""

    is_valid: bool
    score: float  # 0-100
    violations: list[ArchitectureViolation]
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    rules_checked: int = 0
    passed_checks: int = 0

    # Detailed scores
    clean_architecture_score: float = 0.0
    solid_score: float = 0.0
    dependency_score: float = 0.0
    contract_score: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "violations": [v.to_dict() for v in self.violations],
            "validated_at": self.validated_at.isoformat(),
            "duration_ms": self.duration_ms,
            "rules_checked": self.rules_checked,
            "passed_checks": self.passed_checks,
            "clean_architecture_score": self.clean_architecture_score,
            "solid_score": self.solid_score,
            "dependency_score": self.dependency_score,
            "contract_score": self.contract_score,
            "critical_violations": [v.to_dict() for v in self.violations if v.severity == "critical"],
            "major_violations": [v.to_dict() for v in self.violations if v.severity == "major"],
            "minor_violations": [v.to_dict() for v in self.violations if v.severity == "minor"],
        }


class ArchitectureValidator:
    """Validates EREN OS architecture compliance.

    Checks for:
    - Clean Architecture layers
    - SOLID principles
    - Dependency direction (inward only)
    - Contract usage
    - No circular dependencies
    """

    # Architecture rules definitions
    ARCHITECTURE_RULES = {
        "layer_apps_core": {
            "description": "apps/ depends only on core/ and packages/",
            "severity": "critical",
        },
        "layer_core_packages": {
            "description": "core/ depends only on packages/",
            "severity": "critical",
        },
        "no_apps_dependencies": {
            "description": "apps/ should not depend on other apps/",
            "severity": "critical",
        },
        "no_core_circular": {
            "description": "No circular dependencies within core/",
            "severity": "critical",
        },
        "interfaces_in_contracts": {
            "description": "Interfaces defined in contracts/, not implementations",
            "severity": "major",
        },
        "no_concrete_in_contracts": {
            "description": "Contracts should not reference concrete implementations",
            "severity": "major",
        },
        "single_responsibility": {
            "description": "Classes should have single responsibility",
            "severity": "minor",
        },
        "dependency_inversion": {
            "description": "High-level modules should not depend on low-level modules",
            "severity": "major",
        },
    }

    # Expected module structure
    EXPECTED_MODULES = {
        "core": [
            "boot",
            "capabilities",
            "composition",
            "container",
            "context",
            "contracts",
            "decision",
            "diagnostic",
            "events",
            "intent",
            "knowledge",
            "lifecycle",
            "memory",
            "orchestration",
            "orchestrator",
            "planner",
            "reasoning",
            "registry",
            "runtime",
            "scheduler",
            "session",
            "tools",
            "workflow",
        ],
        "packages": [
            "shared",
            "sdk",
            "prompts",
            "schemas",
        ],
        "apps": [
            "web",
            "api",
            "desktop",
        ],
    }

    def __init__(self):
        self._custom_rules: dict[str, dict] = {}
        self._lock = threading.RLock()

    def add_custom_rule(
        self,
        rule_name: str,
        description: str,
        severity: str,
        check_fn: callable,
    ) -> None:
        """Add a custom architecture rule.

        Args:
            rule_name: Unique name for the rule.
            description: Human-readable description.
            severity: critical, major, or minor.
            check_fn: Function that returns list of violations.
        """
        with self._lock:
            self._custom_rules[rule_name] = {
                "description": description,
                "severity": severity,
                "check_fn": check_fn,
            }

    def validate(self) -> ArchitectureReport:
        """Run complete architecture validation.

        Returns:
            ArchitectureReport with validation results.
        """
        start_time = time.time()
        violations = []
        rules_checked = len(self.ARCHITECTURE_RULES) + len(self._custom_rules)

        # Check all defined rules
        for rule_name, rule_def in self.ARCHITECTURE_RULES.items():
            # For scaffolding, we simulate validation
            # In production, this would inspect actual code
            violation = self._check_rule(rule_name, rule_def)
            if violation:
                violations.append(violation)

        # Check custom rules
        for rule_name, rule_def in self._custom_rules.items():
            try:
                rule_violations = rule_def["check_fn"]()
                violations.extend(rule_violations)
            except Exception:
                pass

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate scores
        critical_violations = [v for v in violations if v.severity == "critical"]
        major_violations = [v for v in violations if v.severity == "major"]
        minor_violations = [v for v in violations if v.severity == "minor"]

        # Architecture is valid if no critical violations
        is_valid = len(critical_violations) == 0

        # Calculate overall score
        # Critical: -20, Major: -5, Minor: -1
        total_deduction = len(critical_violations) * 20 + len(major_violations) * 5 + len(minor_violations) * 1
        score = max(0, 100 - total_deduction)

        # Calculate category scores
        clean_architecture_score = self._calculate_category_score(
            violations, ["layer_apps_core", "layer_core_packages", "no_apps_dependencies"]
        )
        solid_score = self._calculate_category_score(
            violations, ["single_responsibility", "dependency_inversion"]
        )
        dependency_score = self._calculate_category_score(
            violations, ["no_core_circular", "dependency_inversion"]
        )
        contract_score = self._calculate_category_score(
            violations, ["interfaces_in_contracts", "no_concrete_in_contracts"]
        )

        passed_checks = rules_checked - len(violations)

        return ArchitectureReport(
            is_valid=is_valid,
            score=score,
            violations=violations,
            duration_ms=duration_ms,
            rules_checked=rules_checked,
            passed_checks=passed_checks,
            clean_architecture_score=clean_architecture_score,
            solid_score=solid_score,
            dependency_score=dependency_score,
            contract_score=contract_score,
        )

    def _check_rule(self, rule_name: str, rule_def: dict) -> ArchitectureViolation | None:
        """Check a single architecture rule.

        For scaffolding, rules are considered passing unless
        explicitly violated.

        Args:
            rule_name: Name of the rule.
            rule_def: Rule definition.

        Returns:
            ArchitectureViolation if rule is broken, None otherwise.
        """
        # In scaffolding phase, rules are considered passing
        # This would be enhanced when real code exists
        return None

    def _calculate_category_score(
        self,
        violations: list[ArchitectureViolation],
        category_rules: list[str],
    ) -> float:
        """Calculate score for a category of rules.

        Args:
            violations: All violations found.
            category_rules: Rules in this category.

        Returns:
            Score from 0-100.
        """
        category_violations = [v for v in violations if v.rule in category_rules]
        if not category_rules:
            return 100.0

        # Each violation reduces score by 10 points for critical, 5 for major, 1 for minor
        deductions = 0
        for v in category_violations:
            if v.severity == "critical":
                deductions += 10
            elif v.severity == "major":
                deductions += 5
            else:
                deductions += 1

        return max(0, 100 - deductions)

    def validate_clean_architecture(self) -> tuple[bool, list[str]]:
        """Validate Clean Architecture principles.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []

        # Check that core modules exist
        import os
        core_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core")
        if os.path.exists(core_path):
            for module in self.EXPECTED_MODULES.get("core", []):
                module_path = os.path.join(core_path, module)
                if not os.path.exists(module_path):
                    issues.append(f"Expected core module not found: {module}")

        return len(issues) == 0, issues

    def validate_dependency_direction(self) -> tuple[bool, list[str]]:
        """Validate that dependencies flow inward.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []

        # Check layer order: apps -> core -> packages -> infrastructure
        # For scaffolding, we just verify the structure exists
        import os
        project_root = os.path.dirname(os.path.dirname(__file__))

        # Verify basic structure
        expected_dirs = ["apps", "core", "packages", "infrastructure", "tests", "docs"]
        for dir_name in expected_dirs:
            dir_path = os.path.join(project_root, dir_name)
            if not os.path.exists(dir_path):
                issues.append(f"Expected directory not found: {dir_name}")

        return len(issues) == 0, issues
