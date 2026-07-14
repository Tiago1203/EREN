"""OpenAI Plugin configuration for EREN OS.

Handles configuration loading and validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from plugins.openai.models import OpenAIModel, get_model_config
from plugins.openai.exceptions import OpenAIConfigurationError

if TYPE_CHECKING:
    pass


@dataclass
class OpenAIConfiguration:
    """Configuration for OpenAI plugin."""

    # Provider
    provider: str = "openai"

    # Model settings
    model: str = "gpt-5-mini"
    temperature: float = 0.2
    max_tokens: int = 4000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    # Request settings
    timeout: int = 60
    retries: int = 3
    retry_delay: float = 1.0
    stream: bool = False

    # API settings
    api_base: str = "https://api.openai.com/v1"
    organization: str = ""

    # Safety settings
    validate_api_key: bool = True
    max_request_size: int = 100000

    # Additional settings
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            OpenAIConfigurationError: If configuration is invalid.
        """
        # Validate model
        if not OpenAIModel.is_supported(self.model):
            raise OpenAIConfigurationError(
                f"Unsupported model: {self.model}. "
                f"Supported models: {[m.value for m in OpenAIModel]}"
            )

        # Validate temperature
        if not 0 <= self.temperature <= 2:
            raise OpenAIConfigurationError(
                f"Temperature must be between 0 and 2, got: {self.temperature}"
            )

        # Validate max_tokens
        model_config = get_model_config(self.model)
        if self.max_tokens > model_config.max_tokens:
            raise OpenAIConfigurationError(
                f"max_tokens ({self.max_tokens}) exceeds model limit ({model_config.max_tokens})"
            )

        # Validate timeout
        if self.timeout <= 0:
            raise OpenAIConfigurationError(f"timeout must be positive, got: {self.timeout}")

        # Validate retries
        if self.retries < 0:
            raise OpenAIConfigurationError(f"retries must be non-negative, got: {self.retries}")

    @classmethod
    def from_dict(cls, data: dict) -> "OpenAIConfiguration":
        """Create configuration from dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            OpenAIConfiguration instance.
        """
        known_fields = {
            "provider", "model", "temperature", "max_tokens", "top_p",
            "frequency_penalty", "presence_penalty", "timeout", "retries",
            "retry_delay", "stream", "api_base", "organization",
            "validate_api_key", "max_request_size",
        }

        config_data = {k: v for k, v in data.items() if k in known_fields}
        metadata = {k: v for k, v in data.items() if k not in known_fields}

        config = cls(**config_data)
        config.metadata = metadata

        return config

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Configuration dictionary.
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "retries": self.retries,
            "retry_delay": self.retry_delay,
            "stream": self.stream,
            "api_base": self.api_base,
            "organization": self.organization,
            "validate_api_key": self.validate_api_key,
            "max_request_size": self.max_request_size,
            **self.metadata,
        }


def load_configuration(config: dict | None = None) -> OpenAIConfiguration:
    """Load configuration from dictionary.

    Args:
        config: Configuration dictionary. Uses defaults if None.

    Returns:
        OpenAIConfiguration instance.
    """
    if config is None:
        return OpenAIConfiguration()

    return OpenAIConfiguration.from_dict(config)


def validate_api_key(api_key: str | None) -> bool:
    """Validate API key format.

    Args:
        api_key: API key to validate.

    Returns:
        True if valid format.

    Raises:
        ValueError: If API key is None or empty.
    """
    if not api_key:
        raise ValueError("API key is required")

    if not api_key.startswith("sk-"):
        raise ValueError("API key must start with 'sk-'")

    if len(api_key) < 40:
        raise ValueError("API key appears to be too short")

    return True
