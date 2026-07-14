"""Pipeline Policies for EREN OS Cognitive Capability Pipeline.

Defines execution policies for pipeline stages.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.pipeline.context import PipelineContext
    from core.pipeline.stage import PipelineStage
    from core.pipeline.types import StageResult, ExecutionPolicy


class PipelinePolicy(ABC):
    """Abstract base class for pipeline execution policies."""

    @abstractmethod
    def should_stop_on_failure(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        context: "PipelineContext",
    ) -> bool:
        """Determine if pipeline should stop on stage failure.

        Args:
            stage: The stage that failed.
            result: The stage result.
            context: Pipeline context.

        Returns:
            True if pipeline should stop.
        """
        ...

    @abstractmethod
    def should_retry(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        attempt: int,
    ) -> bool:
        """Determine if stage should be retried.

        Args:
            stage: The stage to retry.
            result: The previous result.
            attempt: Current retry attempt number.

        Returns:
            True if should retry.
        """
        ...

    @abstractmethod
    def should_skip_optional_stage(
        self,
        stage: "PipelineStage",
        result: "StageResult",
    ) -> bool:
        """Determine if optional stage should be skipped on failure.

        Args:
            stage: The optional stage.
            result: The stage result.

        Returns:
            True if should skip.
        """
        ...

    @abstractmethod
    def should_strict_execution(
        self,
        context: "PipelineContext",
    ) -> bool:
        """Determine if strict execution mode is enabled.

        Args:
            context: Pipeline context.

        Returns:
            True if strict mode.
        """
        ...


class StopOnFailurePolicy(PipelinePolicy):
    """Stop pipeline execution when a required stage fails."""

    def should_stop_on_failure(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        context: "PipelineContext",
    ) -> bool:
        """Always stop on required stage failure."""
        return stage.is_required

    def should_retry(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        attempt: int,
    ) -> bool:
        """Retry if stage has retry count configured."""
        return attempt < stage._retry_count

    def should_skip_optional_stage(
        self,
        stage: "PipelineStage",
        result: "StageResult",
    ) -> bool:
        """Skip optional stages on failure."""
        return True

    def should_strict_execution(
        self,
        context: "PipelineContext",
    ) -> bool:
        """Strict mode disabled by default."""
        return False


class ContinueOnFailurePolicy(PipelinePolicy):
    """Continue pipeline execution even when stages fail."""

    def should_stop_on_failure(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        context: "PipelineContext",
    ) -> bool:
        """Never stop on failure - always continue."""
        return False

    def should_retry(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        attempt: int,
    ) -> bool:
        """Retry if stage has retry count configured."""
        return attempt < stage._retry_count

    def should_skip_optional_stage(
        self,
        stage: "PipelineStage",
        result: "StageResult",
    ) -> bool:
        """Skip optional stages on failure."""
        return True

    def should_strict_execution(
        self,
        context: "PipelineContext",
    ) -> bool:
        """Strict mode disabled."""
        return False


class StrictExecutionPolicy(PipelinePolicy):
    """Strict execution - fail on any issue."""

    def should_stop_on_failure(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        context: "PipelineContext",
    ) -> bool:
        """Stop on any failure."""
        return True

    def should_retry(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        attempt: int,
    ) -> bool:
        """No retries in strict mode."""
        return False

    def should_skip_optional_stage(
        self,
        stage: "PipelineStage",
        result: "StageResult",
    ) -> bool:
        """Don't skip optional stages in strict mode."""
        return False

    def should_strict_execution(
        self,
        context: "PipelineContext",
    ) -> bool:
        """Strict mode always enabled."""
        return True


class SkipOptionalPolicy(PipelinePolicy):
    """Skip optional stages - only execute required ones."""

    def should_stop_on_failure(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        context: "PipelineContext",
    ) -> bool:
        """Stop only on required stage failure."""
        return stage.is_required

    def should_retry(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        attempt: int,
    ) -> bool:
        """Retry if stage has retry count configured."""
        return attempt < stage._retry_count

    def should_skip_optional_stage(
        self,
        stage: "PipelineStage",
        result: "StageResult",
    ) -> bool:
        """Always skip optional stages."""
        return True

    def should_strict_execution(
        self,
        context: "PipelineContext",
    ) -> bool:
        """Strict mode disabled."""
        return False


class RetryStagePolicy(PipelinePolicy):
    """Policy that retries failed stages multiple times."""

    def __init__(self, max_retries: int = 3):
        """Initialize retry policy.

        Args:
            max_retries: Maximum number of retries per stage.
        """
        self._max_retries = max_retries

    def should_stop_on_failure(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        context: "PipelineContext",
    ) -> bool:
        """Only stop after all retries exhausted."""
        return result.retry_attempts >= self._max_retries

    def should_retry(
        self,
        stage: "PipelineStage",
        result: "StageResult",
        attempt: int,
    ) -> bool:
        """Retry up to max_retries times."""
        return attempt < self._max_retries

    def should_skip_optional_stage(
        self,
        stage: "PipelineStage",
        result: "StageResult",
    ) -> bool:
        """Skip optional stages on failure."""
        return True

    def should_strict_execution(
        self,
        context: "PipelineContext",
    ) -> bool:
        """Strict mode disabled."""
        return False


class PolicyFactory:
    """Factory for creating policy instances."""

    _policies: dict[str, type[PipelinePolicy]] = {
        "stop_on_failure": StopOnFailurePolicy,
        "continue_on_failure": ContinueOnFailurePolicy,
        "strict_execution": StrictExecutionPolicy,
        "skip_optional": SkipOptionalPolicy,
        "retry_stage": RetryStagePolicy,
    }

    @classmethod
    def create(cls, policy_name: str, **kwargs) -> PipelinePolicy:
        """Create a policy by name.

        Args:
            policy_name: Name of the policy.
            **kwargs: Additional arguments for policy.

        Returns:
            Policy instance.

        Raises:
            ValueError: If policy name is unknown.
        """
        policy_class = cls._policies.get(policy_name.lower())
        if policy_class is None:
            raise ValueError(f"Unknown policy: {policy_name}")

        return policy_class(**kwargs)

    @classmethod
    def register(cls, name: str, policy_class: type[PipelinePolicy]) -> None:
        """Register a new policy.

        Args:
            name: Policy name.
            policy_class: Policy class.
        """
        cls._policies[name.lower()] = policy_class

    @classmethod
    def list_policies(cls) -> list[str]:
        """List all registered policies.

        Returns:
            List of policy names.
        """
        return list(cls._policies.keys())


@dataclass
class PolicyConfig:
    """Configuration for policy selection."""

    primary_policy: str = "stop_on_failure"
    retry_policy: str | None = None
    skip_optional: bool = True
    strict_mode: bool = False
    max_retries: int = 3

    def create_policy(self) -> PipelinePolicy:
        """Create policy based on configuration.

        Returns:
            Configured policy.
        """
        if self.primary_policy == "retry_stage":
            return RetryStagePolicy(max_retries=self.max_retries)
        elif self.primary_policy == "continue_on_failure":
            return ContinueOnFailurePolicy()
        elif self.primary_policy == "strict_execution":
            return StrictExecutionPolicy()
        elif self.primary_policy == "skip_optional":
            return SkipOptionalPolicy()
        else:
            return StopOnFailurePolicy()
