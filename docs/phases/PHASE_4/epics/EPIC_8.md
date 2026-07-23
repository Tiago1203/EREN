# EPIC 8: Knowledge Quality Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Validar calidad del conocimiento recuperado.

---

## Responsabilidad

**Filtrar evidencia de baja calidad.**

EPIC 8 es responsable de:
- Analizar calidad de evidencia
- Detectar sesgos en fuentes
- Rankear evidencia por calidad
- Detectar duplicados
- Generar reportes de calidad

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Evidence)

### EPICs
- **EPIC 7**: Consume Citation & Traceability

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│              EPIC 8: Knowledge Quality Engine                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       INPUT                               │   │
│  │     EvidencePackage + Citation (from EPIC 7)           │   │
│  │     Evidence items                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       QUALITY                               │   │
│  │  ├── QualityScore ───────────────► Quality metrics          │   │
│  │  ├── ClinicalQualityAnalyzer ────► Analyze quality        │   │
│  │  └── QualityReport ──────────────► Quality report          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                        BIAS                                │   │
│  │  ├── BiasDetector ───────────────► Detect bias            │   │
│  │  ├── ClinicalBiasDetector ───────► Clinical bias          │   │
│  │  └── BiasReport ─────────────────► Bias report             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       RANKING                               │   │
│  │  ├── ClinicalRankingEngine ───────► Rank evidence         │   │
│  │  ├── DuplicateDetector ───────────► Find duplicates       │   │
│  │  └── RankedEvidence ───────────────► Ranked results       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       OUTPUT                               │   │
│  │     Quality-filtered Evidence (confiable)                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_4/epic8_knowledge_quality/
├── __init__.py                    # Módulo principal
├── quality/                        # Análisis de calidad
│   └── __init__.py              # QualityAnalyzer, QualityScore, etc.
├── bias/                          # Detección de sesgos
│   └── __init__.py             # BiasDetector, BiasReport, etc.
└── ranking/                      # Ranking de evidencia
    └── __init__.py            # RankingEngine, DuplicateDetector, etc.
```

---

## Componentes

### 1. Quality

| Componente | Descripción |
|------------|-------------|
| `QualityScore` | Score de calidad multidimensional |
| `QualityReport` | Reporte de calidad |
| `ClinicalQualityAnalyzer` | Analizador de calidad clínica |

**Dimensiones de calidad:**
- `ACCURACY` - Exactitud
- `COMPLETENESS` - Completitud
- `CONSISTENCY` - Consistencia
- `CURRENCY` - Actualidad
- `RELEVANCE` - Relevancia

**Niveles:**
- `EXCELLENT` (≥ 0.9)
- `GOOD` (≥ 0.75)
- `FAIR` (≥ 0.5)
- `POOR` (≥ 0.25)
- `UNACCEPTABLE` (< 0.25)

### 2. Bias

| Componente | Descripción |
|------------|-------------|
| `BiasReport` | Reporte de sesgo |
| `ClinicalBiasDetector` | Detector de sesgos clínicos |
| `BiasIndicator` | Indicador de sesgo |

**Tipos de sesgo:**
- `PUBLICATION` - Sesgo de publicación
- `SELECTION` - Sesgo de selección
- `CONFIRMATION` - Sesgo de confirmación
- `CITATION` - Sesgo de citación
- `LANGUAGE` - Sesgo de idioma
- `GEOGRAPHIC` - Sesgo geográfico
- `TEMPORAL` - Sesgo temporal
- `INDUSTRY` - Sesgo de financiación industrial

### 3. Ranking

| Componente | Descripción |
|------------|-------------|
| `ClinicalRankingEngine` | Motor de ranking clínico |
| `QualityRankingEngine` | Motor de ranking por calidad |
| `DuplicateDetector` | Detector de duplicados |
| `RankedEvidence` | Evidencia con ranking |

**Ranks:**
- `HIGH` - Alta calidad
- `MEDIUM` - Calidad media
- `LOW` - Baja calidad
- `EXCLUDED` - Excluida

---

## Uso

### Análisis de calidad

```python
from core.PHASE_4.epic8_knowledge_quality import ClinicalQualityAnalyzer

analyzer = ClinicalQualityAnalyzer()

report = analyzer.analyze({
    "id": "source_1",
    "text": "Clinical study text...",
    "score": 0.8,
    "metadata": {
        "peer_reviewed": True,
        "title": "Study Title",
        "authors": ["Smith J."],
        "date": "2024-01-15",
    }
})

print(f"Quality: {report.score.level}")
print(f"Acceptable: {report.is_acceptable}")
```

### Detección de sesgos

```python
from core.PHASE_4.epic8_knowledge_quality import ClinicalBiasDetector

detector = ClinicalBiasDetector()

report = detector.detect({
    "id": "source_1",
    "text": "Industry-funded study...",
    "metadata": {
        "funding": "Pharmaceutical company XYZ",
    }
})

print(f"Flagged: {report.is_flagged}")
for indicator in report.indicators:
    print(f"{indicator.bias_type}: {indicator.description}")
```

### Ranking de evidencia

```python
from core.PHASE_4.epic8_knowledge_quality import ClinicalRankingEngine

ranker = ClinicalRankingEngine()

ranked = ranker.rank([
    {"id": "1", "text": "...", "score": 0.9, "quality_score": 0.8},
    {"id": "2", "text": "...", "score": 0.7, "quality_score": 0.6},
])

for evidence in ranked:
    print(f"#{evidence.rank_position}: {evidence.source_id} ({evidence.rank.value})")
```

---

## Flujo de Calidad

```
1. INPUT: EvidencePackage + Citation (from EPIC 7)
          │
          ▼
2. QUALITY: ClinicalQualityAnalyzer
          │ Evidence → QualityScore
          │ Dimensions: Accuracy, Completeness, etc.
          │
          ▼
3. BIAS: ClinicalBiasDetector
          │ Evidence → BiasReport
          │ Types: Industry, Publication, etc.
          │
          ▼
4. DUPLICATE: DuplicateDetector
          │ Find duplicate evidence
          │
          ▼
5. RANKING: ClinicalRankingEngine
          │ Evidence → RankedEvidence
          │ Quality + Evidence Level + Relevance
          │
          ▼
6. FILTER: Exclude LOW/EXCLUDED
          │
          ▼
7. OUTPUT: Quality-filtered Evidence
          │
          ▼
8. NEXT: EPIC 9 (Medical Knowledge Repository)
```

---

## Concatenación

```
EPIC 7 ──► EPIC 8 (consume Citation & Traceability)
FASE 3 ──► EPIC 8 (usa Evidence de Clinical Intelligence)
EPIC 8 ──► EPIC 9 (provee RankedEvidence para repository)
```

---

## Estado

**✅ COMPLETO**

---

## Próximos Pasos

- EPIC 9: Medical Knowledge Repository
- EPIC 10: Knowledge Synchronization Engine

---

*EREN PHASE 4 - EPIC 8*
*Architecture Board - 2026-07-23*
