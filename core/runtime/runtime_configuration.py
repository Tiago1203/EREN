"""Runtime configuration for the Cognitive Operating System.

Defines all configuration options for the Cognitive Runtime.
Configuration is immutable once the runtime is built.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RuntimeConfiguration:
    """Configuration for the Cognitive Runtime.

    This configuration controls all aspects of the runtime behavior,
    including initialization, validation, execution, and shutdown.

    All fields are immutable (frozen=True) to ensure configuration
    consistency throughout the runtime lifecycle.
    """

    # Runtime Identification
    runtime_name: str = "EREN Cognitive Runtime"
    runtime_version: str = "1.0.0"
    environment: str = "development"

    # Initialization
    auto_boot: bool = True
    auto_validate: bool = True
    validate_before_start: bool = True

    # Boot Configuration
    boot_timeout_ms: int = 30000
    boot_stop_on_error: bool = True

    # Component Configuration
    use_composition_root: bool = True
    use_container: bool = True
    use_event_bus: bool = True
    use_capability_registry: bool = True

    # Session Configuration
    max_concurrent_sessions: int = 10
    session_timeout_ms: int = 300000  # 5 minutes
    auto_create_session: bool = True

    # Cognitive Cycle Configuration
    max_cycles_per_session: int = 5
    cycle_timeout_ms: int = 60000  # 1 minute
    enable_cycle_metrics: bool = True
    enable_cycle_trace: bool = True

    # Engine Configuration
    enable_planner: bool = True
    enable_knowledge: bool = True
    enable_memory: bool = True
    enable_reasoning: bool = True
    enable_decision: bool = True
    enable_tools: bool = True

    # Simulation Mode (for demo/testing without real AI)
    simulation_mode: bool = True
    simulation_delay_ms: int = 100

    # Event Configuration
    publish_events: bool = True
    event_buffer_size: int = 1000
    async_events: bool = False

    # Validation Configuration
    validate_contracts: bool = True
    validate_dependencies: bool = True
    validate_cycles: bool = True
    strict_validation: bool = False

    # Health Check Configuration
    enable_health_checks: bool = True
    health_check_interval_ms: int = 30000
    health_check_timeout_ms: int = 5000

    # Metrics Configuration
    enable_metrics: bool = True
    metrics_interval_ms: int = 60000
    record_trace: bool = True

    # Shutdown Configuration
    graceful_shutdown_timeout_ms: int = 30000
    force_shutdown_on_timeout: bool = True
    cleanup_on_shutdown: bool = True

    # Feature Flags
    enable_experimental_features: bool = False
    enable_debug_mode: bool = False

    # Additional Configuration
    custom_config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_default(cls) -> RuntimeConfiguration:
        """Create a default runtime configuration.

        Returns:
            A new configuration with default values.
        """
        return cls()

    @classmethod
    def create_development(cls) -> RuntimeConfiguration:
        """Create a configuration optimized for development.

        Returns:
            A new configuration for development.
        """
        return cls(
            environment="development",
            enable_debug_mode=True,
            enable_metrics=True,
            record_trace=True,
            strict_validation=False,
        )

    @classmethod
    def create_production(cls) -> RuntimeConfiguration:
        """Create a configuration optimized for production.

        Returns:
            A new configuration for production.
        """
        return cls(
            environment="production",
            enable_debug_mode=False,
            enable_metrics=True,
            record_trace=True,
            strict_validation=True,
            simulation_mode=False,
        )

    @classmethod
    def create_testing(cls) -> RuntimeConfiguration:
        """Create a configuration optimized for testing.

        Returns:
            A new configuration for testing.
        """
        return cls(
            environment="testing",
            simulation_mode=True,
            simulation_delay_ms=0,
            enable_debug_mode=True,
            enable_metrics=True,
            record_trace=True,
            auto_boot=True,
            auto_validate=True,
        )

    def merge(self, **overrides: Any) -> RuntimeConfiguration:
        """Create a new configuration with overrides.

        Args:
            **overrides: Fields to override.

        Returns:
            A new configuration with the overrides applied.
        """
        import dataclasses

        # Get current values as dict
        current = dataclasses.asdict(self)

        # Apply overrides
        for key, value in overrides.items():
            if key in current:
                current[key] = value

        # Reconstruct
        return dataclasses.replace(self, **overrides)


@dataclass(frozen=True)
class EngineConfiguration:
    """Configuration for a specific cognitive engine.

    Each engine can have its own configuration within the runtime.
    """

    engine_name: str
    enabled: bool = True
    timeout_ms: int = 10000
    max_retries: int = 3
    custom_config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_planner(cls) -> EngineConfiguration:
        """Create planner engine configuration."""
        return cls(engine_name="planner", timeout_ms=15000)

    @classmethod
    def create_knowledge(cls) -> EngineConfiguration:
        """Create knowledge engine configuration."""
        return cls(engine_name="knowledge", timeout_ms=10000)

    @classmethod
    def create_memory(cls) -> EngineConfiguration:
        """Create memory engine configuration."""
        return cls(engine_name="memory", timeout_ms=8000)

    @classmethod
    def create_reasoning(cls) -> EngineConfiguration:
        """Create reasoning engine configuration."""
        return cls(engine_name="reasoning", timeout_ms=20000)

    @classmethod
    def create_decision(cls) -> EngineConfiguration:
        """Create decision engine configuration."""
        return cls(engine_name="decision", timeout_ms=10000)

    @classmethod
    def create_tools(cls) -> EngineConfiguration:
        """Create tools engine configuration."""
        return cls(engine_name="tools", timeout_ms=15000)


@dataclass
class SessionConfiguration:
    """Configuration for a cognitive session.

    Each session can have its own configuration that overrides
    the global runtime configuration.
    """

    session_type: str = "troubleshooting"
    user_id: str = ""
    hospital_id: str = ""
    priority: int = 5
    max_cycles: int = 5
    timeout_ms: int = 300000
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_default(cls) -> SessionConfiguration:
        """Create a default session configuration."""
        return cls()

    @classmethod
    def create_diagnostic(cls, user_id: str = "") -> SessionConfiguration:
        """Create a diagnostic session configuration."""
        return cls(
            session_type="diagnostic",
            user_id=user_id,
            max_cycles=10,
            priority=10,
        )
