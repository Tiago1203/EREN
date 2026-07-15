# Domain Discovery: Device + Engineering Incident + Knowledge + Maintenance

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
   └─────────────┘         └─────────────┘         └───────────┘
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

---

# PARTE 1: ENGINEERING INCIDENT ♥ (El Corazón)

---

## 1.1 ¿Qué es un Engineering Incident?

```
Un Engineering Incident representa un problema real de ingeniería 
clínica que requiere la atención del ingeniero biomédico.
```

**Ejemplos:**
- "Ventilador Servo-i de UCI-3 presenta alarma de presión alta"
- "Bomba de infusión #452 requiere calibración"
- "Monitor de signos vitales presenta falla en pantalla"

**El nombre es importante:**
- ❌ "Case Management" — Suena a ServiceNow, Jira, CRM
- ❌ "Incident Ticket" — Suena a soporte genérico
- ✅ **"Engineering Incident"** — Lenguaje natural del ingeniero biomédico

---

## 1.2 Responsabilidades del Dominio

```
Engineering Incident ES:
├── Recibir y registrar problemas reportados
├── Rastrear el ciclo de vida del problema
├── Recopilar evidencia técnica
├── Coordinar información entre Device, Knowledge, Maintenance
├── Producir reportes técnicos
└── Aprender de casos similares

Engineering Incident NO ES:
├── Un sistema de tickets genérico
├── Un repositorio de documentos
├── Un módulo de inventory
└── Un sistema de órdenes de compra
```

---

## 1.3 Lenguaje Ubicuo

| Término | Definición |
|---------|------------|
| **Engineering Incident** | Problema reportado que requiere atención del ingeniero |
| **Symptom** | Manifestación reported del problema |
| **Investigation** | Proceso de diagnóstico |
| **Evidence** | Datos recopilados durante la investigación |
| **Resolution** | Solución aplicada al incidente |
| **Escalation** | Cuando requiere nivel de atención superior |
| **Closure** | Cuando se considera resuelto |

---

## 1.4 Ciclo de Vida

```
┌──────────────┐
│   REPORTED   │ ← Ingeniero reporta el problema
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   TRIAGED    │ ← EREN clasifica prioridad
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    OPEN      │ ← Ingeniero acepta el caso
└──────┬───────┘
       │
       ▼
┌───────────────┐
│ IN_PROGRESS   │ ← Trabajando en investigación
└───────┬───────┘
        │
        ├──►┌───────────────┐
        │    │  ESCALATED   │ ← Requiere más recursos
        │    └───────┬───────┘
        │            │
        │            ▼
        │    ┌───────────────┐
        └────│  RESOLVED    │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │    CLOSED     │
             └───────────────┘
```

---

## 1.5 Estados y Transiciones

| Estado | Puede Ir A | Trigger |
|--------|------------|---------|
| REPORTED | TRIAGED, CANCELLED | Incidente recibido |
| TRIAGED | OPEN, CANCELLED | Clasificación completada |
| OPEN | IN_PROGRESS | Ingeniero acepta |
| IN_PROGRESS | RESOLVED, ESCALATED | Solución encontrada |
| ESCALATED | IN_PROGRESS | Recurso disponible |
| RESOLVED | CLOSED | Confirmación |
| CLOSED | (terminal) | Archivado |

---

## 1.6 Invariantes

```
1. Un Engineering Incident siempre tiene un Device asociado
2. Un Engineering Incident siempre tiene un reportero (ingeniero)
3. Un Engineering Incident tiene exactamente un estado válido
4. Un Engineering Incident no puede resolverse sin al menos una acción
5. Un Engineering Incident cerrado no puede reabrirse
6. Un Engineering Incident puede tener múltiples notas
7. Un Engineering Incident puede tener múltiples acciones tomadas
8. Un Engineering Incident tiene exactamente una resolución final
```

---

## 1.7 Eventos del Dominio

| Evento | Descripción |
|--------|-------------|
| IncidentReported | Se reportó un nuevo problema |
| IncidentTriaged | Se clasificó prioridad |
| IncidentOpened | Ingeniero aceptó el caso |
| IncidentProgressed | Se agregó información |
| IncidentEscalated | Se subió nivel de atención |
| IncidentResolved | Se encontró solución |
| IncidentClosed | Archivado |
| AIAssistanceRequested | Se pidió ayuda a la IA |

