# ADR-0004: Sistema de Eventos Interno (`core/events`)

## Status

Accepted

> **Nota de numeración (2026-07-13):** este es el **cuarto ADR escrito** del
> repositorio. El índice [`docs/adr/README.md`](./README.md) reservaba
> `ADR-0004` en su catálogo *planificado* para "Estrategia de Escalabilidad
> Horizontal" (sin archivo). El número `ADR-0004` queda asignado a esta decisión
> (sistema de eventos), que sí tiene archivo; la entrada planificada de
> escalabilidad se renumerará cuando se redacte.

## Context

Los motores cognitivos de EREN (orchestrator, planner, reasoning, memory,
knowledge, diagnostic, workflow, tools) necesitan comunicarse a lo largo de una
interacción sin acoplarse entre sí. Si un motor invocara directamente a otro
para "avisar" de que algo ocurrió (p. ej. que se detectó una intención o que se
completó un diagnóstico), el sistema acumularía dependencias cruzadas rígidas y
sería difícil añadir capacidades transversales (auditoría, métricas, streaming a
la UI) sin tocar a los productores.

EREN requiere, además:

1. **Explicabilidad y auditabilidad**: poder reconstruir qué ocurrió y en qué
   orden durante una interacción.
2. **Extensibilidad**: añadir consumidores (logging, métricas, auditoría) sin
   modificar a quien emite.
3. **Transporte sustituible**: hoy in-process; mañana, potencialmente, colas o
   un broker — sin reescribir productores ni consumidores.

Esta decisión define **solo la arquitectura** del sistema de eventos. No
implementa despacho, hilos, colas ni brokers (alineado con la instrucción del
proyecto en esta fase).

## Decision

Se crea el módulo `core/events/` con:

- **`Event`** (Pydantic v2, `frozen=True`): registro **inmutable** de un hecho.
  Campos comunes: `event_id`, `type`, `timestamp`, `correlation_id`,
  `session_id`, `source`, `payload` (`dict[str, object]` genérico).
- **`EventType`**: catálogo enum de los diez eventos del ciclo cognitivo.
- **`EventPublisher`** / **`EventSubscriber`**: contratos `typing.Protocol`
  (publicar / reaccionar).
- **`EventBus`**: mediador (esqueleto) con `subscribe`, `unsubscribe`,
  `publish`; los métodos lanzan `NotImplementedError`.
- **Eventos concretos**: `VoiceReceived`, `IntentDetected`, `PlanCreated`,
  `KnowledgeRetrieved`, `ReasoningStarted`, `ReasoningFinished`, `ToolExecuted`,
  `DiagnosticCompleted`, `WorkflowCompleted`, `ResponseGenerated`.
- **Excepciones**: `EventError`, `PublishError`, `SubscriptionError`.

Decisiones de diseño:

- **Desacoplamiento total**: los productores dependen de `EventPublisher`; los
  consumidores implementan `EventSubscriber`; el `EventBus` depende solo de esas
  abstracciones (Dependency Inversion). Productores y consumidores no se
  referencian entre sí.
- **Payload genérico** para no acoplar los eventos a los tipos concretos de
  otros motores; cada evento documenta las claves de payload esperadas.
- **Inmutabilidad**: un hecho, una vez emitido, no cambia.
- **Pydantic v2** (ya presente en el proyecto vía `apps/api`); no se añaden
  dependencias.

## Consequences

**Positivas**

- Motores desacoplados que colaboran por eventos, no por llamadas directas.
- Trazabilidad de la interacción vía `correlation_id`/`session_id`/`timestamp`.
- Capacidades transversales (auditoría, métricas, streaming) se añaden como
  nuevos subscribers sin tocar productores.
- El transporte puede evolucionar (in-process → cola → broker) sin romper a los
  consumidores.

**Negativas / trade-offs**

- Flujo indirecto: seguir la ejecución exige mirar suscripciones, no llamadas.
- El `EventBus` es un esqueleto; sin implementación no hay entrega todavía.
- Payload genérico: la forma concreta de cada payload se valida fuera del modelo
  base (responsabilidad de productores/consumidores).

## Benefits

- Bajo acoplamiento y alta extensibilidad.
- Base natural para explicabilidad y auditoría.
- Sustituibilidad del mecanismo de transporte.

## Risks

- Divergencia en las claves de payload entre productores y consumidores si no se
  documentan/versionan.
- Complejidad de depuración por el desacople (mitigable con logging de eventos).

## Alternatives Considered

- **Llamadas directas entre motores**: rechazado por acoplamiento rígido.
- **Callbacks pasados explícitamente**: rechazado; sigue acoplando productor y
  consumidor y no escala a múltiples oyentes.
- **Broker externo desde el inicio (Kafka/RabbitMQ)**: prematuro; se difiere. La
  abstracción `EventBus` permite introducirlo después sin cambiar el core.

## Future Work

- Implementar un `EventBus` in-process (registro de subscribers + despacho).
- Definir esquemas/estabilidad de payloads por evento y su versionado.
- Integrar el bus con el `Orchestrator` para emitir eventos del ciclo de vida.
- Añadir subscribers de auditoría/métricas y, más adelante, transporte
  distribuido.

## References

- [`core/events/README.md`](../../core/events/README.md)
- [CORE_SPECIFICATION.md](../../CORE_SPECIFICATION.md)
- [ADR-0002: Arquitectura General de EREN CORE](./ADR-0002-eren-core-architecture.md)
- [ADR-0003: Objeto de Contexto Cognitivo](./ADR-0003-cognitive-context.md)
