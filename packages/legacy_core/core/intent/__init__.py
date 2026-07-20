"""EREN Intent Engine.

The first real cognitive engine: classifies the intent of an interaction and
enriches the `CognitiveContext`. Rule-based today (no AI), designed so the
classifier can be replaced by an LLM later via dependency injection.
"""

from __future__ import annotations

from core.intent.classifier import DEFAULT_LEXICON, RuleBasedIntentClassifier
from core.intent.engine import IntentEngine
from core.intent.exceptions import ClassificationError, IntentError
from core.intent.interfaces import IntentClassifier, IntentPort
from core.intent.models import IntentResult, IntentType

__all__ = [
    "DEFAULT_LEXICON",
    "ClassificationError",
    "IntentClassifier",
    "IntentEngine",
    "IntentError",
    "IntentPort",
    "IntentResult",
    "IntentType",
    "RuleBasedIntentClassifier",
]
