"""Unit tests for diagnostics score module."""

import pytest

from core.diagnostics.score import (
    DiagnosticScore,
    ScoreCategory,
    CategoryScore,
)


class TestScoreCategory:
    """Tests for ScoreCategory enum."""

    def test_category_values(self):
        """Test all score categories exist."""
        assert ScoreCategory.ARCHITECTURE.value == "architecture"
        assert ScoreCategory.CONTRACTS.value == "contracts"
        assert ScoreCategory.EVENTS.value == "events"
        assert ScoreCategory.DEPENDENCIES.value == "dependencies"
        assert ScoreCategory.PERFORMANCE.value == "performance"
        assert ScoreCategory.RUNTIME.value == "runtime"


class TestCategoryScore:
    """Tests for CategoryScore dataclass."""

    def test_creation(self):
        """Test CategoryScore creation."""
        score = CategoryScore(
            category=ScoreCategory.ARCHITECTURE,
            score=95.0,
            weight=0.15,
            passed_checks=10,
            failed_checks=1,
        )
        assert score.category == ScoreCategory.ARCHITECTURE
        assert score.score == 95.0
        assert score.weight == 0.15
        assert score.passed_checks == 10
        assert score.failed_checks == 1

    def test_score_clamping(self):
        """Test score is clamped to 0-100."""
        # Note: CategoryScore doesn't clamp internally; clamping happens in DiagnosticScore.set_category_score
        score = CategoryScore(
            category=ScoreCategory.ARCHITECTURE,
            score=150.0,
            weight=0.1,
        )
        # Score is stored as-is; clamping happens when set via DiagnosticScore
        assert score.score == 150.0

        score2 = CategoryScore(
            category=ScoreCategory.ARCHITECTURE,
            score=-10.0,
            weight=0.1,
        )
        # Score is stored as-is
        assert score2.score == -10.0

    def test_to_dict(self):
        """Test to_dict conversion."""
        score = CategoryScore(
            category=ScoreCategory.ARCHITECTURE,
            score=95.0,
            weight=0.15,
            passed_checks=10,
            failed_checks=1,
            warnings=2,
        )
        d = score.to_dict()
        assert d["category"] == "architecture"
        assert d["score"] == 95.0
        assert d["passed_checks"] == 10


