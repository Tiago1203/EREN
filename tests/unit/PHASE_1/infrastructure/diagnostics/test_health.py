"""Unit tests for diagnostics health module."""

import pytest
from datetime import datetime, timezone

from core.PHASE_1.infrastructure.diagnostics.health import (
    SystemHealth,
    HealthStatus,
    ComponentHealth,
    HealthCheckResult,
)


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_health_status_values(self):
        """Test HealthStatus enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.FAILED.value == "failed"

    def test_from_score_healthy(self):
        """Test score >= 90 returns HEALTHY."""
        assert HealthStatus.from_score(90) == HealthStatus.HEALTHY
        assert HealthStatus.from_score(100) == HealthStatus.HEALTHY

    def test_from_score_degraded(self):
        """Test score 70-89 returns DEGRADED."""
        assert HealthStatus.from_score(70) == HealthStatus.DEGRADED
        assert HealthStatus.from_score(89) == HealthStatus.DEGRADED

    def test_from_score_unhealthy(self):
        """Test score 40-69 returns UNHEALTHY."""
        assert HealthStatus.from_score(40) == HealthStatus.UNHEALTHY
        assert HealthStatus.from_score(69) == HealthStatus.UNHEALTHY

    def test_from_score_failed(self):
        """Test score < 40 returns FAILED."""
        assert HealthStatus.from_score(0) == HealthStatus.FAILED
        assert HealthStatus.from_score(39) == HealthStatus.FAILED


class TestComponentHealth:
    """Tests for ComponentHealth dataclass."""

    def test_creation(self):
        """Test ComponentHealth creation."""
        health = ComponentHealth(
            component_name="test_component",
            status=HealthStatus.HEALTHY,
            message="All good",
        )
        assert health.component_name == "test_component"
        assert health.status == HealthStatus.HEALTHY
        assert health.message == "All good"
        assert health.checked_at is not None

    def test_to_dict(self):
        """Test ComponentHealth to_dict conversion."""
        health = ComponentHealth(
            component_name="test",
            status=HealthStatus.HEALTHY,
            message="OK",
            details={"key": "value"},
        )
        result = health.to_dict()
        assert result["component_name"] == "test"
        assert result["status"] == "healthy"
        assert result["message"] == "OK"
        assert result["details"] == {"key": "value"}


class TestSystemHealth:
    """Tests for SystemHealth class."""

    def test_initialization(self):
        """Test SystemHealth initialization."""
        health = SystemHealth()
        assert health.get_all_health() == {}

    def test_register_component_health(self):
        """Test registering component health."""
        health = SystemHealth()
        health.register_component_health(
            component_name="orchestrator",
            status=HealthStatus.HEALTHY,
            message="Running",
        )
        result = health.get_component_health("orchestrator")
        assert result is not None
        assert result.status == HealthStatus.HEALTHY

    def test_get_nonexistent_component(self):
        """Test getting health for nonexistent component."""
        health = SystemHealth()
        result = health.get_component_health("nonexistent")
        assert result is None

    def test_get_overall_status_empty(self):
        """Test overall status with no components."""
        health = SystemHealth()
        status, score = health.get_overall_status()
        assert status == HealthStatus.FAILED
        assert score == 0.0

    def test_get_overall_status_healthy(self):
        """Test overall status with healthy components."""
        health = SystemHealth()
        health.register_component_health("comp1", HealthStatus.HEALTHY)
        health.register_component_health("comp2", HealthStatus.HEALTHY)
        status, score = health.get_overall_status()
        assert status == HealthStatus.HEALTHY
        assert score == 100.0

    def test_get_overall_status_mixed(self):
        """Test overall status with mixed health."""
        health = SystemHealth()
        health.register_component_health("comp1", HealthStatus.HEALTHY)
        health.register_component_health("comp2", HealthStatus.DEGRADED)
        status, score = health.get_overall_status()
        assert score == 85.0  # (100 + 70) / 2

    def test_get_overall_status_with_failed(self):
        """Test overall status with failed components."""
        health = SystemHealth()
        health.register_component_health("comp1", HealthStatus.HEALTHY)
        health.register_component_health("comp2", HealthStatus.FAILED)
        status, score = health.get_overall_status()
        assert status == HealthStatus.FAILED
        assert score == 50.0  # (100 + 0) / 2

    def test_check_all_components(self):
        """Test full component health check."""
        health = SystemHealth()
        health.register_component_health("comp1", HealthStatus.HEALTHY)
        health.register_component_health("comp2", HealthStatus.DEGRADED)

        result = health.check_all_components()
        assert result.overall_score == 85.0
        assert result.is_healthy is False
        assert len(result.component_checks) >= 2

    def test_required_components(self):
        """Test that required components are tracked."""
        health = SystemHealth()
        assert "orchestrator" in health.REQUIRED_COMPONENTS
        assert "runtime" in health.REQUIRED_COMPONENTS
        assert "event_bus" in health.REQUIRED_COMPONENTS

    def test_get_statistics(self):
        """Test health statistics."""
        health = SystemHealth()
        health.register_component_health("comp1", HealthStatus.HEALTHY)
        health.register_component_health("comp2", HealthStatus.DEGRADED)

        stats = health.get_statistics()
        assert stats["total_components"] == 2
        assert stats["status_counts"]["healthy"] == 1
        assert stats["status_counts"]["degraded"] == 1


class TestHealthCheckResult:
    """Tests for HealthCheckResult dataclass."""

    def test_creation(self):
        """Test HealthCheckResult creation."""
        result = HealthCheckResult(
            overall_status=HealthStatus.HEALTHY,
            overall_score=95.0,
            component_checks=[],
        )
        assert result.overall_status == HealthStatus.HEALTHY
        assert result.overall_score == 95.0
        assert result.is_healthy is True

    def test_is_production_ready_healthy(self):
        """Test production ready with healthy status."""
        result = HealthCheckResult(
            overall_status=HealthStatus.HEALTHY,
            overall_score=95.0,
            component_checks=[],
        )
        assert result.is_production_ready is True

    def test_is_production_ready_degraded_high_score(self):
        """Test production ready with degraded status but high score."""
        result = HealthCheckResult(
            overall_status=HealthStatus.DEGRADED,
            overall_score=85.0,
            component_checks=[],
        )
        assert result.is_production_ready is True

    def test_is_production_ready_degraded_low_score(self):
        """Test not production ready with degraded status and low score."""
        result = HealthCheckResult(
            overall_status=HealthStatus.DEGRADED,
            overall_score=75.0,
            component_checks=[],
        )
        assert result.is_production_ready is False

    def test_to_dict(self):
        """Test to_dict conversion."""
        result = HealthCheckResult(
            overall_status=HealthStatus.HEALTHY,
            overall_score=95.0,
            component_checks=[],
            duration_ms=100,
            errors=["error1"],
            warnings=["warning1"],
        )
        d = result.to_dict()
        assert d["overall_status"] == "healthy"
        assert d["overall_score"] == 95.0
        assert d["is_healthy"] is True
        assert d["duration_ms"] == 100
        assert "error1" in d["errors"]
        assert "warning1" in d["warnings"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
