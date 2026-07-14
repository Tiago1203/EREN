"""Unit tests for OpenAI mapper modules."""

import pytest

from plugins.openai.mapper import (
    Message,
    OpenAIRequest,
    RequestMapper,
)
from plugins.openai.response_mapper import (
    Usage,
    Choice,
    ResponseMessage,
    OpenAIResponse,
    ResponseMapper,
)


class TestMessage:
    """Tests for Message."""

    def test_creation(self):
        """Test message creation."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None

    def test_with_name(self):
        """Test message with name."""
        msg = Message(role="user", content="Hello", name="user1")
        assert msg.name == "user1"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        msg = Message(role="assistant", content="Hi there")
        d = msg.to_dict()

        assert d["role"] == "assistant"
        assert d["content"] == "Hi there"


class TestOpenAIRequest:
    """Tests for OpenAIRequest."""

    def test_creation(self):
        """Test request creation."""
        request = OpenAIRequest(
            model="gpt-4",
            messages=[Message(role="user", content="Hello")],
        )

        assert request.model == "gpt-4"
        assert len(request.messages) == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        request = OpenAIRequest(
            model="gpt-4",
            messages=[Message(role="user", content="Hello")],
            temperature=0.5,
        )

        d = request.to_dict()

        assert d["model"] == "gpt-4"
        assert d["temperature"] == 0.5
        assert len(d["messages"]) == 1


class TestRequestMapper:
    """Tests for RequestMapper."""

    def test_map_system_message(self):
        """Test mapping system message."""
        msg = RequestMapper.map_system_message("You are helpful.")
        assert msg.role == "system"
        assert msg.content == "You are helpful."

    def test_map_user_message(self):
        """Test mapping user message."""
        msg = RequestMapper.map_user_message("Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_map_assistant_message(self):
        """Test mapping assistant message."""
        msg = RequestMapper.map_assistant_message("Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"

    def test_map_context_simple(self):
        """Test mapping simple context."""
        messages = RequestMapper.map_context("Hello")
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"

    def test_map_context_with_system(self):
        """Test mapping context with system prompt."""
        messages = RequestMapper.map_context(
            "Hello",
            system_prompt="You are helpful.",
        )
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert messages[1].role == "user"

    def test_map_context_with_history(self):
        """Test mapping context with history."""
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        messages = RequestMapper.map_context("How are you?", history=history)
        assert len(messages) == 3

    def test_create_request(self):
        """Test creating request."""
        request = RequestMapper.create_request(
            model="gpt-4",
            prompt="Hello",
            temperature=0.5,
        )

        assert request.model == "gpt-4"
        assert request.temperature == 0.5
        assert len(request.messages) == 1


class TestUsage:
    """Tests for Usage."""

    def test_creation(self):
        """Test usage creation."""
        usage = Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30

    def test_to_dict(self):
        """Test conversion to dictionary."""
        usage = Usage(prompt_tokens=10, completion_tokens=20)
        d = usage.to_dict()

        assert d["prompt_tokens"] == 10
        assert d["completion_tokens"] == 20


class TestResponseMessage:
    """Tests for ResponseMessage."""

    def test_creation(self):
        """Test response message creation."""
        msg = ResponseMessage(role="assistant", content="Hello")
        assert msg.role == "assistant"
        assert msg.content == "Hello"


class TestChoice:
    """Tests for Choice."""

    def test_creation(self):
        """Test choice creation."""
        msg = ResponseMessage(content="Hello")
        choice = Choice(index=0, message=msg, finish_reason="stop")
        assert choice.index == 0
        assert choice.finish_reason == "stop"


class TestOpenAIResponse:
    """Tests for OpenAIResponse."""

    def test_content_property(self):
        """Test content property."""
        msg = ResponseMessage(content="Hello")
        response = OpenAIResponse(
            choices=[Choice(index=0, message=msg)],
        )
        assert response.content == "Hello"

    def test_finish_reason_property(self):
        """Test finish_reason property."""
        msg = ResponseMessage(content="Hello")
        response = OpenAIResponse(
            choices=[Choice(index=0, message=msg, finish_reason="stop")],
        )
        assert response.finish_reason == "stop"

    def test_is_error_true(self):
        """Test is_error when error present."""
        response = OpenAIResponse(error={"message": "Error"})
        assert response.is_error is True

    def test_is_error_false(self):
        """Test is_error when no error."""
        msg = ResponseMessage(content="Hello")
        response = OpenAIResponse(choices=[Choice(index=0, message=msg)])
        assert response.is_error is False


class TestResponseMapper:
    """Tests for ResponseMapper."""

    def test_parse_response(self):
        """Test parsing response."""
        data = {
            "id": "chatcmpl-123",
            "model": "gpt-4",
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        }

        response = ResponseMapper.parse_response(data)
        assert response.id == "chatcmpl-123"
        assert response.content == "Hello"
        assert response.usage.prompt_tokens == 10

    def test_parse_error_response(self):
        """Test parsing error response."""
        data = {
            "error": {
                "message": "Invalid API key",
                "type": "authentication_error",
            }
        }

        response = ResponseMapper.parse_response(data)
        assert response.is_error is True
        assert response.error["message"] == "Invalid API key"

    def test_to_capability_result_success(self):
        """Test converting successful response."""
        response = OpenAIResponse(
            id="chatcmpl-123",
            model="gpt-4",
            choices=[
                Choice(
                    index=0,
                    message=ResponseMessage(content="Hello"),
                    finish_reason="stop",
                )
            ],
            usage=Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )

        result = ResponseMapper.to_capability_result(response, "gpt-4", 100)

        assert result["success"] is True
        assert result["data"]["content"] == "Hello"
        assert result["duration_ms"] == 100

    def test_to_capability_result_error(self):
        """Test converting error response."""
        response = OpenAIResponse(
            error={"message": "Invalid request", "code": "invalid_request"},
        )

        result = ResponseMapper.to_capability_result(response, "gpt-4", 50)

        assert result["success"] is False
        assert "Invalid request" in result["error"]

    def test_calculate_cost(self):
        """Test cost calculation."""
        usage = Usage(prompt_tokens=1000, completion_tokens=500)
        cost = ResponseMapper.calculate_cost(usage, "gpt-4")

        # gpt-4: $0.03/input token + $0.06/output token
        # 1000 * 0.03 + 500 * 0.06 = 60.0
        expected = 60.0
        assert cost == pytest.approx(expected, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
