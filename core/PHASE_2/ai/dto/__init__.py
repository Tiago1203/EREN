"""AI DTOs - Data Transfer Objects del AI Core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


@dataclass
class Content:
    """Contenido de un mensaje."""
    type: ContentType
    text: str | None = None
    url: str | None = None
    data: str | None = None  # Base64 encoded data
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Un mensaje en una conversación."""
    role: MessageRole
    content: str | list[Content]
    name: str | None = None
    tool_call_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInfo:
    """Información sobre un modelo de IA."""
    id: str
    name: str
    provider: str
    max_tokens: int
    supports_functions: bool = False
    supports_vision: bool = False
    supports_streaming: bool = True
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderInfo:
    """Información sobre un proveedor de IA."""
    id: str
    name: str
    base_url: str
    api_version: str
    supported_models: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    rate_limit: int | None = None  # Requests per minute
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIRequest:
    """Request para el AI Core."""
    messages: list[Message]
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float | None = None
    stop: str | list[str] | None = None
    stream: bool = False
    functions: list[dict[str, Any]] | None = None
    function_call: str | dict[str, str] | None = None
    user: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """Response del AI Core."""
    content: str
    model: str
    role: MessageRole = MessageRole.ASSISTANT
    finish_reason: str | None = None
    usage: UsageInfo | None = None
    function_call: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageInfo:
    """Información de uso de tokens."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: dict[str, int] | None = None
    completion_tokens_details: dict[str, int] | None = None


@dataclass
class StreamChunk:
    """Chunk en streaming response."""
    content: str
    delta: str | None = None
    index: int = 0
    finish_reason: str | None = None
    model: str | None = None


@dataclass
class ToolDefinition:
    """Definición de una herramienta."""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema


@dataclass
class ToolCall:
    """Llamada a una herramienta."""
    id: str
    name: str
    arguments: str  # JSON string


@dataclass
class ToolResult:
    """Resultado de una llamada a herramienta."""
    tool_call_id: str
    content: str
    is_error: bool = False


@dataclass
class ModelCapabilities:
    """Capacidades de un modelo."""
    supports_functions: bool = False
    supports_vision: bool = False
    supports_streaming: bool = True
    supports_json_mode: bool = False
    supports_seed: bool = False
    supports_logprobs: bool = False
    max_context_tokens: int = 0
    max_output_tokens: int = 0


@dataclass
class ProviderConfig:
    """Configuración de un proveedor."""
    provider_id: str
    api_key: str | None = None
    base_url: str | None = None
    organization: str | None = None
    default_model: str | None = None
    timeout: int = 60  # seconds
    max_retries: int = 3
    headers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIConfig:
    """Configuración global del AI Core."""
    default_provider: str = "openai"
    default_model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int | None = None
    timeout: int = 60
    max_retries: int = 3
    providers: dict[str, ProviderConfig] = field(default_factory=dict)
    features: dict[str, bool] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextMetadata:
    """Metadatos de contexto."""
    user_id: str | None = None
    session_id: str | None = None
    conversation_id: str | None = None
    tenant_id: str | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIContext:
    """Contexto para una request de IA."""
    request_id: str
    messages: list[Message]
    model: str
    metadata: ContextMetadata = field(default_factory=ContextMetadata)
    system_prompt: str | None = None
    tools: list[ToolDefinition] | None = None
    max_tokens: int | None = None
    temperature: float = 0.7
    raw_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Estado de salud de un componente."""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthReport:
    """Reporte de salud del AI Core."""
    overall_status: str
    timestamp: datetime = field(default_factory=datetime.now)
    components: list[HealthStatus] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
