"""Contract for LLM providers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable, Any
from enum import Enum

from core.contracts.base import CognitiveEngine


class ProviderType(str, Enum):
    """Types of LLM providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    AZURE = "azure"
    VERTEX = "vertex"
    LOCAL = "local"


class ProviderHealth(str, Enum):
    """Health status of a provider."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNAVAILABLE = "unavailable"


@runtime_checkable
class GenerationRequest:
    """Request for text generation."""
    
    prompt: str
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1000


@runtime_checkable
class GenerationResponse:
    """Response from text generation."""
    
    content: str
    model: str
    provider: ProviderType
    tokens_used: int
    finish_reason: str | None = None


@runtime_checkable
class EmbeddingRequest:
    """Request for embeddings."""
    
    texts: list[str]
    model: str | None = None


@runtime_checkable
class EmbeddingResponse:
    """Response from embeddings."""
    
    embeddings: list[list[float]]
    model: str
    provider: ProviderType


@runtime_checkable
class ProviderContract(Protocol):
    """Contract for LLM providers.

    Providers are external services that provide LLM capabilities.
    All providers must implement this contract.
    """

    @property
    def provider_type(self) -> ProviderType:
        """Type of the provider."""
        ...

    @property
    def name(self) -> str:
        """Name of the provider."""
        ...

    @property
    def available_models(self) -> list[str]:
        """List of available models."""
        ...

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text from prompt."""
        ...

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings for texts."""
        ...

    async def health_check(self) -> ProviderHealth:
        """Check provider health."""
        ...
