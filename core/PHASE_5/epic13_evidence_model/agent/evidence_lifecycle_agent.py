"""
EvidenceLifecycleAgent: Agente principal de ciclo de vida de evidencia
"""

from datetime import datetime
from typing import Optional

from core.PHASE_5.foundation import BaseAgent, AgentType, AgentCapability, AgentTask
from core.PHASE_5.epic13_evidence_model.domain import (
    Evidence,
    EvidenceBundle,
    EvidenceQuality,
    EvidenceSource,
    EvidenceContent,
    EvidenceCitation,
    EvidenceType,
    QualityLevel,
    SourceType,
    RelevanceScore,
    ApplicabilityScore,
    EvidenceConfig,
)


class EvidenceLifecycleAgent(BaseAgent):
    """Agente de ciclo de vida de evidencia."""
    
    def __init__(
        self,
        agent_id: str,
        config: Optional[EvidenceConfig] = None,
    ):
        """Inicializa el agente."""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.RESEARCH,
            capabilities=[
                AgentCapability.RESEARCH,
                AgentCapability.VALIDATE,
            ],
        )
        self.config = config or EvidenceConfig()
    
    async def _execute_impl(self, task: AgentTask) -> dict:
        """Implementa la ejecución del agente."""
        action = task.input.get("action", "retrieve")
        
        if action == "retrieve":
            return await self._retrieve_evidence(task.input)
        elif action == "evaluate":
            return await self._evaluate_evidence(task.input)
        elif action == "synthesize":
            return await self._synthesize_evidence(task.input)
        elif action == "bundle":
            return await self._create_bundle(task.input)
        elif action == "trace":
            return await self._trace_evidence(task.input)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _retrieve_evidence(self, input_data: dict) -> dict:
        """Recupera evidencia."""
        query = input_data.get("query")
        if not query:
            return {"error": "query is required"}
        
        # En implementación real, esto consultaría FASE 4/Knowledge
        # Simulación de evidencia retrieved
        evidence_list = []
        for i in range(min(3, self.config.max_evidence)):
            evidence = self._create_sample_evidence(f"ev_{query}_{i}", query)
            evidence_list.append(evidence)
        
        return {
            "query": query,
            "evidence_count": len(evidence_list),
            "evidence": [
                {
                    "id": e.evidence_id,
                    "type": e.evidence_type.value,
                    "quality": e.quality.quality_level.value,
                    "relevance": e.relevance.score,
                }
                for e in evidence_list
            ],
        }
    
    async def _evaluate_evidence(self, input_data: dict) -> dict:
        """Evalúa calidad de evidencia."""
        evidence_id = input_data.get("evidence_id")
        if not evidence_id:
            return {"error": "evidence_id is required"}
        
        # En implementación real, evaluaría con GRADE
        quality = EvidenceQuality(
            quality_level=QualityLevel.MODERATE,
            score=0.7,
            methodology_score=0.8,
            sample_size_score=0.6,
            consistency_score=0.7,
            publication_bias_score=0.2,
        )
        
        return {
            "evidence_id": evidence_id,
            "quality_level": quality.quality_level.value,
            "score": quality.score,
            "limitations": quality.get_limitations(),
        }
    
    async def _synthesize_evidence(self, input_data: dict) -> dict:
        """Sintetiza evidencia."""
        evidence_ids = input_data.get("evidence_ids", [])
        
        # En implementación real, sintetizaría con NLP/ML
        synthesis = f"Synthesis of {len(evidence_ids)} evidence sources. "
        synthesis += "Key findings indicate moderate to high quality evidence support "
        synthesis += "the clinical recommendation with some limitations noted."
        
        return {
            "synthesis": synthesis,
            "evidence_count": len(evidence_ids),
            "confidence": 0.75,
        }
    
    async def _create_bundle(self, input_data: dict) -> dict:
        """Crea bundle de evidencia."""
        query = input_data.get("query", "")
        
        bundle = EvidenceBundle(
            bundle_id=f"bundle_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            query=query,
            evidence_list=[],
        )
        
        return {
            "bundle_id": bundle.bundle_id,
            "query": bundle.query,
            "evidence_count": len(bundle.evidence_list),
            "average_quality": bundle.get_average_quality(),
        }
    
    async def _trace_evidence(self, input_data: dict) -> dict:
        """Traza evidencia de una decisión."""
        decision_id = input_data.get("decision_id")
        if not decision_id:
            return {"error": "decision_id is required"}
        
        # En implementación real, trazaría en base de datos
        return {
            "decision_id": decision_id,
            "evidence_ids": [],
            "trace_complete": True,
        }
    
    def _create_sample_evidence(self, evidence_id: str, query: str) -> Evidence:
        """Crea evidencia de ejemplo."""
        return Evidence(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.CLINICAL_TRIAL,
            source=EvidenceSource(
                source_type=SourceType.PUBMED,
                name="PubMed",
                doi=f"10.1234/example.{evidence_id}",
                published_date=datetime(2024, 6, 15),
                authors=["Smith J", "Johnson A"],
                journal="Journal of Clinical Evidence",
            ),
            content=EvidenceContent(
                title=f"Study on {query}",
                abstract=f"Abstract of study related to {query}...",
                findings="Key findings indicate effectiveness...",
                conclusions="The study supports the use of...",
            ),
            quality=EvidenceQuality(
                quality_level=QualityLevel.MODERATE,
                score=0.7,
                methodology_score=0.8,
                sample_size_score=0.6,
                consistency_score=0.7,
                publication_bias_score=0.2,
            ),
            relevance=RelevanceScore(
                score=0.75,
                relevance_to_query=query,
                population_match=0.8,
                outcome_match=0.7,
            ),
            applicability=ApplicabilityScore(
                score=0.7,
                clinical_setting_match=0.8,
                patient_population_match=0.7,
                resource_availability=0.6,
            ),
            citation=EvidenceCitation(
                citation_text=f"Smith J, Johnson A. Study on {query}. J Clin Evid. 2024.",
                apa=f"Smith, J., & Johnson, A. (2024). Study on {query}. Journal of Clinical Evidence.",
            ),
        )
