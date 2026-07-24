"""
EPIC 14: Uncertainty Quantification Model

Este módulo implementa el Uncertainty Quantification Model que proporciona:
- UncertaintyQuantifier: Cuantifica incertidumbre
- ConfidenceCalibrator: Calibra confianza
- UncertaintyPropagator: Propaga incertidumbre
- UncertaintyCommunicator: Comunica incertidumbre
- UncertaintySourceDetector: Detecta fuentes de incertidumbre

Dependencias:
- FASE 3: Clinical Intelligence (Confidence, Reasoning)

Consumido por:
- EPIC 2-6: Agentes clínicos
- EPIC 8: Consensus Engine
"""

from core.PHASE_5.epic14_uncertainty.domain import (
    Uncertainty,
    ConfidenceLevel,
    UncertaintySource,
    UncertaintyPropagation,
    UncertaintyStatement,
    UncertaintyType,
    UncertaintyConfig,
)

from core.PHASE_5.epic14_uncertainty.agent import UncertaintyAgent

__all__ = [
    "Uncertainty",
    "ConfidenceLevel",
    "UncertaintySource",
    "UncertaintyPropagation",
    "UncertaintyStatement",
    "UncertaintyType",
    "UncertaintyConfig",
    "UncertaintyAgent",
]

__version__ = "2.0.0"
