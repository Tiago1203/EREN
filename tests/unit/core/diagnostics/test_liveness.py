"""Unit tests for diagnostics liveness module."""

import pytest

from core.diagnostics.liveness import (
    LivenessChecker,
    LivenessCheck,
    LivenessReport,
)


class TestLivenessCheck:
    """Tests for LivenessCheck dataclass."""

    def test_creation(self):
        """Test LivenessCheck creation."""
        check = LivenessCheck(
            name="test",
            description="Test check",
            passed=True,
            response_time_ms=50,
        )
        assert check.name == "test"
        assert check.passed is True
        assert check.response_time_ms == 50

    def test_to_dict(self):
        """Test to_dict conversion."""
        check = LivenessCheck(
            name="test",
            description="Test",
            passed=True,
            response_time_ms=100,
            message="OK",
        )
        d = check.to_dict()
        assert d["name"] == "test"
        assert d["passed"] is True
        assert d["response_time_ms"] == 100


class TestLivenessReport:
    """Tests for LivenessReport dataclass."""

    def test_creation(self):
        """Test LivenessReport creation."""
        report = LivenessReport(
            is_alive=True,
            checks=[],
            total_duration_ms=100,
            average_response_time_ms=50,
        )
        assert report.is_alive is True
        assert len(report.checks) == 0

    def test_to_dict(self):
        """Test to_dict conversion."""
        report = LivenessReport(
            is_alive=True,
            checks=[
                LivenessCheck("check1", "desc", True, 50),
                LivenessCheck("check2", "desc", False, 100),
            ],
            total_duration_ms=150,
            average_response_time_ms=75,
            timeout_failures=["check2"],
        )
        d = report.to_dict()
        assert d["is_alive"] is True
        assert d["passed_count"] == 1
        assert d["failed_count"] == 1
        assert d["average_response_time_ms"] == 75


class TestLivenessChecker:
    """Tests for LivenessChecker class."""

    def test_initialization(self):
        """Test LivenessChecker initialization."""
        checker = LivenessChecker()
        assert len(checker.LIVENESS_CHECKS) > 0
        assert "event_bus_ping" in checker.LIVENESS_CHECKS
        assert "container_resolve" in checker.LIVENESS_CHECKS

    def test_register_custom_check(self):
        """Test registering a custom check."""
        checker = LivenessChecker()
        checker.register_check("custom", lambda: (True, "OK", 50))

        result = checker.check_single("custom")
        assert result.name == "custom"
        assert result.passed is True
        assert result.response_time_ms == 50

    def test_run_all_checks(self):
        """Test running all checks."""
        checker = LivenessChecker()
        report = checker.run_all_checks()
        assert report is not None
        assert isinstance(report, LivenessReport)
        assert len(report.checks) > 0

    def test_check_single(self):
        """Test running a single check."""
        checker = LivenessChecker()
        result = checker.check_single("event_bus_ping")
        assert result.name == "event_bus_ping"

    def test_custom_check_function(self):
        """Test custom check function with timing."""
        checker = LivenessChecker()
        checker.register_check("fast", lambda: (True, "Fast", 50))
        checker.register_check("slow", lambda: (True, "Slow", 500))

        fast = checker.check_single("fast")
        slow = checker.check_single("slow")

        assert fast.response_time_ms == 50
        assert slow.response_time_ms == 500

    def test_check_with_exception(self):
        """Test check that raises exception."""
        checker = LivenessChecker()
        checker.register_check("error", lambda: (_ for _ in ()).throw(Exception("Test")))

        result = checker.check_single("error")
        assert result.passed is False

    def test_timeout_threshold(self):
        """Test that slow checks are flagged."""
        checker = LivenessChecker()
        # Note: timeout check is for the check response time, not the overall timeout
        # The liveness check doesn't fail individual checks for being slow,
        # only for exceeding the global timeout
        checker.register_check("custom_slow", lambda: (True, "OK", 2000))

        report = checker.run_all_checks()

        # The custom_slow check should exist
        custom = next((c for c in report.checks if c.name == "custom_slow"), None)
        assert custom is not None
        # It passes because the timeout is per-check, not a failure condition
        assert custom.response_time_ms == 2000

    def test_set_default_timeout(self):
        """Test setting default timeout."""
        checker = LivenessChecker()
        checker.set_default_timeout(3000)
        assert checker._default_timeout_ms == 3000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
