"""Unit tests for model types and descriptors."""

import pytest
from datetime import datetime, timezone

from core.models.types import (
    ModelCategory,
    ModelState,
    ModelSelectionPolicy,
    ModelCapabilities,
    ModelPricing,
    ModelAvailability,
    ModelMetrics,
)
from core.models.descriptor import ModelDescriptor
from core.models.exceptions import (
    ModelNotFoundError,
    ModelAlreadyRegisteredError,
)


class TestModelCategory:
    """Tests for ModelCategory."""

    def test_values(self):
        """Test enum values."""
        assert ModelCategory.GENERAL.value == "general"
        assert ModelCategory.REASONING.value == "reasoning"
        assert ModelCategory.VISION.value == "vision"
        assert ModelCategory.MEDICAL.value == "medical"


class TestModelState:
    """Tests for ModelState."""

    def test_values(self):
        """Test enum values."""
        assert ModelState.UNREGISTERED.value == "unregistered"
        assert ModelState.REGISTERED.value == "registered"
        assert ModelState.AVAILABLE.value == "available"


class TestModelSelectionPolicy:
    """Tests for ModelSelectionPolicy."""

    def test_values(self):
        """Test enum values."""
        assert ModelSelectionPolicy.DEFAULT.value == "default"
        assert ModelSelectionPolicy.FASTEST.value == "fastest"
        assert ModelSelectionPolicy.CHEAPEST.value == "cheapest"


class TestModelCapabilities:
    """Tests for ModelCapabilities."""

    def test_creation(self):
        """Test capabilities creation."""
        caps = ModelCapabilities(reasoning=True, vision=True)
        assert caps.reasoning is True
        assert caps.vision is True
        assert caps.streaming is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        caps = ModelCapabilities(reasoning=True)
        d = caps.to_dict()
        assert d["reasoning"] is True
        assert "vision" in d


class TestModelPricing:
    """Tests for ModelPricing."""

    def test_creation(self):
        """Test pricing creation."""
        pricing = ModelPricing(
            cost_per_input_token=0.01,
            cost_per_output_token=0.03,
        )
        assert pricing.cost_per_input_token == 0.01

    def test_calculate_cost(self):
        """Test cost calculation."""
        pricing = ModelPricing(
            cost_per_input_token=1.0,  # per 1K tokens
            cost_per_output_token=2.0,
        )
        cost = pricing.calculate_cost(1000, 500)
        assert cost == 1.0 + 1.0  # 1000/1000*1 + 500/1000*2


class TestModelAvailability:
    """Tests for ModelAvailability."""

    def test_creation(self):
        """Test availability creation."""
        avail = ModelAvailability(available=True, region="us-east")
        assert avail.available is True
        assert avail.region == "us-east"


class TestModelMetrics:
    """Tests for ModelMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = ModelMetrics()
        assert metrics.total_requests == 0
        assert metrics.success_rate == 0.0

    def test_record_request(self):
        """Test recording requests."""
        metrics = ModelMetrics()
        metrics.record_request(success=True, duration_ms=100)
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1

    def test_success_rate(self):
        """Test success rate calculation."""
        metrics = ModelMetrics()
        metrics.record_request(success=True)
        metrics.record_request(success=True)
        metrics.record_request(success=False)
        assert metrics.success_rate == pytest.approx(66.67, rel=1)

    def test_average_latency(self):
        """Test average latency calculation."""
        metrics = ModelMetrics()
        metrics.record_request(success=True, duration_ms=100)
        metrics.record_request(success=True, duration_ms=200)
        assert metrics.average_latency_ms == 150.0


class TestModelDescriptor:
    """Tests for ModelDescriptor."""

    def test_creation(self):
        """Test descriptor creation."""
        descriptor = ModelDescriptor(
            model_id="gpt-5-mini",
            provider_id="openai",
            display_name="GPT-5 Mini",
        )
        assert descriptor.model_id == "gpt-5-mini"
        assert descriptor.provider_id == "openai"
        assert descriptor.category == ModelCategory.GENERAL

    def test_capabilities(self):
        """Test capabilities property."""
        descriptor = ModelDescriptor(
            model_id="gpt-5",
            provider_id="openai",
            display_name="GPT-5",
            supports_reasoning=True,
            supports_vision=True,
        )
        assert descriptor.capabilities.reasoning is True
        assert descriptor.capabilities.vision is True

    def test_is_available(self):
        """Test availability check."""
        descriptor = ModelDescriptor(
            model_id="gpt-5",
            provider_id="openai",
            display_name="GPT-5",
            state=ModelState.AVAILABLE,
        )
        assert descriptor.is_available() is True

    def test_is_deprecated(self):
        """Test deprecated check."""
        descriptor = ModelDescriptor(
            model_id="gpt-4",
            provider_id="openai",
            display_name="GPT-4",
            state=ModelState.DEPRECATED,
        )
        assert descriptor.is_deprecated() is True

    def test_supports_capability(self):
        """Test capability check."""
        descriptor = ModelDescriptor(
            model_id="gpt-5",
            provider_id="openai",
            display_name="GPT-5",
            supports_reasoning=True,
            supports_vision=True,
        )
        assert descriptor.supports_capability("reasoning") is True
        assert descriptor.supports_capability("vision") is True
        assert descriptor.supports_capability("streaming") is False

    def test_calculate_cost(self):
        """Test cost calculation."""
        descriptor = ModelDescriptor(
            model_id="gpt-5",
            provider_id="openai",
            display_name="GPT-5",
            pricing=ModelPricing(cost_per_input_token=1.0, cost_per_output_token=2.0),
        )
        cost = descriptor.calculate_cost(1000, 500)
        assert cost == 2.0

    def test_enable_disable(self):
        """Test enable and disable."""
        descriptor = ModelDescriptor(
            model_id="gpt-5",
            provider_id="openai",
            display_name="GPT-5",
        )
        descriptor.disable()
        assert descriptor.state == ModelState.DISABLED

        descriptor.enable()
        assert descriptor.state == ModelState.AVAILABLE

    def test_deprecate(self):
        """Test deprecation."""
        descriptor = ModelDescriptor(
            model_id="gpt-4",
            provider_id="openai",
            display_name="GPT-4",
        )
        descriptor.deprecate()
        assert descriptor.state == ModelState.DEPRECATED
        assert descriptor.deprecated_at is not None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        descriptor = ModelDescriptor(
            model_id="gpt-5",
            provider_id="openai",
            display_name="GPT-5",
        )
        d = descriptor.to_dict()
        assert d["model_id"] == "gpt-5"
        assert d["provider_id"] == "openai"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "model_id": "gpt-5",
            "provider_id": "openai",
            "display_name": "GPT-5",
        }
        descriptor = ModelDescriptor.from_dict(data)
        assert descriptor.model_id == "gpt-5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
