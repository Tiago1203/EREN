"""Embedding configuration for EREN Embedding Provider Layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class EmbeddingConfiguration:
    """Configuration for embedding operations."""

    default_provider: str = "openai"
    default_model: str = "text-embedding-3-small"
    default_policy: str = "default"
    max_batch_size: int = 100
    timeout_seconds: int = 60
    retry_attempts: int = 3
    retry_delay_seconds: int = 1
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_caching: bool = False
    cache_ttl_seconds: int = 3600


@dataclass
class ProviderConfiguration:
    """Configuration for a specific provider."""

    provider: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    timeout: int = 60
    max_retries: int = 3
    custom_settings: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "api_key": "***" if self.api_key else "",
            "base_url": self.base_url,
            "model": self.model,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "custom_settings": self.custom_settings,
        }
