"""OpenAI Plugin for EREN OS.

This plugin provides OpenAI GPT reasoning capability for EREN.

Example:
    >>> from plugins.openai import OpenAICapability
    >>> from core.sdk import CapabilityContext, CapabilityResult
    >>> 
    >>> capability = OpenAICapability(api_key="sk-...")
    >>> context = CapabilityContext(prompt="Hello, how are you?")
    >>> 
    >>> capability.initialize(context)
    >>> result = capability.execute(context)
    >>> print(result.data)
"""

from __future__ import annotations

from plugins.openai.capability import OpenAICapability
from plugins.openai.plugin import OpenAIPlugin, create_openai_plugin
from plugins.openai.configuration import (
    OpenAIConfiguration,
    load_configuration,
    validate_api_key,
)
from plugins.openai.models import OpenAIModel, ModelConfig, MODEL_CONFIGS, get_model_config
from plugins.openai.provider import OpenAIClient, OpenAIClientConfig
from plugins.openai.exceptions import (
    OpenAIPluginException,
    OpenAIConfigurationError,
    OpenAIAuthenticationError,
    OpenAIClientError,
    OpenAIRequestError,
    OpenAITimeoutError,
    OpenAIValidationError,
    OpenAIModelError,
    OpenAIRateLimitError,
)

__all__ = [
    # Core
    "OpenAICapability",
    "OpenAIPlugin",
    "create_openai_plugin",
    # Configuration
    "OpenAIConfiguration",
    "load_configuration",
    "validate_api_key",
    # Models
    "OpenAIModel",
    "ModelConfig",
    "MODEL_CONFIGS",
    "get_model_config",
    # Provider
    "OpenAIClient",
    "OpenAIClientConfig",
    # Exceptions
    "OpenAIPluginException",
    "OpenAIConfigurationError",
    "OpenAIAuthenticationError",
    "OpenAIClientError",
    "OpenAIRequestError",
    "OpenAITimeoutError",
    "OpenAIValidationError",
    "OpenAIModelError",
    "OpenAIRateLimitError",
]
