"""Contract for the reasoning capability."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from core.contracts.base import CognitiveEngine


@runtime_checkable
class Reasoning[Question, Evidence, Conclusion](CognitiveEngine, Protocol):
    """Draws explainable conclusions from evidence.

    Generic over the question, the evidence items, and the conclusion. The
    conclusion is expected to carry an auditable justification — explainability
    is a first-class requirement in EREN.
    """

    def reason(self, question: Question, evidence: Sequence[Evidence]) -> Conclusion:
        """Return a conclusion for *question* justified by *evidence*."""
        ...
