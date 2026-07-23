"""
PHASE 4 - EPIC 6: Clinical RAG Pipeline

Pipeline RAG específico para clínica:
- Query Processor (entendimiento de queries médicas)
- Context Builder (armado de contexto clínico)
- Prompt Context (construcción de prompts)
- Evidence Package (empaquetado de evidencia)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol
import re
import uuid

from core.PHASE_4.foundation import (
    KnowledgeQuery,
    RetrievalResult,
    SearchResult,
    KnowledgeDomain,
    EvidenceTrace,
    TracedCitation,
    KnowledgePackage,
)


class ClinicalQueryType(str, Enum):
    """Tipos de query clínica."""
    DIAGNOSIS = "diagnosis"              # Diagnóstico diferencial
    TREATMENT = "treatment"              # Recomendación de tratamiento
    DEVICE_USAGE = "device_usage"        # Uso de dispositivos
    TROUBLESHOOTING = "troubleshooting"  # Resolución de problemas
    SAFETY_ALERT = "safety_alert"        # Alertas de seguridad
    REGULATORY = "regulatory"           # Cumplimiento regulatorio
    PROGNOSIS = "prognosis"             # Pronóstico
    ETIOLOGY = "etiology"               # Etiología/causas
    PREVENTION = "prevention"          # Prevención
    GENERAL = "general"                 # Consulta general


class QueryIntent(str, Enum):
    """Intenciones de query."""
    FIND = "find"           # Encontrar información
    LEARN = "learn"        # Aprender sobre tema
    COMPARE = "compare"     # Comparar opciones
    DECIDE = "decide"       # Tomar decisión
    VERIFY = "verify"       # Verificar algo
    TROUBLESHOOT = "troubleshoot"  # Solucionar problema


@dataclass
class ProcessedQuery:
    """Query procesada con análisis."""
    query_id: str
    original_text: str
    normalized_text: str
    
    # Classification
    query_type: ClinicalQueryType = ClinicalQueryType.GENERAL
    intent: QueryIntent = QueryIntent.FIND
    
    # Context extraction
    extracted_entities: list[str] = field(default_factory=list)
    extracted_conditions: list[str] = field(default_factory=list)
    extracted_devices: list[str] = field(default_factory=list)
    extracted_procedures: list[str] = field(default_factory=list)
    
    # Domain detection
    detected_domain: KnowledgeDomain | None = None
    detected_specialty: str = ""
    
    # Parameters
    filters: dict = field(default_factory=dict)
    top_k: int = 10
    
    # Metadata
    confidence: float = 0.0
    processing_time_ms: int = 0


@dataclass
class ClinicalContext:
    """Contexto clínico para RAG."""
    query: ProcessedQuery
    
    # Retrieved knowledge
    retrieved_chunks: list[SearchResult] = field(default_factory=list)
    chunk_count: int = 0
    
    # Evidence
    evidence_traces: list[EvidenceTrace] = field(default_factory=list)
    citation_package: list[TracedCitation] = field(default_factory=list)
    
    # Medical context
    relevant_conditions: list[str] = field(default_factory=list)
    relevant_devices: list[str] = field(default_factory=list)
    relevant_standards: list[str] = field(default_factory=list)
    
    # Safety
    safety_alerts: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)
    
    # Metrics
    total_tokens: int = 0
    retrieval_time_ms: int = 0
    evidence_count: int = 0


@dataclass
class PromptContext:
    """Contexto para construcción de prompt."""
    # System prompt components
    system_prompt: str = ""
    
    # User prompt components
    task_description: str = ""
    query_text: str = ""
    context_chunks: list[str] = field(default_factory=list)
    evidence_summary: str = ""
    
    # Safety
    safety_instructions: str = ""
    disclaimer: str = ""
    
    # Constraints
    max_context_tokens: int = 4000
    min_citations: int = 3
    
    # Formatting
    output_format: str = "markdown"
    include_reasoning: bool = True


@dataclass
class ClinicalRAGResponse:
    """Respuesta del pipeline RAG clínico."""
    response_id: str
    query_id: str
    
    # Content
    answer: str
    reasoning: str = ""
    
    # Quality
    confidence: float = 0.0
    confidence_level: str = ""  # high, medium, low, unknown
    
    # Evidence
    citations: list[TracedCitation] = field(default_factory=list)
    evidence_package: list[EvidenceTrace] = field(default_factory=list)
    evidence_level_summary: dict[str, int] = field(default_factory=dict)
    
    # Safety
    safety_alerts: list[str] = field(default_factory=list)
    safety_level: str = "safe"  # safe, caution, warning
    
    # Metadata
    model_used: str = ""
    tokens_used: int = 0
    retrieval_time_ms: int = 0
    generation_time_ms: int = 0
    total_time_ms: int = 0
    
    # Sources
    sources_count: int = 0
    source_types: dict[str, int] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ClinicalQueryProcessor:
    """Procesador de queries clínicas."""
    
    def __init__(self):
        # Patterns para clasificación
        self._type_patterns = {
            ClinicalQueryType.DIAGNOSIS: [
                r'\b(diagnos|diagnosis|differential|presenting|symptoms?)\b',
                r'\b(patient|subject)\b.*\b(with|has|showing)\b',
            ],
            ClinicalQueryType.TREATMENT: [
                r'\b(treat|therapy|treatment|manage|prescribe)\b',
                r'\b(recommend|suggest|indicate)\b.*\b(for|use)\b',
            ],
            ClinicalQueryType.DEVICE_USAGE: [
                r'\b(use|operate|setup|configure|calibrat)\b.*\b(pump|ventilator|monitor|device)\b',
                r'\b(how\s+to|instructions?|guide)\b.*\b(device|machine|equipment)\b',
            ],
            ClinicalQueryType.TROUBLESHOOTING: [
                r'\b(error|fault|problem|issue|fail|malfunction)\b',
                r'\b(troubleshoot|fix|resolve|solve)\b',
            ],
            ClinicalQueryType.SAFETY_ALERT: [
                r'\b(safety|alert|warning|recall|hazard|risk)\b',
                r'\b(contraindic|adverse|side\s+effect|complication)\b',
            ],
            ClinicalQueryType.REGULATORY: [
                r'\b(fda|ema|regulation|compliance|standard|guideline)\b',
                r'\b(approve|clear|certif|copyright)\b',
            ],
        }
        
        self._intent_patterns = {
            QueryIntent.FIND: [r'\b(what|which|find|search|look)\b'],
            QueryIntent.LEARN: [r'\b(learn|understand|explain|describe|know)\b'],
            QueryIntent.DECIDE: [r'\b(should|which\s+one|better|recommend)\b'],
            QueryIntent.TROUBLESHOOT: [r'\b(fix|error|problem|not\s+working)\b'],
        }
        
        self._entity_patterns = {
            "condition": [r'\b(hypertension|diabetes|cancer|infarction|arrhythmia)\b'],
            "device": [r'\b(infusion\s+pump|ventilator|defibrillator|pacemaker|monitor)\b'],
            "procedure": [r'\b(surgery|biopsy|catheter|intubation|dialysis)\b'],
        }
    
    async def process(self, query_text: str) -> ProcessedQuery:
        """Procesa query clínica."""
        import time
        import re
        start = time.time()
        
        query_id = str(uuid.uuid4())
        normalized = query_text.lower().strip()
        
        # Classify query type
        query_type = self._classify_type(normalized)
        
        # Classify intent
        intent = self._classify_intent(normalized)
        
        # Extract entities
        entities = self._extract_entities(normalized)
        
        # Detect domain
        domain = self._detect_domain(normalized)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query_type, intent)
        
        processing_time_ms = int((time.time() - start) * 1000)
        
        return ProcessedQuery(
            query_id=query_id,
            original_text=query_text,
            normalized_text=normalized,
            query_type=query_type,
            intent=intent,
            extracted_entities=entities.get("all", []),
            extracted_conditions=entities.get("condition", []),
            extracted_devices=entities.get("device", []),
            extracted_procedures=entities.get("procedure", []),
            detected_domain=domain,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
        )
    
    def _classify_type(self, text: str) -> ClinicalQueryType:
        """Clasifica tipo de query."""
        scores = {}
        
        for qtype, patterns in self._type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[qtype] = scores.get(qtype, 0) + 1
        
        if scores:
            return max(scores, key=scores.get)
        
        return ClinicalQueryType.GENERAL
    
    def _classify_intent(self, text: str) -> QueryIntent:
        """Clasifica intención de query."""
        for intent, patterns in self._intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return intent
        
        return QueryIntent.FIND
    
    def _extract_entities(self, text: str) -> dict:
        """Extrae entidades de la query."""
        import re
        entities = {"all": [], "condition": [], "device": [], "procedure": []}
        
        for etype, patterns in self._entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities[etype].extend(matches)
                entities["all"].extend(matches)
        
        return entities
    
    def _detect_domain(self, text: str) -> KnowledgeDomain | None:
        """Detecta dominio de conocimiento."""
        domain_keywords = {
            KnowledgeDomain.CARDIOLOGY: ["heart", "cardiac", "cardiovascular", "ecg", "ekg"],
            KnowledgeDomain.RADIOLOGY: ["x-ray", "ct", "mri", "imaging", "scan"],
            KnowledgeDomain.ONCOLOGY: ["cancer", "tumor", "malignant", "carcinoma"],
            KnowledgeDomain.CRITICAL_CARE: ["icu", "critical", "ventilator", "sepsis"],
            KnowledgeDomain.NEUROLOGY: ["brain", "neural", "stroke", "seizure"],
        }
        
        for domain, keywords in domain_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return domain
        
        return None
    
    def _calculate_confidence(
        self,
        query_type: ClinicalQueryType,
        intent: QueryIntent,
    ) -> float:
        """Calcula confianza de clasificación."""
        base = 0.5
        
        if query_type != ClinicalQueryType.GENERAL:
            base += 0.2
        
        if intent != QueryIntent.FIND:
            base += 0.1
        
        return min(base, 1.0)


class ClinicalContextBuilder:
    """Construye contexto clínico para RAG."""
    
    def __init__(self):
        self._context_templates = self._load_templates()
    
    def _load_templates(self) -> dict:
        """Carga templates de contexto."""
        return {
            ClinicalQueryType.DIAGNOSIS: """
