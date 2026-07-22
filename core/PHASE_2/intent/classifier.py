"""Deterministic, rule-based intent classifier.

This is the **first real classifier** in EREN — but it uses **no AI/LLM**. It
scores the input against a per-intent keyword lexicon and picks the best match.
Behavior is deterministic and explainable (it reports the matched terms), which
suits auditing and testing.

It implements the :class:`~core.intent.interfaces.IntentClassifier` contract, so
it can later be swapped for an LLM-backed classifier via dependency injection
without changing the engine.
"""

from __future__ import annotations

from core.PHASE_2.context import CognitiveContext
from core.PHASE_2.intent.interfaces import IntentClassifier
from core.PHASE_2.intent.models import IntentResult, IntentType

# Per-intent keyword lexicon (bilingual ES/EN). Data-driven on purpose: adding
# or tuning intents means editing this table, not writing conditional branches.
DEFAULT_LEXICON: dict[IntentType, tuple[str, ...]] = {
    IntentType.DIAGNOSTIC_REQUEST: (
        "falla",
        "fallo",
        "avería",
        "averia",
        "no enciende",
        "no funciona",
        "no prende",
        "error",
        "problema",
        "síntoma",
        "sintoma",
        "reparar",
        "diagnóstico",
        "diagnostico",
        "diagnosticar",
        "fault",
        "broken",
        "not working",
        "troubleshoot",
        "malfunction",
        "issue",
    ),
    IntentType.MAINTENANCE_HISTORY: (
        "mantenimiento",
        "historial",
        "histórico",
        "historico",
        "última revisión",
        "ultima revision",
        "preventivo",
        "correctivo",
        "registro",
        "bitácora",
        "bitacora",
        "maintenance",
        "history",
        "serviced",
        "last service",
        "log",
        "record",
    ),
    IntentType.REGULATION_QUERY: (
        "norma",
        "normativa",
        "regulación",
        "regulacion",
        "estándar",
        "estandar",
        "cumplimiento",
        "protocolo",
        "ley",
        "requisito legal",
        "regulation",
        "standard",
        "compliance",
        "iso",
        "iec",
        "fda",
    ),
    IntentType.DEVICE_QUERY: (
        "equipo",
        "dispositivo",
        "aparato",
        "especificaciones",
        "especificación",
        "especificacion",
        "manual",
        "modelo",
        "fabricante",
        "ventilador",
        "monitor",
        "bomba",
        "desfibrilador",
        "device",
        "equipment",
        "specifications",
        "specs",
        "manufacturer",
        "model",
    ),
    IntentType.GENERAL_CHAT: (
        "hola",
        "buenos días",
        "buenos dias",
        "buenas tardes",
        "gracias",
        "cómo estás",
        "como estas",
        "qué tal",
        "que tal",
        "hello",
        "hi",
        "hey",
        "thanks",
        "thank you",
        "good morning",
    ),
}

# Deterministic tie-break order (clinical priority first).
_PRIORITY: tuple[IntentType, ...] = (
    IntentType.DIAGNOSTIC_REQUEST,
    IntentType.MAINTENANCE_HISTORY,
    IntentType.REGULATION_QUERY,
    IntentType.DEVICE_QUERY,
    IntentType.GENERAL_CHAT,
)


class RuleBasedIntentClassifier(IntentClassifier):
    """Keyword-scoring classifier. No AI. Deterministic and explainable."""

    def __init__(
        self, lexicon: dict[IntentType, tuple[str, ...]] | None = None
    ) -> None:
        self._lexicon = lexicon if lexicon is not None else DEFAULT_LEXICON

    def classify(self, text: str, context: CognitiveContext) -> IntentResult:
        normalized = text.strip().lower()
        if not normalized:
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                rationale="Empty input.",
            )

        matches: dict[IntentType, list[str]] = {
            intent: [term for term in terms if term in normalized]
            for intent, terms in self._lexicon.items()
        }
        total = sum(len(m) for m in matches.values())
        if total == 0:
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                rationale="No known terms matched.",
            )

        best = max(
            _PRIORITY,
            key=lambda intent: (len(matches.get(intent, [])), -_PRIORITY.index(intent)),
        )
        matched_terms = matches[best]
        confidence = round(len(matched_terms) / total, 2)
        return IntentResult(
            intent=best,
            confidence=confidence,
            matched_terms=matched_terms,
            rationale=f"Matched {len(matched_terms)} term(s) for {best.value}.",
        )
