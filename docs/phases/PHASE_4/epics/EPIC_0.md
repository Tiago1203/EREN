# EPIC 0: Knowledge Infrastructure Foundation

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Construir toda la infraestructura base sobre la cual funcionará la plataforma de conocimiento.

---

## Responsabilidad

**Shared Kernel** de toda la FASE 4.

Este módulo es el fundamento sobre el cual se construyen todos los demás EPICs. Proporciona:

- Tipos fundamentales comunes
- Interfaces y contratos
- Configuración centralizada
- Excepciones especializadas
- Eventos de dominio
- Gateways hacia otras fases
- Implementaciones base

---

## Dependencias

### Fases
- **FASE 1**: Consume Device, Knowledge, Incident, Asset contexts
- **FASE 2**: Extiende embeddings, retrieval, context building
- **FASE 3**: Integra reasoning, evidence, decision engines

### EPICs
- Ninguno (este es el EPIC base)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4 - EPIC 0: Foundation                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     KNOWLEDGE KERNEL                     │   │
│  │  ├── Enums (DocumentFormat, KnowledgeDomain, etc.)      │   │
│  │  ├── Value Objects (EmbeddingVector, Citation, etc.)     │   │
│  │  ├── Domain Objects (KnowledgeAsset, KnowledgeChunk)     │   │
│  │  └── Entities (ProcessedDocument, ExtractedKnowledge)    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       CONTRACTS                          │   │
│  │  ├── IDocumentProcessor                                  │   │
│  │  ├── IKnowledgeExtractor                                │   │
│  │  ├── IClinicalEmbedder                                  │   │
│  │  ├── IVectorIndexer                                     │   │
│  │  ├── IHybridRetriever                                   │   │
│  │  ├── IKnowledgeRepository                               │   │
│  │  ├── ICitationTracker                                   │   │
│  │  └── IChunker                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    BASE IMPLEMENTATIONS                  │   │
│  │  ├── BaseKnowledgeService                               │   │
│  │  ├── BaseRetriever                                      │   │
│  │  ├── BaseIndexer                                        │   │
│  │  ├── BaseChunker                                        │   │
│  │  ├── BaseEmbeddingProvider                              │   │
│  │  ├── BaseVectorRepository                                │   │
│  │  ├── BaseCitationBuilder                                 │   │
│  │  └── BaseRAGPipeline                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      GATEWAYS                            │   │
│  │  ├── PHASE1Gateway ────────► PHASE_1 Contexts           │   │
│  │  ├── PHASE2Gateway ────────► PHASE_2 AI Core            │   │
│  │  ├── PHASE3Gateway ────────► PHASE_3 Intelligence      │   │
│  │  └── PHASE5Contract ◄──────── PHASE_5 Output            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     INFRASTRUCTURE                        │   │
│  │  ├── Config (PHASE4Config, EmbeddingConfig, etc.)       │   │
│  │  ├── Exceptions (PHASE4BaseException, etc.)             │   │
│  │  ├── Events (DomainEvent, EventType, etc.)              │   │
│  │  ├── Constants (VERSION, DEFAULT_*, MAX_*)               │   │
│  │  └── Metrics (PHASE4Metrics)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/foundation/
├── __init__.py              # Módulo principal (exports)
├── constants/
│   └── __init__.py         # Constantes globales
├── config/
│   └── __init__.py         # Configuración
├── exceptions/
│   └── __init__.py         # Excepciones
└── events/
    └── __init__.py         # Eventos de dominio
```

---

## Componentes

### 1. Knowledge Kernel

#### Enums

| Enum | Descripción |
|------|-------------|
| `DocumentFormat` | PDF, DOCX, HTML, MARKDOWN, TEXT, XML, JSON |
| `KnowledgeDomain` | CARDIOLOGY, RADIOLOGY, ONCOLOGY, NEUROLOGY, etc. |
| `ProcessingStatus` | PENDING, PROCESSING, COMPLETED, FAILED, PARTIAL |
| `QualityLevel` | HIGH, MEDIUM, LOW, UNVERIFIED |
| `EvidenceLevel` | LEVEL_1A a LEVEL_5 (Oxford) |
| `GovernanceStatus` | DRAFT, REVIEW, APPROVED, PUBLISHED, ARCHIVED, SUPERSEDED |

#### Value Objects

| VO | Descripción |
|----|-------------|
| `EmbeddingVector` | Vector de embedding con modelo y dimensión |
| `SourceReference` | Referencia a fuente (DOI, URL, autores, etc.) |
| `Citation` | Citación completa con nivel de evidencia |
| `MedicalCode` | Código médico (ICD10, SNOMED, LOINC, RxNorm) |

#### Domain Objects

| Object | Descripción |
|--------|-------------|
| `KnowledgeSource` | Fuente de conocimiento (PubMed, FDA, etc.) |
| `KnowledgeMetadata` | Metadata estructurada del conocimiento |
| `KnowledgeChunk` | Chunk de conocimiento con posición |
| `KnowledgeCollection` | Colección de documentos |
| `RetrievalContext` | Contexto de retrieval |
| `SearchRequest` | Solicitud de búsqueda |

#### Entities

| Entity | Descripción |
|--------|-------------|
| `ProcessedDocument` | Documento con contenido extraído |
| `ExtractedKnowledge` | Conocimiento extraído con entidades |
| `ExtractedEntity` | Entidad médica reconocida |
| `ExtractedConcept` | Concepto clínico |
| `ExtractedRelation` | Relación entre entidades |
| `IndexedVector` | Vector indexado en colección |
| `SearchResult` | Resultado de búsqueda |
| `KnowledgeQuery` | Query para retrieval |
| `RetrievalResult` | Resultado de retrieval |
| `KnowledgeAsset` | Asset de conocimiento versionado |
| `KnowledgeVersion` | Versión de asset |
| `TracedCitation` | Citación con trazabilidad |
| `EvidenceTrace` | Trace de evidencia |
| `KnowledgePackage` | Paquete consolidado (output final) |

### 2. Contracts (Interfaces)

```python
class IDocumentProcessor(Protocol):
    async def process(content: bytes, format: DocumentFormat, metadata: dict) -> ProcessedDocument: ...