Based on the clinical presentation described, consider the following diagnostic possibilities:
{evidence}
""",
            ClinicalQueryType.TREATMENT: """
For the management of this condition, consider the following treatment approaches:
{evidence}
""",
            ClinicalQueryType.DEVICE_USAGE: """
Device operation and usage guidelines:
{evidence}
""",
            ClinicalQueryType.TROUBLESHOOTING: """
Troubleshooting steps and solutions:
{evidence}
""",
            ClinicalQueryType.SAFETY_ALERT: """
SAFETY INFORMATION:
{evidence}
""",
        }
    
    async def build(
        self,
        query: ProcessedQuery,
        retrieval_result: RetrievalResult,
    ) -> ClinicalContext:
        """Construye contexto clínico."""
        import time
        start = time.time()
        
        # Extract chunks from retrieval
        chunks = retrieval_result.results[:query.top_k]
        
        # Build context
        context = ClinicalContext(
            query=query,
            retrieved_chunks=chunks,
            chunk_count=len(chunks),
            relevant_devices=query.extracted_devices,
            relevant_conditions=query.extracted_conditions,
        )
        
        # Add safety alerts if relevant
        if query.query_type == ClinicalQueryType.SAFETY_ALERT:
            context.safety_alerts = await self._extract_safety_alerts(chunks)
        
        context.retrieval_time_ms = int((time.time() - start) * 1000)
        
        return context
    
    async def _extract_safety_alerts(
        self,
        chunks: list[SearchResult],
    ) -> list[str]:
        """Extrae alertas de seguridad de chunks."""
        alerts = []
        
        for chunk in chunks:
            payload = chunk.payload
            if "safety_alert" in payload:
                alerts.append(payload["safety_alert"])
        
        return alerts


class PromptContextBuilder:
    """Construye contexto para prompt de LLM."""
    
    def __init__(self):
        self._system_prompt_base = """You are EREN, a Clinical Intelligence System for Clinical Engineering.

