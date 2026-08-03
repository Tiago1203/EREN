# REGLAS DE DEPENDENCIAS

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** Auditoría `docs/audit/DEAD_CODE_REPORT.md` + `docs/audit/PHASE_REPORT.md`

---

## PRINCIPIO FUNDADOR

> "Las dependencias deben apuntar siempre hacia el dominio. Nunca hacia la infraestructura."

---

## JERARQUÍA DE CAPAS

```
domain/          ← depencia más alta
application/     ← depende de domain
contracts/       ← depende de domain
shared/          ← depende de domain
infrastructure/ ← depende de domain, application, contracts
presentation/    ← depende de todo
```

---

## REGLA 1 — Domain puede depender solo de domain

```
✅ device/domain/entities/     → device/domain/value_objects/
✅ device/domain/entities/     → device/domain/events/
✅ ai/domain/embeddings/       → ai/domain/value_objects/
✅ shared/primitives/           → cualquier domain

❌ device/domain/              → clinical/domain/entities/
❌ ai/domain/                  → device/domain/
❌ clinical/domain/           → ai/domain/embeddings/
```

**Evidencia de auditoría:** PHASE_4/foundation/__init__.py importa `EmbeddingManager` de PHASE_2. `EmbeddingManager` es implementación, no dominio. Este import viola la regla.

---

## REGLA 2 — Application puede depender de domain y contracts

```
✅ device/application/CreateDeviceUseCase.py
   → device/domain/entities/Device.py
   → device/domain/value_objects/DeviceId.py
   → device/contracts/DeviceRepository.py

✅ clinical/application/GenerateRecommendationUseCase.py
   → clinical/domain/entities/AIRecommendation.py
   → ai/contracts/EmbeddingPort.py
   → ai/contracts/ReasoningPort.py

❌ device/application/          → infrastructure/repositories/
❌ device/application/           → apps/api/presentation/routers/
```

**Evidencia de auditoría:** Los Use Cases actuales en `apps/api/app/domain/*/service.py` construyen sus dependencias inline en lugar de recibir puertos. Violan DIP.

---

## REGLA 3 — Contracts (Puertos) son la frontera pública

```
✅ clinical/domain/reasoning/ → ai/contracts/EmbeddingPort.py
✅ device/application/        → ai/contracts/MemoryPort.py

❌ clinical/domain/          → ai/domain/embeddings/embedding_manager.py
❌ device/application/        → ai/memory/session_manager.py
```

Los ports son el Published Language de cada Bounded Context. Todo import de otro Context pasa por contracts.

**Evidencia de auditoría:** PHASE_5/foundation/gateways/ tiene los 5 imports comentados porque los gateways no están definidos como contracts.

---

## REGLA 4 — Infrastructure puede depender de todo

```
✅ infrastructure/repositories/DeviceRepositoryImpl.py
   → device/contracts/DeviceRepository.py     ✅ (implementa contrato)
   → infrastructure/models/DeviceModel.py      ✅ (SQLAlchemy)
   → shared/result/Result.py                 ✅ (tipo compartido)

✅ infrastructure/messaging/RabbitMQEventBus.py
   → device/domain/events/DeviceRegistered.py  ✅ (publica evento)
   → clinical/domain/events/RecommendationGenerated.py  ✅

❌ infrastructure/repositories/  → device/domain/ (violación de DIP)
❌ infrastructure/messaging/     → apps/api/presentation/routers/
```

**Evidencia de auditoría:** PHASE_4/foundation/__init__.py importa `EmbeddingManager` de PHASE_2. `EmbeddingManager` es infraestructura de PHASE_2, no un puerto. Esto viola la regla.

---

## REGLA 5 — Presentation puede depender de todo

```
✅ routers/devices.py
   → device/application/CreateDeviceUseCase.py    ✅
   → device/contracts/DeviceRepository.py       ✅
   → schemas/device.py                          ✅

❌ routers/devices.py  → infrastructure/models/DeviceModel.py  (violación de DIP)
```