---

## 1.8 Casos de Uso

### UC-001: Reportar un Problema
```
Actor: BiomedicalEngineer
Flujo:
1. Ingeniero describe el problema
2. EREN identifica dispositivo
3. Sistema crea Engineering Incident
4. Se asigna prioridad inicial
5. Ingeniero confirma o ajusta
```

### UC-002: Investigar con Ayuda de IA
```
Actor: AI Layer
Flujo:
1. AI recibe contexto del incidente
2. AI consulta Knowledge Base
3. AI recupera casos similares
4. AI propone causas probables con % de probabilidad
5. AI sugiere pruebas en orden
6. AI estima probabilidad de resolución
```

### UC-003: Registrar Evidencia
```
Actor: BiomedicalEngineer
Flujo:
1. Ingeniero realiza prueba
2. Ingeniero registra resultado
3. Sistema adjunta evidencia
4. AI analiza nuevo contexto
5. AI actualiza probabilidades
```

### UC-004: Resolver y Cerrar
```
Actor: BiomedicalEngineer
Flujo:
1. Ingeniero identifica solución
2. Ingeniero registra resolución
3. Sistema genera reporte técnico
4. Ingeniero confirma cierre
```

### UC-005: Aprender del Caso
```
Actor: AI Layer
Flujo:
1. AI recibe incidente cerrado
2. AI compila información
3. AI extrae lecciones aprendidas
4. AI actualiza Knowledge Base
5. AI mejora predicciones futuras
```

---

## 1.9 Reglas de Negocio

| Regla | Descripción |
|-------|-------------|
| EI-001 | Todo Engineering Incident debe asociarse a un Device existente |
| EI-002 | Solo ingenieros biomédicos pueden crear incidentes |
| EI-003 | Un incidente no puede resolverse sin al menos una acción |
| EI-004 | CRITICAL requiere respuesta en 15 min |
| EI-005 | HIGH requiere respuesta en 2 horas |
| EI-006 | MEDIUM requiere respuesta en 24 horas |
| EI-007 | LOW requiere respuesta en 72 horas |
| EI-008 | Un incidente cerrado genera automáticamente un reporte |
| EI-009 | El reporte se archiva en historial del Device |

---

# PARTE 2: DEVICE

---

## 2.1 ¿Qué es un Device?

```
Un Device es un equipo médico que requiere gestión 
de ingeniería clínica.
```

---

## 2.2 Responsabilidades

```
Device ES:
├── Registrar equipos médicos
├── Mantener especificaciones técnicas
├── Rastrear ubicación física
├── Reportar estado actual
├── Alertar sobre mantenimiento pendiente
└── Proporcionar contexto para incidentes

Device NO ES:
├── Un catálogo de activos financieros
├── Un sistema de órdenes de compra
├── Un módulo de inventory de repuestos
└── Un sistema de historial médico
```

---

## 2.3 Estados

```
Estado del equipo:
├── ACTIVE ← En uso
├── INACTIVE ← Fuera de servicio temporalmente
└── DECOMMISSIONED ← Retirado permanentemente

Estado operacional (dentro de ACTIVE):
├── OPERATIONAL ← Funcionando correctamente
├── FAULTY ← Con problema reportado
└── MAINTENANCE ← En proceso de mantenimiento
```

---

## 2.4 Información del Device

```
Device:
├── Identificación
│   ├── Serial Number (único)
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
│   ├── Firmware version
│   └── Accessorios
│
├── Estado operacional
│   ├── Status (OPERATIONAL, FAULTY, MAINTENANCE)
│   ├── Criticality (CRITICAL, HIGH, MEDIUM, LOW)
│   └── Hours of operation
│
├── Mantenimiento
│   ├── Last maintenance date
│   ├── Next maintenance due
│   └── Service provider
│
└── Calibración
    ├── Last calibration date
    ├── Next calibration due
    └── Certificate reference
```

---

## 2.5 Invariantes

```
1. Un Device tiene exactamente un Serial Number único
2. Un Device pertenece a un único Model
3. Un Device tiene exactamente una Location
4. Un Device tiene exactamente un Status operacional
5. Un Device puede tener cero o más Engineering Incidents activos
6. Un Device tiene historial completo de incidentes cerrados
7. Un Device sabe cuándo fue el último mantenimiento
8. Un Device sabe cuándo vence el próximo mantenimiento
```

