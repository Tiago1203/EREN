"""Provider Models - Modelos de proveedores."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator


class ProviderType(str, Enum):
    """Tipos de proveedor."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"


class ModelCapability(str, Enum):
    """Capacidades del modelo."""
    TEXT_COMPLETION = "text_completion"
    CHAT_COMPLETION = "chat_completion"
    STREAMING = "streaming"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    EMBEDDINGS = "embeddings"


@dataclass
class ModelInfo:
    """Información de un modelo."""
    id: str
    name: str
    provider: ProviderType
    version: str = "1.0"
    
    # Capacidades
    capabilities: list[ModelCapability] = field(default_factory=list)
    
    # Límites
    max_tokens: int = 4096
    max_context_tokens: int = 8192
    
    # Costos (por 1K tokens)
    input_cost: float = 0.0
    output_cost: float = 0.0
    
    # Metadatos
    description: str = ""
    deprecated: bool = False


@dataclass
class TokenUsage:
    """Uso de tokens."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    @property
    def cost(self) -> float:
        return 0.0  # Calculado por provider


@dataclass
class ChatMessage:
    """Mensaje de chat."""
    role: str  # system, user, assistant
    content: str
    name: str | None = None
    tool_calls: list[ToolCall] | None = None


@dataclass
class ToolCall:
    """Llamada a herramienta."""
    id: str
    name: str
    arguments: str  # JSON string


@dataclass
class CompletionResult:
    """Resultado de completación."""
    content: str
    model: str
    finish_reason: str = "stop"
    usage: TokenUsage = field(default_factory=TokenUsage)
    
    # Metadata
    provider: ProviderType | None = None
    latency_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    # Error
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


@dataclass
class ChatCompletionResult:
    """Resultado de chat completion."""
    message: ChatMessage
    model: str
    finish_reason: str = "stop"
    usage: TokenUsage = field(default_factory=TokenUsage)
    
    # Metadata
    provider: ProviderType | None = None
    latency_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    # Error
    error: str | None = None
    
    @property
    def success(self) -> bool:
        return self.error is None


@dataclass
class StreamChunk:
    """Chunk de streaming."""
    content: str = ""
    delta: str = ""
    is_final: bool = False
    
    # Metadata
    model: str | None = None
    provider: ProviderType | None = None
    
    # Usage (en el último chunk)
    usage: TokenUsage | None = None


@dataclass
class ProviderConfig:
    """Configuración de proveedor."""
    provider_type: ProviderType
    api_key: str | None = None
    api_base: str | None = None  # URL base de API
    api_version: str | None = None
    
    # Modelo
    model: str = "gpt-4"
    max_tokens: int = 4096
    
    # Parámetros de generación
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_day: int = 10000
    
    # Retry
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    
    # Timeout
    timeout_seconds: int = 60
    
    # Seguridad
    allowed_models: list[str] | None = None
    blocked_models: list[str] | None = None


@dataclass
class UsageRecord:
    """Registro de uso."""
    id: str
    provider: ProviderType
    model: str
    user_id: str | None = None
    tenant_id: str | None = None
    
    # Tokens
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Costos
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0
    
    # Tiempos
    created_at: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0
    
    # Metadatos
    conversation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    """Interfaz abstracta de proveedor de IA."""
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Tipo de proveedor."""
        ...
    
    @property
    @abstractmethod
    def available_models(self) -> list[ModelInfo]:
        """Modelos disponibles."""
        ...
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        config: ProviderConfig | None = None,
    ) -> CompletionResult:
        """Completación de texto."""
        ...
    
    @abstractmethod
    async def chat_complete(
        self,
        messages: list[ChatMessage],
        config: ProviderConfig | None = None,
    ) -> ChatCompletionResult:
        """Completación de chat."""
        ...
    
    @abstractmethod
    async def stream_complete(
        self,
        prompt: str,
        config: ProviderConfig | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Completación con streaming."""
        ...
    
    @abstractmethod
    async def stream_chat_complete(
        self,
        messages: list[ChatMessage],
        config: ProviderConfig | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Chat completion con streaming."""
        ...
    
    @abstractmethod
    async def validate_config(self, config: ProviderConfig) -> tuple[bool, str]:
        """Valida la configuración."""
        ...
