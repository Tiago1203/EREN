"""Embedding manager for EREN Embedding Provider Layer.

Main interface for embedding operations.
"""

from __future__ import annotations

import threading
import time
import uuid
from typing import TYPE_CHECKING

from core.PHASE_2.embeddings.exceptions import (
    GenerationError,
)
from core.PHASE_2.embeddings.registry import EmbeddingRegistry, get_embedding_registry
from core.PHASE_2.embeddings.selector import EmbeddingSelector
from core.PHASE_2.embeddings.types import (
    Embedding,
    EmbeddingMetrics,
    EmbeddingModelInfo,
    EmbeddingPolicy,
    EmbeddingProvider,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingTrace,
)

if TYPE_CHECKING:
    pass


class EmbeddingManager:
    """Manager for embedding operations.

    This is the main interface for generating embeddings.

    The manager NEVER knows:
    - OpenAI API details
    - Ollama connection details
    - Any provider-specific implementation

    It only knows the provider interface.
    """

    def __init__(
        self,
        registry: EmbeddingRegistry | None = None,
        selector: EmbeddingSelector | None = None,
    ):
        """Initialize embedding manager.

        Args:
            registry: Embedding registry.
            selector: Embedding selector.
        """
        self._registry = registry or get_embedding_registry()
        self._selector = selector or EmbeddingSelector(self._registry)
        self._lock = threading.RLock()
        self._metrics = EmbeddingMetrics()
        self._traces: dict[str, EmbeddingTrace] = {}

    @property
    def registry(self) -> EmbeddingRegistry:
        """Get embedding registry."""
        return self._registry

    @property
    def selector(self) -> EmbeddingSelector:
        """Get embedding selector."""
        return self._selector

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
        provider: EmbeddingProvider | None = None,
        policy: EmbeddingPolicy = EmbeddingPolicy.DEFAULT,
    ) -> EmbeddingResponse:
        """Generate embeddings.

        Args:
            texts: Texts to embed.
            model: Model to use.
            provider: Specific provider to use.
            policy: Selection policy.

        Returns:
            Embedding response.

        Raises:
            EmbeddingError: If generation fails.
        """
        # Create request
        request = EmbeddingRequest(
            texts=texts,
            model=model,
            provider=provider,
        )

        # Create trace
        trace = EmbeddingTrace(
            trace_id=str(uuid.uuid4()),
            request=request,
        )
        self._traces[trace.trace_id] = trace

        start_time = time.time()

        try:
            # Select provider
            trace.add_step({"action": "select_provider", "start": time.time()})

            if provider:
                selected_provider = self._registry.get(provider)
            else:
                selected_provider = self._selector.select(model, policy)

            trace.add_step({
                "action": "provider_selected",
                "provider": selected_provider.provider_name.value,
            })

            # Generate embeddings
            trace.add_step({"action": "generate_embeddings", "start": time.time()})

            response = await selected_provider.generate(
                texts=texts,
                model=model,
                normalize=True,
            )

            trace.add_step({
                "action": "embeddings_generated",
                "count": len(response.embeddings),
            })

            # Update trace
            trace.finish(
                provider=selected_provider.provider_name,
                model=response.model,
            )

            # Record metrics
            self._record_metrics(response, selected_provider.provider_name)

            return response

        except Exception as e:
            trace.add_error(str(e))
            trace.finish()

            return EmbeddingResponse(
                embeddings=[],
                model=model or "",
                provider=provider or EmbeddingProvider.CUSTOM,
                latency_ms=int((time.time() - start_time) * 1000),
                success=False,
                error=str(e),
            )

    async def embed_single(
        self,
        text: str,
        model: str | None = None,
        provider: EmbeddingProvider | None = None,
        policy: EmbeddingPolicy = EmbeddingPolicy.DEFAULT,
    ) -> Embedding:
        """Generate a single embedding.

        Args:
            text: Text to embed.
            model: Model to use.
            provider: Specific provider to use.
            policy: Selection policy.

        Returns:
            Single embedding.

        Raises:
            EmbeddingError: If generation fails.
        """
        response = await self.embed(
            texts=[text],
            model=model,
            provider=provider,
            policy=policy,
        )

        if not response.success or not response.embeddings:
            raise GenerationError(response.error or "No embeddings generated")

        return response.embeddings[0]

    async def embed_batch(
        self,
        batches: list[list[str]],
        model: str | None = None,
        provider: EmbeddingProvider | None = None,
    ) -> list[EmbeddingResponse]:
        """Generate embeddings for multiple batches.

        Args:
            batches: List of text batches.
            model: Model to use.
            provider: Specific provider to use.

        Returns:
            List of embedding responses.
        """
        import asyncio

        tasks = [
            self.embed(texts, model=model, provider=provider)
            for texts in batches
        ]

        return await asyncio.gather(*tasks)

    async def health_check(
        self,
        provider: EmbeddingProvider | None = None,
    ) -> list[dict]:
        """Check health of providers.

        Args:
            provider: Specific provider (checks all if None).

        Returns:
            List of health statuses.
        """
        import asyncio

        if provider:
            p = self._registry.get(provider)
            health = await p.health_check()
            return [health.to_dict()]

        # Check all providers
        providers = self._registry.list_providers()
        tasks = [self._registry.get(p).health_check() for p in providers]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            r.to_dict() if not isinstance(r, Exception) else {"error": str(r)}
            for r in results
        ]

    def get_model_info(
        self,
        model: str | None = None,
        provider: EmbeddingProvider | None = None,
    ) -> EmbeddingModelInfo:
        """Get information about a model.

        Args:
            model: Model name.
            provider: Provider name.

        Returns:
            Model information.
        """
        if provider:
            p = self._registry.get(provider)
            return p.get_model_info(model)

        # Use default provider
        return self._registry.get_default().get_model_info(model)

    def list_models(
        self,
        provider: EmbeddingProvider | None = None,
    ) -> list[EmbeddingModelInfo]:
        """List available models.

        Args:
            provider: Filter by provider.

        Returns:
            List of model information.
        """
        if provider:
            p = self._registry.get(provider)
            return [p.get_model_info(model) for model in p.supported_models]

        # List from all providers
        models = []
        for p_name in self._registry.list_providers():
            p = self._registry.get(p_name)
            for model in p.supported_models:
                models.append(p.get_model_info(model))

        return models

    def estimate_cost(
        self,
        texts: list[str],
        model: str | None = None,
        provider: EmbeddingProvider | None = None,
    ) -> float:
        """Estimate cost for embedding generation.

        Args:
            texts: Texts to embed.
            model: Model name.
            provider: Provider name.

        Returns:
            Estimated cost in USD.
        """
        if provider:
            p = self._registry.get(provider)
            return p.estimate_cost(texts, model)

        return self._registry.get_default().estimate_cost(texts, model)

    def _record_metrics(
        self,
        response: EmbeddingResponse,
        provider: EmbeddingProvider,
    ) -> None:
        """Record metrics.

        Args:
            response: Embedding response.
            provider: Provider used.
        """
        with self._lock:
            self._metrics.total_requests += 1

            if response.success:
                self._metrics.successful_requests += 1
                self._metrics.total_tokens += response.tokens_used
                self._metrics.total_cost_usd += response.cost_usd
            else:
                self._metrics.failed_requests += 1

            # Track providers
            p_key = provider.value
            self._metrics.providers_used[p_key] = (
                self._metrics.providers_used.get(p_key, 0) + 1
            )

            # Track models
            m_key = response.model
            self._metrics.models_used[m_key] = (
                self._metrics.models_used.get(m_key, 0) + 1
            )

    def get_metrics(self) -> dict:
        """Get metrics.

        Returns:
            Metrics dictionary.
        """
        with self._lock:
            return self._metrics.to_dict()

    def get_trace(self, trace_id: str) -> dict | None:
        """Get a trace by ID.

        Args:
            trace_id: Trace ID.

        Returns:
            Trace dictionary or None.
        """
        trace = self._traces.get(trace_id)
        return trace.to_dict() if trace else None

    def list_traces(self, limit: int = 10) -> list[dict]:
        """List recent traces.

        Args:
            limit: Maximum traces to return.

        Returns:
            List of trace dictionaries.
        """
        traces = sorted(
            self._traces.values(),
            key=lambda t: t.start_time,
            reverse=True,
        )
        return [t.to_dict() for t in traces[:limit]]

    def get_status(self) -> dict:
        """Get manager status.

        Returns:
            Status dictionary.
        """
        return {
            "registry": self._registry.get_status(),
            "selector_policy": self._selector.policy.value,
            "metrics": self.get_metrics(),
        }


# Global manager instance
_global_manager: EmbeddingManager | None = None
_manager_lock = threading.Lock()


def get_embedding_manager() -> EmbeddingManager:
    """Get the global embedding manager.

    Returns:
        Global EmbeddingManager instance.
    """
    global _global_manager
    with _manager_lock:
        if _global_manager is None:
            _global_manager = EmbeddingManager()
        return _global_manager


def reset_embedding_manager() -> None:
    """Reset the global manager."""
    global _global_manager
    with _manager_lock:
        _global_manager = None