---

## 2.6 Eventos del Dominio

| Evento | Descripción |
|--------|-------------|
| DeviceRegistered | Nuevo equipo registrado |
| DeviceLocated | Cambio de ubicación |
| DeviceStatusChanged | Cambio de estado operacional |
| DeviceMaintenanceScheduled | Mantenimiento programado |
| DeviceMaintenanceCompleted | Mantenimiento realizado |
| DeviceCalibrationDue | Calibración requerida |
| DeviceAlertTriggered | Alerta de riesgo |

---

## 2.7 Reglas de Negocio

| Regla | Descripción |
|-------|-------------|
| DR-001 | Todo Device debe tener Serial Number único |
| DR-002 | Todo Device debe tener Location definida |
| DR-003 | Devices CRITICAL requieren mantenimiento mensual |
| DR-004 | Devices HIGH requieren mantenimiento trimestral |
| DR-005 | Devices MEDIUM requieren mantenimiento semestral |
| DR-006 | Devices LOW requieren mantenimiento anual |
| DR-007 | Calibración es independiente del mantenimiento |
| DR-008 | Device con Engineering Incident ACTIVE no puede decommissionarse |

---

# PARTE 3: KNOWLEDGE

---

## 3.1 ¿Qué es Knowledge?

```
Knowledge es la base de conocimiento técnico searchable 
que permite a la IA responder con evidencia.
```

**Knowledge NO es solo manuales.**

---

## 3.2 Componentes del Knowledge

```
Knowledge
│
├── Manuales Técnicos
│   ├── Manuales de usuario
│   ├── Manuales de servicio
│   ├── Diagramas
│   └── Guías de troubleshooting
│
├── Normas y Regulaciones
│   ├── Normas IEC (seguridad eléctrica)
│   ├── Normas ISO (gestión de calidad)
│   ├── Regulaciones FDA
│   └── Guías de práctica clínica
│
├── Boletines del Fabricante
│   ├── Safety Alerts
│   ├── Field Safety Notices
│   ├── Product Updates
│   └── Recall notices
│
├── Recall FDA
│   ├── Device recalls
│   ├── Safety communications
│   └── Enforcement reports
│
├── Alarmas Conocidas
│   ├── Códigos de alarma
│   ├── Significado
│   └── Acciones recomendadas
│
├── Casos Históricos (propios)
│   ├── Engineering Incidents similares
│   ├── Soluciones aplicadas
│   ├── Resultados
│   └── Lecciones aprendidas
│
├── Mejores Prácticas
│   ├── Procedimientos estándar
│   ├── Tips de mantenimiento
│   └── Recomendaciones de fabricante
│
└── Lecciones Aprendidas
    ├── Qué funcionó
    ├── Qué no funcionó
    └── Qué haríamos diferente
```

---

## 3.3 Lo que hace posible

```
Con esta Knowledge Base, EREN puede responder:

"Ya encontré 13 Engineering Incidents similares.
 8 fueron por obstrucción en circuito (62%).
 3 por falla de sensor de presión (23%).
 2 por presión máxima mal configurada (15%).
 Probabilidad de resolver con solución X: 86%."
```

---

## 3.4 Responsabilidades

```
Knowledge ES:
├── Almacenar información técnica estructurada
├── Mantener searchable metadata
├── Vincular información a Devices
├── Actualizar con casos reales
└── Aprender de Engineering Incidents cerrados

Knowledge NO ES:
├── Un repositorio de PDFs sin indexar
├── Un sistema de gestión documental
├── Un wiki genérico
└── Un sistema de entrenamiento de IA
```

---

## 3.5 Eventos del Dominio

| Evento | Descripción |
|--------|-------------|
| KnowledgeAdded | Nueva información agregada |
| KnowledgeIndexed | Información indexada para búsqueda |
| KnowledgeLinked | Vinculada a Device o Incident |
| KnowledgeUpdated | Información actualizada |
| KnowledgeLearned | Lecciones extraídas de caso cerrado |

---

# PARTE 4: MAINTENANCE

---

## 4.1 ¿Qué es Maintenance?

