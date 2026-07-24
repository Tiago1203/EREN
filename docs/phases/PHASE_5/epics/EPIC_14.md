# EPIC 14: Uncertainty Quantification Model

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Construir el modelo de cuantificación de incertidumbre para decisiones clínicas.**

EPIC 14 es responsable de:
- Cuantificar incertidumbre en decisiones
- Calcular confianza calibrada
- Propagar incertidumbre entre etapas
- Comunicar incertidumbre apropiadamente
- Detectar fuentes de incertidumbre

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Confidence, Reasoning)

### EPICs
- **EPIC 12**: Clinical Context Builder (provee contexto)
- **EPIC 13**: Evidence Lifecycle Model (provee evidencia)
- **EPIC 1**: Agent Orchestrator (lo invoca)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│               EPIC 14: Uncertainty Quantification Model                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              UNCERTAINTY QUANTIFICATION MODULES                     │   │
│  │  ├── UncertaintyQuantifier ─────────────── Cuantifica incertidumbre│   │
│  │  ├── ConfidenceCalibrator ─────────────── Calibra confianza        │   │
│  │  ├── UncertaintyPropagator ────────────── Propaga incertidumbre   │   │
│  │  ├── UncertaintyCommunicator ──────────── Comunica incertidumbre  │   │
│  │  └── UncertaintySourceDetector ────────── Detecta fuentes         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── Uncertainty ────────────────────────── Incertidumbre base     │   │
│  │  ├── ConfidenceLevel ────────────────────── Nivel de confianza     │   │
│  │  ├── UncertaintySource ──────────────────── Fuente de incertidumbre│   │
│  │  ├── UncertaintyPropagation ──────────────── Propagación            │   │
│  │  └── UncertaintyStatement ────────────────── Declaración           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    UNCERTAINTY TYPES                               │   │
│  │  ├── Aleatory ───────────────────────────── Aleatoria (variabilidad│   │
│  │  ├── Epistemic ──────────────────────────── Epistémica (conocimiento│   │
│  │  ├── Model ──────────────────────────────── De modelo              │   │
│  │  ├── Parametric ─────────────────────────── Paramétrica            │   │
│  │  └── Measurement ────────────────────────── De medición            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic14_uncertainty/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # Uncertainty, ConfidenceLevel, etc.
├── quantification/
│   ├── __init__.py              # UncertaintyQuantifier
│   ├── aleatory_quantifier.py   # Aleatory uncertainty
│   ├── epistemic_quantifier.py  # Epistemic uncertainty
│   └── bayesian_quantifier.py   # Bayesian quantification
├── calibration/
│   ├── __init__.py              # ConfidenceCalibrator
│   ├── calibration_checker.py   # Calibration checking
│   └── probability_calibrator.py # Probability calibration
├── propagation/
│   ├── __init__.py              # UncertaintyPropagator
│   ├── monte_carlo.py          # Monte Carlo propagation
│   └── analytic_propagator.py  # Analytic propagation
├── communication/
│   ├── __init__.py              # UncertaintyCommunicator
│   └── statement_generator.py   # Statement generation
├── detection/
│   ├── __init__.py              # UncertaintySourceDetector
│   └── source_identifier.py    # Source identification
└── agent/
    └── __init__.py              # UncertaintyAgent
```

---

## Componentes

### 1. UncertaintyAgent

Agente principal de cuantificación de incertidumbre.

```python
class UncertaintyAgent(BaseAgent):
    """Agente de cuantificación de incertidumbre."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta operaciones de incertidumbre."""
```

**Acciones:**
- `quantify`: Cuantificar incertidumbre
- `calibrate`: Calibrar confianza
- `propagate`: Propagar incertidumbre
- `communicate`: Comunicar incertidumbre
- `detect_sources`: Detectar fuentes
- `calibrate_probabilities`: Calibrar probabilidades

### 2. UncertaintyQuantifier

Cuantifica incertidumbre en diferentes tipos.

```python
class UncertaintyQuantifier:
    """Cuantificador de incertidumbre."""
    
    async def quantify(
        self,
        value: Any,
        uncertainty_type: UncertaintyType,
        method: QuantificationMethod,
    ) -> Uncertainty:
        """Cuantifica incertidumbre."""
    
    async def quantify_aleatory(
        self,
        data: list[float],
    ) -> AleatoryUncertainty:
        """Cuantifica incertidumbre aleatoria."""
    
    async def quantify_epistemic(
        self,
        evidence: list[Evidence],
        prior: ProbabilityDistribution | None = None,
    ) -> EpistemicUncertainty:
        """Cuantifica incertidumbre epistémica."""
```

### 3. ConfidenceCalibrator

Calibra niveles de confianza.

```python
class ConfidenceCalibrator:
    """Calibrador de confianza."""
    
    async def calibrate(
        self,
        confidence: ConfidenceLevel,
        actual_outcomes: list[bool],
    ) -> CalibrationResult:
        """Calibra confianza."""
    
    async def check_calibration(
        self,
        predictions: list[Prediction],
        outcomes: list[Outcome],
    ) -> CalibrationCheck:
        """Verifica calibración."""
    
    async def recalibrate(
        self,
        current_calibration: CalibrationResult,
        new_data: CalibrationDataset,
    ) -> UpdatedCalibration:
        """Recalibra con nuevos datos."""
    
    async def get_reliability_diagram(
        self,
        calibration: CalibrationResult,
    ) -> ReliabilityDiagram:
        """Genera diagrama de confiabilidad."""
```

### 4. UncertaintyPropagator

Propaga incertidumbre a través del pipeline.

```python
class UncertaintyPropagator:
    """Propagador de incertidumbre."""
    
    async def propagate(
        self,
        uncertainty: Uncertainty,
        transformation: Transformation,
    ) -> Uncertainty:
        """Propaga incertidumbre."""
    
    async def propagate_monte_carlo(
        self,
        input_uncertainties: list[Uncertainty],
        model: Callable,
        n_iterations: int = 10000,
    ) -> PropagationResult:
        """Propaga usando Monte Carlo."""
    
    async def propagate_analytically(
        self,
        input_uncertainties: list[Uncertainty],
        function: Callable,
    ) -> AnalyticPropagationResult:
        """Propaga analíticamente."""
```

### 5. UncertaintyCommunicator

Comunica incertidumbre de forma apropiada.

```python
class UncertaintyCommunicator:
    """Comunicador de incertidumbre."""
    
    async def communicate(
        self,
        uncertainty: Uncertainty,
        audience: AudienceType,
        format: CommunicationFormat,
    ) -> UncertaintyStatement:
        """Comunica incertidumbre."""
    
    async def generate_probability_statement(
        self,
        probability: float,
        uncertainty: Uncertainty,
    ) -> ProbabilityStatement:
        """Genera declaración de probabilidad."""
    
    async def generate_confidence_interval(
        self,
        estimate: float,
        uncertainty: Uncertainty,
        confidence_level: float,
    ) -> ConfidenceInterval:
        """Genera intervalo de confianza."""
    
    async def generate_natural_language(
        self,
        uncertainty: Uncertainty,
        context: str,
    ) -> str:
        """Genera lenguaje natural."""
```

### 6. UncertaintySourceDetector

Detecta fuentes de incertidumbre.

```python
class UncertaintySourceDetector:
    """Detector de fuentes de incertidumbre."""
    
    async def detect_sources(
        self,
        decision: ClinicalDecision,
        context: ClinicalContext,
    ) -> list[UncertaintySource]:
        """Detecta fuentes de incertidumbre."""
    
    async def classify_source(
        self,
        source: UncertaintySource,
    ) -> UncertaintyType:
        """Clasifica tipo de fuente."""
    
    async def estimate_impact(
        self,
        source: UncertaintySource,
    ) -> ImpactEstimate:
        """Estima impacto de fuente."""
```

---

## Domain Objects

### Uncertainty

```python
@dataclass
class Uncertainty:
    """Incertidumbre base."""
    uncertainty_id: str
    uncertainty_type: UncertaintyType
    value: float
    distribution: ProbabilityDistribution | None
    sources: list[UncertaintySource]
    
    def get_confidence_interval(
        self,
        level: float,
    ) -> ConfidenceInterval:
        """Obtiene intervalo de confianza."""
    
    def get_variance(self) -> float:
        """Obtiene varianza."""
    
    def get_std_deviation(self) -> float:
        """Obtiene desviación estándar."""
```

### ConfidenceLevel

```python
@dataclass
class ConfidenceLevel:
    """Nivel de confianza."""
    level: float  # 0.0 - 1.0
    is_calibrated: bool
    calibration_error: float | None
    based_on: list[EvidenceSource]
    
    def is_high_confidence(self) -> bool:
        """Verifica si es alta confianza."""
    
    def requires_qualification(self) -> bool:
        """Verifica si requiere cualificación."""
```

### UncertaintySource

```python
@dataclass
class UncertaintySource:
    """Fuente de incertidumbre."""
    source_id: str
    source_type: UncertaintyType
    description: str
    estimated_impact: float
    mitigatable: bool
    
    def get_mitigation_strategy(self) -> MitigationStrategy | None:
        """Obtiene estrategia de mitigación."""
```

### UncertaintyPropagation

```python
@dataclass
class UncertaintyPropagation:
    """Propagación de incertidumbre."""
    propagation_id: str
    input_uncertainties: list[Uncertainty]
    output_uncertainty: Uncertainty
    method: PropagationMethod
    sensitivity_analysis: SensitivityAnalysis | None
    
    def get_total_uncertainty(self) -> float:
        """Obtiene incertidumbre total."""
```

### UncertaintyStatement

```python
@dataclass
class UncertaintyStatement:
    """Declaración de incertidumbre."""
    statement: str
    probability: float | None
    confidence_interval: ConfidenceInterval | None
    caveats: list[str]
    audience: AudienceType
    
    def format_for_clinical(self) -> str:
        """Formatea para contexto clínico."""
```

---

## Tipos de Incertidumbre

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `ALEATORY` | Variabilidad inherente | Diferencias entre pacientes |
| `EPISTEMIC` | Falta de conocimiento | Evidencia insuficiente |
| `MODEL` | Limitaciones del modelo | Simplificaciones |
| `PARAMETRIC` | Incertidumbre en parámetros | Errores de medición |
| `MEASUREMENT` | Errores de medición | Sensores imprecisos |

---

## Uso

### Cuantificar incertidumbre

```python
from core.PHASE_5.epic14_uncertainty import (
    UncertaintyAgent,
    UncertaintyConfig,
)

agent = UncertaintyAgent(
    agent_id="uncertainty_1",
    config=UncertaintyConfig(),
)

result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="uncertainty_1",
    task_type="uncertainty",
    input_data={
        "action": "quantify",
        "value": 0.75,
        "uncertainty_type": "epistemic",
        "evidence_ids": ["ev_1", "ev_2"],
    },
))
```

### Calibrar confianza

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="uncertainty_1",
    task_type="uncertainty",
    input_data={
        "action": "calibrate",
        "confidence_level": 0.9,
        "predictions": [0.9, 0.85, 0.88],
        "outcomes": [True, True, False],
    },
))
```

