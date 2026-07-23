"""
PHASE 5 - EPIC 10: Learning Domain Objects

Domain objects especializados para aprendizaje:
- AgentMetric
- LearningSession
- OptimizationReport
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class MetricType(str, Enum):
    """Tipos de métrica."""
    PERFORMANCE = "performance"       # Rendimiento
    ACCURACY = "accuracy"           # Precisión
    RESPONSE_TIME = "response_time" # Tiempo de respuesta
    COLLABORATION = "collaboration" # Colaboración
    LEARNING = "learning"           # Aprendizaje


class SessionStatus(str, Enum):
    """Estado de sesión de aprendizaje."""
    PENDING = "pending"           # Pendiente
    RUNNING = "running"         # En ejecución
    COMPLETED = "completed"      # Completada
    FAILED = "failed"           # Fallida
    PAUSED = "paused"          # Pausada


class OptimizationType(str, Enum):
    """Tipos de optimización."""
    STRATEGY = "strategy"         # Estrategia
    PARAMETER = "parameter"       # Parámetro
    COLLABORATION = "collaboration"  # Colaboración
    RESOURCE = "resource"         # Recurso


# =============================================================================
# METRIC VALUE
# =============================================================================

@dataclass
class MetricValue:
    """Valor de métrica."""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# AGENT METRIC
# =============================================================================

@dataclass
class AgentMetric:
    """Métrica de agente."""
    metric_id: str = ""
    agent_id: str = ""
    
    # Tipo y valor
    metric_type: MetricType = MetricType.PERFORMANCE
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
        if self.current_value > self.previous_value * 1.05:
            return "improving"
        elif self.current_value < self.previous_value * 0.95:
            return "declining"
        else:
            return "stable"
    
    def get_change_percentage(self) -> float:
        """Obtiene el porcentaje de cambio."""
        if self.previous_value == 0:
            return 0.0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100


# =============================================================================
# LEARNING SESSION
# =============================================================================

@dataclass
class LearningSession:
    """Sesión de aprendizaje."""
    session_id: str = ""
    agent_id: str = ""
    
    # Descripción
    description: str = ""
    
    # Estado
    status: SessionStatus = SessionStatus.PENDING
    
    # Métricas
    metrics: list[AgentMetric] = field(default_factory=list)
    
    # Resultados
    improvements: list[str] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
    
    def start(self) -> None:
        """Inicia la sesión."""
        self.status = SessionStatus.RUNNING
        self.started_at = datetime.now(UTC)
    
    def complete(self) -> None:
        """Completa la sesión."""
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
    
    def add_metric(self, metric: AgentMetric) -> None:
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


# =============================================================================
# RECOMMENDATION
# =============================================================================

@dataclass
class Recommendation:
    """Recomendación de optimización."""
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
    
    def __post_init__(self):
        if not self.recommendation_id:
            self.recommendation_id = str(uuid.uuid4())
    
    def implement(self) -> None:
        """Marca como implementada."""
        self.implemented = True
        self.implemented_at = datetime.now(UTC)


# =============================================================================
# OPTIMIZATION REPORT
# =============================================================================

@dataclass
class OptimizationReport:
    """Reporte de optimización."""
    report_id: str = ""
    session_id: str = ""
    
    # Análisis
    analysis_summary: str = ""
    
    # Métricas
    metrics_analyzed: int = 0
    metrics_improved: int = 0
    
    # Recomendaciones
    recommendations: list[Recommendation] = field(default_factory=list)
    
    # Resultados
    overall_improvement: float = 0.0  # 0.0 - 1.0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.report_id:
            self.report_id = str(uuid.uuid4())
        self.metrics_improved = len([r for r in self.recommendations if r.implemented])
    
    def add_recommendation(self, recommendation: Recommendation) -> None:
        """Agrega una recomendación."""
        self.recommendations.append(recommendation)
        self.metrics_analyzed = len(self.recommendations)
        self.metrics_improved = len([r for r in self.recommendations if r.implemented])
    
    def get_top_recommendations(self, count: int = 5) -> list[Recommendation]:
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
    "MetricType",
    "SessionStatus",
    "OptimizationType",
    # Domain Objects
    "MetricValue",
    "AgentMetric",
    "LearningSession",
    "Recommendation",
    "OptimizationReport",
]
