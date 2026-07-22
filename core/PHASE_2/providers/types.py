"""Provider types and enums for EREN OS Multi-Provider Layer.

Defines all types, enums, and value objects used by the provider system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Provider Types
# =============================================================================


class ProviderType(str, Enum):
    """Types of LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"  # Claude
    OLLAMA = "ollama"
    GEMINI = "gemini"
    AZURE_OPENAI = "azure_openai"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    OPENROUTER = "openrouter"
    VERTEX = "vertex"  # Google Vertex AI
    CUSTOM = "custom"
    MOCK = "mock"  # For testing

    # Aliases for backward compatibility
    CLAUDE = ANTHROPIC

    @classmethod
    def is_local(cls, provider_type: ProviderType) -> bool:
        """Check if provider is local (runs on-premise)."""
        return provider_type in (cls.OLLAMA, cls.VERTEX)

    @classmethod
    def is_cloud(cls, provider_type: ProviderType) -> bool:
        """Check if provider is cloud-based."""
        return provider_type in (
            cls.OPENAI, cls.ANTHROPIC, cls.GEMINI,
            cls.AZURE_OPENAI, cls.DEEPSEEK, cls.MISTRAL, cls.OPENROUTER
        )

    @classmethod
    def supports_embeddings(cls, provider_type: ProviderType) -> bool:
        """Check if provider supports embeddings."""
        return provider_type in (
            cls.OPENAI, cls.ANTHROPIC, cls.GEMINI,
            cls.AZURE_OPENAI, cls.OLLAMA, cls.DEEPSEEK, cls.MISTRAL
        )

    @classmethod
    def supports_vision(cls, provider_type: ProviderType) -> bool:
        """Check if provider supports vision/multimodal."""
        return provider_type in (
            cls.OPENAI, cls.ANTHROPIC, cls.GEMINI, cls.AZURE_OPENAI
        )

    @classmethod
    def supports_streaming(cls, provider_type: ProviderType) -> bool:
        """Check if provider supports streaming."""
        return provider_type in (
            cls.OPENAI, cls.ANTHROPIC, cls.GEMINI,
            cls.AZURE_OPENAI, cls.OLLAMA, cls.DEEPSEEK, cls.MISTRAL, cls.OPENROUTER
        )


# =============================================================================
# Provider State
# =============================================================================


class ProviderState(str, Enum):
    """States for provider lifecycle."""

    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


# =============================================================================
# Selection Policies
# =============================================================================


class SelectionPolicy(str, Enum):
    """Policies for provider selection."""

    DEFAULT = "default"
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    HEALTHY_FIRST = "healthy_first"
    LOWEST_LATENCY = "lowest_latency"
    FAILOVER = "failover"
    RANDOM = "random"

    @classmethod
    def is_fallback_policy(cls, policy: SelectionPolicy) -> bool:
        """Check if policy supports fallback."""
        return policy in (cls.FAILOVER, cls.PRIORITY)


# =============================================================================
# Provider Health
# =============================================================================


@dataclass
class ProviderHealth:
    """Health status for a provider."""

    healthy: bool
    state: ProviderState = ProviderState.UNHEALTHY
    latency_ms: int = 0
    message: str = ""
    last_check: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "healthy": self.healthy,
            "state": self.state.value,
            "latency_ms": self.latency_ms,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
            "details": self.details,
        }


# =============================================================================
# Provider Metrics
# =============================================================================


