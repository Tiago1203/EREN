"""Contracts for the Intent Engine.

Two abstractions keep the engine open to future change:

- :class:`IntentClassifier` — the *strategy* that turns text into an
  :class:`IntentResult`. The rule-based classifier implements it today; an
  LLM-backed classifier can implement the same contract tomorrow and be injected
  without touching :class:`~core.intent.engine.IntentEngine`.
- :class:`IntentPort` — the engine capability seen by consumers (the
  orchestrator): take a `CognitiveContext`, classify, and return it enriched.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.PHASE_2.context import CognitiveContext
from core.PHASE_2.intent.models import IntentResult


@runtime_checkable
class IntentClassifier(Protocol):
    """Strategy that classifies input text into an :class:`IntentResult`.

    Implementations must be side-effect free with respect to the context: they
    receive the (read-only) context for signals and return a result; updating
    the context is the engine's job.
    """

    def classify(self, text: str, context: CognitiveContext) -> IntentResult:
        """Classify ``text`` (using ``context`` for optional signals)."""
        ...


@runtime_checkable
class IntentPort(Protocol):
    """Intent Engine capability: enrich a context with the detected intent."""

    def classify_intent(self, context: CognitiveContext) -> CognitiveContext:
        """Analyze the context's input, classify it, update and return it."""
        ...
