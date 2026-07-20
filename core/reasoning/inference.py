"""Inference Engine for EREN Cognitive Reasoning Platform.

Applies reasoning strategies, inferences, rules, and logic.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from core.reasoning.reasoning_types import (
    ConfidenceScore,
    InferenceType,
)

if TYPE_CHECKING:
    pass


class InferenceEngine:
    """Applies reasoning strategies and inference.

    The Inference Engine does NOT:
    - Collect evidence
    - Generate hypotheses
    - Make decisions

    It ONLY:
    - Applies strategies
    - Performs inferences
    - Applies rules
    - Applies logic
    """

    def __init__(self):
        """Initialize inference engine."""
        self._strategies: dict[InferenceType, Callable] = {}
        self._rules: list[Callable] = []

    def register_strategy(
        self,
        inference_type: InferenceType,
        strategy: Callable,
    ) -> None:
        """Register an inference strategy.

        Args:
            inference_type: Type of inference.
            strategy: Strategy function.
        """
        self._strategies[inference_type] = strategy

    def add_rule(self, rule: Callable) -> None:
        """Add a rule.

        Args:
            rule: Rule function.
        """
        self._rules.append(rule)

    def infer(
        self,
        inference_type: InferenceType,
        premises: dict,
        context: dict | None = None,
    ) -> dict:
        """Perform inference.

        Args:
            inference_type: Type of inference.
            premises: Premise data.
            context: Optional context.

        Returns:
            Inference result.
        """
        strategy = self._strategies.get(inference_type)

        if strategy:
            return strategy(premises, context or {})

        return {
            "inference_type": inference_type.value,
            "conclusion": None,
            "confidence": ConfidenceScore(value=0.5),
        }

    def deduct(
        self,
        premises: dict,
        context: dict | None = None,
    ) -> dict:
        """Perform deductive inference.

        Args:
            premises: Premise data.
            context: Optional context.

        Returns:
            Deduction result.
        """
        return self.infer(InferenceType.DEDUCTIVE, premises, context)

    def induce(
        self,
        premises: dict,
        context: dict | None = None,
    ) -> dict:
        """Perform inductive inference.

        Args:
            premises: Premise data.
            context: Optional context.

        Returns:
            Induction result.
        """
        return self.infer(InferenceType.INDUCTIVE, premises, context)

    def abduce(
        self,
        premises: dict,
        context: dict | None = None,
    ) -> dict:
        """Perform abductive inference.

        Args:
            premises: Premise data.
            context: Optional context.

        Returns:
            Abduction result.
        """
        return self.infer(InferenceType.ABDUCTIVE, premises, context)

    def apply_rules(
        self,
        data: dict,
    ) -> list[dict]:
        """Apply all registered rules.

        Args:
            data: Data to apply rules to.

        Returns:
            List of rule results.
        """
        results = []

        for rule in self._rules:
            try:
                result = rule(data)
                if result:
                    results.append(result)
            except Exception:
                pass

        return results


# Global inference engine
_inference_engine: InferenceEngine | None = None
_inference_lock = __import__("threading").Lock()


def get_inference_engine() -> InferenceEngine:
    """Get the global inference engine."""
    global _inference_engine
    with _inference_lock:
        if _inference_engine is None:
            _inference_engine = InferenceEngine()
        return _inference_engine


def reset_inference_engine() -> None:
    """Reset the global inference engine."""
    global _inference_engine
    with _inference_lock:
        _inference_engine = None
