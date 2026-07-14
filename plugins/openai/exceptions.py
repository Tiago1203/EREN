"""OpenAI Plugin exceptions for EREN OS.

Defines all exceptions that can be raised during OpenAI plugin operations.
"""

from __future__ import annotations


class OpenAIPluginException(Exception):
    """Base exception for OpenAI plugin errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class OpenAIConfigurationError(OpenAIPluginException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class OpenAIAuthenticationError(OpenAIPluginException):
    """Raised when API key is invalid."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message)


class OpenAIClientError(OpenAIPluginException):
    """Raised when client operation fails."""

    def __init__(self, message: str, status_code: int | None = None):
        details = {"status_code": status_code} if status_code else {}
        super().__init__(message, details)
        self.status_code = status_code


class OpenAIRequestError(OpenAIPluginException):
    """Raised when API request fails."""

    def __init__(self, message: str, error_code: str = ""):
        details = {"error_code": error_code} if error_code else {}
        super().__init__(message, details)
        self.error_code = error_code


class OpenAITimeoutError(OpenAIPluginException):
    """Raised when request times out."""

    def __init__(self, timeout: int):
        super().__init__(f"Request timed out after {timeout} seconds", {"timeout": timeout})
        self.timeout = timeout


class OpenAIValidationError(OpenAIPluginException):
    """Raised when request validation fails."""

    def __init__(self, message: str, field: str = ""):
        details = {"field": field} if field else {}
        super().__init__(message, details)
        self.field = field


class OpenAIModelError(OpenAIPluginException):
    """Raised when model is invalid or unavailable."""

    def __init__(self, message: str, model: str = ""):
        details = {"model": model} if model else {}
        super().__init__(message, details)
        self.model = model


class OpenAIRateLimitError(OpenAIPluginException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 0):
        super().__init__(message, {"retry_after": retry_after})
        self.retry_after = retry_after
