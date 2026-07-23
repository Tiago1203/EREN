# EPIC 2: Biomedical Knowledge Extraction Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Extraer conocimiento estructurado desde documentos biomédicos.

---

## Responsabilidad

**Convertir texto clínico en conocimiento.**

EPIC 2 es responsable de:
- Extraer entidades biomédicas (dispositivos, drogas, condiciones)
- Extraer conceptos clínicos (diagnósticos, tratamientos)
- Extraer relaciones entre entidades
- Mapear terminología a ontologías médicas
- Generar códigos médicos estandarizados

---

## Dependencias

### Fases
- **FASE 1**: Consume Device, Knowledge, Incident, Asset contexts
- **FASE 2**: Provee entrada para embeddings y retrieval
- **FASE 3**: Integra con Reasoning, Evidence engines

### EPICs
- **EPIC 0**: Usa Foundation (tipos, contratos, excepciones)
- **EPIC 1**: Consume BiomedicalDocument de Document Processing

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│              EPIC 2: Knowledge Extraction Engine               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     BiomedicalDocument (de EPIC 1)                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      EXTRACTORS                            │   │
│  │  ├── EntityExtractor ───► BiomedicalEntities              │   │
│  │  ├── ConceptExtractor ──► BiomedicalConcepts             │   │
│  │  └── RelationExtractor ─► MedicalRelations              │   │
│  │                                                              │   │
│  │              MedicalNER (combinación)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       MAPPERS                              │   │
│  │  ├── SNOMEDMapper ───────► SNOMED CT codes             │   │
│  │  ├── UMLSMapper ─────────► UMLS CUIs                     │   │
│  │  ├── MeSHMapper ────────► MeSH terms                    │   │
│  │  └── ICDMapper ──────────► ICD-10 codes                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       PIPELINES                            │   │
│  │  ├── EntityPipeline ─────── Entity extraction             │   │
│  │  └── KnowledgeExtractionPipeline ─── Full extraction     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     ExtractedKnowledge (structured biomedical knowledge) │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic2_knowledge_extraction/
├── __init__.py                    # Módulo principal
├── extractors/                     # Extractores especializados
│   └── __init__.py              # Entity, Concept, Relation extractors
├── mappers/                       # Mapeadores ontológicos
│   └── __init__.py              # SNOMED, UMLS, MeSH, ICD
└── pipelines/                      # Pipelines de extracción
    └── __init__.py               # Entity, Knowledge pipelines
```

---

## Componentes

### 1. Extractors

| Extractor | Descripción |
|-----------|-------------|
| `EntityExtractor` | Extrae entidades biomédicas (DEVICE, DRUG, CONDITION, etc.) |
| `ConceptExtractor` | Extrae conceptos clínicos (DIAGNOSIS, TREATMENT, etc.) |
| `RelationExtractor` | Extrae relaciones entre entidades |
| `MedicalNER` | Reconocedor de entidades médicas combinando extractores |

### 2. Mappers

| Mapper | Ontología | Descripción |
|--------|----------|-------------|
| `SNOMEDMapper` | SNOMED CT | Map to medical concepts |
| `UMLSMapper` | UMLS | Map to Unified Medical Language System |
| `MeSHMapper` | MeSH | Map to Medical Subject Headings |
| `ICDMapper` | ICD-10 | Map to disease codes |

### 3. Pipelines

| Pipeline | Descripción |
|----------|-------------|
| `EntityPipeline` | Pipeline de extracción de entidades |
| `KnowledgeExtractionPipeline` | Pipeline completo de extracción |

---

## Categorías de Entidades

```python
class EntityCategory(str, Enum):
    DEVICE = "DEVICE"           # infusión pump, ventilator
    DRUG = "DRUG"              # aspirin, metformin
    CONDITION = "CONDITION"     # hypertension, diabetes
    PROCEDURE = "PROCEDURE"     # surgery, biopsy
    ANATOMY = "ANATOMY"        # heart, lung
    ORGANISM = "ORGANISM"        # bacteria, virus
    BIOMARKER = "BIOMARKER"     # troponin, CRP
    GENE = "GENE"              # BRCA1, TP53
    PROTEIN = "PROTEIN"         # hemoglobin
    LAB_TEST = "LAB_TEST"       # glucose, creatinine
    SPECIMEN = "SPECIMEN"       # blood, urine
    VALUE = "VALUE"             # 120/80, 98.6°F
    TEMPORAL = "TEMPORAL"       # today, yesterday
