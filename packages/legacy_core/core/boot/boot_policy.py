"""Boot policies for the Cognitive Boot Manager.

Defines policies for the boot process.

Architecture only -- no implementations, no business logic.
"""


class BootPolicy:
    """Policies for the boot process."""

    def __init__(
        self,
        strict_mode: bool = True,
        stop_on_error: bool = True,
        enable_rollback: bool = True,
        timeout_ms: int = 30000,
        step_timeout_ms: int = 5000,
        validate_contracts: bool = True,
        enable_health_checks: bool = True,
    ):
        self.strict_mode = strict_mode
        self.stop_on_error = stop_on_error
        self.enable_rollback = enable_rollback
        self.timeout_ms = timeout_ms
        self.step_timeout_ms = step_timeout_ms
        self.validate_contracts = validate_contracts
        self.enable_health_checks = enable_health_checks


class BootPolicyPresets:
    """Presets for boot policies."""

    @staticmethod
    def development():
        """Policy for development environments."""
        return BootPolicy(
            strict_mode=False,
            stop_on_error=False,
            enable_rollback=True,
            timeout_ms=60000,
            step_timeout_ms=10000,
        )

    @staticmethod
    def production():
        """Policy for production environments."""
        return BootPolicy(
            strict_mode=True,
            stop_on_error=True,
            enable_rollback=True,
            timeout_ms=30000,
            step_timeout_ms=5000,
        )

    @staticmethod
    def testing():
        """Policy for testing environments."""
        return BootPolicy(
            strict_mode=False,
            stop_on_error=False,
            enable_rollback=False,
            timeout_ms=60000,
            step_timeout_ms=30000,
        )
