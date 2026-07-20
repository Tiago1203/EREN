"""Plugin exceptions for EREN OS Cognitive Plugin Framework.

Defines all exceptions that can be raised during plugin operations.
"""

from __future__ import annotations


class PluginException(Exception):
    """Base exception for all plugin errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PluginInitializationError(PluginException):
    """Raised when plugin fails to initialize."""
    pass


class PluginLoadError(PluginException):
    """Raised when plugin loading fails."""

    def __init__(self, message: str, plugin_id: str = ""):
        super().__init__(message, {"plugin_id": plugin_id})
        self.plugin_id = plugin_id


class PluginNotFoundError(PluginException):
    """Raised when plugin is not found."""

    def __init__(self, plugin_id: str):
        super().__init__(f"Plugin not found: {plugin_id}", {"plugin_id": plugin_id})
        self.plugin_id = plugin_id


class PluginAlreadyRegisteredError(PluginException):
    """Raised when plugin is already registered."""

    def __init__(self, plugin_id: str):
        super().__init__(f"Plugin already registered: {plugin_id}", {"plugin_id": plugin_id})
        self.plugin_id = plugin_id


class PluginValidationError(PluginException):
    """Raised when plugin validation fails."""

    def __init__(self, message: str, plugin_id: str = ""):
        super().__init__(message, {"plugin_id": plugin_id})
        self.plugin_id = plugin_id


class PluginDependencyError(PluginException):
    """Raised when plugin dependency is not satisfied."""

    def __init__(self, message: str, plugin_id: str = "", dependency_id: str = ""):
        super().__init__(message, {"plugin_id": plugin_id, "dependency_id": dependency_id})
        self.plugin_id = plugin_id
        self.dependency_id = dependency_id


class PluginActivationError(PluginException):
    """Raised when plugin activation fails."""

    def __init__(self, message: str, plugin_id: str = ""):
        super().__init__(message, {"plugin_id": plugin_id})
        self.plugin_id = plugin_id


class PluginStateError(PluginException):
    """Raised when plugin operation is invalid for current state."""

    def __init__(self, message: str, plugin_id: str = "", current_state: str = ""):
        super().__init__(message, {"plugin_id": plugin_id, "current_state": current_state})
        self.plugin_id = plugin_id
        self.current_state = current_state


class PluginManifestError(PluginException):
    """Raised when plugin manifest is invalid."""

    def __init__(self, message: str, manifest_path: str = ""):
        super().__init__(message, {"manifest_path": manifest_path})
        self.manifest_path = manifest_path


class PluginContractError(PluginException):
    """Raised when plugin does not satisfy required contracts."""

    def __init__(self, message: str, plugin_id: str = "", contract_name: str = ""):
        super().__init__(message, {"plugin_id": plugin_id, "contract_name": contract_name})
        self.plugin_id = plugin_id
        self.contract_name = contract_name


class PluginLoaderError(PluginException):
    """Raised when plugin loader encounters an error."""

    def __init__(self, message: str, loader_type: str = ""):
        super().__init__(message, {"loader_type": loader_type})
        self.loader_type = loader_type


class PluginPolicyViolationError(PluginException):
    """Raised when plugin violates a policy."""

    def __init__(self, message: str, policy_name: str = ""):
        super().__init__(message, {"policy_name": policy_name})
        self.policy_name = policy_name


class PluginCyclicDependencyError(PluginException):
    """Raised when cyclic dependencies are detected."""

    def __init__(self, message: str, dependency_chain: list[str] | None = None):
        super().__init__(message, {"dependency_chain": dependency_chain or []})
        self.dependency_chain = dependency_chain or []


class PluginDisabledError(PluginException):
    """Raised when plugin is disabled."""

    def __init__(self, plugin_id: str):
        super().__init__(f"Plugin is disabled: {plugin_id}", {"plugin_id": plugin_id})
        self.plugin_id = plugin_id


class PluginVersionError(PluginException):
    """Raised when plugin version is incompatible."""

    def __init__(self, message: str, plugin_id: str = "", required_version: str = ""):
        super().__init__(message, {"plugin_id": plugin_id, "required_version": required_version})
        self.plugin_id = plugin_id
        self.required_version = required_version
