"""OpenAI Capability for EREN OS OpenAI Plugin.

Implements the reasoning capability using OpenAI.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from core.sdk import (
    BaseCapability,
    CapabilityContext,
    CapabilityResult,
    CapabilityHealth,
    CapabilityMetadata,
    CapabilityCategory,
)
from plugins.openai.configuration import OpenAIConfiguration, load_configuration
from plugins.openai.provider import OpenAIClient, OpenAIClientConfig
from plugins.openai.response_mapper import ResponseMapper
from plugins.openai.exceptions import (
    OpenAIPluginException,
    OpenAIAuthenticationError,
    OpenAITimeoutError,
)

if TYPE_CHECKING:
    pass


@dataclass
class OpenAICapabilityMetrics:
    """Metrics for OpenAI capability."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_duration_ms: int = 0
    total_cost: float = 0.0

    def record_request(
        self,
        success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        duration_ms: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Record a request.

        Args:
            success: Whether request succeeded.
            input_tokens: Input tokens used.
            output_tokens: Output tokens generated.
            duration_ms: Request duration.
            cost: Request cost.
        """
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_duration_ms += duration_ms
        self.total_cost += cost

    def get_success_rate(self) -> float:
        """Get success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests * 100

    def get_average_duration_ms(self) -> float:
        """Get average request duration."""
        if self.total_requests == 0:
            return 0.0
        return self.total_duration_ms / self.total_requests

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.get_success_rate(),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_duration_ms": self.total_duration_ms,
            "average_duration_ms": self.get_average_duration_ms(),
            "total_cost": self.total_cost,
        }


class OpenAICapability(BaseCapability):
    """OpenAI capability for EREN.

    Implements reasoning capability using OpenAI's GPT models.
    """

    # Capability identity
    _capability_id: str = "openai-reasoning"
    _version: str = "1.0.0"

    def __init__(
        self,
        api_key: str,
        config: OpenAIConfiguration | dict | None = None,
    ):
        """Initialize OpenAI capability.

        Args:
            api_key: OpenAI API key.
            config: Optional configuration.
        """
        super().__init__()
        self._api_key = api_key
        self._config = load_configuration(config if isinstance(config, dict) else None) if config else OpenAIConfiguration()
        self._client: OpenAIClient | None = None
        self._metrics = OpenAICapabilityMetrics()
        self._response_mapper = ResponseMapper()

    def initialize(self, context: CapabilityContext) -> None:
        """Initialize the capability.

        Args:
            context: Capability context.
        """
        # Create client configuration
        client_config = OpenAIClientConfig(
            api_key=self._api_key,
            api_base=self._config.api_base,
            timeout=self._config.timeout,
            retries=self._config.retries,
            retry_delay=self._config.retry_delay,
            organization=self._config.organization,
        )

        # Create client
        self._client = OpenAIClient(client_config, self._config)

        # Store context config if available
        if context.config:
            self._config = load_configuration(context.config)

    def execute(self, context: CapabilityContext) -> CapabilityResult:
        """Execute the capability.

        Args:
            context: Execution context with prompt and settings.

        Returns:
            Execution result.
        """
        start_time = time.time()

        try:
            if not self._client:
                return CapabilityResult(
                    success=False,
                    error="Client not initialized",
                )

            # Extract prompt from context
            prompt = context.get("prompt", "")
            system_prompt = context.get("system_prompt")
            history = context.get("history", [])
            temperature = context.get("temperature", self._config.temperature)
            max_tokens = context.get("max_tokens", self._config.max_tokens)

            if not prompt:
                return CapabilityResult(
                    success=False,
                    error="No prompt provided",
                )

            # Make request
            response = self._client.complete(
                prompt=prompt,
                system_prompt=system_prompt,
                history=history,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Record metrics
            usage = response.usage
            cost = self._response_mapper.calculate_cost(usage, self._config.model)

            self._metrics.record_request(
                success=True,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                duration_ms=duration_ms,
                cost=cost,
            )

            # Convert to capability result
            result_data = self._response_mapper.to_capability_result(
                response, self._config.model, duration_ms
            )

            return CapabilityResult(
                success=result_data["success"],
                data=result_data["data"],
                error=result_data["error"],
                duration_ms=duration_ms,
                metadata=result_data["metadata"],
            )

        except OpenAIAuthenticationError as e:
            return self._handle_error(e, start_time, "Authentication failed")
        except OpenAITimeoutError as e:
            return self._handle_error(e, start_time, "Request timed out")
        except OpenAIPluginException as e:
            return self._handle_error(e, start_time, str(e))
        except Exception as e:
            return self._handle_error(e, start_time, f"Unexpected error: {e}")

    def _handle_error(
        self,
        error: Exception,
        start_time: float,
        message: str,
    ) -> CapabilityResult:
        """Handle execution error.

        Args:
            error: Exception that occurred.
            start_time: Start time of request.
            message: Error message.

        Returns:
            Error result.
        """
        duration_ms = int((time.time() - start_time) * 1000)

        self._metrics.record_request(
            success=False,
            duration_ms=duration_ms,
        )

        return CapabilityResult(
            success=False,
            error=message,
            duration_ms=duration_ms,
            metadata={"error_type": type(error).__name__},
        )

    def health(self) -> CapabilityHealth:
        """Return health status.

        Returns:
            Health status.
        """
        if not self._client:
            return CapabilityHealth(
                healthy=False,
                message="Client not initialized",
            )

        # Check if we have recent successful requests
        if self._metrics.total_requests > 0:
            success_rate = self._metrics.get_success_rate()
            if success_rate >= 90:
                return CapabilityHealth(
                    healthy=True,
                    message=f"Healthy. Success rate: {success_rate:.1f}%",
                    latency_ms=int(self._metrics.get_average_duration_ms()),
                )
            else:
                return CapabilityHealth(
                    healthy=False,
                    message=f"Degraded. Success rate: {success_rate:.1f}%",
                    latency_ms=int(self._metrics.get_average_duration_ms()),
                )

        return CapabilityHealth(
            healthy=True,
            message="Initialized",
        )

    def metadata(self) -> CapabilityMetadata:
        """Return capability metadata.

        Returns:
            Capability metadata.
        """
        return CapabilityMetadata(
            name="OpenAI Reasoning",
            version=self._version,
            category=CapabilityCategory.LLM,
            description="OpenAI GPT reasoning capability for EREN",
            author="EREN Team",
            contracts=("ReasoningContract",),
            dependencies=(),
            configuration=self._config.to_dict(),
        )

    def shutdown(self) -> None:
        """Shutdown the capability."""
        self._client = None

    def get_metrics(self) -> dict:
        """Get capability metrics.

        Returns:
            Metrics dictionary.
        """
        return self._metrics.to_dict()

    @property
    def model(self) -> str:
        """Get configured model."""
        return self._config.model
