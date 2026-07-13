"""Runtime builder for the Cognitive Operating System.

Provides a fluent builder API for constructing CognitiveRuntime
instances with custom configurations.
"""

from __future__ import annotations

from typing import Any

from .runtime import CognitiveRuntime
from .runtime_configuration import (
    EngineConfiguration,
    RuntimeConfiguration,
    SessionConfiguration,
)


class RuntimeBuilder:
    """Builder for creating CognitiveRuntime instances.

    Provides a fluent API for configuring and building the runtime.

    Usage:
        runtime = (
            RuntimeBuilder()
            .with_name("My Runtime")
            .with_version("1.0.0")
            .with_environment("production")
            .with_simulation_mode(False)
            .with_auto_boot(True)
            .with_auto_validate(True)
            .build()
        )
    """

    def __init__(self):
        """Initialize the builder."""
        self._configuration = RuntimeConfiguration.create_default()
        self._engine_configs: dict[str, EngineConfiguration] = {}

    # =============================================================================
    # Configuration Methods
    # =============================================================================

    def with_name(self, name: str) -> "RuntimeBuilder":
        """Set the runtime name.

        Args:
            name: Runtime name.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(runtime_name=name)
        return self

    def with_version(self, version: str) -> "RuntimeBuilder":
        """Set the runtime version.

        Args:
            version: Runtime version.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(runtime_version=version)
        return self

    def with_environment(self, environment: str) -> "RuntimeBuilder":
        """Set the runtime environment.

        Args:
            environment: Environment (development, production, testing).

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(environment=environment)
        return self

    def with_simulation_mode(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable simulation mode.

        In simulation mode, the runtime uses simulated data instead of
        real AI implementations.

        Args:
            enabled: Whether to enable simulation mode.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(simulation_mode=enabled)
        return self

    def with_simulation_delay(self, delay_ms: int) -> "RuntimeBuilder":
        """Set the simulation delay between stages.

        Args:
            delay_ms: Delay in milliseconds.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(simulation_delay_ms=delay_ms)
        return self

    def with_auto_boot(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable auto-boot.

        Args:
            enabled: Whether to auto-boot.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(auto_boot=enabled)
        return self

    def with_auto_validate(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable auto-validation.

        Args:
            enabled: Whether to auto-validate.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(auto_validate=enabled)
        return self

    def with_validate_before_start(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable pre-start validation.

        Args:
            enabled: Whether to validate before starting.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(
            validate_before_start=enabled
        )
        return self

    def with_strict_validation(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable strict validation.

        In strict mode, warnings are treated as errors.

        Args:
            enabled: Whether to enable strict validation.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(strict_validation=enabled)
        return self

    def with_boot_timeout(self, timeout_ms: int) -> "RuntimeBuilder":
        """Set the boot timeout.

        Args:
            timeout_ms: Boot timeout in milliseconds.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(boot_timeout_ms=timeout_ms)
        return self

    def with_session_timeout(self, timeout_ms: int) -> "RuntimeBuilder":
        """Set the session timeout.

        Args:
            timeout_ms: Session timeout in milliseconds.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(session_timeout_ms=timeout_ms)
        return self

    def with_cycle_timeout(self, timeout_ms: int) -> "RuntimeBuilder":
        """Set the cycle timeout.

        Args:
            timeout_ms: Cycle timeout in milliseconds.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(cycle_timeout_ms=timeout_ms)
        return self

    def with_max_concurrent_sessions(self, max_sessions: int) -> "RuntimeBuilder":
        """Set the maximum concurrent sessions.

        Args:
            max_sessions: Maximum number of concurrent sessions.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(
            max_concurrent_sessions=max_sessions
        )
        return self

    def with_max_cycles_per_session(self, max_cycles: int) -> "RuntimeBuilder":
        """Set the maximum cycles per session.

        Args:
            max_cycles: Maximum number of cycles per session.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(
            max_cycles_per_session=max_cycles
        )
        return self

    def with_metrics_enabled(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable metrics collection.

        Args:
            enabled: Whether to enable metrics.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(enable_metrics=enabled)
        return self

    def with_trace_enabled(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable trace recording.

        Args:
            enabled: Whether to enable tracing.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(record_trace=enabled)
        return self

    def with_health_checks_enabled(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable health checks.

        Args:
            enabled: Whether to enable health checks.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(
            enable_health_checks=enabled
        )
        return self

    def with_event_publishing_enabled(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable event publishing.

        Args:
            enabled: Whether to enable event publishing.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(publish_events=enabled)
        return self

    def with_graceful_shutdown_timeout(self, timeout_ms: int) -> "RuntimeBuilder":
        """Set the graceful shutdown timeout.

        Args:
            timeout_ms: Shutdown timeout in milliseconds.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(
            graceful_shutdown_timeout_ms=timeout_ms
        )
        return self

    def with_debug_mode(self, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable debug mode.

        Args:
            enabled: Whether to enable debug mode.

        Returns:
            Self for chaining.
        """
        self._configuration = self._configuration.merge(enable_debug_mode=enabled)
        return self

    # =============================================================================
    # Engine Configuration Methods
    # =============================================================================

    def with_engine_enabled(self, engine_name: str, enabled: bool) -> "RuntimeBuilder":
        """Enable or disable a specific engine.

        Args:
            engine_name: Name of the engine.
            enabled: Whether to enable the engine.

        Returns:
            Self for chaining.
        """
        config_map = {
            "planner": "enable_planner",
            "knowledge": "enable_knowledge",
            "memory": "enable_memory",
            "reasoning": "enable_reasoning",
            "decision": "enable_decision",
            "tools": "enable_tools",
        }
        config_key = config_map.get(engine_name, f"enable_{engine_name}")
        self._configuration = self._configuration.merge(**{config_key: enabled})
        return self

    def with_engine_config(
        self,
        engine_name: str,
        config: EngineConfiguration,
    ) -> "RuntimeBuilder":
        """Set configuration for a specific engine.

        Args:
            engine_name: Name of the engine.
            config: Engine configuration.

        Returns:
            Self for chaining.
        """
        self._engine_configs[engine_name] = config
        return self

    def with_engine_timeout(
        self,
        engine_name: str,
        timeout_ms: int,
    ) -> "RuntimeBuilder":
        """Set timeout for a specific engine.

        Args:
            engine_name: Name of the engine.
            timeout_ms: Engine timeout in milliseconds.

        Returns:
            Self for chaining.
        """
        if engine_name not in self._engine_configs:
            self._engine_configs[engine_name] = EngineConfiguration(
                engine_name=engine_name
            )
        self._engine_configs[engine_name] = EngineConfiguration(
            engine_name=engine_name,
            enabled=True,
            timeout_ms=timeout_ms,
        )
        return self

    # =============================================================================
    # Custom Configuration
    # =============================================================================

    def with_custom_config(self, key: str, value: Any) -> "RuntimeBuilder":
        """Add custom configuration.

        Args:
            key: Configuration key.
            value: Configuration value.

        Returns:
            Self for chaining.
        """
        custom = dict(self._configuration.custom_config)
        custom[key] = value
        self._configuration = self._configuration.merge(custom_config=custom)
        return self

    def with_custom_configs(self, configs: dict[str, Any]) -> "RuntimeBuilder":
        """Add multiple custom configurations.

        Args:
            configs: Configuration dictionary.

        Returns:
            Self for chaining.
        """
        custom = dict(self._configuration.custom_config)
        custom.update(configs)
        self._configuration = self._configuration.merge(custom_config=custom)
        return self

    # =============================================================================
    # Presets
    # =============================================================================

    def use_development_preset(self) -> "RuntimeBuilder":
        """Use development preset configuration.

        Returns:
            Self for chaining.
        """
        self._configuration = RuntimeConfiguration.create_development()
        return self

    def use_production_preset(self) -> "RuntimeBuilder":
        """Use production preset configuration.

        Returns:
            Self for chaining.
        """
        self._configuration = RuntimeConfiguration.create_production()
        return self

    def use_testing_preset(self) -> "RuntimeBuilder":
        """Use testing preset configuration.

        Returns:
            Self for chaining.
        """
        self._configuration = RuntimeConfiguration.create_testing()
        return self

    # =============================================================================
    # Build
    # =============================================================================

    def build(self, runtime_id: str | None = None) -> CognitiveRuntime:
        """Build the CognitiveRuntime.

        Args:
            runtime_id: Optional runtime ID.

        Returns:
            The configured CognitiveRuntime instance.
        """
        # Add engine configs to custom config
        if self._engine_configs:
            custom = dict(self._configuration.custom_config)
            custom["engine_configs"] = {
                name: config.__dict__
                for name, config in self._engine_configs.items()
            }
            self._configuration = self._configuration.merge(custom_config=custom)

        return CognitiveRuntime(
            configuration=self._configuration,
            runtime_id=runtime_id,
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_default_runtime() -> CognitiveRuntime:
    """Create a runtime with default configuration.

    Returns:
        A new CognitiveRuntime with default settings.
    """
    return RuntimeBuilder().build()


def create_development_runtime() -> CognitiveRuntime:
    """Create a runtime configured for development.

    Returns:
        A new CognitiveRuntime configured for development.
    """
    return RuntimeBuilder().use_development_preset().build()


def create_production_runtime() -> CognitiveRuntime:
    """Create a runtime configured for production.

    Returns:
        A new CognitiveRuntime configured for production.
    """
    return RuntimeBuilder().use_production_preset().build()


def create_testing_runtime() -> CognitiveRuntime:
    """Create a runtime configured for testing.

    Returns:
        A new CognitiveRuntime configured for testing.
    """
    return RuntimeBuilder().use_testing_preset().build()


def create_minimal_runtime() -> CognitiveRuntime:
    """Create a minimal runtime with minimal configuration.

    Returns:
        A new minimal CognitiveRuntime.
    """
    return (
        RuntimeBuilder()
        .with_simulation_mode(True)
        .with_simulation_delay(0)
        .with_auto_boot(True)
        .with_auto_validate(False)
        .with_metrics_enabled(False)
        .with_trace_enabled(False)
        .build()
    )
