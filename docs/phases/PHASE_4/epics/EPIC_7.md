# EPIC 7: Citation & Traceability Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Garantizar trazabilidad completa.

---

## Responsabilidad

**Generar citas verificables.**

EPIC 7 es responsable de:
- Generar citas en múltiples estilos (APA, Vancouver, etc.)
- Resolver DOIs y PMIDs
- Verificar fuentes clínicas
- Mantener pista de auditoría
- Construir cadenas de citación

---

## Dependencias

### EPICs
- **EPIC 6**: Consume EvidencePackage de Clinical RAG Pipeline

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│            EPIC 7: Citation & Traceability Engine                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     EvidencePackage (from EPIC 6)                      │   │
│  │     Source documents                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      CITATIONS                             │   │
│  │  ├── Citation ─────────────────► Citation model           │   │
│  │  ├── ClinicalCitationBuilder ──► Build citations         │   │
│  │  └── CitationValidator ───────► Validate citations       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     REFERENCES                              │   │
│  │  ├── Reference ─────────────────► Reference model         │   │
│  │  ├── DOIResolver ──────────────► Resolve DOIs           │   │
│  │  ├── PubMedResolver ───────────► Resolve PMIDs          │   │
│  │  └── ReferenceIndexer ──────────► Index references       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       SOURCES                               │   │
│  │  ├── SourceEvidence ───────────► Source evidence          │   │
│  │  ├── ClinicalSourceVerifier ───► Verify sources          │   │
│  │  ├── SourceTracker ────────────► Track usage             │   │
│  │  └── AuditTrail ───────────────► Audit log               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     Citation + Traceability (auditable)                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic7_citation_traceability/
├── __init__.py                    # Módulo principal
├── citations/                      # Generación de citas
│   └── __init__.py              # Citation, CitationBuilder, etc.
├── references/                    # Gestión de referencias
│   └── __init__.py             # Reference, DOIResolver, etc.
└── sources/                      # Verificación de fuentes
    └── __init__.py             # SourceVerifier, AuditTrail, etc.
```

---

## Componentes

### 1. Citations

| Componente | Descripción |
|------------|-------------|
| `Citation` | Modelo de citación |
| `ClinicalCitationBuilder` | Builder de citaciones clínicas |
| `CitationValidator` | Validador de citaciones |

**Estilos de citación:**
- `APA` - Autor, año, título, revista
- `Vancouver` - Numérico, Vancouver style
- `MLA` - Modern Language Association
- `Chicago` - Author-date
- `AMA` - American Medical Association

### 2. References

| Componente | Descripción |
|------------|-------------|
| `Reference` | Modelo de referencia |
| `DOIResolver` | Resolución de DOIs |
| `PubMedResolver` | Resolución de PMIDs |
| `ReferenceIndexer` | Indexación de referencias |

### 3. Sources

| Componente | Descripción |
|------------|-------------|
| `SourceEvidence` | Evidencia de fuente |
| `ClinicalSourceVerifier` | Verificador de fuentes clínicas |
| `SourceTracker` | Rastreador de uso |
| `AuditTrail` | Pista de auditoría |

**Tipos de fuente:**
- `PUBMED` - PubMed articles
- `PMC` - PubMed Central
- `CLINICAL_GUIDELINE` - Clinical guidelines
- `REGULATORY` - Regulatory documents
- `MANUFACTURER` - Manufacturer docs
- `TEXTBOOK` - Textbooks
- `WEBSITE` - Web content

---

## Uso

### Generación de citación

```python
from core.PHASE_4.epic7_citation_traceability import (
    ClinicalCitationBuilder,
    CitationStyle,
)

builder = ClinicalCitationBuilder(style=CitationStyle.APA)

citation = builder.build({
    "id": "source_1",
    "text": "Treatment guidelines...",
    "metadata": {
        "title": "Heart Failure Guidelines",
        "authors": ["Smith J.", "Johnson A."],
        "date": "2024-01-15",
        "journal": "JACC",
        "doi": "10.1016/j.jacc.2024.01.001",
    }
})

print(citation.format())  # Formatted APA citation
```

### Verificación de fuente

```python
from core.PHASE_4.epic7_citation_traceability import (
    ClinicalSourceVerifier,
    SourceType,
    SourceEvidence,
)

verifier = ClinicalSourceVerifier()

source = SourceEvidence(
    source_id="src_1",
    source_type=SourceType.PUBMED,
    url="https://pubmed.ncbi.nlm.nih.gov/123456/",
)

verified = await verifier.verify(source)
print(f"Reliability: {verified.reliability_score}")
print(f"Evidence level: {verified.evidence_level}")
```

### Auditoría

```python
from core.PHASE_4.epic7_citation_traceability import AuditTrail

audit = AuditTrail()

audit.log(
    action="citation_generated",
    entity_type="Citation",
    entity_id="cit_123",
    user_id="user_1",
)

# Query audit trail
entries = audit.query(entity_type="Citation")
```

---

## Flujo de Citación

```
1. INPUT: EvidencePackage (from EPIC 6)
          │
          ▼
2. CITATION: ClinicalCitationBuilder
          │ Evidence → Citation
          │ Style formatting (APA, Vancouver, etc.)
          │
          ▼
3. VALIDATION: CitationValidator
          │ DOI format
          │ PMID format
          │
          ▼
4. REFERENCE: DOIResolver / PubMedResolver
          │ Resolve metadata
          │ Cache results
          │
          ▼
5. VERIFICATION: ClinicalSourceVerifier
          │ Source type → Reliability
          │ Evidence level assessment
          │
          ▼
6. TRACKING: SourceTracker + AuditTrail
          │ Usage tracking
          │ Audit log
          │
          ▼
7. OUTPUT: Citation + Traceability
          │
          ▼
8. NEXT: EPIC 8 (Knowledge Quality Engine)
```

---

## Concatenación

```
EPIC 6 ──► EPIC 7 (consume EvidencePackage)
EPIC 0 ──► EPIC 7 (usa Foundation types)
EPIC 7 ──► EPIC 8 (provee Citation para quality)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 8: Knowledge Quality Engine
- EPIC 9: Medical Knowledge Repository

---

*EREN PHASE 4 - EPIC 7*
*Architecture Board - 2026-07-23*
