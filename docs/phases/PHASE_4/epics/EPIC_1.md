# EPIC 1: Biomedical Document Processing Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Procesar cualquier documento biomédico antes de convertirlo en conocimiento.

---

## Responsabilidad

**Normalizar documentos clínicos.**

EPIC 1 es responsable de:
- Parsear documentos de múltiples formatos
- Extraer contenido estructurado (tablas, figuras, secciones)
- Extraer metadata médica especializada
- Limpiar y normalizar texto médico
- Detectar idioma

---

## Dependencias

### Fases
- **FASE 1**: Consume Device, Knowledge, Incident, Asset contexts
- **FASE 2**: Provee entrada para embeddings y retrieval

### EPICs
- **EPIC 0**: Usa Foundation (tipos, contratos, excepciones, eventos)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                EPIC 1: Document Processing Engine              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        INPUT                               │   │
│  │     (PDF, DOCX, HTML, Markdown, TXT)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       PARSERS                              │   │
│  │  ├── PDFParser ──────── PyPDF2, pdfplumber             │   │
│  │  ├── DOCXParser ────── python-docx                     │   │
│  │  ├── HTMLParser ─────── BeautifulSoup                    │   │
│  │  ├── MarkdownParser ──── Custom                           │   │
│  │  └── TextParser ─────── Built-in                         │   │
│  │                                                              │   │
│  │              ParserFactory (crea parser según formato)       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      EXTRACTORS                           │   │
│  │  ├── TableExtractor ── Detecta tablas estructuradas     │   │
│  │  ├── FigureExtractor ─ Detecta figuras y referencias    │   │
│  │  ├── MetadataExtractor ─ Extrae metadata médica          │   │
│  │  ├── SectionExtractor ─ Extrae secciones                 │   │
│  │  └── LanguageDetector ─ Detecta idioma                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      NORMALIZERS                          │   │
│  │  ├── MedicalCleaner ─── Limpia símbolos médicos          │   │
│  │  ├── ContentCleaner ─── Limpia contenido general         │   │
│  │  ├── StructureNormalizer ─ Normaliza estructura          │   │
│  │  └── TerminologyNormalizer ─ Normaliza terminología       │   │
│  │                                                              │   │
│  │              CompositeNormalizer (aplica todos)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        OUTPUT                              │   │
│  │     BiomedicalDocument (normalizado, estructurado)       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic1_document_processing/
├── __init__.py                    # Módulo principal
├── parsers/
│   └── __init__.py               # PDFParser, DOCXParser, HTMLParser, etc.
├── extractors/
│   └── __init__.py               # TableExtractor, FigureExtractor, etc.
└── normalizers/
    └── __init__.py               # MedicalCleaner, TerminologyNormalizer, etc.
```

---

## Componentes

### 1. Parsers

| Parser | Formato | Descripción |
|--------|---------|-------------|
| `PDFParser` | PDF | Extrae texto, páginas, tablas |
| `DOCXParser` | DOCX | Extrae texto, estilos, tablas |
| `HTMLParser` | HTML | Limpia y extrae texto |
| `MarkdownParser` | Markdown | Detecta secciones, headers |
| `TextParser` | TXT | Parse básico de texto |
| `ParserFactory` | - | Crea parser según formato |

```python
# Uso de parsers
factory = ParserFactory()
parser = factory.get_parser(DocumentFormat.PDF)
content = await parser.parse(pdf_bytes)
```

### 2. Extractors

| Extractor | Descripción |
|-----------|-------------|
| `TableExtractor` | Detecta tablas markdown, CSV, estructuradas |
| `FigureExtractor` | Detecta figuras y referencias |
| `MetadataExtractor` | Extrae DOI, PMID, códigos ICD |
| `SectionExtractor` | Detecta headers y secciones |
| `LanguageDetector` | Detecta idioma del texto |

```python
# Extracción de tablas
extractor = TableExtractor()
tables = extractor.extract(content, page_number=1)
for table in tables:
    print(table.to_markdown())
