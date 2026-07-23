# ADR-3120: PHASE_2 → PHASE_3 Clinical Intelligence Integration

## Estado
**Aceptado** - 2026-07-23

## Contexto

Necesitamos que FASE 2 (AI Core / Cognitive OS) pueda invocar las capacidades de Clinical Intelligence de FASE 3. El flujo arquitectónico es:

```
FASE 1 (Business Domain)
        │
        ▼
FASE 2 (AI Core / Cognitive OS)
        │
        ├── AI Kernel
        ├── Context Builder
        ├── Memory Manager
        └── Domain Gateways
                │
                └── ClinicalIntelligenceGateway ← NUEVO
                        │
                        ▼
                PHASE 3 (Clinical Intelligence)
                        │
                        ├── Reasoning Engine
                        ├── Evidence Retrieval
                        ├── Confidence Engine
                        ├── Decision Engine
                        ├── Safety Engine
                        └── Validation Engine
```

Sin esta conexión, PHASE 3 estaría aislada y EREN no podría usar capacidades clínicas.

## Decisión

Crear un **ClinicalIntelligenceGateway** en `core/PHASE_2/ai/domain/` que:

1. Expone una interfaz limpia (`IClinicalIntelligenceGateway`) para AI Core
2. Permite invocar PHASE_3 Clinical Intelligence sin acoplamiento directo
3. Proporciona DTOs para queries (`ClinicalQueryDTO`) y respuestas (`ClinicalResponseDTO`)
4. Mantiene mock implementations para testing sin PHASE_3

### Arquitectura del Gateway

```python
# PHASE_2/ai/domain/clinical_intelligence_gateway.py

@dataclass(frozen=True)
class ClinicalQueryDTO:
    """Query from AI Core to Clinical Intelligence."""
    query_id: str
    device_id: str | None
    incident_id: str | None
    symptoms: list[str]
    context: dict[str, Any]
    tenant_id: str
    requested_at: datetime

@dataclass(frozen=True)
class ClinicalResponseDTO:
    """Response from Clinical Intelligence to AI Core."""
    query_id: str
    reasoning_chain: list[str]
    hypotheses: list[dict[str, Any]]
    evidence_bundle: dict[str, Any]
    confidence_score: float
    recommendations: list[dict[str, Any]]
    safety_validated: bool
    validation_status: str
    generated_at: datetime

class ClinicalIntelligenceGateway:
    async def process_clinical_query(
        self,
        query: ClinicalQueryDTO,
    ) -> ClinicalResponseDTO:
        """Main entry point for clinical intelligence."""
        ...
```

### Flujo de Integración

1. **AI Core recibe input** → ConversationController
2. **Context Builder** → Construye contexto con Domain Gateways (PHASE_1)
3. **ClinicalIntelligenceGateway** → Invoca PHASE_3 Clinical Intelligence
4. **PHASE_3 procesa** → Reasoning → Evidence → Confidence → Decision
5. **AI Core recibe respuesta** → Genera respuesta al usuario

## Consecuencias

### Positivas
- ✅ PHASE_2 puede usar Clinical Intelligence sin acoplamiento
- ✅ Clean Architecture respetado (Dependency Inversion)
- ✅ Testing posible con mocks
- ✅ Flujo completo: PHASE_1 → PHASE_2 → PHASE_3

### Negativas
- ⚠️ Latencia adicional por gateway
- ⚠️ Posible necesidad de async orchestration

### Riesgos Mitigados
- ✅ Aislamiento de PHASE_3 eliminado
- ✅ Dependency Inversion respetado

## Referencias

- [EPIC 10 - Domain Integration Bridge](../epics/epic10/)
- [EPIC 11 - Runtime Integration](../epics/epic11/)
- [ADR-3001 - AI Core Architecture](../epics/epic0/)
- [Clinical Intelligence Foundation](../epics/epic0/)

## Módulos Afectados

| Módulo | Cambio |
|--------|--------|
| `core/PHASE_2/ai/domain/` | Nuevo gateway añadido |
| `core/PHASE_2/ai/domain/__init__.py` | Actualizado con exports |
| `tests/unit/PHASE_2/ai/` | Tests para gateway |
| `docs/phases/PHASE_3/adr/` | Nuevo ADR |

## Verificación

```python
# Verificar que el gateway funciona
from core.PHASE_2.ai.domain import ClinicalIntelligenceGateway

gateway = ClinicalIntelligenceGateway()
response = await gateway.process_clinical_query(query)
assert response.safety_validated is True
assert 0 <= response.confidence_score <= 1
```
