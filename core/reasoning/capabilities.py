"""Capabilities registration for the Cognitive Reasoning Engine.

Provides automatic capability registration to the Capability Registry.

Architecture only -- no AI, no business logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Reasoning Capabilities
# =============================================================================

REASONING_CAPABILITIES = [
    # Analysis capabilities
    {
        "id": "reasoning.analyze",
        "name": "Analyze Evidence",
        "description": "Analyze and evaluate evidence for reasoning",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.compare",
        "name": "Compare Hypotheses",
        "description": "Compare multiple hypotheses by confidence and evidence",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.rank",
        "name": "Rank Hypotheses",
        "description": "Rank hypotheses by probability and confidence",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.validate",
        "name": "Validate Reasoning",
        "description": "Validate reasoning chain and conclusions",
        "category": "reasoning",
        "version": "1.0.0",
    },
    # Hypothesis capabilities
    {
        "id": "reasoning.hypothesis.generate",
        "name": "Generate Hypotheses",
        "description": "Generate potential hypotheses from evidence",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.hypothesis.evaluate",
        "name": "Evaluate Hypothesis",
        "description": "Evaluate a hypothesis against evidence",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.hypothesis.confirm",
        "name": "Confirm Hypothesis",
        "description": "Mark a hypothesis as confirmed",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.hypothesis.reject",
        "name": "Reject Hypothesis",
        "description": "Mark a hypothesis as rejected",
        "category": "reasoning",
        "version": "1.0.0",
    },
    # Evidence capabilities
    {
        "id": "reasoning.evidence.collect",
        "name": "Collect Evidence",
        "description": "Collect and store evidence",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.evidence.incorporate",
        "name": "Incorporate Evidence",
        "description": "Incorporate evidence into hypothesis evaluation",
        "category": "reasoning",
        "version": "1.0.0",
    },
    # Decision capabilities
    {
        "id": "reasoning.decision.generate",
        "name": "Generate Decision",
        "description": "Generate a decision from reasoning",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.decision.justify",
        "name": "Justify Decision",
        "description": "Provide justification for a decision",
        "category": "reasoning",
        "version": "1.0.0",
    },
    # Trace capabilities
    {
        "id": "reasoning.trace",
        "name": "Generate Reasoning Trace",
        "description": "Generate complete reasoning trace",
        "category": "reasoning",
        "version": "1.0.0",
    },
    {
        "id": "reasoning.trace.export",
        "name": "Export Reasoning Trace",
        "description": "Export reasoning trace for audit",
        "category": "reasoning",
        "version": "1.0.0",
    },
]


def get_reasoning_capabilities() -> list[dict]:
    """Get all reasoning capabilities.
    
    Returns:
        List of capability definitions.
    """
    return list(REASONING_CAPABILITIES)
