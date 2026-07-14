# Knowledge Ingestion Pipeline (KIP)

> **This is where EREN really starts to "study".**

Transforms real documents into indexed knowledge.

## Philosophy

The pipeline must:
- ✅ Read documents
- ✅ Extract text
- ✅ Clean text
- ✅ Remove garbage
- ✅ Split into chunks
- ✅ Create metadata
- ✅ Generate embeddings
- ✅ Store in Vector Memory
- ✅ Register the document

The pipeline must NOT:
- ❌ Answer questions
- ❌ Use LLM
- ❌ Do RAG
- ❌ Reason

Only prepare knowledge.

## Architecture

```
PDF / DOCX / TXT / FHIR / HL7
        │
        ▼
Knowledge Ingestion Pipeline
        │
        ├── Extractor
        ├── Cleaner
        ├── Chunker
        ├── Metadata Builder
        ├── Embedding Generator
        └── Vector Memory Writer
        │
        ▼
Knowledge indexed in Vector Memory
```

## Complete Flow

```
Document
        │
        ▼
Extractor
        │
        ▼
Text
        │
        ▼
Cleaner
        │
        ▼
Cleaned Text
        │
        ▼
Chunker
        │
        ▼
Chunks
        │
        ▼
Embedding Generator
        │
        ▼
Embeddings
        │
        ▼
Vector Memory
        │
        ▼
Knowledge registered
```

## Components

| Component | Description |
|-----------|-------------|
| `pipeline.py` | Main orchestration |
| `extractor.py` | Document extraction |
| `cleaner.py` | Text cleaning |
| `chunker.py` | Document chunking |
| `metadata.py` | Metadata building |
| `registry.py` | Document registry |
| `types.py` | Types and models |
| `exceptions.py` | Exception types |

## Supported Formats

| Format | Status |
|--------|--------|
| PDF | ✅ Supported |
| DOCX | ✅ Supported |
| TXT | ✅ Supported |
| Markdown | ✅ Supported |
| HTML | ✅ Supported |
| FHIR | ✅ Supported |
| HL7 | ✅ Supported |

## Usage

### Basic Usage

```python
from core.ingestion import (
    KnowledgeIngestionPipeline,
    RawDocument,
    DocumentType,
)

# Create pipeline
pipeline = KnowledgeIngestionPipeline()

# Create raw document
raw = RawDocument(
    content=open("document.pdf", "rb").read(),
    document_type=DocumentType.PDF,
    source="medical_guideline.pdf",
    filename="medical_guideline.pdf",
)

# Ingest
result = await pipeline.ingest(raw)

print(f"Document: {result.document_id}")
print(f"Chunks: {result.chunks_created}")
print(f"Status: {result.status}")
```

### With Vector Memory

```python
from core.ingestion import KnowledgeIngestionPipeline
from plugins.vector_memory import VectorMemoryPlugin

# Create vector memory plugin
vector_plugin = VectorMemoryPlugin()
await vector_plugin.initialize({})

# Create pipeline with vector memory
pipeline = KnowledgeIngestionPipeline(
    vector_memory_plugin=vector_plugin,
)

# Ingest document
result = await pipeline.ingest(raw)
```

### Batch Ingestion

```python
documents = [
    RawDocument(content=pdf1, type=DocumentType.PDF, source="doc1.pdf"),
    RawDocument(content=pdf2, type=DocumentType.PDF, source="doc2.pdf"),
    RawDocument(content=docx1, type=DocumentType.DOCX, source="doc3.docx"),
]

results = await pipeline.ingest_batch(documents)
```

## Metadata

Documents can include:

| Field | Description |
|-------|-------------|
| `document_id` | Unique identifier |
| `source_type` | Source type (manual, guideline, etc.) |
| `title` | Document title |
| `author` | Author |
| `created_at` | Creation date |
| `medical_specialty` | Medical specialty |
| `language` | Document language |
| `tags` | List of tags |
| `institution` | Institution |
| `department` | Department |

## Output

```
Document
        │
        ▼
324 chunks
        │
        ▼
324 embeddings
        │
        ▼
324 vectors
        │
        ▼
Knowledge registered
```

## Integration

### With Vector Memory Plugin

```python
from core.ingestion import KnowledgeIngestionPipeline
from core.retrieval import SemanticRetrievalEngine

# Create components
vector_plugin = VectorMemoryPlugin()
await vector_plugin.initialize({})

pipeline = KnowledgeIngestionPipeline(
    vector_memory_plugin=vector_plugin,
)

retrieval_engine = SemanticRetrievalEngine()
retrieval_engine.register_memory_provider(
    MemorySource.VECTOR,
    vector_plugin.memory_interface.read,
)

# Ingest and retrieve
await pipeline.ingest(raw_document)
context = retrieval_engine.retrieve_text("What does the guideline say?")
```

### With Embedding Layer

```python
from core.ingestion import KnowledgeIngestionPipeline
from core.embeddings import EmbeddingManager

embedding_manager = EmbeddingManager()
embedding_manager.registry.register(OpenAIEmbeddingProvider())

pipeline = KnowledgeIngestionPipeline()
```

## Testing

```bash
pytest tests/unit/core/ingestion/ -v
```

## License

EREN OS License
