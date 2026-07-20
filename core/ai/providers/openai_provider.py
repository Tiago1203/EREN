"""OpenAI Provider - Proveedor de OpenAI."""

from __future__ import annotations

import time
from typing import Any, AsyncIterator

from core.ai.providers.models import (
    AIProvider,
    ChatCompletionResult,
    ChatMessage,
    CompletionResult,
    ModelCapability,
    ModelInfo,
    ProviderConfig,
    ProviderType,
    StreamChunk,
    TokenUsage,
)


class OpenAIProvider(AIProvider):
    """Proveedor de OpenAI (GPT)."""
    
    DEFAULT_MODELS = [
        ModelInfo(
            id="gpt-4",
            name="GPT-4",
            provider=ProviderType.OPENAI,
            capabilities=[
                ModelCapability.CHAT_COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.FUNCTION_CALLING,
            ],
            max_tokens=8192,
            max_context_tokens=128000,
            input_cost=0.03,
            output_cost=0.06,
        ),
        ModelInfo(
            id="gpt-4-turbo",
            name="GPT-4 Turbo",
            provider=ProviderType.OPENAI,
            capabilities=[
                ModelCapability.CHAT_COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.FUNCTION_CALLING,
            ],
            max_tokens=128000,
            max_context_tokens=128000,
            input_cost=0.01,
            output_cost=0.03,
        ),
        ModelInfo(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            provider=ProviderType.OPENAI,
            capabilities=[
                ModelCapability.CHAT_COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.FUNCTION_CALLING,
            ],
            max_tokens=16385,
            max_context_tokens=16385,
            input_cost=0.0005,
            output_cost=0.0015,
        ),
    ]
    
    def __init__(self, config: ProviderConfig | None = None) -> None:
        self._config = config or ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_base="https://api.openai.com/v1",
        )
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    @property
    def available_models(self) -> list[ModelInfo]:
        return self.DEFAULT_MODELS
    
    async def complete(
        self,
        prompt: str,
        config: ProviderConfig | None = None,
    ) -> CompletionResult:
        """Completación de texto."""
        cfg = config or self._config
        start = time.time()
        
        # Simular llamada (en producción usaría openai-python)
        try:
            # Aquí iría la implementación real
            content = f"Completado: {prompt[:50]}..."
            
            return CompletionResult(
                content=content,
                model=cfg.model,
                finish_reason="stop",
                usage=TokenUsage(
                    prompt_tokens=len(prompt) // 4,
                    completion_tokens=len(content) // 4,
                    total_tokens=(len(prompt) + len(content)) // 4,
                ),
                provider=self.provider_type,
                latency_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return CompletionResult(
                content="",
                model=cfg.model,
                error=str(e),
                provider=self.provider_type,
                latency_ms=(time.time() - start) * 1000,
            )
    
    async def chat_complete(
        self,
        messages: list[ChatMessage],
        config: ProviderConfig | None = None,
    ) -> ChatCompletionResult:
        """Completación de chat."""
        cfg = config or self._config
        start = time.time()
        
        try:
            # Simular respuesta
            content = "Respuesta simulada del modelo."
            
            return ChatCompletionResult(
                message=ChatMessage(
                    role="assistant",
                    content=content,
                ),
                model=cfg.model,
                finish_reason="stop",
                usage=TokenUsage(
                    prompt_tokens=100,
                    completion_tokens=20,
                    total_tokens=120,
                ),
                provider=self.provider_type,
                latency_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return ChatCompletionResult(
                message=ChatMessage(role="assistant", content=""),
                model=cfg.model,
                error=str(e),
                provider=self.provider_type,
                latency_ms=(time.time() - start) * 1000,
            )
    
    async def stream_complete(
        self,
        prompt: str,
        config: ProviderConfig | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Completación con streaming."""
        cfg = config or self._config
        
        # Simular streaming
        content = f"Completado: {prompt[:50]}..."
        for i, char in enumerate(content):
            yield StreamChunk(
                content=char,
                delta=char,
                is_final=i == len(content) - 1,
                model=cfg.model,
                provider=self.provider_type,
            )
            await _async_sleep(0.01)
    
    async def stream_chat_complete(
        self,
        messages: list[ChatMessage],
        config: ProviderConfig | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Chat completion con streaming."""
        cfg = config or self._config
        
        content = "Respuesta en streaming."
        for i, char in enumerate(content):
            yield StreamChunk(
                content=char,
                delta=char,
                is_final=i == len(content) - 1,
                model=cfg.model,
                provider=self.provider_type,
            )
            await _async_sleep(0.01)
    
    async def validate_config(self, config: ProviderConfig) -> tuple[bool, str]:
        """Valida la configuración."""
        if not config.api_key and not config.api_base:
            return False, "Se requiere API key o API base"
        
        if config.model not in [m.id for m in self.available_models]:
            return False, f"Modelo {config.model} no disponible"
        
        if config.temperature < 0 or config.temperature > 2:
            return False, "Temperature debe estar entre 0 y 2"
        
        return True, ""


async def _async_sleep(seconds: float) -> None:
    """Sleep async helper."""
    import asyncio
    await asyncio.sleep(seconds)