Your role is to assist healthcare professionals with:
- Medical device information and usage
- Clinical troubleshooting and problem-solving
- Safety alerts and regulatory compliance
- Evidence-based clinical recommendations

IMPORTANT: Always prioritize patient safety and provide accurate, evidence-based information.
When recommending treatments or procedures, cite your sources clearly.

If you are uncertain about any information, express that uncertainty clearly."""
        
        self._safety_instructions = """
CRITICAL SAFETY NOTES:
- Always verify device settings before patient use
- Cross-reference critical information with primary sources
- Consult clinical protocols specific to your institution
- Report any device safety concerns immediately"""
    
    def build(
        self,
        query: ProcessedQuery,
        context: ClinicalContext,
    ) -> PromptContext:
        """Construye contexto para prompt."""
        # Select template based on query type
        template = self._get_template(query.query_type)
        
        # Format evidence
        evidence_text = self._format_evidence(context)
        
        # Build context chunks
        chunks_text = "\n\n".join([
            f"Source {i+1}:\n{c.result.payload.get('content', c.result.payload.get('title', ''))}"
            for i, c in enumerate(context.retrieved_chunks[:5])
        ])
        
        return PromptContext(
            system_prompt=self._system_prompt_base,
            task_description=template.format(evidence=evidence_text),
            query_text=query.original_text,
            context_chunks=[chunks_text],
            evidence_summary=evidence_text,
            safety_instructions=self._safety_instructions,
            disclaimer="This information is for reference only. Always follow institutional protocols.",
        )
    
    def _get_template(self, query_type: ClinicalQueryType) -> str:
        """Obtiene template según tipo de query."""
        templates = {
            ClinicalQueryType.DIAGNOSIS: "Based on the clinical findings, provide diagnostic considerations:\n{evidence}",
            ClinicalQueryType.TREATMENT: "Based on the clinical context, recommend appropriate treatment:\n{evidence}",
            ClinicalQueryType.DEVICE_USAGE: "Provide device operation guidance:\n{evidence}",
            ClinicalQueryType.TROUBLESHOOTING: "Provide troubleshooting assistance:\n{evidence}",
            ClinicalQueryType.SAFETY_ALERT: "IMPORTANT SAFETY INFORMATION:\n{evidence}",
            ClinicalQueryType.GENERAL: "Based on available evidence:\n{evidence}",
        }
        return templates.get(query_type, "Answer the following question:\n{evidence}")
    
    def _format_evidence(self, context: ClinicalContext) -> str:
        """Formatea evidencia para contexto."""
        if not context.retrieved_chunks:
            return "No relevant evidence found."
        
        evidence_lines = []
        for i, chunk in enumerate(context.retrieved_chunks[:5], 1):
            payload = chunk.result.payload
            title = payload.get('title', 'Untitled')
            content = payload.get('content', '')[:500]
            source = payload.get('source_type', 'unknown')
            
            evidence_lines.append(
                f"[{i}] {title} (Source: {source})\n"
                f"    {content}..."
            )
        
        return "\n\n".join(evidence_lines)


class ClinicalRAGPipeline:
    """Pipeline RAG clínico completo."""
    
    def __init__(
        self,
        query_processor: ClinicalQueryProcessor | None = None,
        context_builder: ClinicalContextBuilder | None = None,
        prompt_builder: PromptContextBuilder | None = None,
        retrieval_engine=None,
    ):
        self.query_processor = query_processor or ClinicalQueryProcessor()
        self.context_builder = context_builder or ClinicalContextBuilder()
        self.prompt_builder = prompt_builder or PromptContextBuilder()
        self.retrieval_engine = retrieval_engine
    
    async def query(
        self,
        query_text: str,
        collection: str | None = None,
        top_k: int = 10,
    ) -> ClinicalRAGResponse:
        """Ejecuta query a través del pipeline."""
        import time
        total_start = time.time()
        
        # 1. Process query
        processed_query = await self.query_processor.process(query_text)
        processed_query.top_k = top_k
        
        # 2. Retrieve knowledge
        retrieval_start = time.time()
        if self.retrieval_engine:
            retrieval_result = await self.retrieval_engine.retrieve(
                KnowledgeQuery(
                    query_id=processed_query.query_id,
                    text=query_text,
                    domain=processed_query.detected_domain,
                    top_k=top_k,
                ),
                collection or "knowledge_articles",
            )
        else:
            # Placeholder
            retrieval_result = RetrievalResult(
                query_id=processed_query.query_id,
                results=[],
                total_found=0,
                retrieval_time_ms=0,
            )
        retrieval_time_ms = int((time.time() - retrieval_start) * 1000)
        
        # 3. Build context
        context = await self.context_builder.build(processed_query, retrieval_result)
        
        # 4. Build prompt context
        prompt_context = self.prompt_builder.build(processed_query, context)
        
        # 5. Generate response (placeholder - would call LLM)
        generation_start = time.time()
        answer = await self._generate_response(prompt_context)
        generation_time_ms = int((time.time() - generation_start) * 1000)
        
        total_time_ms = int((time.time() - total_start) * 1000)
        
        return ClinicalRAGResponse(
            response_id=str(uuid.uuid4()),
            query_id=processed_query.query_id,
            answer=answer,
            confidence=processed_query.confidence,
            confidence_level=self._get_confidence_level(processed_query.confidence),
            evidence_package=context.evidence_traces,
            citations=context.citation_package,
            safety_alerts=context.safety_alerts,
            safety_level=self._get_safety_level(context),
            retrieval_time_ms=retrieval_time_ms,
            generation_time_ms=generation_time_ms,
            total_time_ms=total_time_ms,
            sources_count=len(context.retrieved_chunks),
        )
    
    async def _generate_response(self, prompt_context: PromptContext) -> str:
        """Genera respuesta (placeholder)."""
        return (
            f"Based on the available evidence and clinical context, here is my response "
            f"to your query about '{prompt_context.query_text}'.\n\n"
            f"{prompt_context.evidence_summary}\n\n"
            f"{prompt_context.safety_instructions}"
        )
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Determina nivel de confianza."""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        elif confidence >= 0.3:
            return "low"
        return "unknown"
    
    def _get_safety_level(self, context: ClinicalContext) -> str:
        """Determina nivel de seguridad."""
        if context.safety_alerts:
            return "warning"
        elif len(context.contraindications) > 0:
            return "caution"
        return "safe"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ClinicalQueryType",
    "QueryIntent",
    # Data Classes
    "ProcessedQuery",
    "ClinicalContext",
    "PromptContext",
    "ClinicalRAGResponse",
    # Processors
    "ClinicalQueryProcessor",
    "ClinicalContextBuilder",
    "PromptContextBuilder",
    # Pipeline
    "ClinicalRAGPipeline",
]
