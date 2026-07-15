# Domain Discovery: Case Management + Device Management

**Fecha:** 2026-07-15
**Estado:** DISCOVERY
**Fase:** Phase 1 MVP — Engineering Core

---

## Pregunta Guía

```
"¿Esto ayuda al ingeniero biomédico a resolver 
un problema real más rápido?"
```

Si la respuesta es no, probablemente no pertenece al MVP.

---

## Visión del MVP

```
Ingeniero biomédico
        ↓
Describe un problema del equipo
        ↓
EREN entiende el caso
        ↓
Consulta conocimiento técnico
        ↓
Analiza historial del equipo
        ↓
Propone causas probables
        ↓
Sugiere pruebas
        ↓
Sugiere solución
        ↓
Genera reporte técnico
```

**Ese es el producto.**

---

## Arquitectura del MVP

```
                    AI Core
                       │
                       │
              Case Management ← CORAZÓN
              /      |      \      \
             /       |       \      \
            ▼        ▼        ▼       ▼
         Device  Knowledge  Maintenance  Future
```

---

# PARTE 1: CASE MANAGEMENT

---

## 1.1 ¿Qué es un Case?

```
Un Case representa un problema real de ingeniería clínica.
```

**Ejemplos:**
- "Ventilador Servo-i de UCI-3 presenta alarma de presión alta"
- "Bomba de infusión #452 requiere calibración"
- "Monitor de signos vitales presenta falla en pantalla"

**NO es:**
- Una tarea administrativa
- Un registro de mantenimiento rutinario
- Un ticket genérico de soporte

---

## 1.2 Responsabilidades del Dominio

```
Case Management ES:
├── Recibir y registrar problemas reportados
├── Rastrear el ciclo de vida del problema
├── Coordinar información entre Device, Knowledge, Maintenance
├── Generar evidencia para análisis futuro
└── Producir reportes técnicos

Case Management NO ES:
├── Un sistema de tickets genérico
├── Un repositorio de documentos
├── Un módulo de inventario
└── Un sistema de órdenes de compra
```

---

## 1.3 Lenguaje Ubicuo

| Término | Definición |
|---------|------------|
| **Case** | Un problema reportado que requiere atención del ingeniero biomédico |
| **Incident** | Un evento inesperado que interrumpe el funcionamiento normal de un equipo |
| **Issue** | Una observación que puede convertirse en incident |
| **Resolution** | Solución aplicada al case |
| **Escalation** | Cuando un case requiere nivel de atención superior |
| **Closure** | Cuando el case se considera resuelto |

---

## 1.4 Ciclo de Vida del Case

```
┌─────────┐
│ REPORTED │ ← Ingeniero reporta el problema
└────┬────┘
     │
     ▼
┌─────────┐
│ TRIAGED │ ← EREN clasifica prioridad
└────┬────┘
     │
     ▼
┌─────────┐
│  OPEN   │ ← Ingeniero comienza trabajo
└────┬────┘
     │
     ▼
┌──────────┐
│IN_PROGRESS│ ← Trabajando en solución
└────┬─────┘
     │
     ├──►┌───────────┐
     │    │ESCALATED │ ← Requiere más recursos
     │    └─────┬─────┘
     │          │
     │          ▼
     │    ┌───────────┐
     └────│  RESOLVED │
          └─────┬─────┘
                │
                ▼
          ┌───────────┐
          │  CLOSED   │
          └───────────┘
```

---

## 1.5 Estados y Transiciones

| Estado | Puede Ir A | Trigger |
|--------|------------|---------|
| REPORTED | TRIAGED, CANCELLED | Caso recibido |
| TRIAGED | OPEN, CANCELLED | Clasificación completada |
| OPEN | IN_PROGRESS | Ingeniero acepta |
| IN_PROGRESS | RESOLVED, ESCALATED | Solución encontrada |
| ESCALATED | IN_PROGRESS | Recurso disponible |
| RESOLVED | CLOSED | Confirmación |
| CLOSED | (terminal) | Case archivado |

---

## 1.6 Invariantes del Case

```
1. Un Case siempre tiene un dispositivo asociado
2. Un Case siempre tiene un reportero (ingeniero)
3. Un Case tiene exactamente un estado válido
4. Un Case no puede resolverse sin al menos una acción
5. Un Case cerrado no puede reabrirse
6. Un Case puede tener múltiples notas de conversación
7. Un Case puede tener múltiples acciones tomadas
8. Un Case tiene exactamente una resolución final
```