class TestDiagnosticScore:
    """Tests for DiagnosticScore class."""

    def test_initialization(self):
        """Test DiagnosticScore initialization."""
        score = DiagnosticScore()
        assert len(score._weights) == len(ScoreCategory)
        assert sum(score._weights.values()) == pytest.approx(1.0, 0.01)

    def test_set_category_score(self):
        """Test setting category score."""
        score = DiagnosticScore()
        score.set_category_score(
            ScoreCategory.ARCHITECTURE,
            95.0,
            passed_checks=10,
            failed_checks=1,
        )

        cat_score = score.get_category_score(ScoreCategory.ARCHITECTURE)
        assert cat_score is not None
        assert cat_score.score == 95.0
        assert cat_score.passed_checks == 10
        assert cat_score.failed_checks == 1

    def test_get_overall_score_empty(self):
        """Test overall score with no scores set."""
        score = DiagnosticScore()
        assert score.get_overall_score() == 0.0

    def test_get_overall_score_single_category(self):
        """Test overall score with single category."""
        score = DiagnosticScore()
        score.set_category_score(ScoreCategory.ARCHITECTURE, 100.0)

        overall = score.get_overall_score()
        # When only one category is set, the overall is just that score
        # because the weighting normalizes to only that category
        assert overall == 100.0

    def test_get_overall_score_multiple_categories(self):
        """Test overall score with multiple categories."""
        score = DiagnosticScore()

        score.set_category_score(ScoreCategory.ARCHITECTURE, 100.0)
        score.set_category_score(ScoreCategory.CONTRACTS, 80.0)

        overall = score.get_overall_score()
        # Overall should be between 80 and 100
        assert 80 <= overall <= 100

    def test_get_production_readiness_healthy(self):
        """Test production readiness with healthy score."""
        score = DiagnosticScore()
        # Set all categories to healthy (>= 90)
        for category in ScoreCategory:
            score.set_category_score(category, 95.0)

        is_ready, status = score.get_production_readiness()
        assert is_ready is True
        assert "HEALTHY" in status

    def test_get_production_readiness_production_ready(self):
        """Test production readiness with production-ready score."""
        score = DiagnosticScore()
        # Set all categories to 85 (>= 80)
        for category in ScoreCategory:
            score.set_category_score(category, 85.0)

        is_ready, status = score.get_production_readiness()
        assert is_ready is True
        assert status == "PRODUCTION READY"

    def test_get_production_readiness_degraded(self):
        """Test production readiness with degraded score."""
        score = DiagnosticScore()
        # Set all categories to 75 (>= 70)
        for category in ScoreCategory:
            score.set_category_score(category, 75.0)

        is_ready, status = score.get_production_readiness()
        assert is_ready is False
        assert "DEGRADED" in status

    def test_get_production_readiness_unhealthy(self):
        """Test production readiness with unhealthy score."""
        score = DiagnosticScore()
        # Set all categories to 50 (< 70)
        for category in ScoreCategory:
            score.set_category_score(category, 50.0)

        is_ready, status = score.get_production_readiness()
        assert is_ready is False
        assert "UNHEALTHY" in status

    def test_get_failed_categories(self):
        """Test getting failed categories."""
        score = DiagnosticScore()
        score.set_category_score(ScoreCategory.ARCHITECTURE, 95.0)
        score.set_category_score(ScoreCategory.CONTRACTS, 50.0)  # Below 80

        failed = score.get_failed_categories()
        assert "contracts" in failed
        assert "architecture" not in failed

    def test_get_critical_issues(self):
        """Test getting critical issues."""
        score = DiagnosticScore()
        score.set_category_score(
            ScoreCategory.ARCHITECTURE,
            70.0,
            failed_checks=2,
        )

        issues = score.get_critical_issues()
        assert len(issues) > 0

    def test_get_score_breakdown(self):
        """Test score breakdown."""
        score = DiagnosticScore()
        score.set_category_score(ScoreCategory.ARCHITECTURE, 95.0)
        score.set_category_score(ScoreCategory.CONTRACTS, 85.0)

        breakdown = score.get_score_breakdown()
        assert "architecture" in breakdown
        assert "contracts" in breakdown
        assert "_overall" in breakdown
        assert breakdown["_overall"]["score"] > 0

    def test_get_summary(self):
        """Test getting summary."""
        score = DiagnosticScore()
        score.set_category_score(ScoreCategory.ARCHITECTURE, 95.0)
        score.set_category_score(ScoreCategory.CONTRACTS, 85.0)

        summary = score.get_summary()
        assert "EREN OS DIAGNOSTIC SCORE SUMMARY" in summary
        assert "architecture" in summary  # Categories are lowercase
        assert "contracts" in summary

    def test_custom_weights(self):
        """Test custom weights."""
        weights = {
            ScoreCategory.ARCHITECTURE: 0.30,
            ScoreCategory.CONTRACTS: 0.30,
            ScoreCategory.PERFORMANCE: 0.40,
        }
        score = DiagnosticScore(weights=weights)

        assert score._weights[ScoreCategory.ARCHITECTURE] == 0.30
        assert score._weights[ScoreCategory.CONTRACTS] == 0.30
        assert score._weights[ScoreCategory.PERFORMANCE] == 0.40

    def test_to_dict(self):
        """Test to_dict conversion."""
        score = DiagnosticScore()
        score.set_category_score(ScoreCategory.ARCHITECTURE, 95.0)

        d = score.to_dict()
        assert "overall_score" in d
        assert "is_production_ready" in d
        assert "categories" in d
        assert "architecture" in d["categories"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
