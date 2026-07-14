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
    CLAUDE = "claude"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"

    @classmethod
    def is_local(cls, provider_type: ProviderType) -> bool:
        """Check if provider is local (runs on-premise)."""
        return provider_type == cls.OLLAMA

    @classmethod
    def is_cloud(cls, provider_type: ProviderType) -> bool:
        """Check if provider is cloud-based."""
        return provider_type in (cls.OPENAI, cls.CLAUDE, cls.GEMINI, cls.AZURE_OPENAI)


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