---

## 1.7 Eventos del Dominio

| Evento | Descripción | Datos clave |
|--------|------------|-------------|
| CaseReported | Se reportó un nuevo problema | device_id, reporter_id, description |
| CaseTriaged | Se clasificó prioridad | priority, category |
| CaseOpened | Ingeniero aceptó el case | engineer_id |
| CaseProgressed | Se agregó información | action, note |
| CaseEscalated | Se subió nivel de atención | reason, level |
| CaseResolved | Se encontró solución | resolution, parts_used |
| CaseClosed | Case archivado | final_report |
| AIAssistanceRequested | Se pidió ayuda a la IA | query, context |

---

## 1.8 Actores

| Actor | Rol | Responsabilidad |
|-------|-----|----------------|
| BiomedicalEngineer | Ingeniero biomédico | Reporta, diagnostica, resuelve |
| AISystem | Sistema de IA | Analiza, sugiere, aprende |
| Device | Sistema de equipos | Proveedor de información |
| KnowledgeBase | Base de conocimientos | Proveedor de soluciones conocidas |

---

## 1.9 Casos de Uso

### UC-001: Reportar un Problema
```
Actor: BiomedicalEngineer
Flujo:
1. Ingeniero describe el problema
2. EREN identifica dispositivo (si es posible)
3. EREN crea un Case
4. Sistema asigna prioridad inicial
5. Ingeniero confirma o ajusta

Resultado: Case en estado REPORTED
```

### UC-002: Consultar Conocimiento
```
Actor: AISystem
Flujo:
1. AI recibe contexto del Case
2. AI consulta Knowledge Base
3. AI recupera manuales relevantes
4. AI recupera known issues similares
5. AI propone causas probables

Resultado: Lista de posibles causas con evidencia
```

### UC-003: Registrar Acción
```
Actor: BiomedicalEngineer
Flujo:
1. Ingeniero realiza prueba
2. Ingeniero registra resultado
3. Sistema adjunta evidencia
4. AI analiza nuevo contexto

Resultado: Case actualizado con evidencia
```

### UC-004: Resolver y Cerrar
```
Actor: BiomedicalEngineer
Flujo:
1. Ingeniero identifica solución
2. Ingeniero registra resolución
3. Sistema genera reporte técnico
4. Ingeniero confirma cierre

Resultado: Case en estado CLOSED
```

### UC-005: Generar Reporte
```
Actor: AISystem
Flujo:
1. AI recibe Case cerrado
2. AI compila historial completo
3. AI incluye evidencia y acciones
4. AI incluye lecciones aprendidas
5. AI genera documento para archivo

Resultado: Reporte técnico completo
```

---

## 1.10 Reglas de Negocio

| Regla | Descripción |
|-------|-------------|
| BR-001 | Todo Case debe asociarse a un Device existente |
| BR-002 | Solo ingenieros biomédicos pueden crear Cases |
| BR-003 | Un Case no puede resolverse sin al menos una acción |
| BR-004 | Cases de prioridad CRITICAL requieren respuesta en 15 min |
| BR-005 | Cases de prioridad HIGH requieren respuesta en 2 horas |
| BR-006 | Cases de prioridad MEDIUM requieren respuesta en 24 horas |
| BR-007 | Cases de prioridad LOW requieren respuesta en 72 horas |
| BR-008 | Un Case cerrado genera automáticamente un reporte |
| BR-009 | El reporte final se archiva en el historial del Device |

---

## 1.11 Outside-In vs Inside-Out

```
Outside-In (para el ingeniero):
"Quiero reportar un problema y que EREN me ayude a resolverlo"

Inside-Out (desde el sistema):
1. Case recibe reporte
2. Case pide información a Device
3. Case consulta Knowledge
4. Case retorna sugerencia al ingeniero
```

---

# PARTE 2: DEVICE MANAGEMENT

---

## 2.1 ¿Qué es un Device?

```
Un Device es un equipo médico que requiere gestión de ingeniería clínica.
```

**Ejemplos:**
- Ventilador Servo-i
- Bomba de infusión
- Monitor de signos vitales
- Bomba de jeringa
- Desfibrilador
- Equipo de rayos X portátil

---

