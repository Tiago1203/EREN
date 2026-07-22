"""Models for EREN's Intent Engine.

Declarative Pydantic v2 models: the intent taxonomy (:class:`IntentType`) and the
classification outcome (:class:`IntentResult`). No AI here — these only describe
*what* an intent classification looks like.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IntentType(str, Enum):
    """Intents the Intent Engine can recognize (initial taxonomy)."""

    DEVICE_QUERY = "device_query"
    DIAGNOSTIC_REQUEST = "diagnostic_request"
    MAINTENANCE_HISTORY = "maintenance_history"
    REGULATION_QUERY = "regulation_query"
    GENERAL_CHAT = "general_chat"
    UNKNOWN = "unknown"


class IntentResult(BaseModel):
    """Outcome of classifying one input.

    Carries an explainable trail (`matched_terms`, `rationale`) so the decision
    can be audited — a first-class requirement in EREN.
    """

    model_config = ConfigDict(extra="forbid")

    intent: IntentType = Field(
        default=IntentType.UNKNOWN, description="The classified intent."
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the classification (0.0–1.0).",
    )
    matched_terms: list[str] = Field(
        default_factory=list,
        description="Terms that contributed to the decision (explainability).",
    )
    rationale: str = Field(
        default="", description="Short human-readable explanation of the decision."
    )
