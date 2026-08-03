# PRINCIPIOS DE MIGRACIÓN

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** Auditoría `docs/audit/` + `CORRECTION_LIST.md`

---

## PRINCIPIO 1 — Validar antes de migrar

### ¿Qué significa?

Antes de tocar cualquier archivo, confirmar que el cambio no rompe algo.

### Aplicación

```
PASO 1: Ejecutar tests existentes
PASO 2: Verificar imports actuales con grep
PASO 3: Implementar contract tests para contratos affected
PASO 4: Solo entonces migrar
PASO 5: Ejecutar tests nuevamente
```

### ¿Por qué?

Evidencia en auditoría: los tests de `PHASE_1` y `PHASE_2` tienen collection errors. Si migramos sin validar, podemos romper código que ya tiene problemas.

### Ejemplo concreto

```
Antes de eliminar core/PHASE_1/infrastructure/container/:
1. grep -rn "from core.PHASE_1.infrastructure.container" . --include="*.py"
   → vacío (confirmado dead code)
2. Ejecutar tests: pytest tests/unit/PHASE_1/
   → ¿pasan?
3. Eliminar
4. Verificar CI pasa
```

---

## PRINCIPIO 2 — Migrar sin destruir la funcionando

### ¿Qué significa?

Cada paso de migración debe dejar el sistema funcionando al final del paso. No hay migración que deje el sistema roto.

### Aplicación

```
✅ CORRECTO:
   Migrar un módulo → Tests pasan → Commit
   Migrar siguiente módulo → Tests pasan → Commit

❌ INCORRECTO:
   Migrar 10 módulos → Tests fallan → ¿cuál rompió?
```

### ¿Por qué?

El sistema está en producción. Cada PR que rompe producción es un incidente. La migración no justifica romper producción.

### Ejemplo concreto

```
PR 1: Eliminar código muerto
→ Tests pasan → Merge

PR 2: Crear Composition Root con factory functions
→ Tests pasan → Merge

PR 3: Actualizar routers uno por uno para usar factories
→ Un router a la vez → Tests pasan → Merge

No hacer PR 2 y PR 3 en el mismo commit.
```

---

## PRINCIPIO 3 — Un cambio a la vez

### ¿Qué significa?

Cada PR/commit contiene exactamente un tipo de cambio.

### Aplicación

```
✅ Un PR: "eliminar código muerto"
✅ Otro PR: "crear Composition Root"
✅ Otro PR: "unificar puertos"
✅ Otro PR: "renombrar PHASE → dominio"

❌ NO: "eliminar dead code + crear Composition Root + unificar puertos" en un PR
```

### ¿Por qué?

Si algo rompe, el rollback es trivially reversible. Un PR grande con múltiples cambios es difícil de revertir.

### ¿Cuántos archivos por PR?

Como máximo 20 archivos. Si el cambio requiere más, se divide.

### Ejemplo concreto

```
PR de eliminación de código muerto:
  core/PHASE_1/infrastructure/container/    → eliminar
  core/PHASE_2/runtime/                   → eliminar
  core/LEGACY/                            → eliminar
  apps/api/app/providers/circuit_breaker.py → eliminar
  apps/api/app/infrastructure/unit_of_work.py → eliminar
→ 5 carpetas eliminadas, máximo 20 archivos por decisión
```

---

## PRINCIPIO 4 — Probar donde se rompe

### ¿Qué significa?

Si el cambio afecta tests, los tests se actualizan en el MISMO commit que el cambio.

### Aplicación

```
✅ CORRECTO:
   Modificar DeviceRepository
   → Actualizar contract test para DeviceRepository
   → Actualizar unit tests para DeviceService
   → Commit

❌ INCORRECTO:
   Modificar DeviceRepository
   → "los tests fallan, se arreglarán después"
```

### ¿Por qué?

Tests que fallan en CI bloquean el merge. Si fallan en local y se hace commit de todas formas, se rompe el CI.

### Ejemplo concreto

```
Si un archivo de test referencia el path antiguo de un módulo migrado:
1. Encontrar el test que falla: pytest tests/unit/device/ -v
2. Actualizar el import en el test
3. Verificar que pasa: pytest tests/unit/device/ -v
4. Commit
```

---

## PRINCIPIO 5 — Documentar las excepciones

### ¿Qué significa?

Cuando una migración requiere violar una regla arquitectónica temporalmente, se documenta en un ADR.

### Aplicación

```
Si durante la migración se encuentra que device/ necesita importar clinical/domain/
temporalmente:

1. Crear ADR explicando:
   - Qué regla se viola
   - Por qué es necesario temporalmente
   - Cuándo se resolverá
   - Riesgo introducido

2. El ADR se incluye en el PR
```

### ¿Por qué?

