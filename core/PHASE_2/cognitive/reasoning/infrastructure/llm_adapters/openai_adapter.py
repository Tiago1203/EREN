"""OpenAI LLM Adapter."""
import json
from typing import Any

from core.PHASE_2.cognitive.reasoning.domain.contracts import LLMResponse, EmbeddingResult
from core.PHASE_2.cognitive.reasoning.infrastructure.llm_adapters.base import BaseLLMAdapter, LLMConfig


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI GPT-4o adapter."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        """Generate a text completion using OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stop=stop_sequences,
        )
        
        choice = response.choices[0]
        usage = response.usage
        
        return LLMResponse(
            content=choice.message.content or "",
            finish_reason=choice.finish_reason or "stop",
            tokens_used=usage.total_tokens if usage else 0,
            reasoning_content=None,
        )
    
    async def complete_json(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> LLMResponse:
        """Generate a structured JSON response."""
        messages = []
        
        system_content = system_prompt or ""
        system_content += "\n\nRespond ONLY with valid JSON matching this schema:"
        system_content += f"\n{json.dumps(schema, indent=2)}"
        messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": prompt})
        
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        
        choice = response.choices[0]
        usage = response.usage
        
        return LLMResponse(
            content=choice.message.content or "",
            finish_reason=choice.finish_reason or "stop",
            tokens_used=usage.total_tokens if usage else 0,
            reasoning_content=None,
        )
    
    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResult:
        """Generate embeddings using OpenAI."""
        embedding_model = model or "text-embedding-3-small"
        
        response = await self._client.embeddings.create(
            model=embedding_model,
            input=texts,
        )
        
        embeddings = [item.embedding for item in response.data]
        usage = response.usage
        
        return EmbeddingResult(
            embeddings=embeddings,
            model=embedding_model,
            tokens_used=usage.total_tokens if usage else 0,
        )
    
    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.close()


# Factory function
def create_openai_adapter(
    api_key: str,
    model: str = "gpt-4o",
    base_url: str | None = None,
    **kwargs,
) -> OpenAIAdapter:
    """Create an OpenAI adapter."""
    config = LLMConfig(
        model=model,
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )
    return OpenAIAdapter(config)
