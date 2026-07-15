# Pattern Validation Report

> Patient vs Diagnosis — Validación del EREN Bounded Context Template

**Fecha:** 2026-07-15
**Actualizado:** 2026-07-15

---

## Clasificación de Diferencias

| Tipo | Significado | Acción |
|------|------------|--------|
| ✓ Domain Difference | Diferencia justificada por el dominio | Se mantiene |
| ✓ Infrastructure Difference | Diferencia justificada por tecnología | Se evalúa |
| ✗ Pattern Inconsistency | Diferencia no justificada | **Se corrige** |

---

## Resumen Ejecutivo

| Aspecto | Estado | Clasificación |
|---------|--------|--------------|
| Estructura de archivos | ✅ | Identical |
| Eventos | ✅ | Domain Difference |
| Repository | ✅ | Domain Difference |
| Service | ✅ | Domain Difference |
| Model | ✅ | Domain Difference |
| API Endpoints | ✅ | Identical |
| Tests | ✅ | Identical |

---

## Veredicto

| Pregunta | Respuesta |
|----------|-----------|
| ¿Diagnosis usa el mismo patrón que Patient? | ✅ Sí |
| ¿Las diferencias son del dominio? | ✅ Sí |
| ¿Hay inconsistencias del patrón? | ❌ No |
| ¿Diagnosis puede usarse como template para Treatment? | ✅ Sí |

---

## Detalle por Aspecto

### 1. Estructura de Archivos ✅

```
Patient:
├── __init__.py
├── events.py
├── repository.py
└── service.py

Diagnosis:
├── __init__.py
├── events.py
├── repository.py
└── service.py
```

**Resultado:** Identical.

---

### 2. Eventos ✅

| Componente | Patient | Diagnosis |
|------------|---------|-----------|
| Base class | `PatientEvent` | `DiagnosisEvent` |
| Created/Recorded | `PatientCreated` | `DiagnosisRecorded` |
| Updated/Amended | `PatientUpdated` | `DiagnosisAmended` |
| Deleted | `PatientDeleted` | `DiagnosisDeleted` |

**Diferencia:** `DiagnosisEvent` incluye `patient_id` (referencia de identidad).

**Clasificación:** ✅ Diferencia del dominio (correcta).

---

### 3. Repository ✅

| Método | Patient | Diagnosis |
|--------|---------|-----------|
| `save` | ✅ | ✅ |
| `get_by_id` | ✅ | ✅ |
| `list_by_tenant` | ✅ | ✅ |
| `list_by_patient` | ❌ | ✅ |
| `update` | ✅ | ✅ |
| `soft_delete` | ✅ | ✅ |

**Diferencia:** `list_by_patient` existe solo en Diagnosis.

**Clasificación:** ✅ Diferencia del dominio (Diagnosis necesita listar por paciente).

---

### 4. Service ⚠️

| Método | Patient | Diagnosis |
|--------|---------|-----------|
| `create_patient` | ✅ | ❌ |
| `record_diagnosis` | ❌ | ✅ |
| `get_patient` | ✅ | ❌ |
| `get_diagnosis` | ❌ | ✅ |
| `list_patients` | ✅ | ❌ |
| `list_diagnoses_by_patient` | ❌ | ✅ |
| `list_diagnoses_by_tenant` | ❌ | ✅ |
| `update_patient` | ✅ | ❌ |
| `amend_diagnosis` | ❌ | ✅ |
| `delete_patient` | ✅ | ❌ |
| `delete_diagnosis` | ❌ | ✅ |

**Diferencias:**
- `create` vs `record`
- `update` vs `amend`

**Pregunta:** ¿Es esto una inconsistencia del patrón?

**Análisis:**
- `create_patient` → `record_diagnosis`: "Crear" vs "Registrar"
  - En medicina, diagnósticos se "registran", pacientes se "crean"
  - ¿Tiene sentido unificar? Podría causar confusión en el dominio

- `update_patient` → `amend_diagnosis`: "Actualizar" vs "Corregir"
  - "Amend" tiene connotación de corrección,更适合 clinical context
  - Pero "update" es más genérico y común en CRUD

