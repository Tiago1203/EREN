"""Provider Factory for EREN OS Multi-Provider Layer.

Factory pattern for creating provider instances.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.PHASE_2.providers.providers.base import BaseLLMProvider
from core.PHASE_2.providers.providers.openai_provider import OpenAIProvider
from core.PHASE_2.providers.providers.ollama_provider import OllamaProvider
from core.PHASE_2.providers.providers.mock_provider import MockProvider
from core.PHASE_2.providers.types import ProviderConfig, ProviderType

if TYPE_CHECKING:
    pass


class ProviderFactory:
    """Factory for creating LLM provider instances.

    Supports:
    - Built-in providers
    - Custom provider registration
    - Configuration-based creation
    """

    _instance: ProviderFactory | None = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize factory."""
        self._builders: dict[str, Callable[[], BaseLLMProvider]] = {}
        self._configs: dict[str, ProviderConfig] = {}

        # Register built-in providers
        self._register_builtin_providers()

    @classmethod
    def get_instance(cls) -> ProviderFactory:
        """Get singleton instance.

        Returns:
            Factory instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _register_builtin_providers(self) -> None:
        """Register built-in provider builders."""
        self._builders["openai"] = lambda: OpenAIProvider()
        self._builders["anthropic"] = lambda: AnthropicProvider()
        self._builders["ollama"] = lambda: OllamaProvider()
        self._builders["gemini"] = lambda: GeminiProvider()
        self._builders["azure_openai"] = lambda: AzureOpenAIProvider()
        self._builders["deepseek"] = lambda: DeepSeekProvider()
        self._builders["mistral"] = lambda: MistralProvider()
        self._builders["openrouter"] = lambda: OpenRouterProvider()
        self._builders["mock"] = lambda: MockProvider()

    def register_builder(
        self,
        provider_type: str,
        builder: Callable[[], BaseLLMProvider],
    ) -> None:
        """Register a custom provider builder.

        Args:
            provider_type: Provider type identifier.
            builder: Function that creates provider instance.
        """
        with self._lock:
            self._builders[provider_type] = builder

    def unregister_builder(self, provider_type: str) -> bool:
        """Unregister a provider builder.

        Args:
            provider_type: Provider type identifier.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if provider_type in self._builders:
                del self._builders[provider_type]
                return True
            return False

    def create(self, provider_type: ProviderType | str) -> BaseLLMProvider | None:
        """Create a provider instance.

        Args:
            provider_type: Provider type.

        Returns:
            Provider instance or None.
        """
        type_str = provider_type.value if isinstance(provider_type, ProviderType) else provider_type

        with self._lock:
            builder = self._builders.get(type_str.lower())
            if builder:
                return builder()
            return None

    def create_with_config(self, config: ProviderConfig) -> BaseLLMProvider | None:
        """Create a provider with configuration.

        Args:
            config: Provider configuration.

        Returns:
            Configured provider instance or None.
        """
        provider = self.create(config.provider_type)
        if provider:
            provider._config = config
            self._configs[config.provider_id] = config
        return provider

    def get_registered_types(self) -> list[str]:
        """Get list of registered provider types.

        Returns:
            List of provider type identifiers.
        """
        with self._lock:
            return list(self._builders.keys())

    def has_builder(self, provider_type: str) -> bool:
        """Check if a builder is registered.

        Args:
            provider_type: Provider type identifier.

        Returns:
            True if builder exists.
        """
        with self._lock:
            return provider_type.lower() in self._builders


# =============================================================================
# Provider Type Aliases (placeholders)
# =============================================================================


def AnthropicProvider():
    """Create Anthropic provider (placeholder)."""
    from core.PHASE_2.providers.providers.anthropic_provider import AnthropicProvider as _Impl
    return _Impl()


def GeminiProvider():
    """Create Gemini provider (placeholder)."""
    from core.PHASE_2.providers.providers.gemini_provider import GeminiProvider as _Impl
    return _Impl()


def AzureOpenAIProvider():
    """Create Azure OpenAI provider (placeholder)."""
    from core.PHASE_2.providers.providers.azure_provider import AzureOpenAIProvider as _Impl
    return _Impl()


def DeepSeekProvider():
    """Create DeepSeek provider (placeholder)."""
    from core.PHASE_2.providers.providers.deepseek_provider import DeepSeekProvider as _Impl
    return _Impl()


def MistralProvider():
    """Create Mistral provider (placeholder)."""
    from core.PHASE_2.providers.providers.mistral_provider import MistralProvider as _Impl
    return _Impl()


def OpenRouterProvider():
    """Create OpenRouter provider (placeholder)."""
    from core.PHASE_2.providers.providers.openrouter_provider import OpenRouterProvider as _Impl
    return _Impl()
