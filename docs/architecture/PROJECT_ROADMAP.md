# EREN — Clinical Engineering Copilot

**Fecha:** 2026-07-15
**Versión:** 3.0

---

## Resumen Ejecutivo

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              CLINICAL ENGINEERING COPILOT                   │
│                                                             │
│  El primer copiloto de IA especializado en                  │
│  ingeniería clínica.                                         │
│                                                             │
│  No reemplaza sistemas existentes.                           │
│  Se conecta a ellos y los hace más inteligentes.           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ¿Qué es EREN?

```
EREN es un copiloto de IA que ayuda al ingeniero biomédico
a resolver problemas de equipos médicos de forma más rápida
y basada en evidencia.
```

**Ejemplo de conversación:**
```
Ingeniero: "EREN, el Servo-i de UCI 4 marca High Airway Pressure"

EREN:
├── "Caso creado."
├── "Ya encontré 13 incidentes similares."
│   ├── 8 fueron por obstrucción en circuito (62%)
│   ├── 3 por falla de sensor de presión (23%)
│   └── 2 por presión máxima mal configurada (15%)
├── "Según el manual, sección 4.2 - Verificación de presión:"
├── "Según el historial: último mantenimiento hace 45 días."
├── "Te recomiendo hacer estas pruebas en este orden:"
│   1. Verificar trampa de agua
│   2. Inspeccionar sensor de presión
│   3. Revisar configuración
└── "Probabilidad de resolverlo: 86%."
```

---

## Diferencia con otros sistemas

| Sistema | Rol | EREN es diferente porque... |
|---------|-----|---------------------------|
| HIS (Epic, Cerner) | Gestiona pacientes | EREN no gestiona pacientes |
| CMMS | Gestiona mantenimiento | EREN no es solo gestión |
| ERP (SAP, Odoo) | Gestiona recursos | EREN no reemplaza ERP |
| EREN | **Copiloto de IA** | Entiende, razona, recomienda |

**EREN NO reemplaza. EREN se conecta y hace más inteligente.**

---

## Integraciones posibles

```
Epic ──────┐
            │
Cerner ────┼──► EREN ──► HCE (Hospital más inteligente)
            │
SAP/Odoo ───┤
            │
OpenMRS ────┘
```

EREN puede conectarse a cualquier sistema que tenga información relevante.

---

## Arquitectura del Sistema

```
                        ┌─────────────┐
                        │     AI      │  ← Capa, no dominio
                        │   Layer     │
                        │             │
                        │• Comprende  │
                        │• Consulta   │
                        │• Razonamiento│
                        │• Recomienda │
                        └──────┬──────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
   ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
   │   Device   │         │ Engineering │         │ Knowledge  │
   │            │         │  Incident   │         │            │
   │• Especific.│         │    ♥        │         │• Manuales  │
   │• Status    │         │• Problema   │         │• Normas   │
   │• Ubicación │         │• Contexto   │         │• Boletines│
   │• Historial │         │• Evidencia  │         │• Casos    │
   └─────┬─────┘         └─────┬─────┘         └─────┬─────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                        ┌──────┴──────┐
                        │ Maintenance  │
                        │             │
                        │• Historial  │
                        │• Intervenc. │
                        │• Calibrac.  │
                        └─────────────┘
```

**Nota:** AI NO es un bounded context. AI es la capa que orquesta.

---

## Dominios del Sistema

### 1. Device — Conoce el equipo

```
Responsabilidad: Mantener información técnica del equipo médico.

Preguntas que responde:
├── ¿Qué equipo es este?
├── ¿Dónde está ubicado?
├── ¿Cuál es su estado?
├── ¿Cuándo fue el último mantenimiento?
└── ¿Tiene incidencias previas?
```

### 2. Engineering Incident — Conoce el problema

