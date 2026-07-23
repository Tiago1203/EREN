"""
PHASE 5 - EPIC 4: Knowledge Agent

Agente especializado en búsqueda y gestión de conocimiento biomédico.
Consulta toda la plataforma de conocimiento construida en FASE 4.
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
# IMPORTS FROM EPIC 4 DOMAIN
# =============================================================================

from core.PHASE_5.epic4_knowledge_agent.domain import (
    KnowledgeQuery,
    QueryType,
    KnowledgeSource,
    KnowledgePackage,
    KnowledgeItem,
    CitationBundle,
)

# =============================================================================
# IMPORTS FROM EPIC 4 ENGINES
# =============================================================================

from core.PHASE_5.epic4_knowledge_agent.engines import (
    KnowledgeRetriever,
    CitationCollector,
    KnowledgeSearchEngine,
    LiteratureSearchEngine,
    StandardsSearchEngine,
)


# =============================================================================
# KNOWLEDGE AGENT CONFIG
# =============================================================================

@dataclass
class KnowledgeAgentConfig:
    """Configuración del Knowledge Agent."""
    # Engines
    enable_knowledge_retriever: bool = True
    enable_citation_collector: bool = True
    enable_literature_search: bool = True
    enable_standards_search: bool = True
    
    # Comportamiento
    default_max_results: int = 10
    default_min_relevance: float = 0.7
    
    # Integración FASE 4
    use_rag_pipeline: bool = True
    use_vector_store: bool = True


# =============================================================================
# KNOWLEDGE AGENT
# =============================================================================

class KnowledgeAgent(BaseAgent):
    """
    Agente especializado en búsqueda y gestión de conocimiento.
    
    Responsabilidades:
    - Consultar base de conocimiento (FASE 4)
    - Búsqueda de literatura científica
    - Búsqueda de normas y estándares
    - Generación de citas y referencias
    - Construcción de paquetes de conocimiento
    
    Hereda de BaseAgent y utiliza los motores especializados.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: KnowledgeAgentConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.KNOWLEDGE,
            name="Knowledge Agent",
            description="Agente especializado en búsqueda de conocimiento biomédico",
        )
        
        self.config = config or KnowledgeAgentConfig()
        
        # Inicializar motores
        self._knowledge_retriever = KnowledgeRetriever() if self.config.enable_knowledge_retriever else None
        self._citation_collector = CitationCollector() if self.config.enable_citation_collector else None
        self._literature_engine = LiteratureSearchEngine() if self.config.enable_literature_search else None
        self._standards_engine = StandardsSearchEngine() if self.config.enable_standards_search else None
        
        # Métricas
        self._queries_processed = 0
        self._packages_generated = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el agente."""
        await super().initialize()
        logger.info(f"KnowledgeAgent {self.agent_id} initialized")
        logger.info(f"  - Knowledge Retriever: {self._knowledge_retriever is not None}")
        logger.info(f"  - Citation Collector: {self._citation_collector is not None}")
        logger.info(f"  - Literature Engine: {self._literature_engine is not None}")
        logger.info(f"  - Standards Engine: {self._standards_engine is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el agente."""
        await super().shutdown()
        logger.info(f"KnowledgeAgent {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de conocimiento."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Crear query de conocimiento
            query = self._create_knowledge_query(task)
            
            # Procesar según tipo de query
            if query.query_type == QueryType.FACTUAL:
                result = await self._handle_factual_query(query)
            elif query.query_type == QueryType.REGULATORY:
                result = await self._handle_regulatory_query(query)
            elif query.query_type == QueryType.LITERATURE:
                result = await self._handle_literature_query(query)
            elif query.query_type == QueryType.STANDARDS:
                result = await self._handle_standards_query(query)
            else:
                result = await self._handle_general_query(query)
            
            self._queries_processed += 1
            self._packages_generated += 1
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.90,
            )
            
        except Exception as e:
            logger.error(f"KnowledgeAgent execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # QUERY HANDLERS
    # =============================================================================
    
    async def _handle_factual_query(self, query: KnowledgeQuery) -> dict:
        """Maneja consulta factual."""
        result = {
            "query_type": "factual",
            "question": query.question,
            "package": {},
        }
        
        # Retrieval de conocimiento
        if self._knowledge_retriever:
            retrieval_result = await self._knowledge_retriever.retrieve(query)
            
            # Crear package
            package = KnowledgePackage(
                query_id=query.query_id,
                items=retrieval_result.items,
                retrieval_time_ms=retrieval_result.retrieval_time_ms,
            )
            
            result["package"] = {
                "total_items": package.total_items,
                "avg_relevance": package.avg_relevance,
                "retrieval_time_ms": package.retrieval_time_ms,
                "items": [
                    {
                        "title": item.title,
                        "summary": item.summary,
                        "relevance": item.relevance_score,
                    }
                    for item in package.items[:5]
                ],
            }
        
        return result
    
    async def _handle_regulatory_query(self, query: KnowledgeQuery) -> dict:
        """Maneja consulta regulatoria."""
        result = {
            "query_type": "regulatory",
            "question": query.question,
            "regulations": [],
        }
        
        # Búsqueda de regulaciones
        if self._knowledge_retriever:
            retrieval_result = await self._knowledge_retriever.retrieve(query)
            
            result["regulations"] = [
                {
                    "title": item.title,
                    "source": item.source_name,
                    "relevance": item.relevance_score,
                }
                for item in retrieval_result.items
            ]
        
        return result
    
    async def _handle_literature_query(self, query: KnowledgeQuery) -> dict:
        """Maneja consulta de literatura."""
        result = {
            "query_type": "literature",
            "question": query.question,
            "articles": [],
            "citations": {},
        }
        
        # Búsqueda de literatura
        if self._literature_engine:
            items = await self._literature_engine.search(
                query=query.question,
                peer_reviewed_only=True,
                limit=query.max_results,
            )
            
            result["articles"] = [
                {
                    "title": item.title,
                    "summary": item.summary,
                    "peer_reviewed": item.peer_reviewed,
                }
                for item in items
            ]
        
        # Colección de citas
        if self._citation_collector and items:
            citation_result = await self._citation_collector.collect(query, items)
            bundle = self._citation_collector.create_bundle(
                citation_result.citations,
                topic=query.question,
            )
            
            result["citations"] = {
                "total": bundle.references_count,
                "references_apa": bundle.format_references("apa"),
            }
        
        return result
    
    async def _handle_standards_query(self, query: KnowledgeQuery) -> dict:
        """Maneja consulta de normas."""
        result = {
            "query_type": "standards",
            "question": query.question,
            "standards": [],
        }
        
        # Búsqueda de normas
        if self._standards_engine:
            items = await self._standards_engine.search(
                query=query.question,
                limit=query.max_results,
            )
            
            result["standards"] = [
                {
                    "title": item.title,
                    "code": item.standard_code,
                    "relevance": item.relevance_score,
                }
                for item in items
            ]
        
        return result
    
    async def _handle_general_query(self, query: KnowledgeQuery) -> dict:
        """Maneja consulta general."""
        result = {
            "query_type": "general",
            "question": query.question,
            "package": {},
            "citations": {},
        }
        
        # Retrieval general
        if self._knowledge_retriever:
            retrieval_result = await self._knowledge_retriever.retrieve(query)
            
            package = KnowledgePackage(
                query_id=query.query_id,
                items=retrieval_result.items,
            )
            
            result["package"] = {
                "total_items": package.total_items,
                "avg_relevance": package.avg_relevance,
            }
        
        # Colección de citas
        if self._citation_collector and retrieval_result.items:
            citation_result = await self._citation_collector.collect(
                query,
                retrieval_result.items,
            )
            
            result["citations"] = {
                "total": citation_result.total_found,
            }
        
        return result
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _create_knowledge_query(self, task: AgentTask) -> KnowledgeQuery:
        """Convierte AgentTask a KnowledgeQuery."""
        input_data = task.input_data
        
        # Determinar tipo de query
        query_type_str = input_data.get("query_type", "technical")
        try:
            query_type = QueryType(query_type_str)
        except ValueError:
            query_type = QueryType.TECHNICAL
        
        # Determinar fuentes
        sources_str = input_data.get("sources", [])
        sources = []
        for s in sources_str:
            try:
                sources.append(KnowledgeSource(s))
            except ValueError:
                pass
        
        return KnowledgeQuery(
            query_id=task.task_id,
            query_type=query_type,
            question=input_data.get("question", ""),
            context=input_data.get("context", ""),
            sources=sources,
            keywords=input_data.get("keywords", []),
            max_results=input_data.get("max_results", self.config.default_max_results),
            min_relevance=input_data.get("min_relevance", self.config.default_min_relevance),
        )
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del agente."""
        return {
            "queries_processed": self._queries_processed,
            "packages_generated": self._packages_generated,
            "engines_enabled": {
                "knowledge_retriever": self._knowledge_retriever is not None,
                "citation_collector": self._citation_collector is not None,
                "literature_engine": self._literature_engine is not None,
                "standards_engine": self._standards_engine is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "KnowledgeAgent",
    "KnowledgeAgentConfig",
]
