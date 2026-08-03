# REGLAS ARQUITECTÓNICAS DE EREN

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** Auditoría `docs/audit/` y discusión arquitectónica

---

> Estas reglas son el contrato arquitectónico del proyecto. Toda decisión técnica debe poder responderse con estas reglas. Si una decisión no puede justificarse con ninguna regla, requiere una Architectural Decision Record (ADR) antes de implementarse.

---

## REGLA 1 — Límites de Bounded Context

**Un Bounded Context nunca importa el dominio de otro Bounded Context.**

- `device/domain/` no puede importar `clinical/domain/`
- `ai/domain/` no puede importar `device/domain/`
- Un Context puede importar contratos públicos (`*/contracts/`) de otro Context
- Un Context puede publicar y suscribirse a eventos de otros Contexts

**Justificación:** Previene acoplamiento de dominio que dificulta la evolución independiente de cada Context.

---

## REGLA 2 — Application Layer compartida

**Toda entrada al sistema utiliza los mismos Use Cases.**

Los Use Cases viven en `core/{context}/application/`, no en `apps/`.

```
API → Use Case
CLI → Use Case
Worker → Use Case
PHASE_5 → Use Case
Voice → Use Case
```

No existen Use Cases duplicados en API, Workers y CLI. Son el mismo código.

**Justificación:** Evidencia en auditoría: 22 routers en `apps/api/app/routers/` construyen dependencias inline. Si los Use Cases vivieran en `apps/api/`, Workers y CLI no podrían reutilizarlos.

---

## REGLA 3 — La infraestructura nunca conoce HTTP

**La infraestructura no sabe que existe una API.**

- Los repositories no reciben objetos de request HTTP
- Los adapters no retornan `Response` objects
- El Event Bus no sabe que existe un router FastAPI

La infraestructura recibe y retorna objetos del dominio. Los Presenters/Routers convierten entre HTTP y dominio.

**Justificación:** Previene que cambios en el protocolo de entrada (HTTP → gRPC → CLI) requieran modificar la lógica de negocio.

---

## REGLA 4 — AI es un dominio técnico

**AI es un Bounded Context, no infraestructura.**

Para EREN, la inteligencia clínica ES el producto. Los embeddings, planners, retrievers, reasoners y agents son dominio, no utilities.

No se organizan en `engines/`, `providers/`, `services/`. Se organizan como cualquier otro dominio: con entidades, value objects, repositories y use cases.

**Justificación:** Evidencia en auditoría: PHASE_2 tiene ~600 archivos. Organizar la IA como infraestructura genera confusión sobre qué es el producto y qué es soporte.

---

## REGLA 5 — shared/ solo para lo verdaderamente transversal

**Ningún elemento entra a shared/ que pertenezca claramente a un solo Context.**

Para cada elemento en `shared/` debe poder responderse:

> "¿Por qué pertenece a más de un Context?"

Si la respuesta no es clara, el elemento no pertenece a shared/.

**Justificación:** Previene que shared/ se convierta en el verdadero core, que es el olor arquitectónico más común.

Elementos válidos en shared/:
- `Result[T, E]`, `Ok`, `Err`
- `EntityId`, `AggregateRoot`, `ValueObject`
- Errores base del sistema

---

## REGLA 6 — La estructura crece con el código

**Ninguna carpeta se crea por anticipación. Aparece cuando el código la necesita.**

```
device/
├── device.py           ← Semana 1
├── incident.py        ← Mes 2
├── domain/            ← Mes 3: cuando aparecen value objects
├── application/       ← Mes 4: cuando necesitas use cases
└── contracts/         ← Mes 6: cuando otro Context necesita comunicarse
```

No crear `domain/`, `application/`, `contracts/` si solo van a contener un archivo durante meses.

**Justificación:** Evidencia en auditoría: `core/PHASE_2/ai/di/` es una carpeta vacía. `core/PHASE_1/domain/device/application/` nunca creció.

---

## REGLA 7 — Un contrato por Bounded Context

**Cada Bounded Context define un único sistema de puertos. No coexisten sistemas paralelos.**

Si existe un contrato para `DeviceRepository` en `core/device/contracts/`, ese es el contrato canónico. No puede existir otro `DeviceRepository` con firma diferente en otro lugar del proyecto.

**Justificación:** Evidencia en auditoría: `core/PHASE_1/domain/` y `apps/api/app/domain/` definen interfaces incompatibles. ABC vs Protocol. El sistema usa ambas sin consistencia.

---

## REGLA 8 — Integración entre Contexts por eventos o gateways

**La comunicación entre Bounded Contexts ocurre por:**
- **Eventos:** publicación asíncrona de Domain Events
- **Gateways:** puertos explícitos definidos en el Context consumidor

Nunca por imports directos de implementaciones de otro Context.

```
✅ PHASE_5 → Phase1Gateway (ABC) → adapter implementa
❌ PHASE_5 → DeviceRepository (implementación de core)
```

**Justificación:** Evidencia en auditoría: `core/PHASE_4/foundation/__init__.py:793` importa `EmbeddingManager` (implementación) de PHASE_2. Si `EmbeddingManager` cambia, PHASE_4 rompe.

---

## REGLA 9 — Infrastructure en la capa más externa

**Los adapters, repositories, message brokers y clients viven en la capa de infraestructura de la aplicación, no en core/.**

Excepción: `core/*/events/` y `core/*/contracts/` son protocolo de integración entre Contexts. Son el Published Language. Pertenecen a core/.

**Justificación:** Evidencia en auditoría: `core/PHASE_1/infrastructure/container/` (DI Container) está en core/ pero nunca se usa. La infraestructura de aplicación debe vivir en `apps/`.

---

## REGLA 10 — Excepciones documentadas

**Toda excepción a estas reglas requiere un ADR.**

Las reglas existen para proteger la arquitectura. Las excepciones existen para permitir pragmática. Ambas se documentan.

Un ADR de excepción debe incluir:
1. Qué regla se viola
2. Qué problema real resuelve la excepción
3. Qué costo introduce
4. Cuándo debe eliminarse la excepción

**Justificación:** Sin proceso de例外, las excepciones se acumulan hasta que las reglas dejan de tener sentido.

---

## RESUMEN

| # | Regla | Origen en auditoría |
|---|---|---|
| 1 | BC no importa dominio de otro BC | PHASE_4 → PHASE_2 infrastructure |
| 2 | Use Cases compartidos | EREN multi-entry-point |
| 3 | Infraestructura sin HTTP | Arquitectura por capas |
| 4 | AI es dominio | PHASE_2 como infraestructura vs PHASE_2 como producto |
| 5 | shared/ justificado | shared-hell smell |
| 6 | Estructura crece con código | Carpetas ceremoniales |
| 7 | Un contrato por BC | Dual port system |
| 8 | Eventos y gateways | PHASE_5 placeholders |
| 9 | Infraestructura en apps/ | DI Container en core/ |
| 10 | Excepciones documentadas | Proceso |

---

*Estas reglas son el contrato arquitectónico. Se actualizan por ADR, no por costumbre.*
