"""
EPIC 12: Clinical Context Builder

Este módulo implementa el Clinical Context Builder que proporciona:
- PatientContextBuilder: Construye contexto de paciente
- DeviceContextBuilder: Construye contexto de dispositivo
- HospitalContextBuilder: Construye contexto hospitalario
- ClinicalContextAggregator: Agrega contextos en contexto clínico unificado
- ContextLifecycleManager: Gestiona ciclo de vida del contexto

Dependencias:
- FASE 1: Business Domain (Device, Incident, Knowledge, Asset, Hospital)
- FASE 2: Cognitive Operating System (Memory, Context)
- FASE 3: Clinical Intelligence (Reasoning, Evidence, Decision)
- FASE 4: Knowledge Platform (RAG, Embeddings)

Consumido por:
- EPIC 2-6: Agentes clínicos
- EPIC 8: Consensus Engine
- EPIC 13: Evidence Lifecycle Model
"""

from core.PHASE_5.epic12_clinical_context.domain import (
    ClinicalContext,
    PatientContext,
    DeviceContext,
    HospitalContext,
    ClinicalContextConfig,
)

from core.PHASE_5.epic12_clinical_context.agent import ClinicalContextAgent

__all__ = [
    "ClinicalContext",
    "PatientContext",
    "DeviceContext",
    "HospitalContext",
    "ClinicalContextConfig",
    "ClinicalContextAgent",
]

__version__ = "2.0.0"