## 2.2 Responsabilidades del Dominio

```
Device Management ES:
├── Registrar equipos médicos
├── Mantener especificaciones técnicas
├── Rastrear ubicación física
├── Reportar estado actual
├── Alertar sobre mantenimiento pendiente
└── Proporcionar contexto para Cases

Device Management NO ES:
├── Un catálogo de activos financieros
├── Un sistema de órdenes de compra
├── Un sistema de inventory de repuestos
└── Un módulo de historial médico
```

---

## 2.3 Lenguaje Ubicuo

| Término | Definición |
|---------|------------|
| **Device** | Equipo médico bajo gestión de ingeniería clínica |
| **Model** | Tipo/genérico de equipo (ej: "Servo-i") |
| **SerialNumber** | Identificador único físico del equipo |
| **Location** | Ubicación física en el hospital |
| **Status** | Estado operacional del equipo |
| **Criticality** | Nivel de criticidad para pacientes |

---

## 2.4 Estados del Device

```
┌─────────────┐
│  ACTIVE    │ ← En uso normal
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  INACTIVE  │ ← Fuera de servicio temporalmente
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ DECOMMISSIONED│ ← Retirado permanentemente
└─────────────┘

Estados operacionales (dentro de ACTIVE):
┌─────────────┐
│  OPERATIONAL│ ← Funcionando correctamente
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FAULTY    │ ← Con problema reportado
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MAINTENANCE│ ← En proceso de mantenimiento
└─────────────┘
```

---

## 2.5 Invariantes del Device

```
1. Un Device tiene exactamente un SerialNumber único
2. Un Device pertenece a un único Model
3. Un Device tiene exactamente una Location
4. Un Device tiene exactamente un Status operacional
5. Un Device puede tener cero o más Cases activos
6. Un Device tiene historial completo de Cases cerrados
7. Un Device sabe cuándo fue el último mantenimiento
8. Un Device sabe cuándo vence el próximo mantenimiento
```

---

## 2.6 Eventos del Dominio

| Evento | Descripción | Datos clave |
|--------|------------|-------------|
| DeviceRegistered | Nuevo equipo registrado | serial_number, model_id |
| DeviceLocated | Cambio de ubicación | location |
| DeviceStatusChanged | Cambio de estado operacional | previous_status, new_status |
| DeviceMaintenanceScheduled | Mantenimiento programado | maintenance_id, due_date |
| DeviceMaintenanceCompleted | Mantenimiento realizado | maintenance_id, result |
| DeviceCalibrationDue | Calibración requerida | calibration_due_date |
| DeviceAlertTriggered | Alerta de riesgo | alert_type, severity |

---

## 2.7 Información del Device

```
Device:
├── Identificación
│   ├── Serial Number
│   ├── Model (fabricante, modelo)
│   ├── Class (tipo de equipo)
│   └── UMDNS code
│
├── Localización
│   ├── Hospital
│   ├── Department
│   ├── Unit
│   └── Bed/Location detail
│
├── Especificaciones
│   ├── Fabricante
│   ├── Año de fabricación
│   ├── Número de serie
│   ├── Firmware version
│   └── Accessorios
│
├── Estado operacional
│   ├── Status (OPERATIONAL, FAULTY, MAINTENANCE)
│   ├── Criticality (CRITICAL, HIGH, MEDIUM, LOW)
│   ├── Hours of operation
│   └── Last performance check
│
├── Mantenimiento
│   ├── Last maintenance date
│   ├── Next maintenance due
│   ├── Maintenance contract
│   └── Service provider
│
├── Calibración
│   ├── Last calibration date
│   ├── Next calibration due
│   └── Calibration certificate
│
└── Riesgo
    ├── Risk score
    ├── Age-related risk
    ├── Usage-related risk
    └── Incident history
```

---

## 2.8 Relación Device ↔ Case

```
┌─────────────┐         ┌─────────────┐
│   Device    │ 1    *  │    Case     │
│             ├─────────┤             │
│ - id        │         │ - id        │
│ - serial    │         │ - device_id │
│ - model     │         │ - status    │
│ - location  │         │ - priority   │
│ - status    │         │ - reporter  │
└─────────────┘         └─────────────┘

Relaciones:
- Un Device puede tener muchos Cases (historial)
- Un Case tiene exactamente un Device
- Cuando un Device tiene Case FAULTY, el status del Device cambia a FAULTY
```

