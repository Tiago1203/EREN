"""
PHASE 4 - EPIC 0: Knowledge Infrastructure Foundation

Shared Kernel que conecta PHASE 1, 2, 3 con los EPICs de PHASE 4.
Proporciona contratos, interfaces, tipos comunes y configuración base.

Este módulo es el fundamento sobre el cual se construyen todos los demás EPICs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Protocol, Optional, TypeVar, Generic
import uuid

# Importar submódulos del foundation
from core.PHASE_4.foundation.constants import *
from core.PHASE_4.foundation.exceptions import *
from core.PHASE_4.foundation.events import *
from core.PHASE_4.foundation.config import *


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
# GENERIC TYPE VARIABLES
# =============================================================================

T = TypeVar("T")
TEntity = TypeVar("TEntity")
TId = TypeVar("TId", bound=str)


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


class IKnowledgeRepository(Protocol[TEntity, TId]):
    """Protocolo genérico para repositorio de conocimiento."""
    
    async def store(self, entity: TEntity) -> TId:
        """Almacena entidad."""
        ...
    
    async def get(self, id: TId) -> Optional[TEntity]:
        """Recupera entidad por ID."""
        ...
    
    async def update(self, id: TId, entity: TEntity) -> bool:
        """Actualiza entidad."""
        ...


class ICitationTracker(Protocol):
    """Protocolo para trazabilidad de citas."""
    
    async def cite(self, claim: str, source: Citation) -> TracedCitation:
        """Registra citación para claim."""
        ...
    
    async def get_trace(self, citation_id: str) -> Optional[EvidenceTrace]:
        """Obtiene trace de citación."""
        ...


class IChunker(Protocol):
    """Protocolo para chunking de documentos."""
    
    def chunk(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Divide texto en chunks."""
        ...


class IBaseService(Protocol[T]):
    """Protocolo base para servicios."""
    
    async def initialize(self) -> None:
        """Inicializa el servicio."""
        ...
    
    async def health_check(self) -> dict:
        """Verifica salud del servicio."""
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
# DOMAIN OBJECTS - Objetos de dominio adicionales
# =============================================================================

@dataclass
class KnowledgeSource:
    """Fuente de conocimiento."""
    source_id: str
    source_type: str  # pubmed, fda, guideline, manual, etc
    name: str
    url: str = ""
    description: str = ""
    credibility_score: float = 0.5
    last_synced: datetime | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class KnowledgeMetadata:
    """Metadata de conocimiento."""
    title: str
    domain: KnowledgeDomain
    medical_specialty: str = ""
    device_categories: list[str] = field(default_factory=list)
    icd_codes: list[str] = field(default_factory=list)
    snomed_codes: list[str] = field(default_factory=list)
    loinc_codes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    language: str = "en"
    source: str = ""
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class KnowledgeChunk:
    """Chunk de conocimiento."""
    chunk_id: str
    content: str
    position: int  # Order in document
    document_id: str
    metadata: KnowledgeMetadata = field(default_factory=KnowledgeMetadata)
    embedding: EmbeddingVector | None = None


@dataclass
class KnowledgeCollection:
    """Colección de conocimiento."""
    collection_id: str
    name: str
    description: str = ""
    domain: KnowledgeDomain = KnowledgeDomain.GENERAL
    document_count: int = 0
    chunk_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class RetrievalContext:
    """Contexto de retrieval."""
    query: str
    retrieved_chunks: list[KnowledgeChunk] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    retrieval_time_ms: int = 0


@dataclass
class SearchRequest:
    """Solicitud de búsqueda."""
    query: str
    domain: KnowledgeDomain | None = None
    filters: dict = field(default_factory=dict)
    top_k: int = 10
    min_score: float = 0.5
    include_metadata: bool = True
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))


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
    payload: dict = field(default_factory=dict)
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
# BASE IMPLEMENTATIONS - Implementaciones base para servicios
# =============================================================================

class BaseKnowledgeService:
    """Clase base para servicios de conocimiento."""
    
    def __init__(self, config: PHASE4Config | None = None):
        self.config = config or PHASE4Config()
        self._initialized = False
        self._event_publisher = InMemoryEventPublisher()
    
    async def initialize(self) -> None:
        """Inicializa el servicio."""
        self._initialized = True
    
    async def health_check(self) -> dict:
        """Verifica salud del servicio."""
        return {
            "service": self.__class__.__name__,
            "initialized": self._initialized,
            "status": "healthy" if self._initialized else "not_initialized",
        }