Los routers pueden usar infraestructura directamente para casos de调试 o conveniencia, pero los Use Cases nunca.

---

## REGLA 6 — shared/ solo para lo verdaderamente transversal

```
✅ shared/primitives/EntityId.py       → cualquier domain
✅ shared/result/Result.py             → cualquier domain
✅ shared/errors/SystemError.py         → cualquier domain

❌ shared/utils/helpers.py             → ¿pertenece a un solo context?
❌ shared/constants/business_rules.py  → ¿qué context define esta regla?
```

Para cada elemento en shared/ debe existir respuesta a: "¿Por qué pertenece a más de un Context?"

**Evidencia de auditoría:** `core/PHASE_1/infrastructure/shared/` existe con primitives y value_objects compartidos. Esto es válido porque son tipos transversales del sistema.

---

## REGLA 7 — Eventos de dominio cruzan Contexts solo por el Event Bus

```
✅ device/domain/ → Event Bus → clinical/domain/
✅ clinical/domain/ → Event Bus → audit/domain/

❌ device/domain/ → import directo → clinical/domain/entities/
```

Los Domain Events son el mecanismo de comunicación entre Bounded Contexts. No hay llamadas directas entre domains.

**Excepción documentada:** Los gateways pueden invocar puertos de otro Context síncronamente. Esto se modela como Command, no como Domain Event.

---

## REGLA 8 — Imports circulares están prohibidos

```
❌ device/ → clinical/ → device/
❌ ai/ → device/ → clinical/ → ai/
❌ any/ → shared/ → any/
```

Verificación automática obligatoria en pre-commit.

---

## TABLA RESUMEN: QUÉ PUEDE IMPORTAR QUÉ

| Importador | domain/ | application/ | contracts/ | shared/ | infrastructure/ | presentation/ |
|---|---|---|---|---|---|---|
| **domain/** | ✅ mismo BC | ❌ | ✅ puertos de otros BCs | ✅ transversales | ❌ | ❌ |
| **application/** | ✅ mismo BC | ✅ mismo BC | ✅ contratos de BCs | ✅ transversales | ❌ | ❌ |
| **contracts/** | ✅ | ✅ | ✅ mismo BC | ✅ transversales | ❌ | ❌ |
| **shared/** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **infrastructure/** | ✅ implementa | ✅ usa | ✅ implementa | ✅ | ✅ mismo entry | ❌ |
| **presentation/** | ✅ usa | ✅ usa | ✅ usa | ✅ | ✅ | ✅ mismo entry |

---

## VERIFICACIÓN AUTOMÁTICA

### Linter de imports

```yaml
# .importlinter.toml
[linters]
SelectLinter = "HyperLinter"

[linthook]
pre-commit = true

[imports.lint.core]
name = "Core Dependencies"
layers = [
    {name = "domain", bad_imports = [
        {from = "device.domain", to = "clinical.domain"},
        {from = "ai.domain", to = "device.domain"},
    ]},
    {name = "application", bad_imports = [
        {from = "device.application", to = "infrastructure"},
    ]},
    {name = "shared", bad_imports = [
        {from = "shared", to = "infrastructure"},
    ]},
]
```

### Comandos de verificación manual

```bash
# Verificar que ningún domain importa otro domain directamente
grep -rn "from core.device.domain import" core/clinical/
grep -rn "from core.ai.domain import" core/device/

# Verificar que infrastructure no se importa desde domain
grep -rn "from apps.api.infrastructure" core/

# Verificar que shared no se importa desde infrastructure
grep -rn "from core.shared" apps/api/infrastructure/
```

---

## EXCEPCIONES CONOCIDAS

| Excepción | Ubicación | Razón | Fecha ADR |
|---|---|---|---|
| PHASE_4 → PHASE_2.embeddings | PHASE_4/foundation/__init__.py:793 | PHASE_4 necesita embeddings antes de que gateway exista | Pendiente |

Las excepciones se documentan aquí y se resuelven en el próximo ciclo de arquitectura.

---

*Las dependencias se verifican con import-linter en CI. Cada violación es un build failure.*
