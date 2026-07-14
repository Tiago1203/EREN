"""Diagnostic Score System for EREN OS Diagnostics.

Implements comprehensive scoring for all diagnostic categories:
- Architecture
- Contracts
- Events
- Dependencies
- Performance
- Runtime
- Observability
- Documentation
- Testing
- Security
- Maintainability

Philosophy:
    Every aspect of EREN must be quantifiable. Scores drive improvement.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ScoreCategory(str, Enum):
    """Categories for diagnostic scoring."""

    ARCHITECTURE = "architecture"
    CONTRACTS = "contracts"
    EVENTS = "events"
    DEPENDENCIES = "dependencies"
    PERFORMANCE = "performance"
    RUNTIME = "runtime"
    OBSERVABILITY = "observability"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"


@dataclass
class CategoryScore:
    """Score for a single category."""

    category: ScoreCategory
    score: float  # 0-100
    weight: float  # Importance weight (0-1)
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: int = 0
    details: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "category": self.category.value,
            "score": self.score,
            "weight": self.weight,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warnings": self.warnings,
            "details": self.details,
        }


@dataclass
class DiagnosticScore:
    """Complete diagnostic score for EREN OS.

    Aggregates scores from all diagnostic categories and calculates
    overall production readiness score.
    """

    # Category weights (should sum to 1.0)
    DEFAULT_WEIGHTS = {
        ScoreCategory.ARCHITECTURE: 0.15,
        ScoreCategory.CONTRACTS: 0.12,
        ScoreCategory.EVENTS: 0.08,
        ScoreCategory.DEPENDENCIES: 0.10,
        ScoreCategory.PERFORMANCE: 0.10,
        ScoreCategory.RUNTIME: 0.12,
        ScoreCategory.OBSERVABILITY: 0.08,
        ScoreCategory.DOCUMENTATION: 0.05,
        ScoreCategory.TESTING: 0.10,
        ScoreCategory.SECURITY: 0.05,
        ScoreCategory.MAINTAINABILITY: 0.05,
    }

    # Production readiness thresholds
    PRODUCTION_THRESHOLD = 80.0
    HEALTHY_THRESHOLD = 90.0
    DEGRADED_THRESHOLD = 70.0

    def __init__(self, weights: dict[ScoreCategory, float] | None = None):
        self._category_scores: dict[ScoreCategory, CategoryScore] = {}
        self._weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._lock = threading.RLock()
        self._calculated_at: datetime | None = None

    def set_category_score(
        self,
        category: ScoreCategory,
        score: float,
        passed_checks: int = 0,
        failed_checks: int = 0,
        warnings: int = 0,
        details: dict | None = None,
    ) -> None:
        """Set score for a category.

        Args:
            category: Category to score.
            score: Score value (0-100).
            passed_checks: Number of passed checks.
            failed_checks: Number of failed checks.
            warnings: Number of warnings.
            details: Additional details.
        """
        with self._lock:
            weight = self._weights.get(category, 0.1)
            self._category_scores[category] = CategoryScore(
                category=category,
                score=max(0, min(100, score)),
                weight=weight,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                details=details,
            )

    def get_category_score(self, category: ScoreCategory) -> CategoryScore | None:
        """Get score for a category.

        Args:
            category: Category to retrieve.

        Returns:
            CategoryScore if set, None otherwise.
        """
        with self._lock:
            return self._category_scores.get(category)

    def get_overall_score(self) -> float:
        """Calculate weighted overall score.

        Returns:
            Overall score from 0-100.
        """
        with self._lock:
            if not self._category_scores:
                return 0.0

            total_weight = 0.0
            weighted_sum = 0.0

            for category, weight in self._weights.items():
                if category in self._category_scores:
                    cat_score = self._category_scores[category]
                    weighted_sum += cat_score.score * weight
                    total_weight += weight

            if total_weight == 0:
                return 0.0

            return weighted_sum / total_weight

    def get_production_readiness(self) -> tuple[bool, str]:
        """Determine production readiness status.

        Returns:
            Tuple of (is_production_ready, status_message).
        """
        score = self.get_overall_score()

        if score >= self.HEALTHY_THRESHOLD:
            return True, "PRODUCTION READY (HEALTHY)"
        elif score >= self.PRODUCTION_THRESHOLD:
            return True, "PRODUCTION READY"
        elif score >= self.DEGRADED_THRESHOLD:
            return False, "NOT PRODUCTION READY (DEGRADED)"
        else:
            return False, "NOT PRODUCTION READY (UNHEALTHY)"

    def get_score_breakdown(self) -> dict:
        """Get detailed score breakdown.

        Returns:
            Dictionary with score breakdown.
        """
        with self._lock:
            breakdown = {}
            for category in ScoreCategory:
                if category in self._category_scores:
                    cat_score = self._category_scores[category]
                    breakdown[category.value] = {
                        "score": cat_score.score,
                        "weight": cat_score.weight,
                        "weighted_score": cat_score.score * cat_score.weight,
                        "passed_checks": cat_score.passed_checks,
                        "failed_checks": cat_score.failed_checks,
                        "warnings": cat_score.warnings,
                    }
                else:
                    breakdown[category.value] = {
                        "score": 0.0,
                        "weight": self._weights.get(category, 0.1),
                        "weighted_score": 0.0,
                        "passed_checks": 0,
                        "failed_checks": 0,
                        "warnings": 0,
                    }

            breakdown["_overall"] = {
                "score": self.get_overall_score(),
                "is_production_ready": self.get_production_readiness()[0],
                "status": self.get_production_readiness()[1],
            }

            return breakdown

    def get_failed_categories(self) -> list[str]:
        """Get categories that failed production threshold.

        Returns:
            List of failed category names.
        """
        with self._lock:
            failed = []
            for category, cat_score in self._category_scores.items():
                if cat_score.score < self.PRODUCTION_THRESHOLD:
                    failed.append(category.value)

            return failed

    def get_critical_issues(self) -> list[str]:
        """Get critical issues across all categories.

        Returns:
            List of critical issue descriptions.
        """
        with self._lock:
            issues = []
            for category, cat_score in self._category_scores.items():
                if cat_score.failed_checks > 0:
                    issues.append(
                        f"{category.value}: {cat_score.failed_checks} failed checks"
                    )

            return issues

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with complete score information.
        """
        with self._lock:
            self._calculated_at = datetime.now(UTC)

            is_ready, status = self.get_production_readiness()

            return {
                "overall_score": self.get_overall_score(),
                "is_production_ready": is_ready,
                "status": status,
                "production_threshold": self.PRODUCTION_THRESHOLD,
                "calculated_at": self._calculated_at.isoformat() if self._calculated_at else None,
                "categories": {
                    cat.value: cs.to_dict()
                    for cat, cs in self._category_scores.items()
                },
                "weights": {
                    cat.value: weight
                    for cat, weight in self._weights.items()
                },
                "failed_categories": self.get_failed_categories(),
                "critical_issues": self.get_critical_issues(),
                "breakdown": self.get_score_breakdown(),
            }

    def get_summary(self) -> str:
        """Get human-readable score summary.

        Returns:
            Formatted summary string.
        """
        with self._lock:
            lines = []
            lines.append("=" * 50)
            lines.append("EREN OS DIAGNOSTIC SCORE SUMMARY")
            lines.append("=" * 50)

            overall = self.get_overall_score()
            is_ready, status = self.get_production_readiness()

            lines.append(f"\nOverall Score: {overall:.1f}%")
            lines.append(f"Status: {status}")

            lines.append("\nCategory Scores:")
            for category in ScoreCategory:
                if category in self._category_scores:
                    cs = self._category_scores[category]
                    status_icon = "✓" if cs.score >= self.PRODUCTION_THRESHOLD else "✗"
                    lines.append(
                        f"  {status_icon} {category.value:20} {cs.score:5.1f}% "
                        f"(weight: {cs.weight:.2f})"
                    )

            failed = self.get_failed_categories()
            if failed:
                lines.append(f"\nFailed Categories: {', '.join(failed)}")

            lines.append("=" * 50)
            return "\n".join(lines)