class IKnowledgeExtractor(Protocol):
    async def extract(document: ProcessedDocument) -> ExtractedKnowledge: ...

class IClinicalEmbedder(Protocol):
    async def embed(text: str, model: str) -> EmbeddingVector: ...
    async def embed_batch(texts: list[str], model: str) -> list[EmbeddingVector]: ...

class IVectorIndexer(Protocol):
    async def index(vectors: list[IndexedVector]) -> bool: ...
    async def search(query: EmbeddingVector, top_k: int) -> list[SearchResult]: ...

class IHybridRetriever(Protocol):
    async def retrieve(query: KnowledgeQuery) -> RetrievalResult: ...

class IKnowledgeRepository(Protocol):
    async def store(entity) -> str: ...
    async def get(id: str): ...
    async def update(id: str, entity) -> bool: ...

class ICitationTracker(Protocol):
    async def cite(claim: str, source: Citation) -> TracedCitation: ...
    async def get_trace(citation_id: str) -> Optional[EvidenceTrace]: ...

class IChunker(Protocol):
    def chunk(text: str, chunk_size: int, overlap: int) -> list[str]: ...
```

### 3. Base Implementations

| Clase | Descripción |
|-------|-------------|
| `BaseKnowledgeService` | Clase base para servicios |
| `BaseRetriever` | Clase base para retrievers |
| `BaseIndexer` | Clase base para indexadores |
| `BaseChunker` | Chunking recursivo básico |
| `BaseEmbeddingProvider` | Clase base para providers |
| `BaseVectorRepository` | Clase base para repos vectoriales |
| `BaseCitationBuilder` | Clase base para constructores de citación |
| `BaseRAGPipeline` | Clase base para pipelines RAG |

### 4. Gateways

```python
class PHASE1Gateway:
    """Acceso a PHASE 1 - Business Domain"""
    async def get_knowledge_articles(domain, limit) -> list[dict]: ...
    async def get_device_manuals(device_category) -> list[dict]: ...
    async def get_incident_reports(device_id) -> list[dict]: ...
    async def get_related_knowledge(entity_id, entity_type) -> list[dict]: ...

class PHASE2Gateway:
    """Acceso a PHASE 2 - AI Core"""
    async def get_embeddings(texts, model) -> list[EmbeddingVector]: ...
    async def retrieve_context(query) -> dict: ...
    async def build_prompt_context(query, retrieved) -> str: ...

class PHASE3Gateway:
    """Acceso a PHASE 3 - Clinical Intelligence"""
    async def validate_with_reasoning(claim, evidence) -> dict: ...
    async def check_safety(content) -> list[str]: ...
    async def get_evidence_score(citations) -> float: ...
    async def enhance_with_reasoning(knowledge_package) -> KnowledgePackage: ...

class PHASE5Contract:
    """Output hacia PHASE 5"""
    async def provide_knowledge_package(package) -> bool: ...
    async def provide_evidence_package(evidence) -> bool: ...
    async def provide_clinical_context(context) -> bool: ...
```

### 5. Configuración

```python
@dataclass
class PHASE4Config:
    environment: Environment
    service_name: str
    embedding: EmbeddingConfig
    vector_store: VectorStoreConfig
    document_processing: DocumentProcessingConfig
    knowledge_extraction: KnowledgeExtractionConfig
    retrieval: RetrievalConfig
    rag: RAGConfig
    citation: CitationConfig
    quality: QualityConfig
    governance: GovernanceConfig
    sync: SyncConfig
    logging: LoggingConfig
    observability: ObservabilityConfig