**Recomendación:** Mantener como está (diferencia del dominio) porque refleja el lenguaje clínico.

---

### 5. Model ✅

| Campo | Patient | Diagnosis |
|-------|---------|-----------|
| `id` | ✅ | ✅ |
| `tenant_id` | ✅ | ✅ |
| `patient_id` | ❌ | ✅ |
| `mrn` | ✅ | ❌ |
| `diagnosis_code` | ❌ | ✅ |
| `diagnosis_name` | ❌ | ✅ |
| Clinical fields | ✅ | ✅ |
| `version` | ✅ | ✅ |
| `deleted_at` | ✅ | ✅ |
| `deleted_by` | ✅ | ✅ |
| `delete_reason` | ✅ | ✅ |
| `created_at` | ✅ | ❌ |
| `recorded_at` | ❌ | ✅ |
| `updated_at` | ✅ | ✅ |
| `created_by` | ✅ | ✅ |

**Diferencia:** `created_at` vs `recorded_at`

**Clasificación:** ✅ Diferencia del dominio (un diagnóstico se "registra", no se "crea").

---

### 6. API Endpoints ✅

| Método | Patient | Diagnosis |
|--------|---------|-----------|
| `POST /` | ✅ | ✅ |
| `GET /{id}` | ✅ | ✅ |
| `GET /` | ✅ | ✅ |
| `PATCH /{id}` | ✅ | ✅ |
| `DELETE /{id}` | ✅ | ✅ |

**Resultado:** Identical.

---

### 7. Tests ✅

| Tipo | Patient | Diagnosis |
|------|---------|-----------|
| Unit tests | 9 | 10 |
| Negative tests | 15 | 18 |
| Protocol tests | 5 | 6 |
| **Total** | **29** | **34** |

**Diferencia:** Diagnosis tiene más tests (incluye `list_by_patient`).

**Resultado:** ✅ Misma estructura.

---

## Conclusiones

### ✗ Pattern Inconsistencies

**Ninguna encontrada.**

### ✓ Domain Differences

| Diferencia | Clasificación | Justificación |
|------------|--------------|---------------|
| `record` vs `create` | Domain Difference | Lenguaje clínico: diagnósticos se "registran" |
| `amend` vs `update` | Domain Difference | Lenguaje clínico: diagnósticos se "corrigen" |
| `recorded_at` vs `created_at` | Domain Difference | Clínico vs técnico (ver nota) |
| `list_by_patient` | Domain Difference | Diagnosis necesita filtrar por paciente |
| `patient_id` en evento | Domain Difference | Diagnosis referencia a Patient (identidad) |

#### Nota sobre `created_at` vs `recorded_at`

> "Una cosa es cuándo llegó el registro a la base. Otra distinta es cuándo ocurrió el acto clínico."

**Recomendación futura:**

```
Diagnosis (y todos los contextos)
├── created_at    → Metadato técnico (cuándo se persistió)
├── updated_at    → Metadato técnico (cuándo se modificó)
├── deleted_at    → Metadato técnico (cuándo se soft-deleteó)
└── recorded_at   → Dato clínico (cuándo ocurrió el acto)
```

**No cambiar ahora.** Esto aplica para Treatment y contextos futuros.

---

## Regla para Diferencias Futuras

Cada nueva diferencia debe clasificarse:

```
✓ Domain Difference          → Se mantiene
✓ Infrastructure Difference  → Se evalúa
✗ Pattern Inconsistency      → Se corrige
```

---

## Recomendación

**El patrón está listo para Treatment.**

---

## Para Treatment

```
Treatment será el tercer bounded context.

Regla:
- Usar Diagnosis como template
- Adaptar solo los campos de dominio
- NO modificar Patient ni Diagnosis
- Si algo no encaja, clasificar en la retrospectiva
```

**Primero:** Sesión de diseño (Treatment es más complejo)

---

**Firmado:** OpenHands Agent
**Fecha:** 2026-07-15
