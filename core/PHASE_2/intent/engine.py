"""Intent Engine — EREN's first real cognitive engine.

Pipeline (no AI): **receive** a `CognitiveContext` → **analyze** its input →
**classify** the intent → **update** the context → **return** it.

Classification is delegated to an injected :class:`IntentClassifier`
(Dependency Injection). It defaults to the deterministic
:class:`RuleBasedIntentClassifier`, and can be replaced by an LLM-backed
classifier later without changing this engine.

The engine satisfies the `CognitiveEngine` contract (`name`, `describe`) and the
`IntentPort` capability.
"""

from __future__ import annotations

from core.PHASE_2.context import CognitiveContext
from core.PHASE_2.intent.classifier import RuleBasedIntentClassifier
from core.PHASE_2.intent.interfaces import IntentClassifier
from core.PHASE_2.intent.models import IntentResult

ENGINE_NAME = "intent"


class IntentEngine:
    """Classifies the intent of an interaction and enriches the context."""

    def __init__(self, classifier: IntentClassifier | None = None) -> None:
        self._classifier: IntentClassifier = classifier or RuleBasedIntentClassifier()

    @property
    def name(self) -> str:
        return ENGINE_NAME

    def describe(self) -> str:
        return (
            "Classifies the user's intent from the input (rule-based today, LLM-ready)."
        )

    def classify_intent(self, context: CognitiveContext) -> CognitiveContext:
        """Receive, analyze, classify, update and return the context."""
        text = (
            context.conversation.normalized_input or context.conversation.original_input
        )
        result: IntentResult = self._classifier.classify(text, context)

        context.cognitive_state.detected_intent = result.intent.value
        context.cognitive_state.confidence = result.confidence
        if ENGINE_NAME not in context.cognitive_state.executed_engines:
            context.cognitive_state.executed_engines.append(ENGINE_NAME)
        return context
