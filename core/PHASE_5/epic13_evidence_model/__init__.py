"""
EPIC 13: Evidence Lifecycle Model

Este módulo implementa el Evidence Lifecycle Model que proporciona:
- EvidenceRetriever: Recupera evidencia de literatura, guías, casos
- EvidenceEvaluator: Evalúa calidad (GRADE), relevancia, aplicabilidad
- EvidenceSynthesizer: Sintetiza múltiples evidencias
- EvidenceVersioner: Versiona evidencia para trazabilidad
- EvidenceTracer: Traza uso de evidencia en decisiones

Dependencias:
- FASE 3: Clinical Intelligence
- FASE 4: Knowledge Platform

Consumido por:
- EPIC 2-6: Agentes clínicos
- EPIC 8: Consensus Engine
- EPIC 14: Uncertainty Quantification
"""

from core.PHASE_5.epic13_evidence_model.domain import (
    Evidence,
    EvidenceBundle,
    EvidenceQuality,
    EvidenceSource,
    EvidenceCitation,
    EvidenceType,
    QualityLevel,
    EvidenceConfig,
)

from core.PHASE_5.epic13_evidence_model.agent import EvidenceLifecycleAgent

__all__ = [
    "Evidence",
    "EvidenceBundle",
    "EvidenceQuality",
    "EvidenceSource",
    "EvidenceCitation",
    "EvidenceType",
    "QualityLevel",
    "EvidenceConfig",
    "EvidenceLifecycleAgent",
]

__version__ = "2.0.0"