```
Responsabilidad: Gestionar el ciclo de vida del problema reportado.

Preguntas que responde:
├── ¿Qué problema se está resolviendo?
├── ¿Qué evidencia se ha recopilado?
├── ¿Qué acciones se han tomado?
├── ¿Qué otros casos similares existen?
└── ¿Se resolvió?

♥ Este es el corazón del sistema.
```

### 3. Knowledge — Conoce la evidencia técnica

```
Responsabilidad: Mantener conocimiento técnico searchable.

Preguntas que responde:
├── ¿Qué dice el manual sobre este problema?
├── ¿Hay boletines del fabricante?
├── ¿Existen recalls de FDA?
├── ¿Hay normas IEC/ISO aplicables?
├── ¿Qué casos similares existen?
└── ¿Qué lecciones aprendimos?
```

### 4. Maintenance — Conoce el historial técnico

```
Responsabilidad: Rastrear intervenciones técnicas.

Preguntas que responde:
├── ¿Qué intervenciones se han hecho?
├── ¿Cuándo fue la última calibración?
├── ¿Qué repuestos se usaron?
├── ¿Quién trabajó en el equipo?
└── ¿Qué patrones emergen?
```

---

## Roadmap por Fases

### Phase 1: MVP — Engineering Core (AHORA)

```
Objetivo: Demostrar que EREN ayuda a resolver problemas reales.

Componentes:
├── Device Management
├── Engineering Incident (el corazón)
├── Knowledge Base
├── Maintenance History
└── AI Layer (orquesta)
```

### Phase 2: MVP Comercializable

```
Objetivo: Vender el producto.

Un hospital puede usar EREN para apoyar a su 
departamento de ingeniería clínica sin necesidad 
de integraciones complejas.
```

### Phase 3: Clinical Integration

```
Objetivo: Enriquecer con contexto clínico.

Disponible:
├── Patient (existe en Foundation)
├── Diagnosis (existe en Foundation)
├── Treatment
├── Observation
└── Encounter
```

### Phase 4: Smart Hospital

```
Objetivo: EREN comprende el hospital completo.

La IA correlaciona Clinical + Engineering
convirtiéndose en un verdadero asistente hospitalario.
```

---

## Estado Actual

### ✅ Foundation — CONGELADO

| Componente | Estado |
|------------|--------|
| Patrón arquitectónico | ✅ Listo |
| Patient Context | ✅ Reference Implementation |
| Diagnosis Context | ✅ Reference Implementation |
| Tests | ✅ 48+ passing |

### 🔴 Por construir (Phase 1)

| Dominio | Estado | Prioridad |
|---------|--------|-----------|
| Device | ❌ No existe | 🔴 Crítica |
| Engineering Incident | ❌ No existe | 🔴 Crítica |
| Knowledge | ❌ No existe | 🔴 Crítica |
| Maintenance | ❌ No existe | 🟡 Alta |
| AI Layer | ❌ No existe | 🔴 Crítica |

---

## Métricas de Éxito

```
Arquitectura:
├── ¿Cuántos días tarda crear un dominio?
├── ¿Cuántas inconsistencias de patrón aparecieron?
└── ¿Se tocó Foundation?

Producto:
├── ¿Cuánto tarda EREN en proponer causas?
├── ¿Cuántos incidentes se resuelven en primer contacto?
├── ¿El ingeniero biomédico se siente ayudado?
└── ¿Funciona la integración con sistemas externos?

Porque el producto no son los dominios.
El producto es: ¿EREN resuelve problemas reales más rápido?
```

---

## Lenguaje Ubicuo

| Término | Definición |
|---------|------------|
| **Device** | Equipo médico bajo gestión de ingeniería clínica |
| **Engineering Incident** | Problema reportado que requiere atención del ingeniero |
| **Knowledge** | Información técnica searchable (manuales, normas, casos) |
| **Maintenance** | Intervenciones técnicas realizadas |
| **Copilot** | IA que asiste pero no reemplaza al ingeniero |

---

**Firmado:** OpenHands Agent
**Fecha:** 2026-07-15
