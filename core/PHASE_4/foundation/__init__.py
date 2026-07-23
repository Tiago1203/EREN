"""
PHASE 4 - EPIC 0: Knowledge Infrastructure Foundation

Shared kernel que conecta PHASE 1, 2, 3 con los EPICs de PHASE 4.
Proporciona contratos, interfaces y tipos comunes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Protocol, Optional
import uuid


# =============================================================================
# ENUMS - Tipos fundamentales de la plataforma de conocimiento
# =============================================================================

class DocumentFormat(str, Enum):
    """Formatos de documento soportados."""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"
    XML = "xml"
    JSON = "json"


class KnowledgeDomain(str, Enum):
    """Dominios de conocimiento clínico."""
    CARDIOLOGY = "cardiology"
    RADIOLOGY = "radiology"
    ONCOLOGY = "oncology"
    NEUROLOGY = "neurology"
    ORTHOPEDICS = "orthopedics"
    CRITICAL_CARE = "critical_care"
    EMERGENCY = "emergency"
    SURGERY = "surgery"
    PEDIATRICS = "pediatrics"
    GERIATRICS = "geriatrics"
    GENERAL = "general"


class ProcessingStatus(str, Enum):
    """Estado de procesamiento de documento."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class QualityLevel(str, Enum):
    """Nivel de calidad del conocimiento."""
    HIGH = "high"      # Revisado por pares, evidencia alta
    MEDIUM = "medium"  # Evidencia moderada
    LOW = "low"       # Evidencia limitada
    UNVERIFIED = "unverified"


class EvidenceLevel(str, Enum):
    """Niveles de evidencia médica (Oxford)."""
    LEVEL_1A = "1a"  # Revisión sistemática de RCTs
    LEVEL_1B = "1b"  # RCT individual con CI
    LEVEL_2A = "2a"  # Revisión sistemática de estudios de cohorte
    LEVEL_2B = "2b"  # Estudio de cohorte individual
    LEVEL_3 = "3"    # Estudios de casos y controles
    LEVEL_4 = "4"    # Series de casos
    LEVEL_5 = "5"    # Opinión de expertos


