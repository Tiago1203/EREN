"""Base LLM Adapter."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from core.PHASE_2.cognitive.reasoning.domain.contracts import LLMContract, LLMResponse, EmbeddingResult


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    model: str
    api_key: str
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60


class BaseLLMAdapter(ABC):
    """Base class for all LLM adapters."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client: Any = None
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        """Generate a text completion."""
        pass
    
    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Generate a structured JSON response."""
        pass
    
    @abstractmethod
    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResult:
        """Generate embeddings."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the client connection."""
        pass