```

### 6. Excepciones

Jerarquía de excepciones:

```
PHASE4BaseException
├── KnowledgeNotFoundError
├── KnowledgeVersionNotFoundError
├── KnowledgeValidationError
├── KnowledgeGovernanceError
├── DocumentParseError
├── UnsupportedFormatError
├── DocumentTooLargeError
├── OCRFailedError
├── ExtractionFailedError
├── EntityRecognitionError
├── CodeLinkingError
├── EmbeddingFailedError
├── ModelNotFoundError
├── EmbeddingDimensionMismatchError
├── IndexFailedError
├── CollectionNotFoundError
├── CollectionExistsError
├── VectorStoreError
├── RetrievalFailedError
├── QueryValidationError
├── NoResultsError
├── CitationFailedError
├── DOIResolveError
├── SourceNotAccessibleError
├── QualityAssessmentFailedError
├── BiasDetectionError
├── SyncFailedError
├── SourceUnavailableError
├── GovernanceViolationError
├── RetentionPolicyError
└── RollbackError
```

### 7. Eventos

| Tipo | Descripción |
|------|-------------|
| `DOCUMENT_RECEIVED` | Documento recibido |
| `DOCUMENT_PROCESSED` | Documento procesado |
| `DOCUMENT_FAILED` | Falló procesamiento |
| `EXTRACTION_STARTED` | Extracción iniciada |
| `EXTRACTION_COMPLETED` | Extracción completada |
| `EMBEDDING_GENERATED` | Embedding generado |
| `INDEXING_STARTED` | Indexación iniciada |
| `INDEXING_COMPLETED` | Indexación completada |
| `RETRIEVAL_STARTED` | Retrieval iniciado |
| `RETRIEVAL_COMPLETED` | Retrieval completado |
| `CITATION_CREATED` | Citación creada |
| `QUALITY_ASSESSED` | Calidad evaluada |
| `BIAS_DETECTED` | Sesgo detectado |
| `ASSET_CREATED` | Asset creado |
| `ASSET_PUBLISHED` | Asset publicado |
| `ASSET_ARCHIVED` | Asset archivado |
| `SYNC_COMPLETED` | Sincronización completada |

### 8. Constants

| Constante | Valor |
|-----------|-------|
| `VERSION` | "2.0.0" |
| `DEFAULT_EMBEDDING_MODEL` | PubMedBERT |
| `DEFAULT_EMBEDDING_DIMENSION` | 768 |
| `DEFAULT_TOP_K` | 10 |
| `MAX_RESULTS` | 100 |
| `BM25_K1` | 1.5 |
| `BM25_B` | 0.75 |
| `RRF_K_PARAM` | 60 |
| `HYBRID_VECTOR_WEIGHT` | 0.7 |
| `HYBRID_KEYWORD_WEIGHT` | 0.3 |
| `MAX_CONTEXT_TOKENS` | 4000 |
| `MIN_CITATIONS` | 3 |

### 9. Factories

| Factory | Descripción |
|---------|-------------|
| `KnowledgeAssetFactory` | Crea KnowledgeAssets |
| `DocumentFactory` | Crea ProcessedDocuments |
| `ChunkFactory` | Crea KnowledgeChunks |

---

## Uso

```python
from core.PHASE_4.foundation import (
    # Configuración
    PHASE4Config,
    # Enums
    DocumentFormat,
    KnowledgeDomain,
    # Contracts
    IDocumentProcessor,
    # Gateways
    PHASE1Gateway,
    PHASE2Gateway,
    PHASE3Gateway,
    # Exceptions
    KnowledgeNotFoundError,
    # Events
    DomainEvent,
    EventType,
    # Base implementations
    BaseChunker,
    BaseKnowledgeService,
)

# Crear configuración
config = PHASE4Config.development()

# Usar gateway
phase1 = PHASE1Gateway()
articles = await phase1.get_knowledge_articles(KnowledgeDomain.CARDIOLOGY)

# Usar exception
raise KnowledgeNotFoundError(asset_id="123")

# Usar base implementation
chunker = BaseChunker(chunk_size=512)
chunks = chunker.chunk("Large text to chunk...")
```

---

## Concatenación

```
FASE 1 ──► PHASE1Gateway ──► Foundation
FASE 2 ──► PHASE2Gateway ──► Foundation
FASE 3 ──► PHASE3Gateway ──► Foundation
Foundation ──► PHASE5Contract ──► PHASE 5
Foundation ◄── Todos los EPICs
```

---

## Métricas

```python
@dataclass
class PHASE4Metrics:
    documents_processed: int
    documents_failed: int
    embeddings_generated: int
    vectors_indexed: int
    queries_answered: int
    citations_generated: int
    avg_retrieval_time_ms: float
    avg_processing_time_ms: float
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 1: Document Processing
- EPIC 2: Knowledge Extraction
- EPIC 3: Clinical Embeddings

---

*EREN PHASE 4 - EPIC 0*
*Architecture Board - 2026-07-23*
