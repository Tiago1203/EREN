"""Model exceptions for EREN OS Cognitive Model Registry.

Defines all exceptions that can be raised during model operations.
"""

from __future__ import annotations


class ModelRegistryException(Exception):
    """Base exception for model registry errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ModelNotFoundError(ModelRegistryException):
    """Raised when model is not found."""

    def __init__(self, model_id: str):
        super().__init__(f"Model not found: {model_id}", {"model_id": model_id})
        self.model_id = model_id


class ModelAlreadyRegisteredError(ModelRegistryException):
    """Raised when model is already registered."""

    def __init__(self, model_id: str):
        super().__init__(f"Model already registered: {model_id}", {"model_id": model_id})
        self.model_id = model_id


class ModelNotRegisteredError(ModelRegistryException):
    """Raised when model is not registered."""

    def __init__(self, model_id: str):
        super().__init__(f"Model not registered: {model_id}", {"model_id": model_id})
        self.model_id = model_id


class ModelUnavailableError(ModelRegistryException):
    """Raised when model is unavailable."""

    def __init__(self, model_id: str, reason: str = ""):
        super().__init__(f"Model unavailable: {model_id}. {reason}", 
                        {"model_id": model_id, "reason": reason})
        self.model_id = model_id
        self.reason = reason


class ModelConfigurationError(ModelRegistryException):
    """Raised when model configuration is invalid."""

    def __init__(self, model_id: str, message: str):
        super().__init__(f"Configuration error for {model_id}: {message}",
                        {"model_id": model_id, "message": message})
        self.model_id = model_id


class ModelCapabilityError(ModelRegistryException):
    """Raised when model lacks required capability."""

    def __init__(self, model_id: str, capability: str):
        super().__init__(f"Model {model_id} lacks capability: {capability}",
                        {"model_id": model_id, "capability": capability})
        self.model_id = model_id
        self.capability = capability


class ProviderNotFoundError(ModelRegistryException):
    """Raised when provider is not found."""

    def __init__(self, provider_id: str):
        super().__init__(f"Provider not found: {provider_id}", {"provider_id": provider_id})
        self.provider_id = provider_id


class ModelSelectionError(ModelRegistryException):
    """Raised when model selection fails."""

    def __init__(self, message: str, policy: str = ""):
        super().__init__(f"Model selection error ({policy}): {message}",
                        {"policy": policy, "message": message})
        self.policy = policy


class ModelDiscoveryError(ModelRegistryException):
    """Raised when model discovery fails."""

    def __init__(self, source: str, message: str):
        super().__init__(f"Discovery error from {source}: {message}",
                        {"source": source, "message": message})
        self.source = source
