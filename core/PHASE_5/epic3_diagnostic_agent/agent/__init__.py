"""
PHASE 5 - EPIC 3: Diagnostic Agent

Agente especializado en diagnóstico técnico.
Analiza fallas, genera hipótesis y construye diagnósticos.
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
    AgentCapability,
    AgentCapabilityVO,
    AgentState,
)
from core.PHASE_5.foundation.domain import AgentTask, AgentResult

# =============================================================================
# IMPORTS FROM EPIC 3 DOMAIN
# =============================================================================

from core.PHASE_5.epic3_diagnostic_agent.domain import (
    DiagnosticTask,
    DiagnosticTaskType,
    DiagnosticReport,
    DiagnosisConfidence,
)

# =============================================================================
# IMPORTS FROM EPIC 3 ENGINES
# =============================================================================

from core.PHASE_5.epic3_diagnostic_agent.engines import (
    FailureAnalyzer,
    RootCauseAnalyzer,
    DiagnosticPlanner,
    FaultCorrelator,
)


# =============================================================================
# DIAGNOSTIC AGENT CONFIG
# =============================================================================

@dataclass
class DiagnosticAgentConfig:
    """Configuración del Diagnostic Agent."""
    # Engines
    enable_failure_analyzer: bool = True
    enable_root_cause_analyzer: bool = True
    enable_diagnostic_planner: bool = True
    enable_fault_correlator: bool = True
    
    # Comportamiento
    default_timeout_seconds: int = 300
    max_hypotheses: int = 5
    
    # Calidad
    min_confidence_threshold: float = 0.7
    require_evidence: bool = True


# =============================================================================
# DIAGNOSTIC AGENT
# =============================================================================

class DiagnosticAgent(BaseAgent):
    """
    Agente especializado en diagnóstico técnico.
    
    Responsabilidades:
    - Analizar fallas de equipos médicos
    - Generar hipótesis diagnósticas
    - Identificar causa raíz
    - Construir planes de diagnóstico
    - Correlacionar eventos de falla
    
    Hereda de BaseAgent y utiliza los motores especializados.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: DiagnosticAgentConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.DIAGNOSTIC,
            name="Diagnostic Agent",
            description="Agente especializado en diagnóstico técnico",
        )
        
        self.config = config or DiagnosticAgentConfig()
        
        # Inicializar motores
        self._failure_analyzer = FailureAnalyzer() if self.config.enable_failure_analyzer else None
        self._root_cause_analyzer = RootCauseAnalyzer() if self.config.enable_root_cause_analyzer else None
        self._diagnostic_planner = DiagnosticPlanner() if self.config.enable_diagnostic_planner else None
        self._fault_correlator = FaultCorrelator() if self.config.enable_fault_correlator else None
        
        # Métricas
        self._diagnoses_completed = 0
        self._reports_generated = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el agente."""
        await super().initialize()
        logger.info(f"DiagnosticAgent {self.agent_id} initialized")
        logger.info(f"  - Failure Analyzer: {self._failure_analyzer is not None}")
        logger.info(f"  - Root Cause Analyzer: {self._root_cause_analyzer is not None}")
        logger.info(f"  - Diagnostic Planner: {self._diagnostic_planner is not None}")
        logger.info(f"  - Fault Correlator: {self._fault_correlator is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el agente."""
        await super().shutdown()
        logger.info(f"DiagnosticAgent {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de diagnóstico."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Crear tarea de diagnóstico
            diagnostic_task = self._create_diagnostic_task(task)
            
            # Procesar según tipo
            if diagnostic_task.task_type == DiagnosticTaskType.FAILURE_ANALYSIS:
                result = await self._analyze_failure(diagnostic_task)
            elif diagnostic_task.task_type == DiagnosticTaskType.ROOT_CAUSE:
                result = await self._analyze_root_cause(diagnostic_task)
            elif diagnostic_task.task_type == DiagnosticTaskType.PREDICTIVE:
                result = await self._predictive_diagnosis(diagnostic_task)
            elif diagnostic_task.task_type == DiagnosticTaskType.CORRELATION:
                result = await self._correlate_faults(diagnostic_task)
            elif diagnostic_task.task_type == DiagnosticTaskType.TROUBLESHOOTING:
                result = await self._troubleshoot(diagnostic_task)
            else:
                result = await self._general_diagnosis(diagnostic_task)
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            self._diagnoses_completed += 1
            self._reports_generated += 1
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.85,
            )
            
        except Exception as e:
            logger.error(f"DiagnosticAgent execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # TASK PROCESSING METHODS
    # =============================================================================
    
    async def _analyze_failure(self, task: DiagnosticTask) -> dict:
        """Analiza una falla."""
        result = {
            "task_type": "failure_analysis",
            "device_id": task.device_id,
            "analysis": {},
            "report": {},
        }
        
        if self._failure_analyzer:
            # Analizar falla
            analysis = await self._failure_analyzer.analyze(
                device_id=task.device_id,
                symptoms=[task.symptom],
                error_codes=task.error_codes,
                conditions=task.conditions,
            )
            
            result["analysis"] = {
                "failures": analysis.failures,
                "patterns": [
                    {
                        "name": p.pattern_name,
                        "severity": p.severity.value,
                    }
                    for p in analysis.patterns
                ],
                "severity": analysis.overall_severity.value,
                "mode": analysis.failure_mode,
                "confidence": analysis.confidence,
            }
        
        # Generar reporte
        report = DiagnosticReport(
            task_id=task.task_id,
            diagnosis=f"Failure mode: {result['analysis'].get('mode', 'unknown')}",
            confidence=DiagnosisConfidence.MEDIUM,
            supporting_evidence=[task.symptom],
        )
        
        result["report"] = {
            "diagnosis": report.diagnosis,
            "confidence": report.confidence.value,
            "created_at": report.created_at.isoformat(),
        }
        
        return result
    
    async def _analyze_root_cause(self, task: DiagnosticTask) -> dict:
        """Realiza análisis de causa raíz."""
        result = {
            "task_type": "root_cause_analysis",
            "device_id": task.device_id,
            "root_cause": {},
            "causal_chain": [],
        }
        
        if self._root_cause_analyzer:
            rca = await self._root_cause_analyzer.analyze(
                device_id=task.device_id,
                symptom=task.symptom,
                failure_data=task.conditions,
            )
            
            result["root_cause"] = {
                "cause": rca.root_cause,
                "category": rca.root_cause_category,
                "confidence": rca.confidence,
                "contributing_factors": rca.contributing_factors,
            }
            result["causal_chain"] = rca.causal_chain
        
        return result
    
    async def _predictive_diagnosis(self, task: DiagnosticTask) -> dict:
        """Realiza diagnóstico predictivo."""
        result = {
            "task_type": "predictive_diagnosis",
            "device_id": task.device_id,
            "predictions": [],
            "risk_factors": [],
        }
        
        # Placeholder para análisis predictivo
        # En producción usaría ML y datos históricos
        result["predictions"] = [
            {
                "event": "potential_failure",
                "probability": 0.3,
                "timeframe": "30_days",
            }
        ]
        
        return result
    
    async def _correlate_faults(self, task: DiagnosticTask) -> dict:
        """Correla fallas."""
        result = {
            "task_type": "fault_correlation",
            "device_id": task.device_id,
            "correlations": {},
        }
        
        if self._fault_correlator:
            correlation = await self._fault_correlator.correlate(
                primary_event={"device_id": task.device_id, "event_id": task.task_id},
                event_history=[],
            )
            
            result["correlations"] = {
                "correlated_count": len(correlation.correlated_events),
                "correlation_type": correlation.correlation_type,
                "strength": correlation.correlation_strength,
            }
        
        return result
    
    async def _troubleshoot(self, task: DiagnosticTask) -> dict:
        """Realiza troubleshooting."""
        result = {
            "task_type": "troubleshooting",
            "device_id": task.device_id,
            "steps": [],
            "resolution": {},
        }
        
        # Generar pasos de troubleshooting
        result["steps"] = [
            {
                "step": 1,
                "action": "verify_symptoms",
                "description": "Verify observed symptoms",
            },
            {
                "step": 2,
                "action": "check_logs",
                "description": "Review system logs",
            },
            {
                "step": 3,
                "action": "isolate_cause",
                "description": "Isolate potential causes",
            },
            {
                "step": 4,
                "action": "test_hypothesis",
                "description": "Test diagnostic hypothesis",
            },
            {
                "step": 5,
                "action": "implement_fix",
                "description": "Implement solution",
            },
        ]
        
        result["resolution"] = {
            "status": "pending",
            "estimated_time": "1_hour",
        }
        
        return result
    
    async def _general_diagnosis(self, task: DiagnosticTask) -> dict:
        """Diagnóstico general combinando todos los motores."""
        result = {
            "task_type": "general_diagnosis",
            "device_id": task.device_id,
            "analysis": {},
            "root_cause": {},
            "plan": {},
        }
        
        # Análisis de falla
        if self._failure_analyzer:
            analysis = await self._failure_analyzer.analyze(
                device_id=task.device_id,
                symptoms=[task.symptom],
                error_codes=task.error_codes,
                conditions=task.conditions,
            )
            result["analysis"] = {
                "severity": analysis.overall_severity.value,
                "mode": analysis.failure_mode,
                "confidence": analysis.confidence,
            }
        
        # Análisis de causa raíz
        if self._root_cause_analyzer:
            rca = await self._root_cause_analyzer.analyze(
                device_id=task.device_id,
                symptom=task.symptom,
                failure_data=task.conditions,
            )
            result["root_cause"] = {
                "cause": rca.root_cause,
                "confidence": rca.confidence,
            }
        
        # Plan de diagnóstico
        if self._diagnostic_planner and self._failure_analyzer:
            from core.PHASE_5.epic3_diagnostic_agent.engines import FailureAnalysisResult
            analysis_result = FailureAnalysisResult(
                device_id=task.device_id,
                failures=result.get("analysis", {}).get("failures", []),
            )
            plan = await self._diagnostic_planner.create_plan(task, analysis_result)
            result["plan"] = {
                "steps_count": len(plan.steps),
                "status": plan.status,
            }
        
        return result
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _create_diagnostic_task(self, task: AgentTask) -> DiagnosticTask:
        """Convierte AgentTask a DiagnosticTask."""
        input_data = task.input_data
        
        # Determinar tipo de tarea
        task_type_str = task.task_type
        if not task_type_str:
            task_type_str = input_data.get("task_type", "failure_analysis")
        
        try:
            task_type = DiagnosticTaskType(task_type_str)
        except ValueError:
            task_type = DiagnosticTaskType.INVESTIGATION
        
        return DiagnosticTask(
            task_id=task.task_id,
            task_type=task_type,
            device_id=input_data.get("device_id", ""),
            device_name=input_data.get("device_name", ""),
            component=input_data.get("component", ""),
            symptom=input_data.get("symptom", ""),
            error_codes=input_data.get("error_codes", []),
            conditions=input_data.get("conditions", {}),
            context=input_data.get("context", {}),
            priority=input_data.get("priority", 5),
            timeout_seconds=task.timeout_seconds,
        )
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del agente."""
        return {
            "diagnoses_completed": self._diagnoses_completed,
            "reports_generated": self._reports_generated,
            "engines_enabled": {
                "failure_analyzer": self._failure_analyzer is not None,
                "root_cause_analyzer": self._root_cause_analyzer is not None,
                "diagnostic_planner": self._diagnostic_planner is not None,
                "fault_correlator": self._fault_correlator is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "DiagnosticAgent",
    "DiagnosticAgentConfig",
]