class BaseRetriever:
    """Clase base para retrievers."""
    
    def __init__(self, config: RetrievalConfig | None = None):
        self.config = config or RetrievalConfig()


class BaseIndexer:
    """Clase base para indexadores."""
    
    def __init__(self, config: VectorStoreConfig | None = None):
        self.config = config or VectorStoreConfig()


class BaseChunker:
    """Clase base para chunkers."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str) -> list[str]:
        """Divide texto en chunks."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence or paragraph
            if end < len(text):
                for sep in ['.\n', '.\n\n', '\n\n', '. ']:
                    last_sep = chunk.rfind(sep)
                    if last_sep > self.chunk_size // 2:
                        chunk = chunk[:last_sep + len(sep.strip())]
                        end = start + len(chunk)
                        break
            
            chunks.append(chunk.strip())
            start = end - self.overlap
        
        return chunks


class BaseEmbeddingProvider:
    """Clase base para providers de embedding."""
    
    def __init__(self, config: EmbeddingConfig | None = None):
        self.config = config or EmbeddingConfig()


class BaseVectorRepository:
    """Clase base para repositorio vectorial."""
    
    def __init__(self, config: VectorStoreConfig | None = None):
        self.config = config or VectorStoreConfig()


class BaseCitationBuilder:
    """Clase base para constructores de citación."""
    
    def __init__(self, config: CitationConfig | None = None):
        self.config = config or CitationConfig()


class BaseRAGPipeline:
    """Clase base para pipelines RAG."""
    
    def __init__(self, config: RAGConfig | None = None):
        self.config = config or RAGConfig()


# =============================================================================
# GATEWAYS - Conexiones con otras fases
# =============================================================================

class PHASE1Gateway:
    """Gateway para consumir conocimiento de PHASE 1.
    
    Proporciona acceso a:
    - Knowledge Context (KnowledgeArticle, Category, Tag)
    - Device Context (manuales, especificaciones)
    - Incident Context (reportes, resolutions)
    """
    
    def __init__(self):
        self._knowledge_repo = None
        self._device_repo = None
        self._incident_repo = None
    
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
    
    async def get_related_knowledge(self, entity_id: str, entity_type: str) -> list[dict]:
        """Obtiene conocimiento relacionado a una entidad."""
        return []


class PHASE2Gateway:
    """Gateway para extender funcionalidades de PHASE 2.
    
    Proporciona acceso a:
    - Context Builder
    - Prompt Builder
    - Embedding Services
    - Memory Manager
    """
    
    def __init__(self):
        self._embedding_manager = None
        self._retrieval_engine = None
        self._context_builder = None
        self._prompt_builder = None
    
    async def get_embeddings(self, texts: list[str], model: str) -> list[EmbeddingVector]:
        """Genera embeddings usando PHASE 2."""
        return []
    
    async def retrieve_context(self, query: str) -> dict:
        """Obtiene contexto de PHASE 2."""
        return {}
    
    async def build_prompt_context(self, query: str, retrieved: list) -> str:
        """Construye contexto para prompt."""
        return ""


class PHASE3Gateway:
    """Gateway para integrar con PHASE 3 Clinical Intelligence.
    
    Proporciona acceso a:
    - Reasoning Engine
    - Evidence Retrieval
    - Confidence Engine
    - Safety Engine
    - Decision Engine
    """
    
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
    
    async def enhance_with_reasoning(self, knowledge_package: KnowledgePackage) -> KnowledgePackage:
        """Mejora paquete de conocimiento con razonamiento."""
        return knowledge_package


class PHASE5Contract:
    """Contrato para output hacia PHASE 5.
    
    PHASE 4 produce:
    - Knowledge Package
    - Evidence Package
    - Clinical Context
    - Verified Citations
    """
    
    def __init__(self):
        self._client = None
    
    async def provide_knowledge_package(self, package: KnowledgePackage) -> bool:
        """Proporciona Knowledge Package a PHASE 5."""
        return True
    
    async def provide_evidence_package(self, evidence: list[EvidenceTrace]) -> bool:
        """Proporciona Evidence Package a PHASE 5."""
        return True
    
    async def provide_clinical_context(self, context: RetrievalContext) -> bool:
        """Proporciona Clinical Context a PHASE 5."""
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


