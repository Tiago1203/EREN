"""Exceptions for the Cognitive Boot Manager."""


class BootError(Exception):
    """Base exception for boot errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class BootStepError(BootError):
    """Raised when a boot step fails."""

    def __init__(self, step_name: str = "", error: str = ""):
        super().__init__(f"Boot step '{step_name}' failed: {error}")
        self.step_name = step_name
        self.error = error


class BootTimeoutError(BootError):
    """Raised when boot times out."""

    def __init__(self, timeout_ms: int = 0):
        super().__init__(f"Boot timed out after {timeout_ms}ms")
        self.timeout_ms = timeout_ms


class BootRollbackError(BootError):
    """Raised when rollback fails."""

    def __init__(self, step_name: str = "", error: str = ""):
        super().__init__(f"Rollback failed at '{step_name}': {error}")
        self.step_name = step_name
        self.error = error


class BootConfigurationError(BootError):
    """Raised when configuration is invalid."""

    def __init__(self, config_key: str = "", error: str = ""):
        super().__init__(f"Configuration error for '{config_key}': {error}")
        self.config_key = config_key
        self.error = error


class BootContractViolationError(BootError):
    """Raised when a contract is violated."""

    def __init__(self, contract_name: str = "", error: str = ""):
        super().__init__(f"Contract violation '{contract_name}': {error}")
        self.contract_name = contract_name
        self.error = error
