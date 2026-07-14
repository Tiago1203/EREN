"""Request mapper for EREN OS OpenAI Plugin.

Converts EREN context to OpenAI API format.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class Message:
    """OpenAI message format."""

    role: str
    content: str
    name: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class OpenAIRequest:
    """Request to OpenAI API."""

    model: str
    messages: list[Message] = field(default_factory=list)
    temperature: float = 0.2
    max_tokens: int = 4000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False
    stop: list[str] | None = None
    user: str | None = None

    def to_dict(self) -> dict:
        """Convert to API dictionary."""
        result = {
            "model": self.model,
            "messages": [m.to_dict() for m in self.messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stream": self.stream,
        }

        if self.stop:
            result["stop"] = self.stop

        if self.user:
            result["user"] = self.user

        return result


class RequestMapper:
    """Maps EREN context to OpenAI API format."""

    @staticmethod
    def map_system_message(content: str, name: str | None = None) -> Message:
        """Map system message.

        Args:
            content: Message content.
            name: Optional name.

        Returns:
            OpenAI Message.
        """
        return Message(role="system", content=content, name=name)

    @staticmethod
    def map_user_message(content: str, name: str | None = None) -> Message:
        """Map user message.

        Args:
            content: Message content.
            name: Optional name.

        Returns:
            OpenAI Message.
        """
        return Message(role="user", content=content, name=name)

    @staticmethod
    def map_assistant_message(content: str) -> Message:
        """Map assistant message.

        Args:
            content: Message content.

        Returns:
            OpenAI Message.
        """
        return Message(role="assistant", content=content)

    @classmethod
    def map_context(
        cls,
        prompt: str,
        system_prompt: str | None = None,
        context: dict | None = None,
        history: list[dict] | None = None,
    ) -> list[Message]:
        """Map EREN context to OpenAI messages.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            context: Optional context dictionary.
            history: Optional conversation history.

        Returns:
            List of OpenAI messages.
        """
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append(cls.map_system_message(system_prompt))

        # Add conversation history
        if history:
            for msg in history:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "system":
                    messages.append(cls.map_system_message(content))
                elif role == "user":
                    messages.append(cls.map_user_message(content))
                elif role == "assistant":
                    messages.append(cls.map_assistant_message(content))

        # Add current prompt
        messages.append(cls.map_user_message(prompt))

        return messages

    @classmethod
    def create_request(
        cls,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        context: dict | None = None,
        history: list[dict] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stream: bool = False,
    ) -> OpenAIRequest:
        """Create OpenAI request from context.

        Args:
            model: Model name.
            prompt: User prompt.
            system_prompt: Optional system prompt.
            context: Optional context dictionary.
            history: Optional conversation history.
            temperature: Temperature setting.
            max_tokens: Max tokens setting.
            top_p: Top-p setting.
            frequency_penalty: Frequency penalty.
            presence_penalty: Presence penalty.
            stream: Stream setting.

        Returns:
            OpenAI request.
        """
        messages = cls.map_context(prompt, system_prompt, context, history)

        return OpenAIRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
        )
