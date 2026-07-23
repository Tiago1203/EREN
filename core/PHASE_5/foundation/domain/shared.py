"""
PHASE 5 - EPIC 0: Shared Domain Objects

Domain Objects compartidos por todos los EPICs para evitar duplicación.
Centraliza los objetos de dominio comunes.

Este módulo resuelve los problemas de duplicación DRY identificados:
- SessionStatus (era duplicado en EPIC 7 y 10)
- MetricType (era duplicado en EPIC 1 y 10)
- LearningSession (era duplicado en EPIC 1 y 10)
- AgentMetric (era duplicado en EPIC 1 y 10)
- OptimizationReport (era duplicado en EPIC 1 y 10)
- Recommendation (era duplicado en EPIC 1 y 10)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# SHARED ENUMS
# =============================================================================

class SharedSessionStatus(str, Enum):
    """Estado de sesión compartido por múltiples EPICs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class SharedMetricType(str, Enum):
    """Tipos de métrica compartidos."""
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    RESPONSE_TIME = "response_time"
    COLLABORATION = "collaboration"
    LEARNING = "learning"
    MEMORY = "memory"
    CONSENSUS = "consensus"


class SharedOptimizationType(str, Enum):
    """Tipos de optimización compartidos."""
    STRATEGY = "strategy"
    PARAMETER = "parameter"
    COLLABORATION = "collaboration"
    RESOURCE = "resource"


# =============================================================================
# SHARED VALUE OBJECTS
# =============================================================================

@dataclass
class SharedMetricValue:
    """Valor de métrica compartido."""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# SHARED AGENT METRIC
# =============================================================================

@dataclass
class SharedAgentMetric:
    """Métrica de agente compartida (evita duplicación EPIC 1, 10)."""
    metric_id: str = ""
    agent_id: str = ""
    
    # Tipo y valor
    metric_type: SharedMetricType = SharedMetricType.PERFORMANCE
    current_value: float = 0.0
    previous_value: float = 0.0
    
    # Detalles
    unit: str = ""
    description: str = ""
    
    # Tendencia
    trend: str = "stable"  # improving, declining, stable
    change_percentage: float = 0.0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.metric_id:
            self.metric_id = str(uuid.uuid4())
    
    def calculate_trend(self) -> str:
        """Calcula la tendencia."""
        if self.previous_value == 0:
            return "stable"
        change = ((self.current_value - self.previous_value) / self.previous_value) * 100
        if change > 5:
            return "improving"
        elif change < -5:
            return "declining"
        return "stable"
    
    def get_change_percentage(self) -> float:
        """Obtiene el porcentaje de cambio."""
        if self.previous_value == 0:
            return 0.0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100


# =============================================================================
# SHARED RECOMMENDATION
# =============================================================================

@dataclass
class SharedRecommendation:
    """Recomendación compartida (evita duplicación EPIC 1, 10)."""
    recommendation_id: str = ""
    
    # Descripción
    title: str = ""
    description: str = ""
    
    # Impacto
    expected_impact: float = 0.0  # 0.0 - 1.0
    priority: int = 5  # 1-10
    
    # Estado
    implemented: bool = False
    implemented_at: datetime | None = None
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source_epic: str = ""
    
    def __post_init__(self):
        if not self.recommendation_id:
            self.recommendation_id = str(uuid.uuid4())
    
    def implement(self) -> None:
        """Marca como implementada."""
        self.implemented = True
        self.implemented_at = datetime.now(UTC)


# =============================================================================
# SHARED LEARNING SESSION
# =============================================================================

@dataclass
class SharedLearningSession:
    """Sesión de aprendizaje compartida (evita duplicación EPIC 1, 10)."""
    session_id: str = ""
    agent_id: str = ""
    
    # Descripción
    description: str = ""
    
    # Estado
    status: SharedSessionStatus = SharedSessionStatus.PENDING
    
    # Métricas
    metrics: list[SharedAgentMetric] = field(default_factory=list)
    
    # Resultados
    improvements: list[str] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    recommendations: list[SharedRecommendation] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    def start(self) -> None:
        """Inicia la sesión."""
        self.status = SharedSessionStatus.RUNNING
        self.started_at = datetime.now(UTC)
    
    def complete(self) -> None:
        """Completa la sesión."""
        self.status = SharedSessionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
    
    def fail(self) -> None:
        """Marca como fallida."""
        self.status = SharedSessionStatus.FAILED
        self.completed_at = datetime.now(UTC)
    
    def add_metric(self, metric: SharedAgentMetric) -> None:
        """Agrega una métrica."""
        self.metrics.append(metric)
    
    def add_improvement(self, improvement: str) -> None:
        """Agrega una mejora."""
        if improvement not in self.improvements:
            self.improvements.append(improvement)
    
    def add_insight(self, insight: str) -> None:
        """Agrega un insight."""
        if insight not in self.insights:
            self.insights.append(insight)
    
    def add_recommendation(self, recommendation: SharedRecommendation) -> None:
        """Agrega una recomendación."""
        self.recommendations.append(recommendation)


# =============================================================================
# SHARED OPTIMIZATION REPORT
# =============================================================================

@dataclass
class SharedOptimizationReport:
    """Reporte de optimización compartido (evita duplicación EPIC 1, 10)."""
    report_id: str = ""
    session_id: str = ""
    
    # Análisis
    analysis_summary: str = ""
    
    # Métricas
    metrics_analyzed: int = 0
    metrics_improved: int = 0
    
    # Recomendaciones
    recommendations: list[SharedRecommendation] = field(default_factory=list)
    
    # Resultados
    overall_improvement: float = 0.0  # 0.0 - 1.0
    efficiency_gain: float = 0.0  # Porcentaje de mejora
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    generated_by: str = ""
    
    def __post_init__(self):
        if not self.report_id:
            self.report_id = str(uuid.uuid4())
        self.metrics_improved = len([r for r in self.recommendations if r.implemented])
    
    def add_recommendation(self, recommendation: SharedRecommendation) -> None:
        """Agrega una recomendación."""
        self.recommendations.append(recommendation)
        self.metrics_analyzed = len(self.recommendations)
        self.metrics_improved = len([r for r in self.recommendations if r.implemented])
    
    def get_top_recommendations(self, count: int = 5) -> list[SharedRecommendation]:
        """Obtiene las mejores recomendaciones."""
        sorted_recs = sorted(
            self.recommendations,
            key=lambda r: (r.priority, r.expected_impact),
            reverse=True,
        )
        return sorted_recs[:count]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "SharedSessionStatus",
    "SharedMetricType",
    "SharedOptimizationType",
    # Value Objects
    "SharedMetricValue",
    # Domain Objects
    "SharedAgentMetric",
    "SharedRecommendation",
    "SharedLearningSession",
    "SharedOptimizationReport",
]
