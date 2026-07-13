# ADR-0003: Objeto de Contexto Cognitivo (`core/context` — `CognitiveContext`)

## Status

Accepted

> **Nota de numeración (2026-07-13):** este es el **tercer ADR escrito** del
> repositorio (tras los dos `ADR-0001` y el `ADR-0002`). El índice
> [`docs/adr/README.md`](./README.md) listaba `ADR-0003` como una entrada
> *planificada* ("Arquitectura de Tres Capas") sin archivo; ese tema se
> renumerará cuando se escriba. El número `ADR-0003` queda asignado a esta
> decisión (Cognitive Context), que sí tiene archivo y está aceptada.

## Context

Los motores cognitivos de EREN (orchestrator, planner, reasoning, memory,
knowledge, diagnostic, workflow, tools) deben colaborar durante una interacción
sin acoplarse entre sí. Si cada motor recibiera y devolviera argumentos ad-hoc,
el sistema acumularía dependencias cruzadas frágiles y perdería trazabilidad.

EREN, además, tiene requisitos no negociables:

1. **Explicabilidad y auditabilidad** de cada decisión.
2. **Multi-tenant / multi-hospital**: la identidad del usuario, la organización
   y el hospital deben viajar con cada solicitud.
3. **Evolución a largo plazo** sin reescrituras: la forma del estado compartido
   debe poder crecer de forma aditiva.

Se necesita, por tanto, un **único objeto de estado por interacción** que el
orquestador cree y que cada motor lea y enriquezca.

Esta decisión define **solo el modelo declarativo** de ese objeto. No introduce
lógica, IA ni LLMs (alineado con la instrucción explícita del proyecto en esta
fase).

## Decision

Se crea el módulo `core/context/` con `CognitiveContext`, un modelo **Pydantic
v2** que representa toda la información de una interacción, compuesto por
sub-modelos cohesivos:

- **Identidad** (`Identity`): `request_id`, `session_id`, `timestamp`.
- **Usuario** (`UserInfo`): `user_id`, `user_role`, `organization_id`.
- **Clínica** (`ClinicalContext`): `hospital_id`, `department`, `device_id`,
  `device_type`, `manufacturer`, `model`.
- **Conversación** (`Conversation`): `original_input`, `normalized_input`,
  `detected_language`, `conversation_history`.
- **Estado cognitivo** (`CognitiveState`): `detected_intent`, `confidence`,
  `current_plan`, `current_step`, `executed_engines`, `executed_tools`.
- **Memoria** (`MemoryState`): `short_term_memory`, `long_term_memory`.
- **Conocimiento** (`KnowledgeState`): `retrieved_documents`,
  `retrieved_cases`, `regulations`.
- **Resultado** (`ResultState`): `intermediate_results`, `final_response`.
- **Metadatos** (`ExecutionMetadata`): `execution_time`, `warnings`,
  `citations`.

Decisiones de diseño:

- **Pydantic v2** con `extra="forbid"` para un contrato explícito. Es una
  dependencia ya presente en el proyecto (backend `apps/api`); no se añaden
  dependencias nuevas.
- **Defaults vacíos en todos los campos** para poder construir el contexto de
  forma incremental mientras atraviesa el pipeline.
- `current_plan` se modela como descripciones de pasos ordenadas (`list[str]`)
  para **desacoplar** el contexto de los tipos `Plan`/`PlanStep` del Planner; el
  orquestador realiza el mapeo.
- El objeto **transporta estado; no actúa**. Poblarlo, validarlo o persistirlo
  corresponde a los motores/servicios que lo consumen.

## Consequences

**Positivas**

- Fuente única de verdad por interacción.
- Trazabilidad completa (plan, motores/tools ejecutados, conocimiento y
  citas) → soporta explicabilidad y auditoría.
- Motores desacoplados: dependen de la forma del contexto, no entre sí.
- La identidad multi-tenant viaja con cada solicitud.

**Negativas / trade-offs**

- Riesgo de que el contexto crezca demasiado ("god object"); se mitiga con
  sub-modelos cohesivos y revisiones de diseño.
- Existe temporalmente un `CognitiveContext` dataclass **local** en
  `core/orchestrator/models.py`. Este ADR define el modelo **canónico**; alinear
  el orquestador es trabajo futuro y **no** se hace aquí (no se modifican otros
  motores).

## Benefits

- Explicabilidad y auditabilidad por diseño.
- Bajo acoplamiento entre motores.
- Extensible de forma aditiva sin romper consumidores.

## Risks

- Divergencia entre el contexto canónico y el placeholder del orquestador hasta
  que se unifiquen.
- Sobre-modelado si se añaden campos sin una responsabilidad clara.

## Alternatives Considered

- **Argumentos ad-hoc entre motores**: rechazado por acoplamiento y pérdida de
  trazabilidad.
- **`dict` no tipado como contexto**: rechazado; sin validación ni contrato,
  frágil y difícil de auditar.
- **Dataclasses de stdlib**: viables, pero el proyecto pidió Pydantic v2 y este
  aporta validación y serialización JSON/Schema sin dependencias nuevas.

## Future Work

- Unificar el `CognitiveContext` del orquestador con este modelo canónico.
- Definir políticas de serialización/persistencia y redacción de datos
  sensibles (PII/PHI) para auditoría.
- Especificar el ciclo de vida (creación, enriquecimiento, cierre) en el
  Orchestrator.

## References

- [`core/context/README.md`](../../core/context/README.md)
- [CORE_SPECIFICATION.md](../../CORE_SPECIFICATION.md)
- [`core/contracts/README.md`](../../core/contracts/README.md)
- [ADR-0002: Arquitectura General de EREN CORE](./ADR-0002-eren-core-architecture.md)
