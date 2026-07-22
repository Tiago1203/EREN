"""Anthropic Claude Adapter."""
import json

from core.PHASE_2.cognitive.reasoning.domain.contracts import LLMResponse, EmbeddingResult
from core.PHASE_2.cognitive.reasoning.infrastructure.llm_adapters.base import BaseLLMAdapter, LLMConfig


class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic Claude 3.5 adapter."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the Anthropic client."""
        try:
            from anthropic import AsyncAnthropic
            self._client = AsyncAnthropic(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )
    
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        stop_sequences: list[str] | None = None,
    ) -> LLMResponse:
        """Generate a text completion using Anthropic."""
        response = await self._client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature or self.config.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            stop_sequences=stop_sequences,
        )
        
        content = response.content[0].text if response.content else ""
        
        return LLMResponse(
            content=content,
            finish_reason=str(response.stop_reason) if response.stop_reason else "stop",
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
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
        system_content = system_prompt or ""
        system_content += "\n\nYou must respond ONLY with valid JSON matching this schema:"
        system_content += f"\n{json.dumps(schema, indent=2)}"
        system_content += "\n\nDo not include any text outside the JSON object."
        
        response = await self._client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=temperature,
            system=system_content,
            messages=[{"role": "user", "content": prompt}],
        )
        
        content = response.content[0].text if response.content else ""
        
        return LLMResponse(
            content=content,
            finish_reason=str(response.stop_reason) if response.stop_reason else "stop",
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            reasoning_content=None,
        )
    
    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResult:
        """Generate embeddings using Anthropic."""
        # Anthropic doesn't have an embedding API
        # Use OpenAI or another provider for embeddings
        raise NotImplementedError(
            "Anthropic does not provide an embedding API. "
            "Use OpenAI embeddings or another provider."
        )
    
    async def close(self) -> None:
        """Close the client connection."""
        # Anthropic client doesn't need explicit close
        pass


def create_anthropic_adapter(
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022",
    base_url: str | None = None,
    **kwargs,
) -> AnthropicAdapter:
    """Create an Anthropic adapter."""
    config = LLMConfig(
        model=model,
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )
    return AnthropicAdapter(config)
