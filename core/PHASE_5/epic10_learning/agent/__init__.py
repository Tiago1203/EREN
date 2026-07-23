"""
PHASE 5 - EPIC 10: Agent Learning & Optimization

Motor de aprendizaje y optimización para agentes.
Optimiza continuamente el comportamiento de los agentes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM PHASE 5 FOUNDATION
# =============================================================================

from core.PHASE_5.foundation import (
    BaseAgent,
    AgentType,
    AgentState,
)
from core.PHASE_5.foundation.domain import AgentTask, AgentResult

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
# IMPORTS FROM EPIC 10 ENGINES
# =============================================================================

from core.PHASE_5.epic10_learning.engines import (
    PerformanceAnalyzer,
    StrategyOptimizer,
    AgentEvaluator,
    CollaborationOptimizer,
)


# =============================================================================
# AGENT LEARNING CONFIG
# =============================================================================

@dataclass
class AgentLearningConfig:
    """Configuración del Agent Learning."""
    # Engines
    enable_performance_analyzer: bool = True
    enable_strategy_optimizer: bool = True
    enable_agent_evaluator: bool = True
    enable_collab_optimizer: bool = True
    
    # Comportamiento
    learning_interval_seconds: int = 300
    optimization_threshold: float = 0.7
    min_metrics_for_analysis: int = 5


# =============================================================================
# AGENT LEARNING ENGINE
# =============================================================================

class AgentLearningEngine(BaseAgent):
    """
    Motor de aprendizaje y optimización para agentes.
    
    Responsabilidades:
    - Analizar rendimiento de agentes
    - Optimizar estrategias
    - Evaluar agentes
    - Mejorar colaboración
    
    Hereda de BaseAgent para integrarse con el sistema de agentes.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: AgentLearningConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.LEARNING,
            name="Agent Learning Engine",
            description="Motor de aprendizaje y optimización para agentes",
        )
        
        self.config = config or AgentLearningConfig()
        
        # Inicializar motores
        self._performance_analyzer = PerformanceAnalyzer() if self.config.enable_performance_analyzer else None
        self._strategy_optimizer = StrategyOptimizer() if self.config.enable_strategy_optimizer else None
        self._agent_evaluator = AgentEvaluator() if self.config.enable_agent_evaluator else None
        self._collab_optimizer = CollaborationOptimizer() if self.config.enable_collab_optimizer else None
        
        # Sesiones de aprendizaje
        self._sessions: dict[str, LearningSession] = {}
        
        # Métricas acumuladas
        self._metrics_history: dict[str, list[AgentMetric]] = {}
        
        # Métricas
        self._analyses_performed = 0
        self._optimizations_performed = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el motor."""
        await super().initialize()
        logger.info(f"AgentLearningEngine {self.agent_id} initialized")
        logger.info(f"  - Performance Analyzer: {self._performance_analyzer is not None}")
        logger.info(f"  - Strategy Optimizer: {self._strategy_optimizer is not None}")
        logger.info(f"  - Agent Evaluator: {self._agent_evaluator is not None}")
        logger.info(f"  - Collaboration Optimizer: {self._collab_optimizer is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el motor."""
        await super().shutdown()
        logger.info(f"AgentLearningEngine {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de aprendizaje."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Obtener parámetros
            input_data = task.input_data
            action = input_data.get("action", "analyze")
            
            # Procesar según acción
            if action == "analyze":
                result = await self._handle_analyze(input_data)
            elif action == "optimize":
                result = await self._handle_optimize(input_data)
            elif action == "evaluate":
                result = await self._handle_evaluate(input_data)
            elif action == "collab_optimize":
                result = await self._handle_collab_optimize(input_data)
            elif action == "session":
                result = await self._handle_session(input_data)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.93,
            )
            
        except Exception as e:
            logger.error(f"AgentLearningEngine execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # ANALYZE HANDLERS
    # =============================================================================
    
    async def _handle_analyze(self, input_data: dict) -> dict:
        """Maneja análisis de rendimiento."""
        result = {"action": "analyze"}
        
        agent_id = input_data.get("agent_id", "")
        metrics_data = input_data.get("metrics", [])
        
        # Convertir métricas
        metrics = []
        for m_data in metrics_data:
            try:
                metric = AgentMetric(
                    agent_id=agent_id,
                    metric_type=MetricType(m_data.get("type", "performance")),
                    current_value=m_data.get("current_value", 0.0),
                    previous_value=m_data.get("previous_value", 0.0),
                    unit=m_data.get("unit", ""),
                )
                metrics.append(metric)
            except ValueError:
                pass
        
        # Analizar
        if self._performance_analyzer and metrics:
            analysis = await self._performance_analyzer.analyze(agent_id, metrics)
            
            result["agent_id"] = analysis.agent_id
            result["avg_performance"] = analysis.avg_performance
            result["metrics_count"] = len(analysis.metrics)
            
            self._analyses_performed += 1
            
            # Guardar métricas
            if agent_id not in self._metrics_history:
                self._metrics_history[agent_id] = []
            self._metrics_history[agent_id].extend(metrics)
        
        return result
    
    # =============================================================================
    # OPTIMIZE HANDLERS
    # =============================================================================
    
    async def _handle_optimize(self, input_data: dict) -> dict:
        """Maneja optimización."""
        result = {"action": "optimize"}
        
        agent_id = input_data.get("agent_id", "")
        current_strategy = input_data.get("strategy", {})
        performance_data = input_data.get("performance_data", {})
        
        if self._strategy_optimizer:
            opt_result = await self._strategy_optimizer.optimize(
                agent_id=agent_id,
                current_strategy=current_strategy,
                performance_data=performance_data,
            )
            
            result["optimization_id"] = opt_result.optimization_id
            result["success"] = opt_result.success
            result["recommendations_count"] = len(opt_result.recommendations)
            result["expected_improvement"] = opt_result.expected_improvement
            
            self._optimizations_performed += 1
        
        return result
    
    # =============================================================================
    # EVALUATE HANDLERS
    # =============================================================================
    
    async def _handle_evaluate(self, input_data: dict) -> dict:
        """Maneja evaluación de agente."""
        result = {"action": "evaluate"}
        
        agent_id = input_data.get("agent_id", "")
        metrics_data = input_data.get("metrics", [])
        
        # Convertir métricas
        metrics = []
        for m_data in metrics_data:
            try:
                metric = AgentMetric(
                    agent_id=agent_id,
                    metric_type=MetricType(m_data.get("type", "performance")),
                    current_value=m_data.get("current_value", 0.0),
                )
                metrics.append(metric)
            except ValueError:
                pass
        
        # Obtener métricas anteriores
        previous_metrics = self._metrics_history.get(agent_id, [])
        
        if self._agent_evaluator:
            eval_result = await self._agent_evaluator.evaluate(
                agent_id=agent_id,
                metrics=metrics,
                previous_metrics=previous_metrics[-10:] if previous_metrics else None,
            )
            
            result["agent_id"] = eval_result.agent_id
            result["overall_score"] = eval_result.overall_score
            result["performance_score"] = eval_result.performance_score
            result["collaboration_score"] = eval_result.collaboration_score
            result["learning_score"] = eval_result.learning_score
            result["comparison_with_previous"] = eval_result.comparison_with_previous
        
        return result
    
    # =============================================================================
    # COLLAB OPTIMIZE HANDLERS
    # =============================================================================
    
    async def _handle_collab_optimize(self, input_data: dict) -> dict:
        """Maneja optimización de colaboración."""
        result = {"action": "collab_optimize"}
        
        agent_ids = input_data.get("agent_ids", [])
        collaboration_data = input_data.get("collaboration_data", {})
        
        if self._collab_optimizer:
            opt_result = await self._collab_optimizer.optimize(
                agent_ids=agent_ids,
                collaboration_data=collaboration_data,
            )
            
            result["agents_count"] = len(opt_result.agents_involved)
            result["improvements"] = opt_result.collaboration_improvements
            result["improvement_score"] = opt_result.improvement_score
        
        return result
    
    # =============================================================================
    # SESSION HANDLERS
    # =============================================================================
    
    async def _handle_session(self, input_data: dict) -> dict:
        """Maneja sesiones de aprendizaje."""
        result = {"action": "session"}
        operation = input_data.get("operation", "create")
        
        if operation == "create":
            session = LearningSession(
                agent_id=input_data.get("agent_id", ""),
                description=input_data.get("description", ""),
            )
            self._sessions[session.session_id] = session
            result["session_id"] = session.session_id
            result["status"] = session.status.value
        
        elif operation == "start":
            session_id = input_data.get("session_id")
            if session_id in self._sessions:
                self._sessions[session_id].start()
                result["status"] = SessionStatus.RUNNING.value
        
        elif operation == "complete":
            session_id = input_data.get("session_id")
            if session_id in self._sessions:
                self._sessions[session_id].complete()
                result["status"] = SessionStatus.COMPLETED.value
        
        return result
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del motor."""
        return {
            "analyses_performed": self._analyses_performed,
            "optimizations_performed": self._optimizations_performed,
            "active_sessions": len([s for s in self._sessions.values() if s.status == SessionStatus.RUNNING]),
            "engines_enabled": {
                "performance_analyzer": self._performance_analyzer is not None,
                "strategy_optimizer": self._strategy_optimizer is not None,
                "agent_evaluator": self._agent_evaluator is not None,
                "collab_optimizer": self._collab_optimizer is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AgentLearningEngine",
    "AgentLearningConfig",
]
