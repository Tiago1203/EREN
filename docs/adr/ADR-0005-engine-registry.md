# ADR-0005: Registro Dinámico de Motores (`core/registry`)

## Status

Accepted

> **Nota de numeración (2026-07-13):** este es el **quinto ADR escrito** del
> repositorio. El índice [`docs/adr/README.md`](./README.md) reservaba
> `ADR-0005` en su catálogo *planificado* para "Arquitectura de Microservicios
> vs Monolito Modular" (sin archivo). El número `ADR-0005` queda asignado a esta
> decisión (registro de motores), que sí tiene archivo; la entrada planificada
> de microservicios se renumerará cuando se redacte.

## Context

El `Orchestrator` (y otros consumidores) necesitan **descubrir e invocar** los
motores cognitivos (planner, reasoning, memory, knowledge, diagnostic, workflow,
tools, …) sin acoplarse a sus clases concretas. Resolver motores mediante
condicionales por tipo (`if intent == ... : return PlannerEngine()`) produce
`if/elif` gigantes que crecen con cada motor, violan Open/Closed y acoplan al
consumidor con cada implementación.

Se necesita un mecanismo que:

1. Permita **registrar/quitar** motores dinámicamente (`register`,
   `unregister`).
2. Permita **resolver/listar** motores (`get`, `list`).
3. Dependa de la **abstracción** `CognitiveEngine`, no de clases concretas.
4. Evite condicionales de despacho.

## Decision

Se crea el módulo `core/registry/` con:

- **`EngineRegistry`**: contenedor en memoria de motores indexados por
  `engine.name` (diccionario). Métodos `register(engine, *, replace=False)`,
  `unregister(name)`, `get(name)`, `list()`; además `name in registry` y
  `len(registry)`.
- **`EngineRegistryPort`** (`typing.Protocol`): contrato para que los
  consumidores dependan de la *abstracción* del registro, no de la clase
  concreta.
- **Excepciones**: `RegistryError`, `EngineNotFoundError`,
  `EngineAlreadyRegisteredError`.

Decisiones de diseño:

- **Dependency Injection**: los motores se **inyectan** desde fuera (constructor
  `EngineRegistry(engines=[...])` o `register(...)`). El registro **no construye
  motores** y depende solo de `CognitiveEngine` (`core/contracts`).
- **Sin `if` gigantes**: la resolución es un **lookup de diccionario** O(1) por
  `engine.name`. Añadir un motor nuevo no implica editar un despachador
  condicional: basta registrarlo (Open/Closed).
- **Infraestructura fina, no cognición**: el registro almacena y devuelve
  objetos; no contiene IA ni lógica de dominio. A diferencia de otros módulos de
  esta fase (que son solo contratos/esqueletos), aquí la petición requiere un
  registro **funcional**, por lo que se implementa la mecánica mínima y genérica
  de almacenamiento/consulta.

## Consequences

**Positivas**

- Consumidores desacoplados de las clases concretas de motores.
- Extensible: nuevos motores se añaden registrándolos, sin tocar despachadores.
- Composición explícita en el *composition root* (quién crea y cablea los
  motores).

**Negativas / trade-offs**

- El registro es en memoria y **no** ofrece garantías de concurrencia ni
  persistencia (fuera de alcance; se abordará si se necesita).
- La unicidad de nombres depende de `engine.name`; nombres colisionantes se
  rechazan salvo `replace=True`.

## Benefits

- Dependency Inversion + Open/Closed aplicados al descubrimiento de motores.
- Base natural para que el `Orchestrator` obtenga motores por nombre.

## Risks

- Un `name` incorrecto o duplicado en un motor produciría resolución errónea
  (mitigado por `EngineAlreadyRegisteredError`).
- Uso concurrente sin sincronización externa podría competir por el diccionario
  (documentado como límite).

## Alternatives Considered

- **Despacho por condicionales (`if/elif` por tipo/intención)**: rechazado por
  `if` gigantes, acoplamiento y violación de Open/Closed.
- **Service locator global/singleton import-time**: rechazado; oculta las
  dependencias y dificulta pruebas. Se prefiere DI explícita.
- **Descubrimiento por entry points/plugins**: potente pero prematuro; la
  abstracción `EngineRegistryPort` permite introducirlo después.

## Future Work

- Integrar el registro con el `Orchestrator` (obtener motores por nombre).
- Considerar sincronización/inmutabilidad si se comparte entre hilos.
- Poblar el registro en el arranque de la app (composition root) sin acoplar el
  core a `apps/*`.

## References

- [`core/registry/README.md`](../../core/registry/README.md)
- [`core/contracts/README.md`](../../core/contracts/README.md)
- [CORE_SPECIFICATION.md](../../CORE_SPECIFICATION.md)
- [ADR-0002: Arquitectura General de EREN CORE](./ADR-0002-eren-core-architecture.md)
