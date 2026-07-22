"""Reasoning domain contracts (ports)."""
from typing import Protocol, AsyncIterator
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """LLM response severity."""
    FULL = "full"
    TRUNCATED = "truncated"


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    finish_reason: str
    tokens_used: int
    reasoning_content: str | None = None


@dataclass
class EmbeddingResult:
    """Embedding result."""
    embeddings: list[list[float]]
    model: str
    tokens_used: int


class LLMContract(Protocol):
    """Contract for all LLM providers."""
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        """Generate a text completion."""
        ...
    
    async def complete_json(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Generate a structured JSON response."""
        ...
    
    async def embed(
        self,
        texts: list[str],
        model: str = "embedding-model",
    ) -> EmbeddingResult:
        """Generate embeddings for RAG."""
        ...