---

## 2.9 Relación Device ↔ Maintenance

```
┌─────────────┐         ┌─────────────┐
│   Device    │ 1    *  │ Maintenance │
│             ├─────────┤             │
│ - id        │         │ - id        │
│ - last_main │         │ - device_id │
│ - next_main │         │ - type      │
└─────────────┘         │ - scheduled │
                        │ - completed │
                        └─────────────┘
```

---

## 2.10 Reglas de Negocio

| Regla | Descripción |
|-------|-------------|
| DR-001 | Todo Device debe tener Serial Number único |
| DR-002 | Todo Device debe tener Location definida |
| DR-003 | Devices CRITICAL requieren mantenimiento preventivo mensual |
| DR-004 | Devices HIGH requieren mantenimiento preventivo trimestral |
| DR-005 | Devices MEDIUM requieren mantenimiento preventivo semestral |
| DR-006 | Devices LOW requieren mantenimiento preventivo anual |
| DR-007 | Calibración es independiente del mantenimiento |
| DR-008 | Device con Case ACTIVE no puede decommissionarse |

---

# PARTE 3: RELACIONES ENTRE DOMINIOS

---

## 3.1 Mapa de Contexto

```
┌─────────────────────────────────────────────────────────────┐
│                        AI Core                               │
│                         │                                   │
│                         ▼                                   │
│              ┌───────────────────────┐                     │
│              │   Case Management     │                     │
│              │         ♥             │                     │
│              └───────────┬───────────┘                     │
│                          │                                  │
│        ┌─────────────────┼─────────────────┐              │
│        │                 │                 │              │
│        ▼                 ▼                 ▼              │
│  ┌───────────┐    ┌───────────┐    ┌───────────────┐     │
│  │  Device   │    │ Knowledge  │    │ Maintenance   │     │
│  │           │    │           │    │               │     │
│  │ • Info    │    │ • Manuals │    │ • Work Orders │     │
│  │ • Status  │    │ • Issues  │    │ • Calibration │     │
│  │ • History │    │ • Resol.  │    │ • Preventive  │     │
│  └───────────┘    └───────────┘    └───────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.2 Flujo de Información

```
1. Ingeniero reporta → Case Management → Crea Case
                                              │
                                              ▼
                              ┌───────────────────────────┐
                              │ AI Core analiza contexto   │
                              └─────────────┬─────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              │                             │                             │
              ▼                             ▼                             ▼
     ┌───────────────┐            ┌───────────────┐            ┌───────────────┐
     │    Device     │            │   Knowledge   │            │  Maintenance  │
     │               │            │               │            │               │
     │• Get specs    │            │• Search issues│            │• Get history  │
     │• Get history  │            │• Get manuals  │            │• Check due    │
     │• Get status   │            │• Get resol.   │            │• Create order │
     └───────────────┘            └───────────────┘            └───────────────┘
              │                             │                             │
              └─────────────────────────────┼─────────────────────────────┘
                                            │
                                            ▼
                              ┌───────────────────────────┐
                              │ AI Core propone solución   │
                              └─────────────┬─────────────┘
                                            │
                                            ▼
                                   Case Management
                                          │
                                          ▼
                                   Ingeniero recibe
                                   sugerencia
```

---

## 3.3 Preguntas que AI Core debe responder

| Pregunta | Fuentes consultadas |
|----------|---------------------|
| ¿Qué equipo está afectado? | Device |
| ¿Cuáles son las specs? | Device |
| ¿Dónde está ubicado? | Device |
| ¿Qué pasó antes? | Case + Maintenance |
| ¿Hay casos similares? | Knowledge |
| ¿Qué manuales aplican? | Knowledge |
| ¿Qué mantenimiento tiene pendiente? | Maintenance |
| ¿Qué repuestos se usaron antes? | Maintenance + Knowledge |

---

## 3.4 Integración con Clinical (Futuro)

```
┌─────────────────────────────────────────────────────────┐
│                      EREN                                │
│                                                         │
│    ┌───────────┐         ┌───────────┐                │
│    │Engineering │         │ Clinical  │                │
│    │  Core     │         │   Core    │                │
│    │           │         │           │                │
│    │• Device   │         │• Patient  │                │
│    │• Case     │         │• Diagnosis│                │
│    │• Knowledge│         │• Treatment│                │
│    │• Maint.   │         │           │                │
│    └─────┬─────┘         └─────┬─────┘                │
│          │                       │                      │
│          └───────────┬───────────┘                      │
│                      │                                  │
│                      ▼                                  │
│              ┌───────────────┐                        │
│              │  AI Core      │                        │
│              │               │                        │
│              │ Correlaciona  │                        │
│              │ información   │                        │
│              └───────────────┘                        │
└─────────────────────────────────────────────────────────┘