@dataclass
class ProviderMetrics:
    """Metrics for a provider."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_duration_ms: int = 0
    total_cost: float = 0.0
    retry_count: int = 0
    failover_count: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def average_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.total_requests == 0:
            return 0.0
        return self.total_duration_ms / self.total_requests

    def record_request(
        self,
        success: bool,
        duration_ms: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Record a request."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_duration_ms += duration_ms
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost

    def record_retry(self) -> None:
        """Record a retry."""
        self.retry_count += 1

    def record_failover(self) -> None:
        """Record a failover."""
        self.failover_count += 1

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.success_rate,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_duration_ms": self.total_duration_ms,
            "average_latency_ms": self.average_latency_ms,
            "total_cost": self.total_cost,
            "retry_count": self.retry_count,
            "failover_count": self.failover_count,
        }


# =============================================================================
# Provider Configuration
# =============================================================================


@dataclass
class ProviderConfig:
    """Configuration for a provider."""

    provider_id: str
    provider_type: ProviderType
    enabled: bool = True
    priority: int = 100
    endpoint: str = ""
    api_key: str = ""
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    max_tokens: int = 4000
    default_model: str = ""
    models: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type.value,
            "enabled": self.enabled,
            "priority": self.priority,
            "endpoint": self.endpoint,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "max_tokens": self.max_tokens,
            "default_model": self.default_model,
            "models": self.models,
            "metadata": self.metadata,
        }


# =============================================================================
# Generation Request/Response
# =============================================================================


@dataclass
class GenerationRequest:
    """Request for text generation."""

    prompt: str
    model: str = ""
    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    stop: list[str] | None = None
    stream: bool = False
    context: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "prompt": self.prompt,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stop": self.stop,
            "stream": self.stream,
            "context": self.context,
            "metadata": self.metadata,
        }


@dataclass
class GenerationResponse:
    """Response from text generation."""

    content: str
    model: str
    provider_id: str
    success: bool = True
    error: str = ""
    finish_reason: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: int = 0
    cost: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "provider_id": self.provider_id,
            "success": self.success,
            "error": self.error,
            "finish_reason": self.finish_reason,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "duration_ms": self.duration_ms,
            "cost": self.cost,
            "metadata": self.metadata,
        }


# =============================================================================
# Task Types
# =============================================================================


class TaskType(str, Enum):
    """Types of tasks for provider selection."""

    GENERAL = "general"
    CODE = "code"
    REASONING = "reasoning"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    QUESTION_ANSWERING = "question_answering"
    EMBEDDING = "embedding"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"


# =============================================================================
# Provider Capabilities
# =============================================================================


@dataclass
class ProviderCapabilities:
    """Capabilities of a provider."""

    provider_type: ProviderType
    supports_streaming: bool = False
    supports_embeddings: bool = False
    supports_vision: bool = False
    supports_function_calling: bool = False
    supports_json_mode: bool = False
    max_context_length: int = 0
    max_output_tokens: int = 0
    supported_task_types: list[TaskType] = field(default_factory=list)
    supported_languages: list[str] = field(default_factory=list)
    privacy_compliant: bool = True
    data_residency: str = ""  # e.g., "us-east-1", "eu-west-1"
    pricing_tier: str = "standard"  # budget, standard, premium

    def supports_task(self, task_type: TaskType) -> bool:
        """Check if provider supports a task type."""
        return task_type in self.supported_task_types or task_type == TaskType.GENERAL

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_type": self.provider_type.value,
            "supports_streaming": self.supports_streaming,
            "supports_embeddings": self.supports_embeddings,
            "supports_vision": self.supports_vision,
            "supports_function_calling": self.supports_function_calling,
            "supports_json_mode": self.supports_json_mode,
            "max_context_length": self.max_context_length,
            "max_output_tokens": self.max_output_tokens,
            "supported_task_types": [t.value for t in self.supported_task_types],
            "supported_languages": self.supported_languages,
            "privacy_compliant": self.privacy_compliant,
            "data_residency": self.data_residency,
            "pricing_tier": self.pricing_tier,
        }


# =============================================================================
# Provider Metadata
# =============================================================================


@dataclass
class ProviderMetadata:
    """Metadata about a provider."""

    provider_id: str
    provider_type: ProviderType
    name: str
    version: str = "1.0.0"
    description: str = ""
    documentation_url: str = ""
    api_version: str = ""
    status_url: str = ""
    support_url: str = ""
    pricing_url: str = ""
    region: str = ""
    datacenter: str = ""
    tags: list[str] = field(default_factory=list)
    capabilities: ProviderCapabilities | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type.value,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "documentation_url": self.documentation_url,
            "api_version": self.api_version,
            "status_url": self.status_url,
            "support_url": self.support_url,
            "pricing_url": self.pricing_url,
            "region": self.region,
            "datacenter": self.datacenter,
            "tags": self.tags,
            "capabilities": self.capabilities.to_dict() if self.capabilities else None,
        }


# =============================================================================
# Streaming Types
# =============================================================================


@dataclass
class StreamChunk:
    """A chunk from a streaming response."""

    content: str
    delta: str = ""
    is_final: bool = False
    model: str = ""
    provider_id: str = ""
    index: int = 0
    finish_reason: str = ""
    usage: dict = field(default_factory=dict)


# =============================================================================
# Cost Estimation
# =============================================================================


@dataclass
class CostEstimate:
    """Cost estimation for a request."""

    provider_id: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    currency: str = "USD"
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "estimated_cost": self.estimated_cost,
            "currency": self.currency,
            "input_cost_per_1k": self.input_cost_per_1k,
            "output_cost_per_1k": self.output_cost_per_1k,
        }


# =============================================================================
# Provider Selection Criteria
# =============================================================================


@dataclass
class SelectionCriteria:
    """Criteria for provider selection."""

    task_type: TaskType = TaskType.GENERAL
    required_capabilities: list[str] = field(default_factory=list)
    preferred_providers: list[str] = field(default_factory=list)
    excluded_providers: list[str] = field(default_factory=list)
    max_cost: float = 0.0
    max_latency_ms: int = 0
    max_context_length: int = 0
    privacy_required: bool = False
    preferred_regions: list[str] = field(default_factory=list)
    require_streaming: bool = False
    require_embeddings: bool = False
    require_vision: bool = False
    require_function_calling: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task_type": self.task_type.value,
            "required_capabilities": self.required_capabilities,
            "preferred_providers": self.preferred_providers,
            "excluded_providers": self.excluded_providers,
            "max_cost": self.max_cost,
            "max_latency_ms": self.max_latency_ms,
            "max_context_length": self.max_context_length,
            "privacy_required": self.privacy_required,
            "preferred_regions": self.preferred_regions,
            "require_streaming": self.require_streaming,
            "require_embeddings": self.require_embeddings,
            "require_vision": self.require_vision,
            "require_function_calling": self.require_function_calling,
        }
