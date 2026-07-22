"""Provider exceptions for EREN OS Multi-Provider Layer.

Defines all exceptions that can be raised during provider operations.
"""

from __future__ import annotations


class ProviderException(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ProviderNotFoundError(ProviderException):
    """Raised when provider is not found."""

    def __init__(self, provider_id: str):
        super().__init__(f"Provider not found: {provider_id}", {"provider_id": provider_id})
        self.provider_id = provider_id


class ProviderNotRegisteredError(ProviderException):
    """Raised when provider is not registered."""

    def __init__(self, provider_id: str):
        super().__init__(f"Provider not registered: {provider_id}", {"provider_id": provider_id})
        self.provider_id = provider_id


class ProviderAlreadyRegisteredError(ProviderException):
    """Raised when provider is already registered."""

    def __init__(self, provider_id: str):
        super().__init__(f"Provider already registered: {provider_id}", {"provider_id": provider_id})
        self.provider_id = provider_id


class ProviderConfigurationError(ProviderException):
    """Raised when provider configuration is invalid."""

    def __init__(self, provider_id: str, message: str):
        super().__init__(f"Configuration error for {provider_id}: {message}",
                        {"provider_id": provider_id, "message": message})
        self.provider_id = provider_id


class ProviderInitializationError(ProviderException):
    """Raised when provider initialization fails."""

    def __init__(self, provider_id: str, message: str):
        super().__init__(f"Initialization error for {provider_id}: {message}",
                        {"provider_id": provider_id, "message": message})
        self.provider_id = provider_id


class ProviderConnectionError(ProviderException):
    """Raised when provider connection fails."""

    def __init__(self, provider_id: str, message: str = ""):
        super().__init__(f"Connection error for {provider_id}: {message}",
                        {"provider_id": provider_id, "message": message})
        self.provider_id = provider_id


class ProviderAuthenticationError(ProviderException):
    """Raised when provider authentication fails."""

    def __init__(self, provider_id: str, message: str = "Authentication failed"):
        super().__init__(f"Authentication error for {provider_id}: {message}",
                        {"provider_id": provider_id, "message": message})
        self.provider_id = provider_id


class ProviderRateLimitError(ProviderException):
    """Raised when provider rate limit is exceeded."""

    def __init__(self, provider_id: str, retry_after: int = 0):
        super().__init__(f"Rate limit exceeded for {provider_id}",
                        {"provider_id": provider_id, "retry_after": retry_after})
        self.provider_id = provider_id
        self.retry_after = retry_after


class ProviderTimeoutError(ProviderException):
    """Raised when provider request times out."""

    def __init__(self, provider_id: str, timeout: int):
        super().__init__(f"Request timeout for {provider_id} after {timeout}s",
                        {"provider_id": provider_id, "timeout": timeout})
        self.provider_id = provider_id
        self.timeout = timeout


class ProviderHealthCheckError(ProviderException):
    """Raised when provider health check fails."""

    def __init__(self, provider_id: str, message: str):
        super().__init__(f"Health check failed for {provider_id}: {message}",
                        {"provider_id": provider_id, "message": message})
        self.provider_id = provider_id


class ProviderUnavailableError(ProviderException):
    """Raised when no provider is available."""

    def __init__(self, message: str = "No provider available"):
        super().__init__(message)


class ProviderPolicyError(ProviderException):
    """Raised when provider policy cannot be satisfied."""

    def __init__(self, policy: str, message: str):
        super().__init__(f"Policy error ({policy}): {message}",
                        {"policy": policy, "message": message})
        self.policy = policy


class ProviderFallbackError(ProviderException):
    """Raised when all providers in fallback chain fail."""

    def __init__(self, providers: list[str]):
        super().__init__(f"All providers failed: {', '.join(providers)}",
                        {"providers": providers})
        self.providers = providers