### Generar declaración de incertidumbre

```python
result = await agent.execute(AgentTask(
    task_id="task_3",
    agent_id="uncertainty_1",
    task_type="uncertainty",
    input_data={
        "action": "communicate",
        "uncertainty_id": "unc_123",
        "audience": "clinical",
        "format": "natural_language",
    },
))
```

---

## Integración con FASE 3

```
FASE 3 (Confidence Engine) ───────────────────────┐
                                                    │
EPIC 13 (Evidence) ────────────────────────────────┼──► UncertaintyAgent
                                                    │              │
EPIC 12 (Clinical Context) ───────────────────────┴──► UncertaintyQuantifier
                                                              │
                                                              ▼
                                                      UncertaintyStatement
```

---

## Concatenación

```
EPIC 12 (Clinical Context) ──► EPIC 14 (provee contexto)
EPIC 13 (Evidence Lifecycle) ──► EPIC 14 (evidencia → incertidumbre)
EPIC 1 (Orchestrator) ──► EPIC 14 (cuantifica incertidumbre)
EPIC 14 ──► EPIC 2-6 (provee incertidumbre a agentes)
EPIC 14 ──► EPIC 8 (consenso con incertidumbre)
```

---

## Estado

**✅ IMPLEMENTADO**

Este EPIC cierra el gap de Uncertainty Model (0/100 → 85/100).

---

## Próximos Pasos

- PHASE 5 Cognitive Evolution completa
- PHASE 6: Hospital Digital

---

*EREN PHASE 5 - EPIC 14*
*Architecture Board - 2026-07-24*