```

---

## Categorías de Conceptos

```python
class ConceptCategory(str, Enum):
    DIAGNOSIS = "DIAGNOSIS"
    TREATMENT = "TREATMENT"
    SYMPTOM = "SYMPTOM"
    ETIOLOGY = "ETIOLOGY"
    PROGNOSIS = "PROGNOSIS"
    PREVENTION = "PREVENTION"
    COMPLICATION = "COMPLICATION"
    CONTRAINDICATION = "CONTRAINDICATION"
    INDICATION = "INDICATION"
    SIDE_EFFECT = "SIDE_EFFECT"
    INTERACTION = "INTERACTION"
    ASSESSMENT = "ASSESSMENT"
```

---

## Categorías de Relaciones

```python
class RelationCategory(str, Enum):
    TREATS = "TREATS"
    CAUSES = "CAUSES"
    PREVENTS = "PREVENTS"
    COMPLICATES = "COMPLICATES"
    DIAGNOSES = "DIAGNOSES"
    MANIFESTS_AS = "MANIFESTS_AS"
    INTERACTS_WITH = "INTERACTS_WITH"
    IS_A = "IS_A"
    PART_OF = "PART_OF"
    LOCATED_IN = "LOCATED_IN"
    ASSESSES = "ASSESSES"
    PRODUCES = "PRODUCES"
```

---

## Uso

### Extracción básica de entidades

```python
from core.PHASE_4.epic2_knowledge_extraction import MedicalNER

ner = MedicalNER()
entities = ner.recognize(
    "Patient has hypertension and takes lisinopril 10mg daily."
)

for entity in entities:
    print(f"{entity.text} -> {entity.category.value}")
```

Output:
```
hypertension -> CONDITION
lisinopril -> DRUG
10mg -> VALUE
```

### Pipeline completo de extracción

```python
from core.PHASE_4.epic2_knowledge_extraction import KnowledgeExtractionPipeline
from core.PHASE_4.foundation import KnowledgeDomain

pipeline = KnowledgeExtractionPipeline()

knowledge = await pipeline.extract(
    text="Patient with heart failure treated with metformin...",
    domain=KnowledgeDomain.CARDIOLOGY
)

print(f"Entities: {knowledge.entity_count}")
print(f"Concepts: {knowledge.concept_count}")
print(f"Relations: {knowledge.relation_count}")
print(f"Medical codes: {knowledge.code_count}")
```

### Mapeo a ontologías

```python
from core.PHASE_4.epic2_knowledge_extraction.mappers import TerminologyMapperFactory

mappers = TerminologyMapperFactory.create_all()

result = await mappers["SNOMED"].map_term("heart failure")
print(f"Code: {result.best_match.code}")
# Output: Code: 84114007
```

---

## Domain Objects

### BiomedicalEntity

```python
@dataclass
class BiomedicalEntity:
    entity_id: str
    text: str
    category: EntityCategory
    normalized_text: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str
    synonyms: list[str]
    medical_codes: list[str]  # ontology:code
    properties: dict
```

### BiomedicalConcept

```python
@dataclass
class BiomedicalConcept:
    concept_id: str
    text: str
    category: ConceptCategory
    definition: str
    confidence: float
    synonyms: list[str]
    related_concepts: list[str]
    medical_codes: list[str]
```

### MedicalRelation

```python
@dataclass
class MedicalRelation:
    relation_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationCategory
    confidence: float
    evidence: str
    context: str
    bidirectional: bool
```

### OntologyReference

```python
@dataclass
class OntologyReference:
    reference_id: str
    ontology: str  # SNOMED, UMLS, MeSH, ICD-10
    code: str
    display_name: str
    synonyms: list[str]
    definition: str
    hierarchy: list[str]  # Path to root
```

---

## Flujo de Extracción

```
1. INPUT: BiomedicalDocument (de EPIC 1)
          │
          ▼
2. NER: MedicalNER.recognize(text)
          │
          ▼
3. ENTITY: EntityExtractor → BiomedicalEntities
          │
          ▼
4. CONCEPT: ConceptExtractor → BiomedicalConcepts
          │
          ▼
5. RELATION: RelationExtractor → MedicalRelations
          │
          ▼
6. MAP: TerminologyMapper → OntologyReferences
          │
          ▼
7. CODES: Extract codes from mappings
          │
          ▼
8. OUTPUT: ExtractedKnowledge
          │
          ▼
9. NEXT: EPIC 3 (Clinical Embeddings)
```

---

## Concatenación

```
EPIC 1 ──► EPIC 2 (consume BiomedicalDocument)
EPIC 0 ──► EPIC 2 (usa Foundation types)
EPIC 2 ──► EPIC 3 (provee ExtractedKnowledge)
EPIC 2 ──► FASE 2 (provee entrada para embeddings)
EPIC 2 ──► FASE 3 (provee entrada para reasoning)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 3: Clinical Embeddings
- EPIC 4: Vector Indexing

---

*EREN PHASE 4 - EPIC 2*
*Architecture Board - 2026-07-23*
