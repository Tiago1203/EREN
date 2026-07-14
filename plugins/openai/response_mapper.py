"""Response mapper for EREN OS OpenAI Plugin.

Converts OpenAI API responses to EREN CapabilityResult format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class Usage:
    """Token usage information."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class Choice:
    """Response choice."""

    index: int
    message: "ResponseMessage"
    finish_reason: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason,
        }


@dataclass
class ResponseMessage:
    """OpenAI response message."""

    role: str = "assistant"
    content: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass
class OpenAIResponse:
    """OpenAI API response."""

    id: str = ""
    object: str = "chat.completion"
    created: int = 0
    model: str = ""
    choices: list[Choice] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    error: dict | None = None

    @property
    def content(self) -> str:
        """Get content from first choice."""
        if self.choices and len(self.choices) > 0:
            return self.choices[0].message.content
        return ""

    @property
    def finish_reason(self) -> str:
        """Get finish reason from first choice."""
        if self.choices and len(self.choices) > 0:
            return self.choices[0].finish_reason
        return ""

    @property
    def is_error(self) -> bool:
        """Check if response is an error."""
        return self.error is not None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [c.to_dict() for c in self.choices],
            "usage": self.usage.to_dict(),
            "error": self.error,
        }


class ResponseMapper:
    """Maps OpenAI API responses to EREN format."""

    @staticmethod
    def parse_response(response_data: dict) -> OpenAIResponse:
        """Parse OpenAI API response.

        Args:
            response_data: Raw API response data.

        Returns:
            OpenAIResponse instance.
        """
        # Check for error
        if "error" in response_data:
            return OpenAIResponse(error=response_data["error"])

        # Parse usage
        usage_data = response_data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        # Parse choices
        choices = []
        for idx, choice_data in enumerate(response_data.get("choices", [])):
            message_data = choice_data.get("message", {})
            message = ResponseMessage(
                role=message_data.get("role", "assistant"),
                content=message_data.get("content", ""),
            )
            choice = Choice(
                index=idx,
                message=message,
                finish_reason=choice_data.get("finish_reason", ""),
            )
            choices.append(choice)

        return OpenAIResponse(
            id=response_data.get("id", ""),
            object=response_data.get("object", "chat.completion"),
            created=response_data.get("created", 0),
            model=response_data.get("model", ""),
            choices=choices,
            usage=usage,
        )

    @staticmethod
    def to_capability_result(
        response: OpenAIResponse,
        model: str,
        duration_ms: int = 0,
    ) -> dict:
        """Convert OpenAI response to CapabilityResult format.

        Args:
            response: OpenAI response.
            model: Model used.
            duration_ms: Request duration.

        Returns:
            Dictionary in CapabilityResult format.
        """
        if response.is_error:
            return {
                "success": False,
                "error": response.error.get("message", "Unknown error"),
                "data": None,
                "duration_ms": duration_ms,
                "metadata": {
                    "model": model,
                    "error_code": response.error.get("code"),
                    "error_type": response.error.get("type"),
                },
            }

        return {
            "success": True,
            "error": "",
            "data": {
                "content": response.content,
                "finish_reason": response.finish_reason,
                "model": model,
                "usage": response.usage.to_dict(),
            },
            "duration_ms": duration_ms,
            "metadata": {
                "response_id": response.id,
                "model": model,
                "finish_reason": response.finish_reason,
            },
        }

    @staticmethod
    def calculate_cost(
        usage: Usage,
        model: str,
    ) -> float:
        """Calculate estimated cost.

        Args:
            usage: Token usage.
            model: Model name.

        Returns:
            Estimated cost in USD.
        """
        # Import here to avoid circular dependency
        from plugins.openai.models import get_model_config

        try:
            config = get_model_config(model)
            input_cost = usage.prompt_tokens * config.cost_per_input_token
            output_cost = usage.completion_tokens * config.cost_per_output_token
            return input_cost + output_cost
        except ValueError:
            return 0.0
