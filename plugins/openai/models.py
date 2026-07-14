"""OpenAI models for EREN OS OpenAI Plugin.

Defines supported models and their configurations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class OpenAIModel(str, Enum):
    """Supported OpenAI models."""

    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_O = "gpt-4o"
    GPT_4_O_MINI = "gpt-4o-mini"

    @classmethod
    def is_supported(cls, model: str) -> bool:
        """Check if model is supported."""
        return model in [m.value for m in cls]

    @classmethod
    def default(cls) -> "OpenAIModel":
        """Get default model."""
        return cls.GPT_5_MINI


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for a model."""

    name: str
    max_tokens: int = 16000
    supports_vision: bool = False
    supports_function_calling: bool = True
    context_window: int = 128000
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "max_tokens": self.max_tokens,
            "supports_vision": self.supports_vision,
            "supports_function_calling": self.supports_function_calling,
            "context_window": self.context_window,
        }


# Model configurations
MODEL_CONFIGS: dict[str, ModelConfig] = {
    "gpt-5": ModelConfig(
        name="gpt-5",
        max_tokens=16000,
        supports_vision=True,
        supports_function_calling=True,
        context_window=128000,
        cost_per_input_token=0.01,
        cost_per_output_token=0.03,
    ),
    "gpt-5-mini": ModelConfig(
        name="gpt-5-mini",
        max_tokens=8000,
        supports_vision=True,
        supports_function_calling=True,
        context_window=64000,
        cost_per_input_token=0.00015,
        cost_per_output_token=0.0006,
    ),
    "gpt-5-nano": ModelConfig(
        name="gpt-5-nano",
        max_tokens=4000,
        supports_vision=False,
        supports_function_calling=True,
        context_window=32000,
        cost_per_input_token=0.00003,
        cost_per_output_token=0.0001,
    ),
    "gpt-4": ModelConfig(
        name="gpt-4",
        max_tokens=8000,
        supports_vision=False,
        supports_function_calling=True,
        context_window=128000,
        cost_per_input_token=0.03,
        cost_per_output_token=0.06,
    ),
    "gpt-4-turbo": ModelConfig(
        name="gpt-4-turbo",
        max_tokens=16000,
        supports_vision=True,
        supports_function_calling=True,
        context_window=128000,
        cost_per_input_token=0.01,
        cost_per_output_token=0.03,
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        max_tokens=16000,
        supports_vision=True,
        supports_function_calling=True,
        context_window=128000,
        cost_per_input_token=0.005,
        cost_per_output_token=0.015,
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        max_tokens=8000,
        supports_vision=True,
        supports_function_calling=True,
        context_window=128000,
        cost_per_input_token=0.00015,
        cost_per_output_token=0.0006,
    ),
}


def get_model_config(model: str) -> ModelConfig:
    """Get configuration for a model.

    Args:
        model: Model name.

    Returns:
        Model configuration.

    Raises:
        ValueError: If model is not supported.
    """
    if model not in MODEL_CONFIGS:
        raise ValueError(f"Unsupported model: {model}")
    return MODEL_CONFIGS[model]


def get_default_max_tokens(model: str) -> int:
    """Get default max tokens for a model.

    Args:
        model: Model name.

    Returns:
        Default max tokens.
    """
    config = MODEL_CONFIGS.get(model)
    return config.max_tokens if config else 4000
