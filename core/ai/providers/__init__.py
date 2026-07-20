"""AI Providers - Abstracción de proveedores de IA.

Este módulo proporciona una capa de abstracción para múltiples proveedores de IA,
incluyendo OpenAI, Anthropic, Google Gemini, Ollama y Azure OpenAI.

Características:
- Fallback automático entre proveedores
- Rate limiting
- Retry con backoff
- Tracking de uso y costos
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from core.ai.contracts import AIProvider, ProviderRegistry
from core.ai.dto import (
    AIRequest,
    AIResponse,
    HealthReport,
    ModelInfo,
    ProviderInfo,
    StreamChunk,
    ToolDefinition,
    UsageInfo,
)
from core.ai.exceptions import (
    AIInitializationError,
    AIProviderError,
    AIProviderNotFoundError,
)

# Importar componentes del provider manager
from core.ai.providers.models import (
    ProviderType,
    ModelCapability,
    ModelInfo as ProviderModelInfo,
    TokenUsage,
    ChatMessage,
    ToolCall,
    CompletionResult,
    ChatCompletionResult,
    StreamChunk as ProviderStreamChunk,
    ProviderConfig,
    UsageRecord,
    ProviderStats,
    AIProvider as BaseAIProvider,
)
from core.ai.providers.manager import ProviderManager, RateLimiter
from core.ai.providers.openai_provider import OpenAIProvider
from core.ai.providers.anthropic_provider import AnthropicProvider


class BaseProvider(AIProvider):
    """
    Clase base para proveedores de IA.
    
    Provee funcionalidad común que todos los proveedores pueden heredar.
    """

    def __init__(self, provider_id: str) -> None:
        self._provider_id = provider_id
        self._initialized = False
        self._config: dict[str, Any] = {}

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            id=self._provider_id,
            name=self._provider_id,
            base_url="",
            api_version="",
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa el proveedor con la configuración."""
        self._config = config
        self._initialized = True

    async def shutdown(self) -> None:
        """Apaga el proveedor limpiamente."""
        self._initialized = False

    async def generate(self, request: AIRequest) -> AIResponse:
        """Genera una respuesta."""
        raise NotImplementedError

    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """Genera una respuesta en streaming."""
        raise NotImplementedError

    async def list_models(self) -> list[ModelInfo]:
        """Lista los modelos disponibles."""
        return []

    async def get_model(self, model_id: str) -> ModelInfo | None:
        """Obtiene información de un modelo específico."""
        models = await self.list_models()
        for model in models:
            if model.id == model_id:
                return model
        return None

    async def health_check(self) -> HealthReport:
        """Verifica la salud del proveedor."""
        return HealthReport(
            overall_status="healthy" if self._initialized else "unhealthy",
            components=[],
        )

    def _validate_initialized(self) -> None:
        """Valida que el proveedor esté inicializado."""
        if not self._initialized:
            raise AIInitializationError(
                f"Provider {self._provider_id} not initialized"
            )


class ProviderFactory:
    """
    Factory para crear instancias de proveedores.
    """

    def __init__(self) -> None:
        self._registry = ProviderRegistry()

    def register(self, provider_id: str, provider_class: type) -> None:
        """Registra una clase de proveedor."""
        self._registry.register_provider(provider_id, provider_class)

    async def create(
        self,
        provider_id: str,
        config: dict[str, Any],
    ) -> AIProvider:
        """Crea una instancia de un proveedor."""
        provider_class = self._registry.get_provider_class(provider_id)

        if provider_class is None:
            raise AIProviderNotFoundError(provider_id)

        try:
            provider = provider_class(provider_id)
            await provider.initialize(config)
            return provider
        except Exception as e:
            raise AIProviderError(
                f"Failed to create provider {provider_id}: {e}",
                provider=provider_id,
            )


# ============== OpenAI Provider (Template) ==============

