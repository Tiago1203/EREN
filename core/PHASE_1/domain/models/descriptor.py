"""Model descriptor for EREN OS Cognitive Model Registry.

Defines the model descriptor that contains all model metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.domain.models.types import (
    ModelAvailability,
    ModelCapabilities,
    ModelCategory,
    ModelMetrics,
    ModelPricing,
    ModelState,
)

if TYPE_CHECKING:
    pass


@dataclass
class ModelDescriptor:
    """Descriptor containing all model metadata.

    Every model registered in the system must have a descriptor
    that announces its capabilities, pricing, and availability.
    """

    # Identification
    model_id: str
    provider_id: str
    display_name: str
    version: str = "1.0.0"

    # Context and limits
    context_window: int = 128000
    max_output_tokens: int = 16000

    # Capabilities
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_json_mode: bool = False
    supports_multimodal: bool = False
    supports_reasoning: bool = False
    supports_embeddings: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    supports_tools: bool = False

    # Category
    category: ModelCategory = ModelCategory.GENERAL

    # State
    state: ModelState = ModelState.REGISTERED

    # Pricing
    pricing: ModelPricing = field(default_factory=ModelPricing)

    # Availability
    availability: ModelAvailability = field(default_factory=ModelAvailability)

    # Performance metrics
    latency_ms: int = 0
    quality_score: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    deprecated_at: datetime | None = None

    # Metadata
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Initialize computed fields."""
        # Build capabilities from supports_* fields
        self._capabilities = ModelCapabilities(
            reasoning=self.supports_reasoning,
            tool_calling=self.supports_tools,
            json_output=self.supports_json_mode,
            vision=self.supports_vision,
            streaming=self.supports_streaming,
            embeddings=self.supports_embeddings,
            function_calling=self.supports_function_calling,
            long_context=self.context_window >= 100000,
            image_understanding=self.supports_multimodal or self.supports_vision,
            audio_understanding=self.supports_audio,
            multimodal=self.supports_multimodal,
            medical=self.category == ModelCategory.MEDICAL,
            code=self.category == ModelCategory.CODE,
        )

    @property
    def capabilities(self) -> ModelCapabilities:
        """Get model capabilities."""
        return self._capabilities

    def is_available(self) -> bool:
        """Check if model is available."""
        return self.state == ModelState.AVAILABLE and self.availability.available

    def is_deprecated(self) -> bool:
        """Check if model is deprecated."""
        return self.state == ModelState.DEPRECATED

    def supports_capability(self, capability: str) -> bool:
        """Check if model supports a specific capability.

        Args:
            capability: Capability name to check.

        Returns:
            True if supported.
        """
        capability_map = {
            "reasoning": self.supports_reasoning,
            "tool_calling": self.supports_tools,
            "json_output": self.supports_json_mode,
            "vision": self.supports_vision,
            "streaming": self.supports_streaming,
            "embeddings": self.supports_embeddings,
            "function_calling": self.supports_function_calling,
            "long_context": self.context_window >= 100000,
            "image_understanding": self.supports_multimodal or self.supports_vision,
            "audio_understanding": self.supports_audio,
            "multimodal": self.supports_multimodal,
        }
        return capability_map.get(capability, False)

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given tokens.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost.
        """
        return self.pricing.calculate_cost(input_tokens, output_tokens)

    def deprecate(self) -> None:
        """Mark model as deprecated."""
        self.state = ModelState.DEPRECATED
        self.deprecated_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def enable(self) -> None:
        """Enable the model."""
        self.state = ModelState.AVAILABLE
        self.updated_at = datetime.now(UTC)

    def disable(self) -> None:
        """Disable the model."""
        self.state = ModelState.DISABLED
        self.updated_at = datetime.now(UTC)

    def update_metrics(self, metrics: ModelMetrics) -> None:
        """Update model metrics.

        Args:
            metrics: New metrics to merge.
        """
        self.latency_ms = int(metrics.average_latency_ms)
        self.quality_score = metrics.success_rate
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "model_id": self.model_id,
            "provider_id": self.provider_id,
            "display_name": self.display_name,
            "version": self.version,
            "context_window": self.context_window,
            "max_output_tokens": self.max_output_tokens,
            "supports_streaming": self.supports_streaming,
            "supports_function_calling": self.supports_function_calling,
            "supports_json_mode": self.supports_json_mode,
            "supports_multimodal": self.supports_multimodal,
            "supports_reasoning": self.supports_reasoning,
            "supports_embeddings": self.supports_embeddings,
            "supports_vision": self.supports_vision,
            "supports_audio": self.supports_audio,
            "supports_tools": self.supports_tools,
            "category": self.category.value,
            "state": self.state.value,
            "pricing": self.pricing.to_dict(),
            "availability": self.availability.to_dict(),
            "latency_ms": self.latency_ms,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ModelDescriptor:
        """Create from dictionary.

        Args:
            data: Dictionary data.

        Returns:
            ModelDescriptor instance.
        """
        # Handle nested objects
        if "pricing" in data and isinstance(data["pricing"], dict):
            data["pricing"] = ModelPricing(**data["pricing"])
        if "availability" in data and isinstance(data["availability"], dict):
            data["availability"] = ModelAvailability(**data["availability"])

        # Handle enums
        if "category" in data and isinstance(data["category"], str):
            data["category"] = ModelCategory(data["category"])
        if "state" in data and isinstance(data["state"], str):
            data["state"] = ModelState(data["state"])

        return cls(**data)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ModelDescriptor("
            f"id={self.model_id}, "
            f"provider={self.provider_id}, "
            f"category={self.category.value}, "
            f"state={self.state.value})"
        )