```
Maintenance rastrea el historial técnico de intervenciones,
calibraciones y mantenimientos preventivos de los Devices.
```

---

## 4.2 Responsabilidades

```
Maintenance ES:
├── Registrar intervenciones técnicas
├── Rastrear calibraciones
├── Documentar mantenimientos preventivos
├── Mantener historial de repuestos usados
└── Proporcionar contexto para nuevos Engineering Incidents

Maintenance NO ES:
├── Un sistema de órdenes de compra
├── Un módulo de inventory de repuestos
├── Un sistema de contratos de servicio
└── Un sistema de scheduling de citas
```

---

## 4.3 Información de Maintenance

```
Maintenance Record:
├── Device reference
├── Tipo (Preventivo, Correctivo, Calibración)
├── Fecha realizada
├── Ingeniero responsable
├── Actividades realizadas
├── Repuestos utilizados
├── Tiempo invertido
├── Resultado
├── Próxima fecha de mantenimiento
└── Notas
```

---

## 4.4 Eventos del Dominio

| Evento | Descripción |
|--------|-------------|
| MaintenanceScheduled | Mantenimiento programado |
| MaintenancePerformed | Mantenimiento realizado |
| CalibrationPerformed | Calibración realizada |
| PartReplaced | Repuesto reemplazado |
| MaintenanceOverdue | Mantenimiento vencido |

---

# PARTE 5: AI LAYER (Capa, no Dominio)

---

## 5.1 ¿Qué es AI Layer?

```
AI Layer NO es un bounded context.

AI Layer ES una capa que:
├── Comprende la intención del usuario
├── Consulta los dominios
├── Razonamiento
└── Entrega recomendaciones

La IA no posee datos.
La IA no posee reglas del negocio.
La IA consume reglas.
La IA orquesta.
```

---

## 5.2 Responsabilidades de AI Layer

```
AI Layer ES:
├── Interfaz conversacional
├── Comprensión de lenguaje natural
├── Consulta a dominios (Device, Incident, Knowledge, Maintenance)
├── Razonamiento basado en evidencia
├── Generación de recomendaciones
└── Aprendizaje de casos cerrados

AI Layer NO ES:
├── Un dominio con estado propio
├── Un repositorio de datos
├── Un sistema de reglas de negocio
└── Una base de conocimiento
```

---

## 5.3 Flujo de AI Layer

```
1. Usuario reporta problema
   └─► AI Layer recibe input

2. AI Layer consulta Device
   └─► ¿Qué equipo es? ¿Specs? ¿Ubicación?

3. AI Layer consulta Knowledge
   └─► ¿Manuales? ¿Casos similares? ¿Normas?

4. AI Layer consulta Maintenance
   └─► ¿Historial? ¿Último mantenimiento? ¿Repuestos?

5. AI Layer consulta Engineering Incident
   └─► ¿Hay incidentes similares abiertos?

6. AI Layer razona
   └─► Genera probabilidades, sugiere pruebas, estima resolución

7. AI Layer responde
   └─► Recomendación al ingeniero
```

---

## 5.4 Preguntas que AI Layer responde

| Pregunta | Fuentes |
|----------|---------|
| ¿Qué equipo está afectado? | Device |
| ¿Cuáles son las specs? | Device |
| ¿Dónde está ubicado? | Device |
| ¿Qué pasó antes? | Incident + Maintenance |
| ¿Hay casos similares? | Knowledge + Incident |
| ¿Qué manuales aplican? | Knowledge |
| ¿Qué mantenimiento tiene pendiente? | Maintenance |
| ¿Qué repuestos se usaron antes? | Maintenance + Knowledge |
| ¿Cuál es la probabilidad de resolver? | AI Layer (razonamiento) |

---

# PARTE 6: RELACIONES

---

## 6.1 Mapa de Contexto

