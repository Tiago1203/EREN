"""SDK exceptions for EREN OS Cognitive Capability SDK.

Defines all exceptions that can be raised during SDK operations.
"""

from __future__ import annotations


class SDKException(Exception):
    """Base exception for SDK errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CapabilityInitializationError(SDKException):
    """Raised when capability fails to initialize."""

    def __init__(self, message: str, capability_id: str = ""):
        super().__init__(message, {"capability_id": capability_id})
        self.capability_id = capability_id


class CapabilityExecutionError(SDKException):
    """Raised when capability execution fails."""

    def __init__(self, message: str, capability_id: str = ""):
        super().__init__(message, {"capability_id": capability_id})
        self.capability_id = capability_id


class CapabilityNotFoundError(SDKException):
    """Raised when capability is not found."""

    def __init__(self, capability_id: str):
        super().__init__(f"Capability not found: {capability_id}", {"capability_id": capability_id})
        self.capability_id = capability_id


class CapabilityAlreadyRegisteredError(SDKException):
    """Raised when capability is already registered."""

    def __init__(self, capability_id: str):
        super().__init__(f"Capability already registered: {capability_id}", {"capability_id": capability_id})
        self.capability_id = capability_id


class CapabilityValidationError(SDKException):
    """Raised when capability validation fails."""

    def __init__(self, message: str, capability_id: str = ""):
        super().__init__(message, {"capability_id": capability_id})
        self.capability_id = capability_id


class CapabilityDependencyError(SDKException):
    """Raised when capability dependency is not satisfied."""

    def __init__(self, message: str, capability_id: str = "", dependency_id: str = ""):
        super().__init__(message, {"capability_id": capability_id, "dependency_id": dependency_id})
        self.capability_id = capability_id
        self.dependency_id = dependency_id


class CapabilityContractError(SDKException):
    """Raised when capability does not satisfy required contracts."""

    def __init__(self, message: str, capability_id: str = "", contract_name: str = ""):
        super().__init__(message, {"capability_id": capability_id, "contract_name": contract_name})
        self.capability_id = capability_id
        self.contract_name = contract_name


class CapabilityStateError(SDKException):
    """Raised when capability operation is invalid for current state."""

    def __init__(self, message: str, capability_id: str = "", current_state: str = ""):
        super().__init__(message, {"capability_id": capability_id, "current_state": current_state})
        self.capability_id = capability_id
        self.current_state = current_state


class CapabilityBuilderError(SDKException):
    """Raised when capability builder encounters an error."""

    def __init__(self, message: str):
        super().__init__(message)


class CapabilityContextError(SDKException):
    """Raised when capability context is invalid."""

    def __init__(self, message: str, context_key: str = ""):
        super().__init__(message, {"context_key": context_key})
        self.context_key = context_key