Preguntas futuras:
├── ¿Este ventilador está asignado a algún paciente?
├── ¿Qué diagnóstico tiene el paciente conectado?
├── ¿Existe una orden médica que impida apagar el equipo?
└── ¿Qué medicamentos está recibiendo?
```

---

# PARTE 4: VALIDACIÓN DEL DISEÑO

---

## 4.1 Preguntas de Validación

| Pregunta | Respuesta esperada |
|----------|-------------------|
| ¿Un ingeniero biomédico entendería estos términos? | Sí |
| ¿Las responsabilidades están claras? | Sí |
| ¿Los límites entre contextos son claros? | Sí |
| ¿Se evitan acoplamientos no deseados? | Sí |
| ¿El diseño soporta escalabilidad? | Sí |

---

## 4.2 Métricas de Éxito del MVP

```
1. ¿Cuánto tarda un ingeniero en reportar un problema?
   → Meta: < 2 minutos

2. ¿Cuánto tarda EREN en proponer causas probables?
   → Meta: < 30 segundos

3. ¿Cuántos casos se resuelven en primer contacto?
   → Meta: > 60%

4. ¿Cuánto tarda en generar un reporte técnico?
   → Meta: < 1 minuto

5. ¿El ingeniero biomédico se siente ayudado?
   → Meta: > 90% satisfacción
```

---

## 4.3 Lo que NO pertenece al MVP

| Descartado | Razón |
|------------|-------|
| Órdenes de compra | No ayuda directamente a resolver el problema |
| Inventory de repuestos | Puede agregarse después |
| Contratos de servicio | No es el foco del MVP |
| Historial financiero | No es relevante para el ingeniero |

---

## 4.4 Lo que SÍ pertenece al MVP

| Incluido | Razón |
|----------|-------|
| Registro de Device | Sin esto no hay contexto |
| Registro de Case | Es el corazón del sistema |
| Conversación con IA | Es el diferenciador |
| Consulta de Knowledge | Reduce tiempo de resolución |
| Historial de mantenimiento | Proporciona contexto |
| Generación de reportes | Cierra el ciclo |

---

# PARTE 5: PRÓXIMOS PASOS

---

## 5.1 Después del Domain Discovery

```
1. Validar este documento con stakeholders
2. Ajustar basado en feedback
3. Crear bounded contexts siguiendo EREN Template
4. Implementar Device Context primero
5. Implementar Case Management después
6. Integrar con AI Core
7. Probar flujo completo de extremo a extremo
```

---

## 5.2 Orden de Implementación Sugerido

```
Paso 1: Device Management
├── Events
├── Repository
├── Service
├── Model
├── Router
└── Tests

Paso 2: Case Management
├── Events
├── Repository
├── Service
├── Model
├── Router
└── Tests

Paso 3: AI Core Integration
├── Conversational interface
├── Knowledge retrieval
├── Case context assembly
└── Suggestion engine

Paso 4: Flujo Completo
├── End-to-end test
├── Performance validation
└── User acceptance
```

---

## 5.3 Preguntas Pendientes

```
1. ¿Cómo se identifica automáticamente el dispositivo?
   (QR, RFID, búsqueda manual, ...)

2. ¿Qué nivel de integración con sistemas externos en MVP?
   (Epic, Cerner, HL7, FHIR, ...)

3. ¿Cómo se entrena el modelo de IA?
   (Histórico de cases, Knowledge Base, manuales, ...)

4. ¿Qué formato tienen los manuales técnicos?
   (PDF, texto, structured data, ...)

5. ¿Cómo se valida la calidad de las sugerencias de IA?
   (Review humano, metrics, A/B testing, ...)
```

---

**Estado:** Listo para revisión
**Pendiente:** Validación con stakeholders

---

**Firmado:** OpenHands Agent
**Fecha:** 2026-07-15
