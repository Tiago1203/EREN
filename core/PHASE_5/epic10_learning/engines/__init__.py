"""
PHASE 5 - EPIC 10: Learning Engines

Motores especializados para aprendizaje:
- PerformanceAnalyzer
- StrategyOptimizer
- AgentEvaluator
- CollaborationOptimizer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM EPIC 10 DOMAIN
# =============================================================================

from core.PHASE_5.epic10_learning.domain import (
    AgentMetric,
    MetricType,
    LearningSession,
    SessionStatus,
    OptimizationReport,
    OptimizationType,
    Recommendation,
)


# =============================================================================
# RESULT CLASSES
# =============================================================================

@dataclass
class AnalysisResult:
    """Resultado de análisis."""
    agent_id: str
    
    # Métricas
    metrics: list[AgentMetric] = field(default_factory=list)
    
    # Stats
    avg_performance: float = 0.0
    best_metric: AgentMetric | None = None
    worst_metric: AgentMetric | None = None
    
    # Metadatos
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class OptimizationResult:
    """Resultado de optimización."""
    optimization_id: str
    
    # Resultado
    success: bool = False
    recommendations: list[Recommendation] = field(default_factory=list)
    
    # Impacto
    expected_improvement: float = 0.0
    
    # Metadatos
    optimized_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class EvaluationResult:
    """Resultado de evaluación."""
    agent_id: str
    
    # Score
    overall_score: float = 0.0
    
    # Detalles
    performance_score: float = 0.0
    collaboration_score: float = 0.0
    learning_score: float = 0.0
    
    # Comparación
    comparison_with_previous: float = 0.0
    
    # Metadatos
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CollabOptimizationResult:
    """Resultado de optimización de colaboración."""
    agents_involved: list[str]
    
    # Optimizaciones
    collaboration_improvements: list[str] = field(default_factory=list)
    
    # Impacto
    improvement_score: float = 0.0
    
    # Metadatos
    optimized_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# PERFORMANCE ANALYZER
# =============================================================================

class PerformanceAnalyzer:
    """
    Analizador de rendimiento.
    
    Responsabilidades:
    - Analizar métricas de agentes
    - Detectar tendencias
    - Identificar áreas de mejora
    """
    
    async def analyze(
        self,
        agent_id: str,
        metrics: list[AgentMetric],
    ) -> AnalysisResult:
        """
        Analiza el rendimiento de un agente.
        
        Args:
            agent_id: ID del agente
            metrics: Métricas a analizar
        
        Returns:
            AnalysisResult con el análisis
        """
        logger.info(f"Analyzing performance for agent {agent_id}")
        
        if not metrics:
            return AnalysisResult(agent_id=agent_id)
        
        # Calcular promedio
        avg_perf = sum(m.current_value for m in metrics) / len(metrics)
        
        # Encontrar mejor y peor
        best = max(metrics, key=lambda m: m.current_value)
        worst = min(metrics, key=lambda m: m.current_value)
        
        return AnalysisResult(
            agent_id=agent_id,
            metrics=metrics,
            avg_performance=avg_perf,
            best_metric=best,
            worst_metric=worst,
        )
    
    async def detect_anomalies(
        self,
        metrics: list[AgentMetric],
    ) -> list[AgentMetric]:
        """Detecta anomalías en métricas."""
        if len(metrics) < 2:
            return []
        
        avg = sum(m.current_value for m in metrics) / len(metrics)
        anomalies = []
        
        for metric in metrics:
            if abs(metric.current_value - avg) > avg * 0.3:
                anomalies.append(metric)
        
        return anomalies


# =============================================================================
# STRATEGY OPTIMIZER
# =============================================================================

class StrategyOptimizer:
    """
    Optimizador de estrategias.
    
    Responsabilidades:
    - Optimizar estrategias de agentes
    - Proponer cambios
    - Validar optimizaciones
    """
    
    async def optimize(
        self,
        agent_id: str,
        current_strategy: dict,
        performance_data: dict,
    ) -> OptimizationResult:
        """
        Optimiza la estrategia de un agente.
        
        Args:
            agent_id: ID del agente
            current_strategy: Estrategia actual
            performance_data: Datos de rendimiento
        
        Returns:
            OptimizationResult con el resultado
        """
        logger.info(f"Optimizing strategy for agent {agent_id}")
        
        recommendations = []
        
        # Analizar y proponer mejoras
        if performance_data.get("response_time", 0) > 5.0:
            recommendations.append(Recommendation(
                title="Improve Response Time",
                description="Optimize prompt templates and retrieval",
                expected_impact=0.3,
                priority=8,
            ))
        
        if performance_data.get("accuracy", 0) < 0.8:
            recommendations.append(Recommendation(
                title="Improve Accuracy",
                description="Increase evidence retrieval quality",
                expected_impact=0.4,
                priority=9,
            ))
        
        # Calcular impacto esperado
        expected = sum(r.expected_impact for r in recommendations) / max(len(recommendations), 1)
        
        return OptimizationResult(
            optimization_id=f"opt_{agent_id}",
            success=True,
            recommendations=recommendations,
            expected_improvement=expected,
        )
    
    async def apply_recommendation(
        self,
        recommendation: Recommendation,
        current_config: dict,
    ) -> dict:
        """Aplica una recomendación."""
        # Placeholder - en producción aplicaría cambios
        recommendation.implement()
        return current_config


# =============================================================================
# AGENT EVALUATOR
# =============================================================================

class AgentEvaluator:
    """
    Evaluador de agentes.
    
    Responsabilidades:
    - Evaluar rendimiento de agentes
    - Comparar con agentes similares
    - Generar scores
    """
    
    async def evaluate(
        self,
        agent_id: str,
        metrics: list[AgentMetric],
        previous_metrics: list[AgentMetric] | None = None,
    ) -> EvaluationResult:
        """
        Evalúa un agente.
        
        Args:
            agent_id: ID del agente
            metrics: Métricas actuales
            previous_metrics: Métricas anteriores
        
        Returns:
            EvaluationResult con la evaluación
        """
        logger.info(f"Evaluating agent {agent_id}")
        
        # Calcular scores por tipo
        perf_metrics = [m for m in metrics if m.metric_type == MetricType.PERFORMANCE]
        collab_metrics = [m for m in metrics if m.metric_type == MetricType.COLLABORATION]
        learn_metrics = [m for m in metrics if m.metric_type == MetricType.LEARNING]
        
        perf_score = sum(m.current_value for m in perf_metrics) / max(len(perf_metrics), 1)
        collab_score = sum(m.current_value for m in collab_metrics) / max(len(collab_metrics), 1)
        learn_score = sum(m.current_value for m in learn_metrics) / max(len(learn_metrics), 1)
        
        # Score general
        overall = (perf_score * 0.5) + (collab_score * 0.3) + (learn_score * 0.2)
        
        # Comparación con anterior
        comparison = 0.0
        if previous_metrics:
            prev_overall = sum(m.current_value for m in previous_metrics) / max(len(previous_metrics), 1)
            comparison = ((overall - prev_overall) / prev_overall) * 100 if prev_overall > 0 else 0
        
        return EvaluationResult(
            agent_id=agent_id,
            overall_score=overall,
            performance_score=perf_score,
            collaboration_score=collab_score,
            learning_score=learn_score,
            comparison_with_previous=comparison,
        )


# =============================================================================
# COLLABORATION OPTIMIZER
# =============================================================================

class CollaborationOptimizer:
    """
    Optimizador de colaboración.
    
    Responsabilidades:
    - Optimizar patrones de colaboración
    - Mejorar comunicación entre agentes
    - Reducir conflictos
    """
    
    async def optimize(
        self,
        agent_ids: list[str],
        collaboration_data: dict,
    ) -> CollabOptimizationResult:
        """
        Optimiza la colaboración entre agentes.
        
        Args:
            agent_ids: IDs de agentes
            collaboration_data: Datos de colaboración
        
        Returns:
            CollabOptimizationResult con el resultado
        """
        logger.info(f"Optimizing collaboration for {len(agent_ids)} agents")
        
        improvements = []
        
        # Analizar patrones de comunicación
        if collaboration_data.get("message_count", 0) > 100:
            improvements.append("Reduce message overhead by batching")
        
        if collaboration_data.get("conflict_count", 0) > 5:
            improvements.append("Implement better conflict resolution")
        
        if collaboration_data.get("response_time", 0) > 10.0:
            improvements.append("Optimize messaging protocols")
        
        # Calcular score
        base_score = 0.7
        penalty = len(improvements) * 0.05
        score = max(0.0, min(1.0, base_score - penalty))
        
        return CollabOptimizationResult(
            agents_involved=agent_ids,
            collaboration_improvements=improvements,
            improvement_score=score,
        )
    
    async def suggest_role_adjustments(
        self,
        agent_ids: list[str],
        performance_data: dict,
    ) -> list[dict]:
        """Sugiere ajustes de roles."""
        suggestions = []
        
        for agent_id in agent_ids:
            perf = performance_data.get(agent_id, {})
            
            if perf.get("overloaded", False):
                suggestions.append({
                    "agent_id": agent_id,
                    "suggestion": "redistribute_tasks",
                    "reason": "Agent is overloaded",
                })
            
            if perf.get("underutilized", False):
                suggestions.append({
                    "agent_id": agent_id,
                    "suggestion": "assign_more_tasks",
                    "reason": "Agent has capacity",
                })
        
        return suggestions


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Result classes
    "AnalysisResult",
    "OptimizationResult",
    "EvaluationResult",
    "CollabOptimizationResult",
    # Engines
    "PerformanceAnalyzer",
    "StrategyOptimizer",
    "AgentEvaluator",
    "CollaborationOptimizer",
]
