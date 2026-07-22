"""Contract for the diagnostic capability."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.PHASE_1.infrastructure.contracts.base import CognitiveEngine


@runtime_checkable
class Diagnostic[Symptoms, Diagnosis](CognitiveEngine, Protocol):
    """Analyzes equipment faults and proposes justified hypotheses.

    Generic over the input symptoms and the produced diagnosis.
    """

    def diagnose(self, symptoms: Symptoms) -> Diagnosis:
        """Analyze *symptoms* and return a diagnosis with ranked hypotheses."""
        ...
