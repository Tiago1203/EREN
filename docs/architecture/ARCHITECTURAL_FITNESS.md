# Architectural Fitness

> Cada nuevo bounded context debe responder sí a estas preguntas antes de ser mergeado.

---

## Las 7 Preguntas

### 1. ¿Tiene Aggregate propio?

```python
# ✅ Correcto
apps/api/app/domain/patient/aggregate.py
apps/api/app/domain/diagnosis/aggregate.py

# ❌ Incorrecto
apps/api/app/domain/shared/base_aggregate.py  # Acoplamiento
```

Un aggregate define el estado y las invariantes de negocio de un bounded context.
No debe compartir estado con otros contextos.

---

### 2. ¿Tiene Repository propio?

```python
# ✅ Correcto
PatientRepository  # Solo conoce Patient
DiagnosisRepository  # Solo conoce Diagnosis

# ❌ Incorrecto
class PatientDiagnosisRepository:  # Acoplamiento entre contextos
    patient_repo: PatientRepository
    diagnosis_repo: DiagnosisRepository
```

Regla: Un bounded context **nunca** accede al repository de otro contexto directamente.

---

### 3. ¿Tiene Service propio?

```python
# ✅ Correcto
PatientService
    ├── repository: PatientRepository
    └── event_bus: EventBus

# ❌ Incorrecto
PatientService
    ├── repository: PatientRepository
    ├── event_bus: EventBus
    └── diagnosis_repo: DiagnosisRepository  # Violación de límites
```

El service orquesta operaciones dentro de su contexto. Si necesita información de otro contexto, usa eventos o APIs.

---

### 4. ¿Tiene eventos propios?

```python
# ✅ Correcto
PatientCreated, PatientUpdated, PatientDeleted
DiagnosisSuggested, DiagnosisConfirmed

# ❌ Incorrecto
# Los eventos no deben contener estado de otros contextos
PatientCreated {
    patient_id,
    diagnosis_details: {...}  # ❌ No
}
```

Los eventos representan hechos de negocio. Cada contexto define los suyos.

---

### 5. ¿Tiene tests propios?

```python
# ✅ Correcto
tests/unit/test_patient_service.py
tests/unit/test_patient_service_negative.py
tests/integration/test_patient_flow.py

# ✅ tests específicos del dominio
tests/integration/test_tenant_isolation.py
tests/integration/test_optimistic_locking.py
```

Cada bounded context tiene tests unitarios, negativos e integración.

---

### 6. ¿Conoce repositorios de otros contextos?

```python
# ❌ Incorrecto - Nunca hacer esto
class PatientService:
    def get_diagnosis_for_patient(self, patient_id):
        return self.diagnosis_repo.find_by_patient(patient_id)  # ❌

# ✅ Correcto - Usar eventos o APIs
class PatientService:
    async def on_diagnosis_created(self, event):
        # Reaccionar a eventos de otros contextos
        pass
```

**Regla absoluta:** Un contexto no sabe que existen otros contextos.

---

### 7. ¿Puede eliminarse sin romper los demás?

```python
# ✅ Verificación antes de eliminar un contexto

# 1. ¿Otros contextos escuchan eventos de este?
grep -r "PatientCreated" apps/api/app/domain/*/

# 2. ¿Otros contextos acceden a este via API?
grep -r "/api/v1/patient" apps/api/app/routers/

# 3. ¿Hay dependencias en core que lo requieran?
grep -r "from app.domain.patient" core/
```

Si la respuesta es **no** a todas, el contexto puede eliminarse limpiamente.

---

## Checklist de Code Review

Antes de merge de un nuevo bounded context:

```markdown
- [ ] Aggregate creado en `domain/<name>/aggregate.py`
- [ ] Repository Protocol definido en `domain/<name>/repository.py`
- [ ] Repository Implementation en `infrastructure/<name>_repo.py`
- [ ] Service creado en `domain/<name>/service.py`
- [ ] Eventos definidos en `domain/<name>/events.py`
- [ ] Schemas en `schemas/<name>.py`
- [ ] Router en `routers/<name>.py`
- [ ] Tests unitarios en `tests/unit/test_<name>_service.py`
- [ ] Tests negativos en `tests/unit/test_<name>_service_negative.py`
- [ ] Tests de integración en `tests/integration/test_<name>_flow.py`
- [ ] Tests de tenant isolation
- [ ] No hay imports cruzados con otros contextos
- [ ] Repository no es accedido por otros contextos
- [ ] Service no inyecta repos de otros contextos
```

---

## Principios Derivados

### Del patrón Repository

1. **SQLAlchemy vive en el Repository**
   - Services no contienen `select()`, `join()`, `session.execute()`
   - Si ves SQL en un Service, es una señal de alarma

2. **Un Repository por Aggregate**
   - `PatientRepository` solo conoce `Patient`
   - `DiagnosisRepository` solo conoce `Diagnosis`
   - No hay `SharedRepository`

### Del patrón Events

3. **EventBus es compartido, no por contexto**
   - Todos los contextos publican al mismo broker
   - El evento pertenece al contexto que lo publica
   - Los consumidores escuchan eventos relevantes

4. **Eventos = Hechos, no estado**
   - Un evento dice "algo ocurrió"
   - Un aggregate dice "este es el estado actual"
   - Si necesitas estado actual, consulta el aggregate

### Del patrón Bounded Context

5. **Contextos no se hablan directamente**
   - PatientService → PatientRepository ✅
   - PatientService → DiagnosisRepository ❌
   - PatientService → DiagnosisService (via API o eventos) ✅

6. **Límites claros**
   - Si puedes deletear un contexto y los demás siguen funcionando, los límites están bien
   - Si al deletear un contexto otros fallan, hay acoplamiento

---

## Template de Nuevo Bounded Context

```
apps/api/app/domain/<name>/
├── __init__.py
├── aggregate.py      # Entidad principal
├── repository.py      # Protocolo + Implementación
├── service.py         # Lógica de aplicación
└── events.py          # Eventos del dominio

apps/api/app/schemas/
└── <name>.py         # Pydantic schemas

apps/api/app/routers/
└── <name>.py         # Endpoints API

apps/api/tests/
├── unit/
│   ├── test_<name>_service.py
│   └── test_<name>_service_negative.py
└── integration/
    └── test_<name>_flow.py
```

---

## Versión

- **Fecha:** 2026-07-15
- **Epic:** Foundation Stabilization
- **Autor:** EREN Architecture Team