class GovernanceStatus(str, Enum):
    """Estado de gobernanza del conocimiento."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


# =============================================================================
# CONTRACTS - Interfaces para los gateways y servicios
# =============================================================================

class IDocumentProcessor(Protocol):
    """Protocolo para procesador de documentos."""
    
    async def process(self, content: bytes, format: DocumentFormat, metadata: dict) -> ProcessedDocument:
        """Procesa un documento y retorna resultado."""
        ...


class IKnowledgeExtractor(Protocol):
    """Protocolo para extractor de conocimiento."""
    
    async def extract(self, document: ProcessedDocument) -> ExtractedKnowledge:
        """Extrae entidades, conceptos y relaciones."""
        ...


class IClinicalEmbedder(Protocol):
    """Protocolo para embedder clínico."""
    
    async def embed(self, text: str, model: str) -> EmbeddingVector:
        """Genera embedding para texto."""
        ...
    
    async def embed_batch(self, texts: list[str], model: str) -> list[EmbeddingVector]:
        """Genera embeddings para batch de textos."""
        ...


class IVectorIndexer(Protocol):
    """Protocolo para indexador de vectores."""
    
    async def index(self, vectors: list[IndexedVector]) -> bool:
        """Indexa vectores en la colección."""
        ...
    
    async def search(self, query: EmbeddingVector, top_k: int) -> list[SearchResult]:
        """Busca vectores similares."""
        ...


class IHybridRetriever(Protocol):
    """Protocolo para retrieval híbrido."""
    
    async def retrieve(self, query: KnowledgeQuery) -> RetrievalResult:
        """Recupera conocimiento relevante."""
        ...


class IKnowledgeRepository(Protocol):
    """Protocolo para repositorio de conocimiento."""
    
    async def store(self, knowledge: KnowledgeAsset) -> str:
        """Almacena asset de conocimiento."""
        ...
    
    async def get(self, id: str) -> Optional[KnowledgeAsset]:
        """Recupera asset por ID."""
        ...
    
    async def update(self, id: str, knowledge: KnowledgeAsset) -> bool:
        """Actualiza asset."""
        ...
    
    async def list_versions(self, id: str) -> list[KnowledgeVersion]:
        """Lista versiones de un asset."""
        ...


class ICitationTracker(Protocol):
    """Protocolo para trazabilidad de citas."""
    
    async def cite(self, claim: str, source: Citation) -> TracedCitation:
        """Registra citación para claim."""
        ...
    
    async def get_trace(self, citation_id: str) -> Optional[EvidenceTrace]:
        """Obtiene trace de citación."""
        ...


# =============================================================================
# VALUE OBJECTS - Objetos de valor fundamentales
# =============================================================================

@dataclass(frozen=True)
class EmbeddingVector:
    """Vector de embedding."""
    values: list[float]
    model: str
    dimension: int
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SourceReference:
    """Referencia a fuente de conocimiento."""
    source_id: str
    source_type: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: str = ""
    doi: str = ""
    url: str = ""
    journal: str = ""
    volume: str = ""
    pages: str = ""


@dataclass(frozen=True)
class Citation:
    """Citación con metadata completa."""
    citation_id: str
    reference: SourceReference
    evidence_level: EvidenceLevel = EvidenceLevel.LEVEL_5
    quality_score: float = 0.0
    accessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class MedicalCode:
    """Código médico (ICD, SNOMED, LOINC, etc)."""
    system: str  # ICD10, SNOMED, LOINC, RxNorm
    code: str
    display: str = ""
    version: str = ""


# =============================================================================
# ENTITIES - Entidades principales
# =============================================================================

@dataclass
class ProcessedDocument:
    """Documento procesado con contenido extraído."""
    document_id: str
    content: str
    format: DocumentFormat
    metadata: dict
    status: ProcessingStatus = ProcessingStatus.PENDING
    pages: int = 0
    word_count: int = 0
    language: str = "en"
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    errors: list[str] = field(default_factory=list)


@dataclass
class ExtractedKnowledge:
    """Conocimiento extraído de documento."""
    extraction_id: str
    document_id: str
    entities: list[ExtractedEntity] = field(default_factory=list)
    concepts: list[ExtractedConcept] = field(default_factory=list)
    relations: list[ExtractedRelation] = field(default_factory=list)
    summary: str = ""
    keywords: list[str] = field(default_factory=list)
    medical_codes: list[MedicalCode] = field(default_factory=list)
    quality_score: float = 0.0
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ExtractedEntity:
    """Entidad extraída (persona, lugar, organización, dispositivo)."""
    entity_id: str
    text: str
    type: str  # DEVICE, DRUG, CONDITION, PROCEDURE, ORGANIZATION
    confidence: float
    start_pos: int
    end_pos: int
    normalized_form: str = ""
    medical_codes: list[MedicalCode] = field(default_factory=list)


@dataclass
class ExtractedConcept:
    """Concepto clínico extraído."""
    concept_id: str
    text: str
    category: str  # DIAGNOSIS, TREATMENT, SYMPTOM, ANATOMY
    definition: str = ""
    synonyms: list[str] = field(default_factory=list)
    medical_codes: list[MedicalCode] = field(default_factory=list)


@dataclass
class ExtractedRelation:
    """Relación entre entidades."""
    relation_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str  # TREATS, CAUSES, INTERACTS_WITH, IS_A
    confidence: float
    evidence: str = ""


@dataclass
class IndexedVector:
    """Vector indexado en la colección."""
    vector_id: str
    embedding: EmbeddingVector
    collection: str
    payload: dict = field(default_factory=dict)  # Document metadata, tags, etc
    indexed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SearchResult:
    """Resultado de búsqueda."""
    result_id: str
    score: float
    payload: dict
    highlights: list[str] = field(default_factory=list)


@dataclass
class KnowledgeQuery:
    """Query para retrieval de conocimiento."""
    query_id: str
    text: str
    domain: KnowledgeDomain | None = None
    filters: dict = field(default_factory=dict)
    top_k: int = 10
    min_relevance: float = 0.5
    include_metadata: bool = True


@dataclass
class RetrievalResult:
    """Resultado de retrieval."""
    query_id: str
    results: list[SearchResult]
    total_found: int
    retrieval_time_ms: int
    metadata: dict = field(default_factory=dict)


@dataclass
class KnowledgeAsset:
    """Asset de conocimiento versionado."""
    asset_id: str
    version: str
    content: str
    title: str
    domain: KnowledgeDomain
    metadata: dict = field(default_factory=dict)
    
    # Extracción
    entities: list[ExtractedEntity] = field(default_factory=list)
    concepts: list[ExtractedConcept] = field(default_factory=list)
    relations: list[ExtractedRelation] = field(default_factory=list)
    medical_codes: list[MedicalCode] = field(default_factory=list)
    
    # Calidad
    quality_level: QualityLevel = QualityLevel.UNVERIFIED
    quality_score: float = 0.0
    
    # Gobernanza
    governance_status: GovernanceStatus = GovernanceStatus.DRAFT
    created_by: str = ""
    approved_by: str = ""
    
    # Versiones
    previous_version_id: str | None = None
    supersedes_id: str | None = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    published_at: datetime | None = None


@dataclass
class KnowledgeVersion:
    """Versión de un asset de conocimiento."""
    version_id: str
    asset_id: str
    version: str
    changes_summary: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""


@dataclass
class TracedCitation:
    """Citación con trazabilidad."""
    trace_id: str
    citation: Citation
    claim: str
    reasoning_path: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    traced_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class EvidenceTrace:
    """Trace de evidencia para auditoría."""
    trace_id: str
    claim: str
    citations: list[Citation]
    evidence_chain: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class KnowledgePackage:
    """Paquete de conocimiento consolidado (output de PHASE 4)."""
    package_id: str
    query_id: str
    
    # Contenido
    knowledge_chunks: list[str] = field(default_factory=list)
    aggregated_context: str = ""
    
    # Evidencia
    evidence_package: list[EvidenceTrace] = field(default_factory=list)
    citation_package: list[TracedCitation] = field(default_factory=list)
    
    # Metadatos
    sources_count: int = 0
    evidence_levels: dict[str, int] = field(default_factory=dict)
    avg_quality_score: float = 0.0
    
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# GATEWAYS - Conexiones con otras fases
# =============================================================================

class PHASE1Gateway:
    """Gateway para consumir conocimiento de PHASE 1."""
    
    def __init__(self):
        self._knowledge_repo = None  # PHASE_1 KnowledgeRepository
        self._device_repo = None      # PHASE_1 DeviceRepository
        self._incident_repo = None    # PHASE_1 IncidentRepository
    
    async def get_knowledge_articles(self, domain: KnowledgeDomain, limit: int = 100) -> list[dict]:
        """Obtiene artículos de conocimiento del dominio."""
        # Placeholder - would connect to PHASE_1
        return []
    
    async def get_device_manuals(self, device_category: str) -> list[dict]:
        """Obtiene manuales de dispositivos."""
        return []
    
    async def get_incident_reports(self, device_id: str) -> list[dict]:
        """Obtiene reportes de incidentes."""
        return []


class PHASE2Gateway:
    """Gateway para extender funcionalidades de PHASE 2."""
    
    def __init__(self):
        self._embedding_manager = None
        self._retrieval_engine = None
        self._context_builder = None
    
    async def get_embeddings(self, texts: list[str], model: str) -> list[EmbeddingVector]:
        """Genera embeddings usando PHASE 2."""
        return []
    
    async def retrieve_context(self, query: str) -> dict:
        """Obtiene contexto de PHASE 2."""
        return {}


class PHASE3Gateway:
    """Gateway para integrar con PHASE 3 Clinical Intelligence."""
    
    def __init__(self):
        self._reasoning_engine = None
        self._evidence_engine = None
        self._decision_engine = None
        self._safety_engine = None
    
    async def validate_with_reasoning(self, claim: str, evidence: list) -> dict:
        """Valida claim con motor de razonamiento de PHASE 3."""
        return {"valid": True, "confidence": 0.8}
    
    async def check_safety(self, content: str) -> list[str]:
        """Verifica seguridad con PHASE 3."""
        return []
    
    async def get_evidence_score(self, citations: list[Citation]) -> float:
        """Obtiene score de evidencia de PHASE 3."""
        return 0.8


class PHASE5Contract:
    """Contrato para output hacia PHASE 5."""
    
    async def provide_knowledge_package(self, package: KnowledgePackage) -> bool:
        """Proporciona Knowledge Package a PHASE 5."""
        # Placeholder - would send to PHASE 5
        return True
    
    async def provide_evidence_package(self, evidence: list[EvidenceTrace]) -> bool:
        """Proporciona Evidence Package a PHASE 5."""
        return True


# =============================================================================
# FACTORIES - Fábricas para crear objetos
# =============================================================================

class KnowledgeAssetFactory:
    """Fábrica para crear KnowledgeAssets."""
    
    @staticmethod
    def create(
        title: str,
        content: str,
        domain: KnowledgeDomain,
        created_by: str = "system",
    ) -> KnowledgeAsset:
        """Crea un nuevo asset de conocimiento."""
        return KnowledgeAsset(
            asset_id=str(uuid.uuid4()),
            version="1.0.0",
            title=title,
            content=content,
            domain=domain,
            created_by=created_by,
            governance_status=GovernanceStatus.DRAFT,
        )
    
    @staticmethod
    def create_version(
        previous: KnowledgeAsset,
        content: str,
        changes_summary: str,
        updated_by: str,
    ) -> KnowledgeAsset:
        """Crea nueva versión de un asset existente."""
        # Parse version
        parts = previous.version.split(".")
        new_patch = int(parts[2]) + 1
        new_version = f"{parts[0]}.{parts[1]}.{new_patch}"
        
        return KnowledgeAsset(
            asset_id=previous.asset_id,
            version=new_version,
            title=previous.title,
            content=content,
            domain=previous.domain,
            metadata=previous.metadata,
            previous_version_id=previous.asset_id,
            created_by=updated_by,
            governance_status=GovernanceStatus.DRAFT,
        )


# =============================================================================
# EVENTS - Eventos de dominio
# =============================================================================

class KnowledgeEvent(str, Enum):
    """Eventos de dominio de conocimiento."""
    DOCUMENT_PROCESSED = "knowledge.document.processed"
    KNOWLEDGE_EXTRACTED = "knowledge.extracted"
    KNOWLEDGE_INDEXED = "knowledge.indexed"
    KNOWLEDGE_QUALITY_ASSESSED = "knowledge.quality.assessed"
    KNOWLEDGE_PUBLISHED = "knowledge.published"
    KNOWLEDGE_UPDATED = "knowledge.updated"
    KNOWLEDGE_SUPERSEDED = "knowledge.superseded"
    KNOWLEDGE_ARCHIVED = "knowledge.archived"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "DocumentFormat",
    "KnowledgeDomain", 
    "ProcessingStatus",
    "QualityLevel",
    "EvidenceLevel",
    "GovernanceStatus",
    "KnowledgeEvent",
    # Contracts
    "IDocumentProcessor",
    "IKnowledgeExtractor",
    "IClinicalEmbedder",
    "IVectorIndexer",
    "IHybridRetriever",
    "IKnowledgeRepository",
    "ICitationTracker",
    # Value Objects
    "EmbeddingVector",
    "SourceReference",
    "Citation",
    "MedicalCode",
    # Entities
    "ProcessedDocument",
    "ExtractedKnowledge",
    "ExtractedEntity",
    "ExtractedConcept",
    "ExtractedRelation",
    "IndexedVector",
    "SearchResult",
    "KnowledgeQuery",
    "RetrievalResult",
    "KnowledgeAsset",
    "KnowledgeVersion",
    "TracedCitation",
    "EvidenceTrace",
    "KnowledgePackage",
    # Gateways
    "PHASE1Gateway",
    "PHASE2Gateway",
    "PHASE3Gateway",
    "PHASE5Contract",
    # Factories
    "KnowledgeAssetFactory",
]
