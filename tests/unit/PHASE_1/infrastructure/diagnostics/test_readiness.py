"""Unit tests for diagnostics readiness module."""

import pytest

from core.PHASE_1.infrastructure.diagnostics.readiness import (
    ReadinessChecker,
    ReadinessCheck,
    ReadinessReport,
)


class TestReadinessCheck:
    """Tests for ReadinessCheck dataclass."""

    def test_creation(self):
        """Test ReadinessCheck creation."""
        check = ReadinessCheck(
            name="test_check",
            description="A test check",
            passed=True,
            message="All good",
            duration_ms=50,
        )
        assert check.name == "test_check"
        assert check.description == "A test check"
        assert check.passed is True
        assert check.duration_ms == 50

    def test_to_dict(self):
        """Test to_dict conversion."""
        check = ReadinessCheck(
            name="test",
            description="Test",
            passed=True,
            message="OK",
        )
        d = check.to_dict()
        assert d["name"] == "test"
        assert d["passed"] is True


class TestReadinessReport:
    """Tests for ReadinessReport dataclass."""

    def test_creation(self):
        """Test ReadinessReport creation."""
        report = ReadinessReport(
            is_ready=True,
            checks=[],
            total_duration_ms=100,
        )
        assert report.is_ready is True
        assert len(report.checks) == 0

    def test_to_dict(self):
        """Test to_dict conversion."""
        report = ReadinessReport(
            is_ready=True,
            checks=[
                ReadinessCheck("check1", "desc1", True),
                ReadinessCheck("check2", "desc2", False),
            ],
            total_duration_ms=100,
            critical_failures=["fail1"],
        )
        d = report.to_dict()
        assert d["is_ready"] is True
        assert d["passed_count"] == 1
        assert d["failed_count"] == 1


class TestReadinessChecker:
    """Tests for ReadinessChecker class."""

    def test_initialization(self):
        """Test ReadinessChecker initialization."""
        checker = ReadinessChecker()
        assert len(checker.READINESS_CHECKS) > 0
        assert "composition_root" in checker.READINESS_CHECKS
        assert "runtime" in checker.READINESS_CHECKS

    def test_register_custom_check(self):
        """Test registering a custom check."""
        checker = ReadinessChecker()
        checker.register_check("custom_check", lambda: (True, "OK"))
        result = checker.check_single("custom_check")
        assert result.name == "custom_check"
        assert result.passed is True

    def test_run_all_checks(self):
        """Test running all checks."""
        checker = ReadinessChecker()
        report = checker.run_all_checks()
        assert report is not None
        assert isinstance(report, ReadinessReport)
        assert len(report.checks) > 0

    def test_check_single(self):
        """Test running a single check."""
        checker = ReadinessChecker()
        result = checker.check_single("composition_root")
        assert result.name == "composition_root"
        assert result.description is not None

    def test_custom_check_function(self):
        """Test custom check function."""
        checker = ReadinessChecker()
        checker.register_check("passing", lambda: (True, "Passed"))
        checker.register_check("failing", lambda: (False, "Failed"))

        passing = checker.check_single("passing")
        failing = checker.check_single("failing")

        assert passing.passed is True
        assert failing.passed is False
        assert failing.message == "Failed"

    def test_check_with_exception(self):
        """Test check that raises exception."""
        checker = ReadinessChecker()
        checker.register_check("error", lambda: (_ for _ in ()).throw(Exception("Test")))

        result = checker.check_single("error")
        assert result.passed is False
        assert "Test" in result.message

    def test_critical_checks(self):
        """Test that critical checks are identified."""
        checker = ReadinessChecker()
        assert checker.READINESS_CHECKS["composition_root"]["critical"] is True
        assert checker.READINESS_CHECKS["scheduler"]["critical"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