class OpenAIProvider(BaseProvider):
    """
    Proveedor para OpenAI.
    
    Este es un template que debe ser completado con la implementación real.
    """

    def __init__(self) -> None:
        super().__init__("openai")

    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            id="openai",
            name="OpenAI",
            base_url="https://api.openai.com",
            api_version="v1",
            supported_models=[
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-3.5-turbo",
            ],
            capabilities=["chat", "functions", "vision", "streaming"],
            rate_limit=500,
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa el proveedor OpenAI."""
        await super().initialize(config)
        # TODO: Initialize OpenAI client with config

    async def generate(self, request: AIRequest) -> AIResponse:
        """Genera una respuesta usando OpenAI."""
        self._validate_initialized()

        # TODO: Implement actual OpenAI API call
        # placeholder response
        return AIResponse(
            content="OpenAI response placeholder",
            model=request.model,
            finish_reason="stop",
            usage=UsageInfo(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )

    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """Genera una respuesta en streaming."""
        self._validate_initialized()

        # TODO: Implement actual OpenAI streaming
        yield StreamChunk(content="", delta="", index=0)


# ============== Anthropic Provider (Template) ==============

class AnthropicProvider(BaseProvider):
    """
    Proveedor para Anthropic (Claude).
    """

    def __init__(self) -> None:
        super().__init__("anthropic")

    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            id="anthropic",
            name="Anthropic",
            base_url="https://api.anthropic.com",
            api_version="v1",
            supported_models=[
                "claude-3-opus",
                "claude-3-sonnet",
                "claude-3-haiku",
                "claude-3-5-sonnet",
            ],
            capabilities=["chat", "functions", "vision", "streaming"],
            rate_limit=100,
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa el proveedor Anthropic."""
        await super().initialize(config)

    async def generate(self, request: AIRequest) -> AIResponse:
        """Genera una respuesta usando Anthropic."""
        self._validate_initialized()

        return AIResponse(
            content="Anthropic response placeholder",
            model=request.model,
            finish_reason="stop",
            usage=UsageInfo(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )

    async def stream(self, request: AIRequest) -> AsyncIterator[StreamChunk]:
        """Genera una respuesta en streaming."""
        self._validate_initialized()

        yield StreamChunk(content="", delta="", index=0)


# ============== Azure OpenAI Provider (Template) ==============

class AzureOpenAIProvider(BaseProvider):
    """
    Proveedor para Azure OpenAI.
    """

    def __init__(self) -> None:
        super().__init__("azure-openai")

    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            id="azure-openai",
            name="Azure OpenAI",
            base_url="",
            api_version="2024-02-01",
            supported_models=[
                "gpt-4",
                "gpt-4-turbo",
                "gpt-35-turbo",
            ],
            capabilities=["chat", "functions", "vision", "streaming"],
        )

    async def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa el proveedor Azure OpenAI."""
        await super().initialize(config)

    async def generate(self, request: AIRequest) -> AIResponse:
        """Genera una respuesta usando Azure OpenAI."""
        self._validate_initialized()

        return AIResponse(
            content="Azure OpenAI response placeholder",
            model=request.model,
            finish_reason="stop",
            usage=UsageInfo(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )


# ============== Provider Router ==============

class ProviderRouter:
    """
    Enrutador de requests a proveedores.
    
    Selecciona el proveedor apropiado basado en el modelo o configuración.
    """

    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}
        self._model_to_provider: dict[str, str] = {}
        self._default_provider: str = "openai"

    def register_provider(self, provider: AIProvider) -> None:
        """Registra un proveedor."""
        self._providers[provider.provider_id] = provider

        # Map models to provider
        for model in provider.provider_info.supported_models:
            self._model_to_provider[model] = provider.provider_id

    def unregister_provider(self, provider_id: str) -> bool:
        """Elimina un proveedor registrado."""
        if provider_id in self._providers:
            del self._providers[provider_id]
            # Remove model mappings
            to_remove = [
                m for m, p in self._model_to_provider.items()
                if p == provider_id
            ]
            for m in to_remove:
                del self._model_to_provider[m]
            return True
        return False

    def get_provider_for_model(self, model: str) -> AIProvider:
        """Obtiene el proveedor apropiado para un modelo."""
        provider_id = self._model_to_provider.get(model, self._default_provider)

        if provider_id not in self._providers:
            raise AIProviderNotFoundError(provider_id)

        return self._providers[provider_id]

    def set_default_provider(self, provider_id: str) -> None:
        """Establece el proveedor por defecto."""
        if provider_id not in self._providers:
            raise AIProviderNotFoundError(provider_id)
        self._default_provider = provider_id

    def list_providers(self) -> list[str]:
        """Lista todos los proveedores registrados."""
        return list(self._providers.keys())