```

### 3. Normalizers

| Normalizer | Descripción |
|------------|-------------|
| `MedicalCleaner` | Limpia símbolos médicos (µg→mcg, smart quotes) |
| `ContentCleaner` | Remueve headers/footers, artifacts OCR |
| `StructureNormalizer` | Normaliza estructura de headers |
| `TerminologyNormalizer` | Expande abreviaturas médicas |
| `CompositeNormalizer` | Aplica múltiples normalizadores |

```python
# Normalización completa
normalizer = MedicalNormalizerFactory.create_full()
result = normalizer.normalize(text)
print(f"Changes: {result.changes}")
print(f"Word count: {result.word_count}")
```

---

## Domain Objects

### BiomedicalDocument

```python
@dataclass
class BiomedicalDocument:
    """Documento biomédico normalizado."""
    document_id: str
    title: str
    content: str
    format: DocumentFormat
    metadata: MedicalMetadata
    tables: list[Table]
    figures: list[Figure]
    sections: list[Section]
    language: str
    word_count: int
    processed_at: datetime
```

### MedicalMetadata

```python
@dataclass
class MedicalMetadata:
    """Metadata médica especializada."""
    pmid: str = ""
    pmcid: str = ""
    doi: str = ""
    icd_codes: list[str] = field(default_factory=list)
    snomed_codes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    medical_specialty: str = ""
    peer_reviewed: bool = False
```

### Table

```python
@dataclass
class Table:
    """Tabla extraída."""
    table_id: str
    headers: list[str]
    rows: list[list[str]]
    caption: str = ""
    page_number: int = 0
    confidence: float = 1.0
```

---

## Flujo de Procesamiento

```
1. INPUT: Documento (PDF, DOCX, HTML, etc.)
          │
          ▼
2. PARSE: ParserFactory → Parser específico
          │
          ▼
3. EXTRACT: Tablas, Figuras, Metadata, Secciones
          │
          ▼
4. NORMALIZE: MedicalCleaner, TerminologyNormalizer
          │
          ▼
5. OUTPUT: BiomedicalDocument (normalizado, estructurado)
          │
          ▼
6. NEXT EPIC: EPIC 2 (Knowledge Extraction)
```

---

## Uso

### Procesamiento básico

```python
from core.PHASE_4.epic1_document_processing import (
    ParserFactory,
    TableExtractor,
    MedicalNormalizerFactory,
)

# 1. Parsear
factory = ParserFactory()
parser = factory.get_parser(DocumentFormat.PDF)
content = await parser.parse(pdf_bytes)

# 2. Extraer tablas
table_extractor = TableExtractor()
tables = table_extractor.extract(content.text)

# 3. Normalizar
normalizer = MedicalNormalizerFactory.create_full()
normalized = normalizer.normalize(content.text)
```

### Pipeline completo

```python
from core.PHASE_4.epic1_document_processing import (
    DocumentProcessingPipeline,
    DocumentFormat,
)

pipeline = DocumentProcessingPipeline()

result = await pipeline.process(
    content=pdf_bytes,
    format=DocumentFormat.PDF,
    metadata={'source': 'FDA'},
)

print(f"Title: {result.metadata.title}")
print(f"Tables: {len(result.tables)}")
print(f"Word count: {result.word_count}")
```

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `DOCUMENT_RECEIVED` | Documento recibido |
| `DOCUMENT_PROCESSED` | Documento procesado exitosamente |
| `DOCUMENT_FAILED` | Falló procesamiento |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `DocumentParseError` | Falló parsing del documento |
| `UnsupportedFormatError` | Formato no soportado |
| `DocumentTooLargeError` | Documento excede límite |
| `OCRFailedError` | Falló OCR |

---

## Concatenación

```
FASE 1 ──► EPIC 1 (consume Knowledge articles)
EPIC 0 ──► EPIC 1 (usa Foundation types)
EPIC 1 ──► EPIC 2 (output: BiomedicalDocument)
EPIC 1 ──► FASE 2 (provee entrada para embeddings)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 2: Knowledge Extraction
- EPIC 3: Clinical Embeddings

---

*EREN PHASE 4 - EPIC 1*
*Architecture Board - 2026-07-23*
