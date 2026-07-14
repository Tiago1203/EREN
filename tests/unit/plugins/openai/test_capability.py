"""Unit tests for OpenAI capability module."""

import pytest
from unittest.mock import MagicMock, patch

from plugins.openai.capability import (
    OpenAICapability,
    OpenAICapabilityMetrics,
)
from plugins.openai.configuration import OpenAIConfiguration
from plugins.openai.exceptions import (
    OpenAIAuthenticationError,
    OpenAITimeoutError,
)
from core.sdk import CapabilityContext, CapabilityResult


class TestOpenAICapabilityMetrics:
    """Tests for OpenAICapabilityMetrics."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = OpenAICapabilityMetrics()
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0

    def test_record_successful_request(self):
        """Test recording successful request."""
        metrics = OpenAICapabilityMetrics()
        metrics.record_request(
            success=True,
            input_tokens=100,
            output_tokens=50,
            duration_ms=1000,
            cost=0.002,
        )

        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.total_input_tokens == 100
        assert metrics.total_output_tokens == 50

    def test_record_failed_request(self):
        """Test recording failed request."""
        metrics = OpenAICapabilityMetrics()
        metrics.record_request(success=False, duration_ms=500)

        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1

    def test_success_rate(self):
        """Test success rate calculation."""
        metrics = OpenAICapabilityMetrics()
        metrics.record_request(success=True)
        metrics.record_request(success=True)
        metrics.record_request(success=False)

        assert metrics.get_success_rate() == pytest.approx(66.67, rel=0.1)

    def test_average_duration(self):
        """Test average duration calculation."""
        metrics = OpenAICapabilityMetrics()
        metrics.record_request(success=True, duration_ms=1000)
        metrics.record_request(success=True, duration_ms=2000)

        assert metrics.get_average_duration_ms() == 1500.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = OpenAICapabilityMetrics()
        metrics.record_request(success=True, duration_ms=1000)

        d = metrics.to_dict()
        assert "total_requests" in d
        assert "success_rate" in d
        assert "average_duration_ms" in d


class TestOpenAICapability:
    """Tests for OpenAICapability."""

    @pytest.fixture
    def capability(self):
        """Create test capability."""
        return OpenAICapability(api_key="sk-test-key123456789")

    def test_initialization(self, capability):
        """Test capability initialization."""
        assert capability._api_key == "sk-test-key123456789"
        assert capability._client is None
        assert capability._metrics is not None

    def test_metadata(self, capability):
        """Test metadata."""
        metadata = capability.metadata()
        assert metadata.name == "OpenAI Reasoning"
        assert metadata.category.value == "llm"
        assert "ReasoningContract" in metadata.contracts

    def test_health_not_initialized(self, capability):
        """Test health check when not initialized."""
        health = capability.health()
        assert health.healthy is False
        assert "not initialized" in health.message

    def test_health_with_successful_requests(self, capability):
        """Test health check with successful requests."""
        # Initialize the capability first
        capability._client = MagicMock()
        capability._metrics.record_request(success=True, duration_ms=500)

        health = capability.health()
        assert health.healthy is True
        assert "Success rate: 100.0%" in health.message

    def test_health_with_low_success_rate(self, capability):
        """Test health check with low success rate."""
        # Initialize the capability first
        capability._client = MagicMock()
        capability._metrics.record_request(success=True)
        capability._metrics.record_request(success=False)
        capability._metrics.record_request(success=False)

        health = capability.health()
        assert health.healthy is False
        assert "Degraded" in health.message

    def test_get_metrics(self, capability):
        """Test getting metrics."""
        capability._metrics.record_request(success=True)

        metrics = capability.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1

    def test_model_property(self, capability):
        """Test model property."""
        assert capability.model == "gpt-5-mini"

    def test_shutdown(self, capability):
        """Test shutdown."""
        capability.shutdown()
        assert capability._client is None


class TestOpenAICapabilityExecute:
    """Tests for OpenAICapability.execute."""

    @pytest.fixture
    def capability(self):
        """Create test capability."""
        cap = OpenAICapability(api_key="sk-test-key123456789")
        # Mock the client
        cap._client = MagicMock()
        return cap

    def test_execute_without_prompt(self, capability):
        """Test execute without prompt."""
        context = CapabilityContext(metadata={"prompt": ""})
        result = capability.execute(context)

        assert result.success is False
        assert "No prompt provided" in result.error

    def test_execute_with_prompt(self, capability):
        """Test execute with prompt."""
        # Create a proper OpenAIResponse object for testing
        from plugins.openai.response_mapper import OpenAIResponse, Usage, Choice, ResponseMessage
        
        usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        choice = Choice(index=0, message=ResponseMessage(content="Hello!"), finish_reason="stop")
        response = OpenAIResponse(
            id="test-123",
            model="gpt-4",
            choices=[choice],
            usage=usage,
        )

        capability._client.complete.return_value = response

        context = CapabilityContext(metadata={"prompt": "Hello"})
        result = capability.execute(context)

        assert result.success is True
        assert result.duration_ms >= 0
        capability._client.complete.assert_called_once()

    def test_execute_with_system_prompt(self, capability):
        """Test execute with system prompt."""
        from plugins.openai.response_mapper import OpenAIResponse, Usage, Choice, ResponseMessage
        
        usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        choice = Choice(index=0, message=ResponseMessage(content="Hello!"), finish_reason="stop")
        response = OpenAIResponse(
            id="test-123",
            model="gpt-4",
            choices=[choice],
            usage=usage,
        )

        capability._client.complete.return_value = response

        context = CapabilityContext(metadata={
            "prompt": "Hello",
            "system_prompt": "You are helpful.",
        })
        result = capability.execute(context)

        assert result.success is True
        capability._client.complete.assert_called_once()

    def test_execute_with_auth_error(self, capability):
        """Test execute with authentication error."""
        capability._client.complete.side_effect = OpenAIAuthenticationError()

        context = CapabilityContext(metadata={"prompt": "Hello"})
        result = capability.execute(context)

        assert result.success is False
        assert "Authentication failed" in result.error

    def test_execute_with_timeout_error(self, capability):
        """Test execute with timeout error."""
        capability._client.complete.side_effect = OpenAITimeoutError(60)

        context = CapabilityContext(metadata={"prompt": "Hello"})
        result = capability.execute(context)

        assert result.success is False
        assert "timed out" in result.error

    def test_execute_without_client(self):
        """Test execute without client initialized."""
        capability = OpenAICapability(api_key="sk-test")
        capability._client = None

        context = CapabilityContext(metadata={"prompt": "Hello"})
        result = capability.execute(context)

        assert result.success is False
        assert "not initialized" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
