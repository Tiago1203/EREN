"""Router exceptions for EREN OS Cognitive Capability Router.

Defines all exceptions that can be raised during router operations.
"""

from __future__ import annotations


class RouterException(Exception):
    """Base exception for all router errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RouterInitializationError(RouterException):
    """Raised when router fails to initialize."""
    pass


class RoutingError(RouterException):
    """Raised when routing fails."""

    def __init__(self, message: str, intent_type: str = ""):
        super().__init__(message, {"intent_type": intent_type})
        self.intent_type = intent_type


class NoMatchingPipelineError(RoutingError):
    """Raised when no pipeline matches the intent."""

    def __init__(self, intent_type: str, reason: str = ""):
        super().__init__(
            f"No pipeline found for intent type: {intent_type}. Reason: {reason}",
            intent_type,
        )
        self.reason = reason


class MultipleMatchingPipelinesError(RoutingError):
    """Raised when multiple pipelines match the intent."""

    def __init__(self, intent_type: str, matches: list[str]):
        super().__init__(
            f"Multiple pipelines match intent type: {intent_type}",
            intent_type,
        )
        self.matches = matches


class PipelineNotEligibleError(RoutingError):
    """Raised when a pipeline is not eligible for selection."""

    def __init__(self, pipeline_name: str, reason: str):
        super().__init__(
            f"Pipeline '{pipeline_name}' is not eligible: {reason}",
        )
        self.pipeline_name = pipeline_name
        self.reason = reason


class PolicyViolationError(RouterException):
    """Raised when a routing policy is violated."""

    def __init__(self, message: str, policy_name: str = ""):
        super().__init__(message, {"policy_name": policy_name})
        self.policy_name = policy_name


class StrictPolicyError(PolicyViolationError):
    """Raised when strict policy cannot be satisfied."""

    def __init__(self, message: str):
        super().__init__(message, "StrictPolicy")
        self.message = message


class FallbackError(RouterException):
    """Raised when fallback pipeline selection fails."""

    def __init__(self, message: str, attempted_pipelines: list[str]):
        super().__init__(message, {"attempted_pipelines": attempted_pipelines})
        self.attempted_pipelines = attempted_pipelines


class RouterStateError(RouterException):
    """Raised when an operation is invalid for current state."""

    def __init__(self, message: str, current_state: str = "", operation: str = ""):
        super().__init__(message, {
            "current_state": current_state,
            "operation": operation,
        })
        self.current_state = current_state
        self.operation = operation


class InvalidTransitionError(RouterStateError):
    """Raised when state transition is invalid."""

    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            f"Invalid state transition: {from_state} -> {to_state}",
            from_state,
            "transition",
        )
        self.from_state = from_state
        self.to_state = to_state


class RuleValidationError(RouterException):
    """Raised when a routing rule is invalid."""

    def __init__(self, message: str, rule_id: str = ""):
        super().__init__(message, {"rule_id": rule_id})
        self.rule_id = rule_id


class RegistryError(RouterException):
    """Raised when there's an error with routing registry."""

    def __init__(self, message: str, registry_key: str = ""):
        super().__init__(message, {"registry_key": registry_key})
        self.registry_key = registry_key


class RuleNotFoundError(RegistryError):
    """Raised when a rule is not found in registry."""

    def __init__(self, rule_id: str):
        super().__init__(
            f"Rule '{rule_id}' not found in registry",
            rule_id,
        )
        self.rule_id = rule_id


class RuleAlreadyRegisteredError(RegistryError):
    """Raised when a rule is already registered."""

    def __init__(self, rule_id: str):
        super().__init__(
            f"Rule '{rule_id}' is already registered",
            rule_id,
        )
        self.rule_id = rule_id


class SelectorError(RouterException):
    """Raised when pipeline selection fails."""

    def __init__(self, message: str, candidate_count: int = 0):
        super().__init__(message, {"candidate_count": candidate_count})
        self.candidate_count = candidate_count


class MatcherError(RouterException):
    """Raised when pipeline matching fails."""

    def __init__(self, message: str, intent_type: str = ""):
        super().__init__(message, {"intent_type": intent_type})
        self.intent_type = intent_type


class ContextError(RouterException):
    """Raised when there's an error with routing context."""

    def __init__(self, message: str, context_key: str = ""):
        super().__init__(message, {"context_key": context_key})
        self.context_key = context_key


class MetadataError(RouterException):
    """Raised when pipeline metadata is invalid."""

    def __init__(self, message: str, pipeline_name: str = ""):
        super().__init__(message, {"pipeline_name": pipeline_name})
        self.pipeline_name = pipeline_name