Las excepciones olvidadas se acumulan hasta que la arquitectura deja de tener sentido.

---

## PRINCIPIO 6 — Rollback en un comando

### ¿Qué significa?

Cada paso de migración debe poder deshacerse con `git checkout` o `git revert`.

### Aplicación

```
✅ Después de cada PR:
   git log --oneline -3
   # Si algo falla:
   git revert <commit-hash>

❌ Después de migración compleja:
   "modifiqué 50 archivos, no sé cómo revertirlo"
```

### ¿Por qué?

Si algo sale mal en producción, la recuperación debe ser rápida.

---

## PRINCIPIO 7 — La estructura crece con el código

### ¿Qué significa?

Las carpetas y módulos nuevos aparecen cuando el código los necesita, no antes.

### Aplicación

```
✅ CORRECTO:
   device/device.py           ← existe desde semana 1
   device/incident.py         ← aparece en mes 2
   device/domain/            ← aparece cuando hay value objects (mes 3)
   device/application/       ← aparece cuando hay use cases (mes 4)
   device/contracts/        ← aparece cuando otro Context necesita comunicarse (mes 6)

❌ INCORRECTO:
   device/domain/           ← creado el día 1 con 0 archivos
   device/application/       ← creado el día 1 con 0 archivos
   device/contracts/        ← creado el día 1 con 0 archivos
```

### ¿Por qué?

Evidencia en auditoría: `core/PHASE_2/ai/di/` es una carpeta vacía. Las carpetas ceremoniales generan confusión.

---

## PRINCIPIO 8 — No migrar por dogma

### ¿Qué significa?

Si una regla arquitectónica no resuelve un problema real, no se aplica.

### Aplicación

```
✅ VALE LA PENA:
   Eliminar 117 archivos de código muerto
   → Reduce 30% de tiempo en análisis estático
   → Elimina confusión para nuevos desarrolladores

❌ NO VALE LA PENA:
   Mover "correctamente" infraestructura a su lugar "ideal"
   → Toma 3 semanas
   → El sistema funciona igual
   → Solo se cumple una regla teórica
```

### ¿Por qué?

El objetivo es un sistema mantenible durante 10 años. Las reglas arquitectónicas son herramientas, no fines en sí mismas.

---

## PRINCIPIO 9 — Tres criterios para migrar

Un cambio se hace si y solo si cumple los tres:

1. **Reduce deuda**: ¿Elimina código problemático confirmado por la auditoría?
2. **Reduce riesgo**: ¿Previene una falla futura?
3. **Añade valor**: ¿Permite hacer algo que antes no era posible?

Si no cumple al menos uno de estos tres, el cambio es opcional y puede esperar.

### Ejemplos

| Cambio | ¿Reduce deuda? | ¿Reduce riesgo? | ¿Añade valor? | Ejecutar? |
|---|---|---|---|---|
| Eliminar DI Container dead | ✅ (117 archivos) | ✅ (confusión) | ❌ | **SÍ** |
| Composition Root | ❌ | ✅ (consistencia) | ✅ (testing) | **SÍ** |
| Renombrar PHASE → dominio | ❌ | ❌ | ✅ (claridad) | **OPCIONAL** |
| Unificar puertos | ✅ (2 sistemas) | ✅ (compatibilidad) | ✅ (integración) | **SÍ** |
| Contract tests | ✅ | ✅ (regresiones) | ✅ (confianza) | **SÍ** |

---

## PRINCIPIO 10 — La migración más valiosa es la más simple

### ¿Qué significa?

Siempre empezar por el cambio de mayor impacto con menor esfuerzo.

### Aplicación

```
Orden de migración recomendado (de la auditoría):

1. 🔴 Eliminar código muerto (~5 horas, riesgo casi nulo)
2. 🟡 Completar CI con tests (1 día, riesgo bajo)
3. 🟡 Composition Root (3-5 días, riesgo medio)
4. 🟠 Contract tests (1 semana, riesgo medio)
5. 🟠 Unificar puertos (1-2 semanas, riesgo alto)
...
```

### ¿Por qué?

Cada paso的成功 genera confianza para el siguiente. Los cambios pequeños y exitosos construyen momentum.

---

## RESUMEN: NUNCA HACER

```
❌ No migrar sin tests que pasen
❌ No hacer múltiples cambios en un PR
❌ No dejar tests fallando en local
❌ No crear carpetas sin contenido
❌ No aplicar reglas por dogma
❌ No migrar algo que no reduce deuda, riesgo o añade valor
❌ No olvidar documentar las excepciones
❌ No hacer cambios irreversibles sin rollback plan
```

---

*La migración es evolución, no revolución. Cada paso pequeño y exitoso es mejor que un gran cambio arriesgado.*
