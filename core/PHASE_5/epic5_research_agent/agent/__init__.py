"""
PHASE 5 - EPIC 5: Research Agent

Agente dedicado a investigación biomédica.
Busca evidencia científica, compara artículos y genera resúmenes técnicos.
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
# IMPORTS FROM EPIC 5 DOMAIN
# =============================================================================

from core.PHASE_5.epic5_research_agent.domain import (
    ResearchRequest,
    ResearchType,
    ResearchScope,
    ResearchResult,
    ResearchFinding,
    EvidenceStrength,
    LiteratureReview,
)

# =============================================================================
# IMPORTS FROM EPIC 5 ENGINES
# =============================================================================

from core.PHASE_5.epic5_research_agent.engines import (
    ResearchPlanner,
    EvidenceComparator,
    PaperAnalyzer,
    LiteratureReviewer,
)


# =============================================================================
# RESEARCH AGENT CONFIG
# =============================================================================

@dataclass
class ResearchAgentConfig:
    """Configuración del Research Agent."""
    # Engines
    enable_research_planner: bool = True
    enable_evidence_comparator: bool = True
    enable_paper_analyzer: bool = True
    enable_literature_reviewer: bool = True
    
    # Comportamiento
    default_max_articles: int = 50
    default_scope: ResearchScope = ResearchScope.COMPREHENSIVE
    
    # Integración
    use_external_databases: bool = True
    include_gray_literature: bool = False


# =============================================================================
# RESEARCH AGENT
# =============================================================================

class ResearchAgent(BaseAgent):
    """
    Agente dedicado a investigación biomédica.
    
    Responsabilidades:
    - Planificar investigaciones sistemáticas
    - Analizar artículos científicos
    - Comparar evidencia entre estudios
    - Generar revisiones de literatura
    - Producir resúmenes técnicos
    
    Hereda de BaseAgent y utiliza los motores especializados.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: ResearchAgentConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.RESEARCH,
            name="Research Agent",
            description="Agente dedicado a investigación biomédica",
        )
        
        self.config = config or ResearchAgentConfig()
        
        # Inicializar motores
        self._research_planner = ResearchPlanner() if self.config.enable_research_planner else None
        self._evidence_comparator = EvidenceComparator() if self.config.enable_evidence_comparator else None
        self._paper_analyzer = PaperAnalyzer() if self.config.enable_paper_analyzer else None
        self._literature_reviewer = LiteratureReviewer() if self.config.enable_literature_reviewer else None
        
        # Métricas
        self._research_completed = 0
        self._reviews_generated = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el agente."""
        await super().initialize()
        logger.info(f"ResearchAgent {self.agent_id} initialized")
        logger.info(f"  - Research Planner: {self._research_planner is not None}")
        logger.info(f"  - Evidence Comparator: {self._evidence_comparator is not None}")
        logger.info(f"  - Paper Analyzer: {self._paper_analyzer is not None}")
        logger.info(f"  - Literature Reviewer: {self._literature_reviewer is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el agente."""
        await super().shutdown()
        logger.info(f"ResearchAgent {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de investigación."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Crear request de investigación
            request = self._create_research_request(task)
            
            # Procesar según tipo
            if request.research_type == ResearchType.SYSTEMATIC_REVIEW:
                result = await self._perform_systematic_review(request)
            elif request.research_type == ResearchType.META_ANALYSIS:
                result = await self._perform_meta_analysis(request)
            elif request.research_type == ResearchType.TECHNICAL_REVIEW:
                result = await self._perform_technical_review(request)
            else:
                result = await self._perform_general_research(request)
            
            self._research_completed += 1
            self._reviews_generated += 1
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.85,
            )
            
        except Exception as e:
            logger.error(f"ResearchAgent execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # RESEARCH METHODS
    # =============================================================================
    
    async def _perform_systematic_review(self, request: ResearchRequest) -> dict:
        """Realiza revisión sistemática."""
        result = {
            "research_type": "systematic_review",
            "request_id": request.request_id,
            "plan": {},
            "findings": [],
            "literature_review": {},
        }
        
        # Crear plan
        if self._research_planner:
            plan = await self._research_planner.create_plan(request)
            result["plan"] = {
                "steps_count": len(plan.steps),
                "estimated_duration_minutes": plan.estimated_duration_minutes,
            }
        
        # Placeholder para búsqueda y análisis
        # En producción consultaría bases de datos reales
        
        # Crear hallazgos
        findings = [
            ResearchFinding(
                description="Evidence suggests positive outcomes",
                evidence_strength=EvidenceStrength.MODERATE,
                confidence_level=0.75,
            )
        ]
        
        for f in findings:
            result["findings"].append({
                "description": f.description,
                "evidence_strength": f.evidence_strength.value,
                "confidence": f.confidence_level,
            })
        
        # Generar revisión
        if self._literature_reviewer:
            analyses = []  # Placeholder
            review = await self._literature_reviewer.create_review(request, analyses, findings)
            result["literature_review"] = {
                "title": review.title,
                "sections_count": len(review.sections),
                "references_count": review.references_count,
                "quality_score": review.quality_score,
            }
        
        return result
    
    async def _perform_meta_analysis(self, request: ResearchRequest) -> dict:
        """Realiza meta-análisis."""
        result = {
            "research_type": "meta_analysis",
            "request_id": request.request_id,
            "pooled_estimate": {},
            "heterogeneity": {},
        }
        
        # Placeholder para meta-análisis
        result["pooled_estimate"] = {
            "effect_size": 0.65,
            "confidence_interval": [0.45, 0.85],
        }
        result["heterogeneity"] = {
            "i_squared": 0.45,
            "q_statistic": 12.5,
        }
        
        return result
    
    async def _perform_technical_review(self, request: ResearchRequest) -> dict:
        """Realiza revisión técnica."""
        result = {
            "research_type": "technical_review",
            "request_id": request.request_id,
            "technical_summary": {},
            "recommendations": [],
        }
        
        # Placeholder
        result["technical_summary"] = {
            "key_technologies": ["Technology A", "Technology B"],
            "standards_compliance": ["IEC 60601-1", "ISO 14971"],
        }
        result["recommendations"] = [
            "Implement according to IEC standards",
            "Consider cost-benefit analysis",
        ]
        
        return result
    
    async def _perform_general_research(self, request: ResearchRequest) -> dict:
        """Realiza investigación general."""
        result = {
            "research_type": "general_research",
            "request_id": request.request_id,
            "summary": {},
            "sources": [],
        }
        
        # Placeholder
        result["summary"] = {
            "articles_found": 10,
            "key_findings": ["Finding 1", "Finding 2"],
        }
        
        return result
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _create_research_request(self, task: AgentTask) -> ResearchRequest:
        """Convierte AgentTask a ResearchRequest."""
        input_data = task.input_data
        
        # Determinar tipo de investigación
        research_type_str = input_data.get("research_type", "systematic_review")
        try:
            research_type = ResearchType(research_type_str)
        except ValueError:
            research_type = ResearchType.SYSTEMATIC_REVIEW
        
        # Determinar alcance
        scope_str = input_data.get("scope", "comprehensive")
        try:
            scope = ResearchScope(scope_str)
        except ValueError:
            scope = ResearchScope.COMPREHENSIVE
        
        return ResearchRequest(
            request_id=task.task_id,
            research_type=research_type,
            research_question=input_data.get("research_question", ""),
            background=input_data.get("background", ""),
            objectives=input_data.get("objectives", []),
            scope=scope,
            keywords=input_data.get("keywords", []),
            max_articles=input_data.get("max_articles", self.config.default_max_articles),
            inclusion_criteria=input_data.get("inclusion_criteria", []),
            exclusion_criteria=input_data.get("exclusion_criteria", []),
        )
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del agente."""
        return {
            "research_completed": self._research_completed,
            "reviews_generated": self._reviews_generated,
            "engines_enabled": {
                "research_planner": self._research_planner is not None,
                "evidence_comparator": self._evidence_comparator is not None,
                "paper_analyzer": self._paper_analyzer is not None,
                "literature_reviewer": self._literature_reviewer is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ResearchAgent",
    "ResearchAgentConfig",
]
