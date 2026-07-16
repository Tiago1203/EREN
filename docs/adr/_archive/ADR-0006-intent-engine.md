# ADR-0006: Intent Engine (`core/intent`) — primer motor cognitivo, sin IA

## Status

Accepted

> **Nota de numeración (2026-07-13):** sexto ADR **escrito**. Continúa la
> secuencia de ADRs con archivo (0001–0005). El catálogo *planificado* de
> [`docs/adr/README.md`](./README.md) usa rangos temáticos (backend 0010+,
> motores 0030+); los números reservados sin archivo se reasignarán cuando se
> redacten.

## Context

EREN necesita su **primer motor cognitivo funcional**: un componente que, dada
una interacción, determine *qué quiere* el usuario. Esta clasificación de
intención es la entrada del resto del pipeline (planner, knowledge, reasoning,
diagnostic…).

Restricciones de esta fase:

- **Sin IA / sin LLM** todavía.
- Debe **funcionar** de forma determinista (auditable y testeable).
- Debe integrarse con el objeto compartido `CognitiveContext` (`core/context`).
- El diseño debe permitir **sustituir** la clasificación por un LLM en el futuro
  sin reescribir el motor.

Intenciones iniciales requeridas: `DEVICE_QUERY`, `DIAGNOSTIC_REQUEST`,
`MAINTENANCE_HISTORY`, `REGULATION_QUERY`, `GENERAL_CHAT`, `UNKNOWN`.

## Decision

Se crea `core/intent/` con:

- **`IntentType`** (enum): la taxonomía de seis intenciones.
- **`IntentResult`** (Pydantic v2): `intent`, `confidence` (0.0–1.0),
  `matched_terms`, `rationale` — con **traza explicable** de la decisión.
- **`IntentClassifier`** (`typing.Protocol`): la *estrategia* de clasificación
  `classify(text, context) -> IntentResult`.
- **`RuleBasedIntentClassifier`**: clasificador **determinista por palabras
  clave** (léxico bilingüe ES/EN, `DEFAULT_LEXICON`). Puntúa la entrada por
  coincidencias, elige la intención con mayor puntaje (desempate por prioridad
  clínica) y reporta los términos coincidentes. **Sin IA.**
- **`IntentEngine`**: motor que ejecuta el pipeline *recibir → analizar →
  clasificar → actualizar → retornar* sobre el `CognitiveContext`. Satisface el
  contrato `CognitiveEngine` (`name`, `describe`) y la capacidad `IntentPort`.
- **Excepciones**: `IntentError`, `ClassificationError`.

Decisiones de diseño:

- **Estrategia inyectable (DI)**: `IntentEngine(classifier=...)`. Por defecto usa
  `RuleBasedIntentClassifier`; mañana se puede inyectar un
  `LLMIntentClassifier` que implemente el mismo `IntentClassifier` **sin tocar el
  motor** (Open/Closed + Dependency Inversion + Strategy).
- **Sin condicionales gigantes**: la clasificación por reglas se basa en una
  **tabla de léxico** (datos), no en cadenas `if/elif`. Añadir/ajustar
  intenciones es editar la tabla.
- **Explicabilidad**: `IntentResult` lleva `matched_terms`/`rationale`; encaja
  con el requisito de decisiones auditables de EREN.
- **Acoplamiento con el contexto**: el motor escribe `detected_intent`
  (`IntentType.value`, un `str`) y `confidence` en `cognitive_state`, y registra
  `"intent"` en `executed_engines`. El `CognitiveContext` permanece desacoplado
  del enum (guarda `str`).
- **Reutiliza Pydantic v2** ya presente; sin dependencias nuevas.

## Consequences

**Positivas**

- Primer flujo cognitivo real end-to-end sobre el `CognitiveContext`.
- Ruta de evolución clara a un clasificador LLM sin refactor del motor.
- Determinista, explicable y fácil de testear.

**Negativas / trade-offs**

- La clasificación por keywords es limitada (sin semántica): frases ambiguas o
  sin términos conocidos caen en `UNKNOWN`.
- El léxico requiere mantenimiento manual hasta que llegue el LLM.
- La `confidence` es heurística (proporción de coincidencias), no una
  probabilidad calibrada.

## Benefits

- Strategy + DI: comportamiento sustituible sin cambiar el consumidor.
- Base explicable para auditoría desde el primer motor.

## Risks

- Falsos positivos/negativos por solapamiento de vocabulario entre intenciones
  (mitigado por prioridad de desempate y `matched_terms` para depurar).
- Dependencia del idioma/vocabulario del léxico (mitigable ampliando la tabla).

## Alternatives Considered

- **Clasificador con LLM desde ahora**: descartado por la restricción de no usar
  IA en esta fase; habilitado más adelante vía el mismo contrato.
- **`if/elif` embebido en el motor**: descartado; acopla reglas y motor, y
  crece sin control.
- **Regex/gramáticas complejas**: innecesariamente rígidas para el objetivo
  inicial; el léxico puntuado es suficiente y simple.

## Future Work

- Añadir `LLMIntentClassifier` (mismo `IntentClassifier`) e inyectarlo por
  configuración.
- Normalización previa de la entrada (idioma, sinónimos) en `core/context` o un
  paso previo.
- Umbral de confianza para decidir entre `GENERAL_CHAT` y `UNKNOWN`.
- Integrar el motor en el registro (`core/registry`) y el `Orchestrator`.

## References

- [`core/intent/README.md`](../../core/intent/README.md)
- [`core/context/README.md`](../../core/context/README.md)
- [`core/contracts/README.md`](../../core/contracts/README.md)
- [CORE_SPECIFICATION.md](../../CORE_SPECIFICATION.md)
- [ADR-0003: Objeto de Contexto Cognitivo](./ADR-0003-cognitive-context.md)
