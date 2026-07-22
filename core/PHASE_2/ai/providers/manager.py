"""Provider Manager - Gestor de proveedores con fallback."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, AsyncIterator

from core.PHASE_2.ai.providers.models import (
    AIProvider,
    ChatCompletionResult,
    ChatMessage,
    CompletionResult,
    ModelInfo,
    ProviderConfig,
    ProviderType,
    StreamChunk,
    TokenUsage,
    UsageRecord,
)


@dataclass
class ProviderStats:
    """Estadísticas de uso de proveedor."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    # Rate limiting
    requests_this_minute: int = 0
    requests_this_hour: int = 0
    requests_this_day: int = 0
    last_request_time: datetime = field(default_factory=datetime.now)
    
    # Latencia
    avg_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0


class RateLimiter:
    """Rate limiter simple."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
    ) -> None:
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._rpd = requests_per_day
        
        self._minute_start = datetime.now()
        self._hour_start = datetime.now()
        self._day_start = datetime.now()
        
        self._minute_count = 0
        self._hour_count = 0
        self._day_count = 0
    
    def _reset_counters(self) -> None:
        """Resetea contadores si es necesario."""
        now = datetime.now()
        
        if now - self._minute_start >= timedelta(minutes=1):
            self._minute_count = 0
            self._minute_start = now
        
        if now - self._hour_start >= timedelta(hours=1):
            self._hour_count = 0
            self._hour_start = now
        
        if now - self._day_start >= timedelta(days=1):
            self._day_count = 0
            self._day_start = now
    
    async def acquire(self) -> bool:
        """Intenta adquirir permiso para hacer request."""
        self._reset_counters()
        
        if self._minute_count >= self._rpm:
            return False
        if self._hour_count >= self._rph:
            return False
        if self._day_count >= self._rpd:
            return False
        
        self._minute_count += 1
        self._hour_count += 1
        self._day_count += 1
        return True
    
    async def wait_if_needed(self) -> None:
        """Espera si se alcanzó el rate limit."""
        while not await self.acquire():
            await asyncio.sleep(1)


class ProviderManager:
    """
    Gestor de proveedores de IA.
    
    Maneja:
    - Fallback entre proveedores
    - Reintentos automáticos
    - Rate limiting
    - Tracking de uso y costos
    """

    def __init__(
        self,
        default_provider: ProviderType = ProviderType.OPENAI,
    ) -> None:
        self._providers: dict[ProviderType, AIProvider] = {}
        self._configs: dict[ProviderType, ProviderConfig] = {}
        self._stats: dict[ProviderType, ProviderStats] = defaultdict(ProviderStats)
        self._usage_records: list[UsageRecord] = []
        self._default_provider = default_provider
        self._rate_limiters: dict[ProviderType, RateLimiter] = {}

    def register_provider(
        self,
        provider: AIProvider,
        config: ProviderConfig,
    ) -> None:
        """Registra un proveedor."""
        self._providers[provider.provider_type] = provider
        self._configs[provider.provider_type] = config
        
        self._rate_limiters[provider.provider_type] = RateLimiter(
            requests_per_minute=config.requests_per_minute,
            requests_per_hour=config.requests_per_day,
            requests_per_day=config.requests_per_day,
        )
    
    def unregister_provider(self, provider_type: ProviderType) -> bool:
        """Elimina un proveedor."""
        if provider_type in self._providers:
            del self._providers[provider_type]
            del self._configs[provider_type]
            return True
        return False
    
    def get_provider(self, provider_type: ProviderType) -> AIProvider | None:
        """Obtiene un proveedor."""
        return self._providers.get(provider_type)
    
    def list_providers(self) -> list[ProviderType]:
        """Lista proveedores registrados."""
        return list(self._providers.keys())
    
    def get_stats(self, provider_type: ProviderType) -> ProviderStats | None:
        """Obtiene estadísticas de un proveedor."""
        return self._stats.get(provider_type)
    
    async def complete(
        self,
        prompt: str,
        provider_type: ProviderType | None = None,
        fallback_order: list[ProviderType] | None = None,
        **kwargs: Any,
    ) -> CompletionResult:
        """
        Completación con fallback automático.
        
        Args:
            prompt: Prompt de entrada
            provider_type: Proveedor específico (None = default)
            fallback_order: Orden de fallback si falla
            **kwargs: Parámetros adicionales
            
        Returns:
            Resultado de completación
        """
        if provider_type:
            return await self._try_provider(
                provider_type,
                lambda p: p.complete(prompt, **kwargs),
            )
        
        # Usar orden de fallback
        order = fallback_order or [self._default_provider]
        
        for pt in order:
            if pt not in self._providers:
                continue
            
            result = await self._try_provider(
                pt,
                lambda p: p.complete(prompt, **kwargs),
            )
            
            if result.success:
                return result
        
        # Todos fallaron
        return CompletionResult(
            content="",
            model="",
            error="Todos los proveedores fallaron",
        )
    
    async def chat_complete(
        self,
        messages: list[ChatMessage],
        provider_type: ProviderType | None = None,
        fallback_order: list[ProviderType] | None = None,
        **kwargs: Any,
    ) -> ChatCompletionResult:
        """
        Chat completion con fallback automático.
        """
        if provider_type:
            return await self._try_provider(
                provider_type,
                lambda p: p.chat_complete(messages, **kwargs),
            )
        
        order = fallback_order or [self._default_provider]
        
        for pt in order:
            if pt not in self._providers:
                continue
            
            result = await self._try_provider(
                pt,
                lambda p: p.chat_complete(messages, **kwargs),
            )
            
            if result.success:
                return result
        
        return ChatCompletionResult(
            message=ChatMessage(role="assistant", content=""),
            model="",
            error="Todos los proveedores fallaron",
        )
    
    async def _try_provider(
        self,
        provider_type: ProviderType,
        func: Any,
    ) -> Any:
        """Intenta ejecutar en un proveedor con retry."""
        provider = self._providers.get(provider_type)
        config = self._configs.get(provider_type)
        
        if not provider or not config:
            raise ValueError(f"Proveedor {provider_type} no registrado")
        
        limiter = self._rate_limiters.get(provider_type)
        max_retries = config.max_retries
        retry_delay = config.retry_delay_seconds
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Verificar rate limit
                if limiter:
                    await limiter.wait_if_needed()
                
                # Ejecutar
                result = await func(provider)
                
                # Actualizar estadísticas
                self._update_stats(provider_type, result, attempt == 0)
                
                return result
            
            except Exception as e:
                last_error = str(e)
                
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))
        
        # Crear resultado de error
        if hasattr(result, 'content'):
            result.error = last_error
            return result
        
        raise Exception(last_error)
    
    def _update_stats(
        self,
        provider_type: ProviderType,
        result: Any,
        first_attempt: bool,
    ) -> None:
        """Actualiza estadísticas."""
        stats = self._stats[provider_type]
        
        stats.total_requests += 1
        
        if result.success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
        
        if hasattr(result, 'usage'):
            usage = result.usage
            stats.total_tokens += usage.total_tokens
            
            # Calcular costo
            model_info = self._get_model_info(provider_type, result.model)
            if model_info:
                cost = (
                    usage.prompt_tokens * model_info.input_cost / 1000 +
                    usage.completion_tokens * model_info.output_cost / 1000
                )
                stats.total_cost += cost
                
                # Registrar uso
                self._usage_records.append(UsageRecord(
                    id=f"usage-{len(self._usage_records)}",
                    provider=provider_type,
                    model=result.model,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                    input_cost=usage.prompt_tokens * model_info.input_cost / 1000,
                    output_cost=usage.completion_tokens * model_info.output_cost / 1000,
                    total_cost=cost,
                    latency_ms=result.latency_ms,
                ))
        
        # Actualizar latencia
        if hasattr(result, 'latency_ms'):
            latency = result.latency_ms
            stats.avg_latency_ms = (
                (stats.avg_latency_ms * (stats.total_requests - 1) + latency) /
                stats.total_requests
            )
            stats.min_latency_ms = min(stats.min_latency_ms, latency)
            stats.max_latency_ms = max(stats.max_latency_ms, latency)
    
    def _get_model_info(
        self,
        provider_type: ProviderType,
        model_id: str,
    ) -> ModelInfo | None:
        """Obtiene información del modelo."""
        provider = self._providers.get(provider_type)
        if not provider:
            return None
        
        for model in provider.available_models:
            if model.id == model_id:
                return model
        
        return None
    
    def get_usage_records(
        self,
        provider_type: ProviderType | None = None,
        limit: int = 100,
    ) -> list[UsageRecord]:
        """Obtiene registros de uso."""
        records = self._usage_records
        
        if provider_type:
            records = [r for r in records if r.provider == provider_type]
        
        return records[-limit:]
    
    def get_total_cost(self, provider_type: ProviderType | None = None) -> float:
        """Obtiene costo total."""
        if provider_type:
            return self._stats[provider_type].total_cost
        
        return sum(s.total_cost for s in self._stats.values())
