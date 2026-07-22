"""Integration tests for diagnostics engine."""

import pytest

from core.PHASE_1.infrastructure.diagnostics import (
    ERENDiagnostics,
    SystemHealth,
    HealthStatus,
    ReadinessChecker,
    LivenessChecker,
    ArchitectureValidator,
    ContractValidator,
    DependencyValidator,
    IntegrationValidator,
    RuntimeValidator,
    PerformanceProfiler,
    DiagnosticScore,
    ScoreCategory,
)


class TestDiagnosticsIntegration:
    """Integration tests combining multiple diagnostics components."""

    def test_full_diagnostics_pipeline(self):
        """Test running complete diagnostics pipeline."""
        diag = ERENDiagnostics()
        report = diag.run_full_system_validation()

        # Verify report structure
        assert report is not None
        assert report.correlation_id is not None
        assert report.duration_ms >= 0
        assert 0 <= report.score <= 100

        # Verify sub-reports
        if report.health_report:
            assert report.health_report.overall_score >= 0
        if report.readiness_report:
            assert isinstance(report.readiness_report.is_ready, bool)
        if report.architecture_report:
            assert report.architecture_report.score >= 0

    def test_diagnostics_with_score_calculation(self):
        """Test that diagnostics correctly calculates scores."""
        diag = ERENDiagnostics()
        report = diag.run_full_system_validation()

        # Score should be calculated
        assert report.score > 0
        assert report.production_ready is not None
        assert isinstance(report.production_ready, bool)

    def test_health_and_readiness_integration(self):
        """Test health and readiness check integration."""
        # Run health check
        health = SystemHealth()
        health.register_component_health("orchestrator", HealthStatus.HEALTHY)
        health.register_component_health("planner", HealthStatus.HEALTHY)
        health_result = health.check_all_components()

        # Run readiness check
        readiness = ReadinessChecker()
        readiness_result = readiness.run_all_checks()

        # Both should complete
        assert health_result.overall_score > 0
        assert isinstance(readiness_result.is_ready, bool)

    def test_validator_integration(self):
        """Test multiple validators work together."""
        # Architecture validation
        arch_validator = ArchitectureValidator()
        arch_report = arch_validator.validate()

        # Contract validation
        contract_validator = ContractValidator()
        contract_report = contract_validator.validate()

        # Dependency validation
        dep_validator = DependencyValidator()
        dep_validator.register_dependencies("orchestrator", ["planner"])
        dep_report = dep_validator.validate()

        # Integration validation
        int_validator = IntegrationValidator()
        int_report = int_validator.validate()

        # All should complete
        assert arch_report.score >= 0
        assert contract_report.score >= 0
        assert dep_report.score >= 0
        assert int_report.score >= 0

    def test_score_aggregation(self):
        """Test that scores aggregate correctly."""
        score = DiagnosticScore()

        # Set scores for multiple categories
        score.set_category_score(ScoreCategory.ARCHITECTURE, 100.0)
        score.set_category_score(ScoreCategory.CONTRACTS, 90.0)
        score.set_category_score(ScoreCategory.PERFORMANCE, 85.0)

        overall = score.get_overall_score()

        # Overall should be weighted average
        assert 85 <= overall <= 100
        assert score.get_production_readiness()[0] is True

    def test_performance_profiling_integration(self):
        """Test performance profiler integration."""
        profiler = PerformanceProfiler()
        profiler.start_profiling()

        # Record some measurements
        profiler.record_component_time("orchestrator", 50.0)
        profiler.record_component_time("planner", 30.0)
        profiler.record_event("test_event")

        # Generate report
        report = profiler.profile()

        assert report.score >= 0
        assert len(report.metrics) > 0


class TestDiagnosticsReport:
    """Tests for diagnostic report generation."""

    def test_report_summary(self):
        """Test report summary generation."""
        diag = ERENDiagnostics()
        report = diag.run_full_system_validation()

        summary = report.summary()
        assert "EREN OS DIAGNOSTIC REPORT" in summary
        assert "Final Score" in summary or "Score" in summary

    def test_report_recommendations(self):
        """Test report recommendations generation."""
        diag = ERENDiagnostics()
        report = diag.run_full_system_validation()

        recommendations = report.get_recommendations()
        assert isinstance(recommendations, list)

    def test_report_to_dict(self):
        """Test report to_dict conversion."""
        diag = ERENDiagnostics()
        report = diag.run_full_system_validation()

        d = report.to_dict()
        assert "score" in d
        assert "production_ready" in d
        assert "generated_at" in d


class TestDiagnosticsEvents:
    """Tests for diagnostics event publishing."""

    def test_events_published(self):
        """Test that diagnostic events are published."""
        from core.PHASE_1.infrastructure.diagnostics.events import get_publisher, DiagnosticsEventType

        publisher = get_publisher()
        publisher.clear_history()

        # Run diagnostics
        diag = ERENDiagnostics()
        diag.run_full_system_validation()

        # Check events were published
        history = publisher.get_event_history()
        assert len(history) > 0

        # Check for start and completion events
        event_types = [e["event_type"] for e in history]
        has_started = "diagnostics_started" in event_types
        has_other_started = any("started" in et for et in event_types)
        assert has_started or has_other_started


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
