"""Model types and enums for EREN OS Cognitive Model Registry.

Defines all types, enums, and value objects used by the model registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Model Categories
# =============================================================================


class ModelCategory(str, Enum):
    """Categories for model classification."""

    GENERAL = "general"
    REASONING = "reasoning"
    VISION = "vision"
    EMBEDDING = "embedding"
    CODE = "code"
    MEDICAL = "medical"
    MULTIMODAL = "multimodal"
    AUDIO = "audio"
    CUSTOM = "custom"


# =============================================================================
# Model State
# =============================================================================


class ModelState(str, Enum):
    """States for model lifecycle."""

    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


# =============================================================================
# Selection Policies
# =============================================================================


class ModelSelectionPolicy(str, Enum):
    """Policies for model selection."""

    DEFAULT = "default"
    FASTEST = "fastest"
    CHEAPEST = "cheapest"
    HIGHEST_QUALITY = "highest_quality"
    LONGEST_CONTEXT = "longest_context"
    REASONING = "reasoning"
    MULTIMODAL = "multimodal"
    CUSTOM = "custom"


# =============================================================================
# Model Capabilities
# =============================================================================


@dataclass
class ModelCapabilities:
    """Capabilities of a model."""

    reasoning: bool = False
    tool_calling: bool = False
    json_output: bool = False
    vision: bool = False
    streaming: bool = False
    embeddings: bool = False
    function_calling: bool = False
    long_context: bool = False
    image_understanding: bool = False
    audio_understanding: bool = False
    multimodal: bool = False
    medical: bool = False
    code: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "reasoning": self.reasoning,
            "tool_calling": self.tool_calling,
            "json_output": self.json_output,
            "vision": self.vision,
            "streaming": self.streaming,
            "embeddings": self.embeddings,
            "function_calling": self.function_calling,
            "long_context": self.long_context,
            "image_understanding": self.image_understanding,
            "audio_understanding": self.audio_understanding,
            "multimodal": self.multimodal,
            "medical": self.medical,
            "code": self.code,
        }


# =============================================================================
# Model Pricing
# =============================================================================


@dataclass
class ModelPricing:
    """Pricing information for a model."""

    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0
    currency: str = "USD"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given tokens."""
        return (input_tokens * self.cost_per_input_token / 1000) + \
               (output_tokens * self.cost_per_output_token / 1000)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "cost_per_input_token": self.cost_per_input_token,
            "cost_per_output_token": self.cost_per_output_token,
            "currency": self.currency,
            "last_updated": self.last_updated.isoformat(),
        }


# =============================================================================
# Model Metrics
# =============================================================================


@dataclass
class ModelMetrics:
    """Metrics for a model."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_duration_ms: int = 0
    total_cost: float = 0.0
    error_count: int = 0

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
        error: bool = False,
    ) -> None:
        """Record a request."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error:
                self.error_count += 1
        self.total_duration_ms += duration_ms
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost

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
            "error_count": self.error_count,
        }


# =============================================================================
# Model Availability
# =============================================================================


@dataclass
class ModelAvailability:
    """Availability information for a model."""

    available: bool = True
    region: str = "global"
    rate_limit_per_minute: int = 0
    rate_limit_per_day: int = 0
    current_usage_percent: float = 0.0
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "available": self.available,
            "region": self.region,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "rate_limit_per_day": self.rate_limit_per_day,
            "current_usage_percent": self.current_usage_percent,
            "last_check": self.last_check.isoformat(),
        }
