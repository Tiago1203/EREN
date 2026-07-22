"""Anthropic Provider - Proveedor de Anthropic (Claude)."""

from __future__ import annotations

import time
from typing import Any, AsyncIterator

from core.PHASE_2.ai.providers.models import (
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


class AnthropicProvider(AIProvider):
    """Proveedor de Anthropic (Claude)."""
    
    DEFAULT_MODELS = [
        ModelInfo(
            id="claude-3-opus-20240229",
            name="Claude 3 Opus",
            provider=ProviderType.ANTHROPIC,
            capabilities=[
                ModelCapability.CHAT_COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.VISION,
            ],
            max_tokens=4096,
            max_context_tokens=200000,
            input_cost=0.015,
            output_cost=0.075,
        ),
        ModelInfo(
            id="claude-3-sonnet-20240229",
            name="Claude 3 Sonnet",
            provider=ProviderType.ANTHROPIC,
            capabilities=[
                ModelCapability.CHAT_COMPLETION,
                ModelCapability.STREAMING,
                ModelCapability.VISION,
            ],
            max_tokens=4096,
            max_context_tokens=200000,
            input_cost=0.003,
            output_cost=0.015,
        ),
        ModelInfo(
            id="claude-3-haiku-20240307",
            name="Claude 3 Haiku",
            provider=ProviderType.ANTHROPIC,
            capabilities=[
                ModelCapability.CHAT_COMPLETION,
                ModelCapability.STREAMING,
            ],
            max_tokens=4096,
            max_context_tokens=200000,
            input_cost=0.00025,
            output_cost=0.00125,
        ),
    ]
    
    def __init__(self, config: ProviderConfig | None = None) -> None:
        self._config = config or ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_base="https://api.anthropic.com/v1",
        )
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC
    
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
        
        try:
            content = f"Claude: {prompt[:50]}..."
            
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
            content = "Respuesta de Claude."
            
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
        
        content = f"Claude streaming: {prompt[:30]}..."
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
        
        content = "Claude en streaming."
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
        if not config.api_key:
            return False, "Se requiere API key de Anthropic"
        
        if config.model not in [m.id for m in self.available_models]:
            return False, f"Modelo {config.model} no disponible"
        
        if config.temperature < 0 or config.temperature > 1:
            return False, "Temperature debe estar entre 0 y 1"
        
        return True, ""


async def _async_sleep(seconds: float) -> None:
    import asyncio
    await asyncio.sleep(seconds)
