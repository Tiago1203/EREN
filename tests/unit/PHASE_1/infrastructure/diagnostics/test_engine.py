"""Unit tests for diagnostics engine module."""

import pytest

from core.PHASE_1.infrastructure.diagnostics.engine import ERENDiagnostics, DiagnosticsEngine


class TestERENDiagnostics:
    """Tests for ERENDiagnostics class."""

    def test_initialization(self):
        """Test ERENDiagnostics initialization."""
        diag = ERENDiagnostics()
        assert diag._correlation_id is not None
        assert diag._correlation_id.startswith("diag_")
        assert diag._validation_options["architecture"] is True
        assert diag._validation_options["contracts"] is True

    def test_fluent_api_architecture(self):
        """Test fluent API for architecture validation."""
        diag = ERENDiagnostics()
        result = diag.with_architecture_validation(False)
        assert result is diag
        assert diag._validation_options["architecture"] is False

    def test_fluent_api_contracts(self):
        """Test fluent API for contracts validation."""
        diag = ERENDiagnostics()
        result = diag.with_contract_validation(False)
        assert result is diag
        assert diag._validation_options["contracts"] is False

    def test_fluent_api_dependencies(self):
        """Test fluent API for dependencies validation."""
        diag = ERENDiagnostics()
        result = diag.with_dependency_validation(False)
        assert result is diag
        assert diag._validation_options["dependencies"] is False

    def test_fluent_api_integration(self):
        """Test fluent API for integration validation."""
        diag = ERENDiagnostics()
        result = diag.with_integration_validation(False)
        assert result is diag
        assert diag._validation_options["integration"] is False

    def test_fluent_api_runtime(self):
        """Test fluent API for runtime validation."""
        diag = ERENDiagnostics()
        result = diag.with_runtime_validation(False)
        assert result is diag
        assert diag._validation_options["runtime"] is False

    def test_fluent_api_health(self):
        """Test fluent API for health check."""
        diag = ERENDiagnostics()
        result = diag.with_health_check(False)
        assert result is diag
        assert diag._validation_options["health"] is False

    def test_fluent_api_readiness(self):
        """Test fluent API for readiness check."""
        diag = ERENDiagnostics()
        result = diag.with_readiness_check(False)
        assert result is diag
        assert diag._validation_options["readiness"] is False

    def test_fluent_api_liveness(self):
        """Test fluent API for liveness check."""
        diag = ERENDiagnostics()
        result = diag.with_liveness_check(False)
        assert result is diag
        assert diag._validation_options["liveness"] is False

    def test_fluent_api_performance(self):
        """Test fluent API for performance profiling."""
        diag = ERENDiagnostics()
        result = diag.with_performance_profiling(False)
        assert result is diag
        assert diag._validation_options["performance"] is False

    def test_run_full_system_validation(self):
        """Test running full system validation."""
        diag = ERENDiagnostics()
        report = diag.run_full_system_validation()

        assert report is not None
        assert report.correlation_id is not None
        assert report.score >= 0
        assert report.score <= 100

    def test_run_minimal_validation(self):
        """Test running minimal validation."""
        diag = (
            ERENDiagnostics()
            .with_architecture_validation()
            .with_contract_validation()
            .with_dependency_validation()
        )
        report = diag.run_full_system_validation()

        assert report is not None
        assert report.score >= 0

    def test_diagnostics_engine_alias(self):
        """Test that DiagnosticsEngine is an alias for ERENDiagnostics."""
        assert DiagnosticsEngine is ERENDiagnostics


class TestValidationOptions:
    """Tests for validation options."""

    def test_all_validations_enabled_by_default(self):
        """Test that all validations are enabled by default."""
        diag = ERENDiagnostics()
        for key, enabled in diag._validation_options.items():
            assert enabled is True, f"{key} should be enabled by default"

    def test_disable_all_validations(self):
        """Test disabling all validations."""
        diag = (
            ERENDiagnostics()
            .with_architecture_validation(False)
            .with_contract_validation(False)
            .with_dependency_validation(False)
            .with_integration_validation(False)
            .with_runtime_validation(False)
            .with_health_check(False)
            .with_readiness_check(False)
            .with_liveness_check(False)
            .with_performance_profiling(False)
        )
        for key, enabled in diag._validation_options.items():
            assert enabled is False, f"{key} should be disabled"

    def test_enable_specific_validations(self):
        """Test enabling only specific validations."""
        diag = (
            ERENDiagnostics()
            .with_architecture_validation(False)
            .with_contract_validation(False)
            .with_dependency_validation(False)
            .with_integration_validation(False)
            .with_runtime_validation(False)
            .with_health_check(False)
            .with_readiness_check(False)
            .with_liveness_check(False)
            .with_performance_profiling(False)
        )
        # Now enable just architecture
        diag.with_architecture_validation(True)

        assert diag._validation_options["architecture"] is True
        # Others should still be False
        for key in diag._validation_options:
            if key != "architecture":
                assert diag._validation_options[key] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