```
┌─────────────────────────────────────────────────────────────┐
│                        AI Layer                              │
│                         (capa)                              │
│                           │                                 │
│                           ▼                                 │
│              ┌───────────────────────┐                     │
│              │ Engineering Incident   │                     │
│              │         ♥             │                     │
│              └───────────┬───────────┘                     │
│                          │                                  │
│        ┌─────────────────┼─────────────────┐              │
│        │                 │                 │              │
│        ▼                 ▼                 ▼              │
│  ┌───────────┐    ┌───────────┐    ┌───────────────┐     │
│  │  Device   │    │ Knowledge  │    │  Maintenance  │     │
│  │           │    │           │    │               │     │
│  │• Info     │    │• Manuales │    │• Historial    │     │
│  │• Status   │    │• Normas   │    │• Calibrac.    │     │
│  │• History  │    │• Casos    │    │• Intervenc.   │     │
│  └───────────┘    └───────────┘    └───────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 6.2 Integración con Clinical (Futuro)

```
┌─────────────────────────────────────────────────────────────┐
│                      EREN                                   │
│                      AI Layer                               │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │              │
│  ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐     │
│  │ Engineering │   │  Clinical   │   │  Future     │     │
│  │  Core       │   │   Core      │   │             │     │
│  │             │   │             │   │             │     │
│  │• Device     │   │• Patient    │   │• Finance    │     │
│  │• Incident ♥ │   │• Diagnosis │   │• Inventory  │     │
│  │• Knowledge  │   │• Treatment │   │• Protocols  │     │
│  │• Maint.     │   │• Observe   │   │             │     │
│  └─────────────┘   └─────────────┘   └─────────────┘     │
└─────────────────────────────────────────────────────────────┘

Preguntas futuras que AI Layer podrá responder:
├── ¿Este ventilador está asignado a algún paciente?
├── ¿Qué diagnóstico tiene el paciente conectado?
├── ¿Existe una orden médica que impida apagar el equipo?
└── ¿Qué medicamentos está recibiendo?
```

---

# PARTE 7: VALIDACIÓN

---

## 7.1 Métricas de Éxito del MVP

| Métrica | Meta |
|---------|------|
| Tiempo en reportar un problema | < 2 min |
| Tiempo en proponer causas probables | < 30 seg |
| Incidentes resueltos en primer contacto | > 60% |
| Tiempo en generar reporte técnico | < 1 min |
| Probabilidad de resolución predicha | > 80% accuracy |
| Satisfacción del ingeniero biomédico | > 90% |

---

## 7.2 Lo que NO pertenece al MVP

| Descartado | Razón |
|------------|-------|
| Órdenes de compra | No ayuda a resolver el problema |
| Inventory de repuestos | Puede agregarse después |
| Contratos de servicio | No es el foco del MVP |
| Historial financiero | No es relevante para el ingeniero |

---

## 7.3 Lo que SÍ pertenece al MVP

| Incluido | Razón |
|----------|-------|
| Registro de Device | Sin esto no hay contexto |
| Engineering Incident | Es el corazón del sistema |
| Conversación con AI Layer | Es el diferenciador |
| Knowledge Base | Reduce tiempo de resolución |
| Maintenance History | Proporciona contexto |
| Generación de reportes | Cierra el ciclo |

---

## 7.4 Orden de Implementación

```
Paso 1: Device Management
├── Events
├── Repository
├── Service
├── Model
├── Router
└── Tests

Paso 2: Engineering Incident
├── Events
├── Repository
├── Service
├── Model
├── Router
└── Tests

Paso 3: Knowledge Base
├── Estructura de datos
├── Indexación
├── Búsqueda
└── Vincular con Device

Paso 4: Maintenance
├── Events
├── Repository
├── Service
├── Model
└── Tests

Paso 5: AI Layer
├── Interfaz conversacional
├── Consulta a dominios
├── Razonamiento
└── Recomendaciones
```

---

## 7.5 Preguntas Pendientes

```
1. ¿Cómo se identifica automáticamente el dispositivo?
   (QR, RFID, búsqueda manual)

2. ¿Qué nivel de integración con sistemas externos en MVP?
   (Epic, Cerner, HL7, FHIR)

3. ¿Cómo se entrena el modelo de IA?
   (Histórico de Engineering Incidents, Knowledge Base)

4. ¿Qué formato tienen los manuales técnicos?
   (PDF, texto, structured data)

5. ¿Cómo se valida la calidad de las sugerencias de IA?
   (Review humano, métricas, A/B testing)
```

---

**Estado:** Listo para revisión
**Pendiente:** Validación con stakeholders

---

**Firmado:** OpenHands Agent
**Fecha:** 2026-07-15
