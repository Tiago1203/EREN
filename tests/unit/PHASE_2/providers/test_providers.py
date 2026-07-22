"""Unit tests for provider types and enums."""

import pytest
from datetime import datetime, timezone

from core.PHASE_2.providers.types import (
    ProviderType,
    ProviderState,
    SelectionPolicy,
    ProviderHealth,
    ProviderMetrics,
    ProviderConfig,
    GenerationRequest,
    GenerationResponse,
)


class TestProviderType:
    """Tests for ProviderType."""

    def test_values(self):
        """Test enum values."""
        assert ProviderType.OPENAI.value == "openai"
        assert ProviderType.ANTHROPIC.value == "anthropic"
        assert ProviderType.OLLAMA.value == "ollama"
        assert ProviderType.GEMINI.value == "gemini"
        assert ProviderType.DEEPSEEK.value == "deepseek"
        assert ProviderType.MISTRAL.value == "mistral"

    def test_is_local(self):
        """Test local provider check."""
        assert ProviderType.is_local(ProviderType.OLLAMA) is True
        assert ProviderType.is_local(ProviderType.OPENAI) is False

    def test_is_cloud(self):
        """Test cloud provider check."""
        assert ProviderType.is_cloud(ProviderType.OPENAI) is True
        assert ProviderType.is_cloud(ProviderType.ANTHROPIC) is True
        assert ProviderType.is_cloud(ProviderType.OLLAMA) is False


class TestProviderState:
    """Tests for ProviderState."""

    def test_values(self):
        """Test enum values."""
        assert ProviderState.UNREGISTERED.value == "unregistered"
        assert ProviderState.HEALTHY.value == "healthy"
        assert ProviderState.UNHEALTHY.value == "unhealthy"


class TestSelectionPolicy:
    """Tests for SelectionPolicy."""

    def test_values(self):
        """Test enum values."""
        assert SelectionPolicy.DEFAULT.value == "default"
        assert SelectionPolicy.PRIORITY.value == "priority"
        assert SelectionPolicy.ROUND_ROBIN.value == "round_robin"

    def test_is_fallback_policy(self):
        """Test fallback policy check."""
        assert SelectionPolicy.is_fallback_policy(SelectionPolicy.FAILOVER) is True
        assert SelectionPolicy.is_fallback_policy(SelectionPolicy.PRIORITY) is True
        assert SelectionPolicy.is_fallback_policy(SelectionPolicy.RANDOM) is False


class TestProviderHealth:
    """Tests for ProviderHealth."""

    def test_creation(self):
        """Test health creation."""
        health = ProviderHealth(healthy=True, state=ProviderState.HEALTHY)
        assert health.healthy is True
        assert health.state == ProviderState.HEALTHY

    def test_to_dict(self):
        """Test conversion to dictionary."""
        health = ProviderHealth(healthy=True, latency_ms=100)
        d = health.to_dict()
        assert d["healthy"] is True
        assert d["latency_ms"] == 100


class TestProviderMetrics:
    """Tests for ProviderMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = ProviderMetrics()
        assert metrics.total_requests == 0
        assert metrics.success_rate == 0.0

    def test_record_request(self):
        """Test recording requests."""
        metrics = ProviderMetrics()
        metrics.record_request(success=True, duration_ms=100)
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0

    def test_record_failed_request(self):
        """Test recording failed request."""
        metrics = ProviderMetrics()
        metrics.record_request(success=False)
        assert metrics.total_requests == 1
        assert metrics.failed_requests == 1

    def test_success_rate(self):
        """Test success rate calculation."""
        metrics = ProviderMetrics()
        metrics.record_request(success=True)
        metrics.record_request(success=True)
        metrics.record_request(success=False)
        assert metrics.success_rate == pytest.approx(66.67, rel=1)

    def test_average_latency(self):
        """Test average latency calculation."""
        metrics = ProviderMetrics()
        metrics.record_request(success=True, duration_ms=100)
        metrics.record_request(success=True, duration_ms=200)
        assert metrics.average_latency_ms == 150.0

    def test_record_retry(self):
        """Test retry recording."""
        metrics = ProviderMetrics()
        metrics.record_retry()
        assert metrics.retry_count == 1

    def test_record_failover(self):
        """Test failover recording."""
        metrics = ProviderMetrics()
        metrics.record_failover()
        assert metrics.failover_count == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = ProviderMetrics()
        metrics.record_request(success=True)
        d = metrics.to_dict()
        assert "total_requests" in d
        assert "success_rate" in d


class TestProviderConfig:
    """Tests for ProviderConfig."""

    def test_creation(self):
        """Test config creation."""
        config = ProviderConfig(
            provider_id="openai",
            provider_type=ProviderType.OPENAI,
        )
        assert config.provider_id == "openai"
        assert config.provider_type == ProviderType.OPENAI
        assert config.enabled is True
        assert config.priority == 100

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = ProviderConfig(
            provider_id="openai",
            provider_type=ProviderType.OPENAI,
        )
        d = config.to_dict()
        assert d["provider_id"] == "openai"
        assert d["provider_type"] == "openai"


class TestGenerationRequest:
    """Tests for GenerationRequest."""

    def test_creation(self):
        """Test request creation."""
        request = GenerationRequest(prompt="Hello", model="gpt-4")
        assert request.prompt == "Hello"
        assert request.model == "gpt-4"
        assert request.temperature == 0.7

    def test_with_system_prompt(self):
        """Test request with system prompt."""
        request = GenerationRequest(
            prompt="Hello",
            system_prompt="You are helpful.",
        )
        assert request.system_prompt == "You are helpful."

    def test_to_dict(self):
        """Test conversion to dictionary."""
        request = GenerationRequest(prompt="Hello")
        d = request.to_dict()
        assert d["prompt"] == "Hello"
        assert "temperature" in d


class TestGenerationResponse:
    """Tests for GenerationResponse."""

    def test_creation(self):
        """Test response creation."""
        response = GenerationResponse(
            content="Hi there!",
            model="gpt-4",
            provider_id="openai",
        )
        assert response.content == "Hi there!"
        assert response.model == "gpt-4"
        assert response.success is True

    def test_failure_response(self):
        """Test failure response."""
        response = GenerationResponse(
            content="",
            model="gpt-4",
            provider_id="openai",
            success=False,
            error="API error",
        )
        assert response.success is False
        assert response.error == "API error"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        response = GenerationResponse(
            content="Hello",
            model="gpt-4",
            provider_id="openai",
        )
        d = response.to_dict()
        assert d["content"] == "Hello"
        assert d["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
