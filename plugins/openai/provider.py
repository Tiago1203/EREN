"""OpenAI Provider for EREN OS OpenAI Plugin.

Handles HTTP communication with OpenAI API.
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from plugins.openai.configuration import OpenAIConfiguration
from plugins.openai.mapper import OpenAIRequest, RequestMapper
from plugins.openai.response_mapper import (
    OpenAIResponse,
    ResponseMapper,
    Choice,
    ResponseMessage,
)
from plugins.openai.exceptions import (
    OpenAIClientError,
    OpenAIRequestError,
    OpenAITimeoutError,
    OpenAIAuthenticationError,
    OpenAIRateLimitError,
    OpenAIModelError,
)

if TYPE_CHECKING:
    pass


@dataclass
class OpenAIClientConfig:
    """Configuration for OpenAI client."""

    api_key: str
    api_base: str = "https://api.openai.com/v1"
    timeout: int = 60
    retries: int = 3
    retry_delay: float = 1.0
    organization: str = ""

    def get_headers(self) -> dict:
        """Get HTTP headers."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers


class OpenAIClient:
    """Client for OpenAI API."""

    def __init__(
        self,
        config: OpenAIClientConfig,
        plugin_config: OpenAIConfiguration | None = None,
    ):
        """Initialize OpenAI client.

        Args:
            config: Client configuration.
            plugin_config: Plugin configuration.
        """
        self._config = config
        self._plugin_config = plugin_config or OpenAIConfiguration()
        self._request_mapper = RequestMapper()
        self._response_mapper = ResponseMapper()

    @property
    def model(self) -> str:
        """Get configured model."""
        return self._plugin_config.model

    def _make_request(
        self,
        request: OpenAIRequest,
        on_chunk: Callable[[str], None] | None = None,
    ) -> OpenAIResponse:
        """Make request to OpenAI API.

        Args:
            request: OpenAI request.
            on_chunk: Optional callback for streaming.

        Returns:
            OpenAI response.

        Raises:
            OpenAIClientError: On request failure.
        """
        url = f"{self._config.api_base}/chat/completions"
        headers = self._config.get_headers()

        # Don't set Content-Type for streaming
        if request.stream:
            headers = {k: v for k, v in headers.items() if k != "Content-Type"}

        body = json.dumps(request.to_dict()).encode("utf-8")

        # Make request with retries
        last_error = None
        for attempt in range(self._config.retries + 1):
            try:
                return self._execute_request(
                    url, headers, body, request.stream, on_chunk
                )
            except (OpenAITimeoutError, OpenAIRateLimitError) as e:
                last_error = e
                if attempt < self._config.retries:
                    time.sleep(self._config.retry_delay * (attempt + 1))
                    continue
                raise

        raise OpenAIClientError(f"Request failed after {self._config.retries + 1} attempts: {last_error}")

    def _execute_request(
        self,
        url: str,
        headers: dict,
        body: bytes,
        stream: bool,
        on_chunk: Callable[[str], None] | None,
    ) -> OpenAIResponse:
        """Execute HTTP request.

        Args:
            url: Request URL.
            headers: HTTP headers.
            body: Request body.
            stream: Whether to stream.
            on_chunk: Optional streaming callback.

        Returns:
            OpenAI response.

        Raises:
            OpenAIClientError: On request failure.
        """
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers=headers,
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=self._config.timeout) as response:
                if stream:
                    return self._handle_stream_response(response, on_chunk)
                else:
                    return self._handle_response(response)

        except urllib.error.HTTPError as e:
            return self._handle_http_error(e)
        except urllib.error.URLError as e:
            if "timed out" in str(e.reason).lower():
                raise OpenAITimeoutError(self._config.timeout)
            raise OpenAIClientError(f"Network error: {e.reason}")
        except TimeoutError:
            raise OpenAITimeoutError(self._config.timeout)

    def _handle_response(self, response: urllib.request.urlopen) -> OpenAIResponse:
        """Handle non-streaming response.

        Args:
            response: HTTP response.

        Returns:
            OpenAI response.
        """
        data = json.loads(response.read().decode("utf-8"))
        return self._response_mapper.parse_response(data)

    def _handle_stream_response(
        self,
        response: urllib.request.urlopen,
        on_chunk: Callable[[str], None],
    ) -> OpenAIResponse:
        """Handle streaming response.

        Args:
            response: HTTP response.
            on_chunk: Streaming callback.

        Returns:
            OpenAI response with accumulated content.
        """
        accumulated = ""

        for line in response:
            line = line.decode("utf-8").strip()
            if not line or not line.startswith("data: "):
                continue

            if line.startswith("data: "):
                try:
                    data_str = line[6:].strip()
                    if data_str:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            accumulated += content
                            if on_chunk:
                                on_chunk(content)
                except (json.JSONDecodeError, IndexError):
                    continue

        return OpenAIResponse(
            choices=[
                Choice(
                    index=0,
                    message=ResponseMessage(content=accumulated),
                    finish_reason="stop",
                )
            ]
        )

    def _handle_http_error(self, error: urllib.error.HTTPError) -> OpenAIResponse:
        """Handle HTTP error response.

        Args:
            error: HTTP error.

        Returns:
            OpenAI response with error.

        Raises:
            OpenAIAuthenticationError: On auth failure.
            OpenAIRateLimitError: On rate limit.
            OpenAIModelError: On model error.
            OpenAIRequestError: On other errors.
        """
        try:
            data = json.loads(error.read().decode("utf-8"))
        except json.JSONDecodeError:
            data = {"error": {"message": error.reason, "type": "http_error"}}

        error_data = data.get("error", {})
        error_msg = error_data.get("message", "Unknown error")
        error_code = error_data.get("code", "")

        if error.code == 401:
            raise OpenAIAuthenticationError(error_msg)
        elif error.code == 429:
            retry_after = int(error.headers.get("Retry-After", 0))
            raise OpenAIRateLimitError(error_msg, retry_after)
        elif error.code == 404 and "model" in error_msg.lower():
            raise OpenAIModelError(error_msg, self.model)
        else:
            raise OpenAIRequestError(error_msg, error_code)

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        context: dict | None = None,
        history: list[dict] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> OpenAIResponse:
        """Generate completion.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            context: Optional context.
            history: Optional conversation history.
            temperature: Override temperature.
            max_tokens: Override max tokens.

        Returns:
            OpenAI response.
        """
        request = self._request_mapper.create_request(
            model=self._plugin_config.model,
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            history=history,
            temperature=temperature or self._plugin_config.temperature,
            max_tokens=max_tokens or self._plugin_config.max_tokens,
            top_p=self._plugin_config.top_p,
            frequency_penalty=self._plugin_config.frequency_penalty,
            presence_penalty=self._plugin_config.presence_penalty,
            stream=self._plugin_config.stream,
        )

        return self._make_request(request)

    def complete_with_messages(
        self,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> OpenAIResponse:
        """Generate completion with messages.

        Args:
            messages: List of message dictionaries.
            temperature: Override temperature.
            max_tokens: Override max tokens.

        Returns:
            OpenAI response.
        """
        from plugins.openai.mapper import Message

        request = OpenAIRequest(
            model=self._plugin_config.model,
            messages=[Message(role=m["role"], content=m["content"]) for m in messages],
            temperature=temperature or self._plugin_config.temperature,
            max_tokens=max_tokens or self._plugin_config.max_tokens,
            top_p=self._plugin_config.top_p,
            frequency_penalty=self._plugin_config.frequency_penalty,
            presence_penalty=self._plugin_config.presence_penalty,
            stream=self._plugin_config.stream,
        )

        return self._make_request(request)