class DocumentFactory:
    """Fábrica para crear documentos procesados."""
    
    @staticmethod
    def create(
        document_id: str,
        content: str,
        format: DocumentFormat,
        metadata: dict | None = None,
    ) -> ProcessedDocument:
        """Crea un documento procesado."""
        return ProcessedDocument(
            document_id=document_id,
            content=content,
            format=format,
            metadata=metadata or {},
        )


class ChunkFactory:
    """Fábrica para crear chunks de conocimiento."""
    
    @staticmethod
    def create(
        content: str,
        position: int,
        document_id: str,
        metadata: KnowledgeMetadata | None = None,
    ) -> KnowledgeChunk:
        """Crea un chunk de conocimiento."""
        return KnowledgeChunk(
            chunk_id=str(uuid.uuid4()),
            content=content,
            position=position,
            document_id=document_id,
            metadata=metadata or KnowledgeMetadata(title="", domain=KnowledgeDomain.GENERAL),
        )


# =============================================================================
# METRICS - Métricas del sistema
# =============================================================================

@dataclass
class PHASE4Metrics:
    """Métricas de PHASE 4."""
    documents_processed: int = 0
    documents_failed: int = 0
    embeddings_generated: int = 0
    vectors_indexed: int = 0
    queries_answered: int = 0
    citations_generated: int = 0
    avg_retrieval_time_ms: float = 0.0
    avg_processing_time_ms: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "documents_processed": self.documents_processed,
            "documents_failed": self.documents_failed,
            "embeddings_generated": self.embeddings_generated,
            "vectors_indexed": self.vectors_indexed,
            "queries_answered": self.queries_answered,
            "citations_generated": self.citations_generated,
            "avg_retrieval_time_ms": self.avg_retrieval_time_ms,
            "avg_processing_time_ms": self.avg_processing_time_ms,
        }


# =============================================================================
# KNOWLEDGE EVENT ENUM (alias for backward compatibility)
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
    # Version
    "VERSION",
    "PHASE",
    "EPIC",
    # Enums
    "DocumentFormat",
    "KnowledgeDomain", 
    "ProcessingStatus",
    "QualityLevel",
    "EvidenceLevel",
    "GovernanceStatus",
    "KnowledgeEvent",
    "Environment",
    "EventType",
    # Contracts
    "IDocumentProcessor",
    "IKnowledgeExtractor",
    "IClinicalEmbedder",
    "IVectorIndexer",
    "IHybridRetriever",
    "IKnowledgeRepository",
    "ICitationTracker",
    "IChunker",
    "IBaseService",
    # Value Objects
    "EmbeddingVector",
    "SourceReference",
    "Citation",
    "MedicalCode",
    # Domain Objects
    "KnowledgeSource",
    "KnowledgeMetadata",
    "KnowledgeChunk",
    "KnowledgeCollection",
    "RetrievalContext",
    "SearchRequest",
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
    # Base Implementations
    "BaseKnowledgeService",
    "BaseRetriever",
    "BaseIndexer",
    "BaseChunker",
    "BaseEmbeddingProvider",
    "BaseVectorRepository",
    "BaseCitationBuilder",
    "BaseRAGPipeline",
    # Factories
    "KnowledgeAssetFactory",
    "DocumentFactory",
    "ChunkFactory",
    # Config
    "PHASE4Config",
    "EmbeddingConfig",
    "VectorStoreConfig",
    "DocumentProcessingConfig",
    "RetrievalConfig",
    "RAGConfig",
    "CitationConfig",
    "QualityConfig",
    "GovernanceConfig",
    "SyncConfig",
    "LoggingConfig",
    "ObservabilityConfig",
    # Exceptions
    "PHASE4BaseException",
    "KnowledgeNotFoundError",
    "DocumentParseError",
    "EmbeddingFailedError",
    # Events
    "DomainEvent",
    "InMemoryEventPublisher",
    "IEventPublisher",
    # Metrics
    "PHASE4Metrics",
]
