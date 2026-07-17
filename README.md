# EREN - Cognitive Operating System for Clinical Engineering

> **Sistema Operativo Cognitivo especializado en Ingeniería Clínica**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)

---

## ¿Qué es EREN?

EREN es un **Cognitive Operating System (COS)** especializado en Ingeniería Clínica. No es una aplicación, no es un chatbot, no es un asistente. Es un sistema operativo cognitivo que orquesta procesos de pensamiento, gestiona conocimiento institucional, y amplifica la capacidad humana.

**Para la máxima autoridad del proyecto, ver [VISION.md](./VISION.md).**

> **Estado actual:** EPIC-2 (Core Business Domain) ✅ MERGED.
> Épica 0: Documentación ✅ · Épica 1: Infraestructura ✅ · Épica 2: Core Domain ✅ MERGED
> Documentos canónicos:
> [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) ·
> [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) ·
> [CORE_SPECIFICATION.md](./CORE_SPECIFICATION.md) ·
> [MASTER_ROADMAP.md](./MASTER_ROADMAP.md).

---

## Quick Start

### Prerequisites

- Docker y Docker Compose
- Python 3.12+ (solo para desarrollo local)
- Supabase project (para auth, opcional para desarrollo)

### Setup — Producción (Docker Compose)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Tiago1203/EREN.git
cd EREN

# 2. Configurar variables de entorno
cp apps/api/.env.example apps/api/.env
# Editar apps/api/.env con tus credenciales de Supabase

# 3. Levantar con Docker Compose
docker-compose up -d

# 4. Verificar que está corriendo
curl http://localhost:8000/api/v1/health
```

### Setup — Desarrollo Local (sin Docker)

```bash
cd apps/api

# Instalar dependencias
pip install -e ".[test]"

# Correr tests
pytest tests/ -v

# Correr con hot-reload
uvicorn app.main:app --reload --port 8000
```

### Stack de Servicios

```
docker-compose up -d
```
Levanta todos los servicios:
- **API**: http://localhost:8000 (FastAPI + Uvicorn)
- **RabbitMQ**: http://localhost:15672 (Management UI, user: eren / pass: eren)
- **Jaeger**: http://localhost:16686 (Distributed tracing)
- **Grafana**: http://localhost:3001 (Metrics dashboard, admin / admin)
- **Prometheus**: http://localhost:9091 (Metrics)
- **PostgreSQL**: localhost:5432 (user: eren / pass: eren / db: eren)
- **Redis**: localhost:6379

### CI/CD

El proyecto usa GitHub Actions. Verifica el estado en la pestaña "Actions" del repositorio.

**Checks:**
- ✅ Lint (Ruff + Black)
- ✅ Typecheck (mypy)
- ✅ Test Suite (108 tests + integration)
- ✅ Docker Build
- ✅ Architecture Validation

---

## Estado de Implementación

### ✅ Épica 0 — Documentación y Planificación

| Componente | Estado |
|------------|--------|
| VISION.md | ✅ |
| ARCHITECTURE_OVERVIEW.md | ✅ |
| SYSTEM_DESIGN.md | ✅ |
| CORE_SPECIFICATION.md | ✅ |
| MASTER_ROADMAP.md | ✅ |
| Tech Bible | ✅ |

### ✅ Infraestructura (Épica 1)

| Componente | Estado | Notas |
|------------|--------|-------|
| Docker & Docker Compose | ✅ | API + Worker + Postgres + Redis + RabbitMQ |
| PostgreSQL + Alembic | ✅ | Multi-schema, async |
| SQLAlchemy Models | ✅ | Patient, Diagnosis, Device, Incident, Recommendation, Knowledge |
| Repository Implementations | ✅ | SQLAlchemy async |
| Unit of Work | ✅ | Async session management |
| Redis Cache | ✅ | CacheService con TTL |
| RabbitMQ Event Bus | ✅ | Transactional Outbox |
| Pydantic Settings | ✅ | Vault-ready |
| Structured Logging | ✅ | JSON + correlation IDs |
| OpenTelemetry | ✅ | Tracing + instrumentation |
| Health Checks | ✅ | /health, /health/live, /health/ready, /health/full |
| CI/CD (GitHub Actions) | ✅ | Lint + Typecheck + Tests + Docker Build |
| Pre-commit Hooks | ✅ | Ruff + Black + isort + MyPy + Bandit |

### ✅ Bounded Contexts (Épica 2)

| Context | Estado | Tests |
|---------|--------|-------|
| Shared Kernel | ✅ | Done |
| Patient Context | ✅ | Moved to EPIC 5 scope |
| Device Context | ✅ | Done |
| Incident Context | ✅ | Done |
| Recommendation Context | ✅ | Done |
| Knowledge Context | ✅ | Done |
| WorkOrder Sub-Aggregate | ✅ | Done (PR #128) |

**Total: 228+ tests passing (unit + integration)**

### 🎯 Próximo (Épica 3)

- **Épica 3: Hospital Management Platform** — Próximo
- Épica 4: AI Core
- Épica 5: Clinical Intelligence
- Épica 6: Integrations
- Épica 7: User Experience
- Épica 8: Production Readiness
- Épica 9: Machine Learning
- Épica 10: Enterprise Release

**Ver estado completo en:** [`docs/epic0/README.md`](./docs/epic0/README.md) · [`docs/adr/README.md`](./docs/adr/README.md)

---

## Device API — Referencia Rápida

Base URL: `http://localhost:8000/api/v1`

Todos los endpoints requieren header `X-Tenant-ID`. La autenticación se configura via middleware.

### Registro de dispositivo

```bash
POST /devices
{
  "serial_number": "SN-MRI-001",
  "name": "MRI Scanner",
  "device_type": "imaging",
  "manufacturer_name": "Siemens",
  "manufacturer_model": "MAGNETOM Vida",
  "building": "Main Hospital",
  "floor": "2",
  "room": "201",
  "department": "Radiology",
  "is_critical": true,
  "calibration_interval_days": 365
}
```

### CRUD

```bash
GET    /devices                    # Lista con filtros y paginación
GET    /devices/{id}               # Detalle por ID
PATCH  /devices/{id}               # Actualizar (optimistic locking: version)
DELETE /devices/{id}               # Eliminar
```

### Lifecycle

```bash
POST /devices/{id}/transfer        # Transferir a nueva ubicación
POST /devices/{id}/maintenance      # Programar mantenimiento
POST /devices/{id}/maintenance/start   # Iniciar mantenimiento
POST /devices/{id}/maintenance/finish # Finalizar mantenimiento
POST /devices/{id}/calibrate       # Registrar calibración
POST /devices/{id}/out-of-service # Sacar de servicio
POST /devices/{id}/return-service  # Reactivar
POST /devices/{id}/decommission   # Dar de baja permanente
```

### Filtros de listado

```
?status=active|in_maintenance|decommissioned|...
&device_type=imaging|diagnostic|therapeutic|...
&building=Main+Hospital
&department=Radiology
&is_critical=true
&search=palabra
&sort_by=created_at&sort_order=desc
&page=1&page_size=50
```

### Domain Events

Los eventos se publican via **Outbox Pattern** (consistencia eventual):

| Evento | Trigger |
|--------|---------|
| `DeviceRegistered` | Registro |
| `DeviceUpdated` | Actualización |
| `DeviceTransferred` | Transferencia |
| `MaintenanceScheduled` | Programación |
| `MaintenanceStarted` | Inicio de mantenimiento |
| `MaintenanceCompleted` | Finalización |
| `CalibrationCompleted` | Calibración |
| `DeviceOutOfService` | Fuera de servicio |
| `DeviceReturnedToService` | Reactivación |
| `DeviceDecommissioned` | Baja |

### Validaciones de negocio

- No registrar serial duplicado (por tenant)
- No operar equipo desincorporado
- No iniciar mantenimiento ya en mantenimiento
- No activar equipo sin calibración válida
- Reactivación requiere calibración vigente

---

## Visión

EREN será la infraestructura cognitiva estándar sobre la cual opera la ingeniería clínica mundial, permitiendo que cada hospital opere con la inteligencia colectiva de toda la red.

## Misión

Capturar, preservar y amplificar el conocimiento técnico de ingeniería clínica para mejorar la seguridad del paciente y la eficiencia hospitalaria.

---

## Objetivos

### Objetivos Principales

1. **Capturar Conocimiento Tácito**: Convertir experiencia individual en inteligencia institucional estructurada
2. **Orquestar Procesos Cognitivos**: Gestionar motores de razonamiento, memoria y aprendizaje
3. **Amplificar Capacidad Humana**: Permitir que cada ingeniero opere al nivel de la experiencia colectiva
4. **Mejorar Seguridad del Paciente**: Reducir errores técnicos que afectan pacientes
5. **Evolucionar Continuamente**: Aprender de cada interacción, caso, e integración

### Objetivos Técnicos

1. **Arquitectura para 15 Años**: Sistema diseñado para escalar a 10,000+ hospitales
2. **Motores Cognitivos Especializados**: Orchestrator, Planner, Reasoning, Memory, Knowledge, Diagnostic, Workflow, Tools
3. **IA Responsable**: Explicabilidad obligatoria, auditoría completa, control humano
4. **Seguridad por Diseño**: Compliance con HIPAA/GDPR, encryption, RLS
5. **Multi-Interfaz**: Conversacional, visual, programática, móvil

## Problema que Resuelve

### Problema Actual

- **Pérdida de Conocimiento**: Cuando ingenieros experimentados se retiran, su conocimiento se pierde irreversiblemente
- **Diagnóstico Ineficiente**: Falta de acceso rápido a información técnica relevante y contextualizada
- **Curva de Aprendizaje**: Nuevos ingenieros tardan años en alcanzar competencia operativa
- **Conocimiento Fragmentado**: Manuales, protocolos y experiencias dispersos en sistemas no integrados
- **Reinventar la Rueda**: Mismos problemas resueltos múltiples veces sin compartir soluciones
- **Falta de Trazabilidad**: Difícil auditar decisiones técnicas y aprender de errores sistémicos
- **Decisiones sin Contexto**: Falta de acceso a historia, patrones y casos similares

### Solución EREN

- **Sistema Operativo Cognitivo**: Orquesta motores de razonamiento, memoria y aprendizaje
- **Memoria Institucional Estructurada**: Captura, indexa y preserva conocimiento técnico
- **Razonamiento Explicable**: Sistema multi-motor que analiza problemas con trazabilidad completa
- **Aprendizaje Continuo**: Cada interacción mejora el sistema de forma estructurada
- **Conocimiento Unificado**: Repositorio centralizado, indexado y accesible
- **Inteligencia Distribuida**: Opcionalmente compartir conocimiento anonimizado entre hospitales
- **Trazabilidad Total**: Auditoría completa de decisiones cognitivas y acciones

---

## Arquitectura de EREN

### Tres Capas Fundamentales

**Capa 1: EREN CORE (Cognitive Operating System)** — ocho motores canónicos sobre `core/contracts`:
- Orchestrator Engine: Coordina los motores y el ciclo de vida cognitivo
- Planner Engine: Descompone objetivos en planes ordenados
- Reasoning Engine: Razonamiento explicable sobre evidencia
- Memory Engine: Memoria a corto y largo plazo
- Knowledge Engine: Gestión y recuperación de conocimiento institucional
- Diagnostic Engine: Análisis de fallas de equipos clínicos
- Workflow Engine: Procesos operativos duraderos multi-paso
- Tool Engine: Registro/adaptadores de capacidades externas

> Aprendizaje (Learning), permisos (Permission) y auditoría (Audit) se tratan como
> capacidades transversales/futuras. Detalle en [CORE_SPECIFICATION.md](./CORE_SPECIFICATION.md).

**Capa 2: Dominios de Negocio**
- Equipment Domain: Gestión de equipos médicos
- Maintenance Domain: Procesos de mantenimiento
- Case Domain: Casos de resolución
- Knowledge Domain: Conocimiento técnico
- User Domain: Gestión de usuarios y permisos
- Hospital Domain: Configuración multi-hospital

**Capa 3: Interfaces de Usuario**
- Conversational Interface: Chat natural
- Visual Interface: Dashboards y visualizaciones
- Mobile Interface: Apps móviles
- Programmatic Interface: API y SDK
- Integration Interface: Conexión con sistemas externos

## Estructura del Repositorio (Monorepo)

EREN está organizado como un **monorepo** para escalar durante años sin
reescrituras. Cada capa tiene un lugar explícito:

```
eren/
├── apps/                # Aplicaciones desplegables (superficies de entrega)
│   ├── web/             # Interfaz web (Next.js) — migrada desde la raíz
│   ├── api/             # API HTTP (FastAPI) — scaffolding
│   └── desktop/         # Cliente de escritorio — placeholder
│
├── core/                # Núcleo cognitivo (motores, agnóstico de interfaz)
│   ├── orchestrator/    # Coordina los motores y el ciclo de vida cognitivo
│   ├── planner/         # Descompone objetivos en pasos ejecutables
│   ├── reasoning/       # Estrategias de razonamiento explicable
│   ├── memory/          # Memoria institucional (corto/largo plazo)
│   ├── diagnostic/      # Diagnóstico de ingeniería clínica
│   ├── workflow/        # Procesos operativos multi-paso
│   ├── knowledge/       # Conocimiento institucional estructurado
│   └── tools/           # Registro/adaptadores de capacidades
│
├── packages/            # Librerías compartidas (@eren/*)
│   ├── shared/          # Utilidades, tipos y constantes transversales
│   ├── sdk/             # SDK cliente tipado
│   ├── prompts/         # Librería de prompts versionada
│   └── schemas/         # Contratos de datos y validación
│
├── infrastructure/      # IaC, CI/CD, base de datos y operación
│   └── database/        # Scripts SQL y de diagnóstico (antes en scripts/)
│
├── docs/                # Documentación (preservada)
│
└── tests/               # Pruebas que cruzan varios workspaces (e2e, integración)
```

> **Nota:** `core/`, `packages/`, `apps/api` y `apps/desktop` son *scaffolding*
> de arquitectura. No contienen lógica de negocio, IA ni agentes todavía.
>
> Cada carpeta incluye un `README.md` que describe su propósito y sus límites de
> dependencia.

### Desarrollo (npm workspaces)

El repositorio usa **npm workspaces**. Desde la raíz:

```bash
npm install     # instala todos los workspaces
npm run dev     # levanta la app web (@eren/web)
npm run build   # construye la app web
npm run lint    # lint de la app web
```

## Público Objetivo

### Primario

- **Ingenieros Biomédicos**: Usuarios principales que diagnostican y reparan equipos
- **Técnicos de Mantenimiento**: Personal técnico que ejecuta reparaciones
- **Gerentes de Ingeniería**: Responsables de gestión de equipos y personal

### Secundario

- **Directores Hospitalarios**: Toman decisiones basadas en datos de mantenimiento
- **Personal de Compras**: Necesitan información para decisiones de adquisición
- **Reguladores**: Requieren trazabilidad y cumplimiento normativo

### Terciario (Futuro)

- **Personal Clínico**: Médicos y enfermeras que reportan fallas
- **Investigadores**: Acceso a datos para investigación biomédica
- **Estudiantes**: Formación en ingeniería clínica

## Estado actual vs. Roadmap

> **Importante:** lo listado en el *roadmap* abajo describe funcionalidad
> **planificada**, no implementada. Hoy el repositorio contiene únicamente
> *scaffolding* de arquitectura. Ver [MASTER_ROADMAP.md](./MASTER_ROADMAP.md).

### Implementado hoy (scaffolding)

- **Monorepo** (`apps/`, `core/`, `packages/`, `infrastructure/`, `docs/`, `tests/`) con npm workspaces y README por carpeta.
- **apps/web**: app Next.js existente reubicada en `apps/web` (`@eren/web`), comportamiento preservado.
- **apps/api**: esqueleto FastAPI de arquitectura limpia; único endpoint `GET /api/v1/health`.
- **core/**: ocho motores como clases vacías documentadas.
- **core/contracts/**: interfaces SOLID (`CognitiveEngine`, `Tool`, `Planner`, `Memory`, `Knowledge`, `Workflow`, `Diagnostic`, `Reasoning`).

### Planificado — v0.1.0 (MVP)

- Autenticación multi-hospital (Supabase Auth)
- Inventario de equipos y órdenes de mantenimiento
- Case Base y búsqueda vectorial de conocimiento técnico
- Punto de entrada conversacional a través de `core/orchestrator`
- Cuatro bases de conocimiento (KB, CB, MB, DB)

### Planificado — versiones posteriores

- Learning (ML), permisos granulares y auditoría avanzada
- Multi-hospital colaborativo; integraciones HL7/DICOM/FHIR; móvil nativo

> Desglose completo por versión en [docs/roadmap/complete-roadmap.md](./docs/roadmap/complete-roadmap.md).

## Tecnologías

### Frontend (`apps/web`)
- **Next.js 16** (App Router, React 19)
- **TypeScript 5**: Type safety
- **Tailwind CSS 4** (vía `@tailwindcss/postcss`): estilos utility-first
- **Supabase** (`@supabase/ssr`, `@supabase/supabase-js`): auth/sesión

### Backend (`apps/api`)
- **Python 3.12**: Lenguaje principal
- **FastAPI**: Framework web asíncrono
- **uv**: Gestión de paquetes y entornos Python
- **Pydantic v2**: Validación de datos
- **SQLAlchemy 2 (async) + Alembic**: ORM y migraciones
- **Ruff** y **Pytest**: lint/formato y tests

> **Nota:** frameworks de IA/agentes (p. ej. LangChain/LangGraph) son dirección
> objetivo, aún **no** integrados.

### Base de Datos
- **Supabase**: PostgreSQL como servicio
  - Autenticación
  - Base de datos relacional
  - Storage (archivos)
  - Realtime (WebSockets)

### Vector Database (planificado)
- **Qdrant**: Base de datos vectorial (búsqueda semántica, similitud, escala horizontal)

### IA/ML (planificado)
- **OpenAI GPT-4** / modelos de lenguaje
- **LangGraph**: Orquestación de agentes
- **Embeddings**: OpenAI text-embedding-3

### Infraestructura (parcial / planificado)
- **GitHub**: Control de versiones (en uso)
- **Docker** / **Docker Compose**: contenedores y orquestación local (planificado)
- **GitHub Actions**: CI/CD (planificado)

### Desarrollo
- **uv**: Gestión de entornos Python
- **npm workspaces**: Gestión de paquetes Node.js (monorepo)
- **VS Code/Cursor/Devin**: Editores de código

## Filosofía del Proyecto

EREN se rige por los principios establecidos en [VISION.md](./VISION.md) y [EREN_MANIFESTO.md](./EREN_MANIFESTO.md):

1. **Amplificación, no Reemplazo**: EREN amplifica la capacidad humana, no la reemplaza
2. **Explicabilidad Obligatoria**: Toda decisión cognitiva debe ser explicable
3. **Conocimiento Estructurado**: El conocimiento tácito se convierte en explícito y estructurado
4. **Comprensión Antes de Respuesta**: Precisión sobre velocidad
5. **Confianza Basada en Evidencia**: Citas, razonamiento, admisión de incertidumbre
6. **Contexto Clínico Prioritario**: La seguridad del paciente es el norte
7. **Aprendizaje Continuo**: Cada interacción es una oportunidad de aprendizaje
8. **Seguridad por Diseño**: Seguridad como fundamento, no parche
9. **Interoperabilidad Profunda**: Integración es esencial, no opcional
10. **Arquitectura para 15 Años**: Pensamos en décadas, no en quarters

## Roadmap Resumido

> Hoja de ruta **planificada**. El detalle reconciliado con el estado actual está
> en [MASTER_ROADMAP.md](./MASTER_ROADMAP.md).

### v0.1.0 - MVP (Q3 2026)
- Primeros motores operativos: orchestrator, knowledge, memory, reasoning, tools
- Interfaz conversacional como punto de entrada
- 4 bases de conocimiento (KB, CB, MB, DB)
- 2 hospitales piloto

### v0.2.0 - Core (Q4 2026)
- Planner Engine y Workflow Engine operativos
- Permisos granulares (transversal)
- Mejoras en UI/UX
- Tests completos

### v0.3.0 - Advanced (Q1 2027)
- Diagnostic Engine operativo
- Multi-hospital colaborativo (opcional)
- Móvil web
- Integración básica HL7

### v1.0.0 - Production (Q2 2027)
- Estabilidad completa (99.9% uptime)
- Documentación exhaustiva
- Soporte enterprise
- CI/CD completo

### v2.0.0 - Scale (Q4 2027)
- Escalabilidad horizontal (Kubernetes)
- Análisis avanzado
- App nativa móvil
- 500 hospitales globales

### v3.0.0 - Intelligence (Q2 2028)
- 10+ motores cognitivos
- Predicción de fallas
- Optimización de inventario
- 2,000+ hospitales

### v4.0.0 - Ecosystem (Q4 2028)
- API pública y SDK
- Marketplace de aplicaciones
- Integración profunda EMR/EHR
- Research platform

### v5.0.0 - Vision (Q2 2029)
- Infraestructura cognitiva estándar
- Red global de conocimiento
- IA generativa de conocimiento
- 10,000+ hospitales

## Documentación

**Documentos Fundamentales**
- [VISION.md](./VISION.md) - Máxima autoridad del proyecto: definición de EREN como COS
- [EREN_MANIFESTO.md](./EREN_MANIFESTO.md) - Filosofía y principios del proyecto
- [TECH_BIBLE.md](./TECH_BIBLE.md) - Constitución técnica del proyecto
- [PROJECT_BOOTSTRAP.md](./PROJECT_BOOTSTRAP.md) - Guía profesional de instalación

**Documentos Canónicos de Arquitectura**
- [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) - Mapa de alto nivel de la arquitectura actual
- [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) - Diseño a nivel de componentes y runtime
- [CORE_SPECIFICATION.md](./CORE_SPECIFICATION.md) - Especificación del núcleo cognitivo (`core/`)
- [MASTER_ROADMAP.md](./MASTER_ROADMAP.md) - Hoja de ruta reconciliada con el estado actual

**Arquitectura (detalle)**
- [docs/adr/](./docs/adr/) - Architecture Decision Records (índice por categorías)
- [docs/architecture/](./docs/architecture/) - Documentación de arquitectura
- [core/contracts/](./core/contracts/) - Capa de contratos SOLID de los motores
- [docs/core/](./docs/core/) - EREN CORE: diseño de motores cognitivos
- [docs/domain/](./docs/domain/) - Dominios de negocio (DDD)
- [docs/knowledge/](./docs/knowledge/) - Arquitectura del conocimiento

**Gobernanza Arquitectónica**
- [docs/architecture/ARCHITECTURE_HARDENING_REPORT.md](./docs/architecture/ARCHITECTURE_HARDENING_REPORT.md) - Reporte de hardening
- [docs/architecture/ARCHITECTURE_CONSISTENCY_REPORT.md](./docs/architecture/ARCHITECTURE_CONSISTENCY_REPORT.md) - Reporte de consistencia
- [docs/architecture/DEAD_CODE_REPORT.md](./docs/architecture/DEAD_CODE_REPORT.md) - Análisis de código muerto
- [docs/architecture/CONTRACT_COVERAGE_REPORT.md](./docs/architecture/CONTRACT_COVERAGE_REPORT.md) - Cobertura de contratos
- [docs/architecture/DEPENDENCY_HEALTH_REPORT.md](./docs/architecture/DEPENDENCY_HEALTH_REPORT.md) - Salud de dependencias
- [docs/architecture/MODULE_MAP.md](./docs/architecture/MODULE_MAP.md) - Mapa de módulos
- [docs/architecture/SYSTEM_OVERVIEW.md](./docs/architecture/SYSTEM_OVERVIEW.md) - Vista general del sistema
- [docs/architecture/CODING_CONVENTIONS.md](./docs/architecture/CODING_CONVENTIONS.md) - Convenciones de código
- [docs/architecture/NAMING_CONVENTIONS.md](./docs/architecture/NAMING_CONVENTIONS.md) - Convenciones de nombres
- [docs/architecture/MODULE_CREATION_GUIDE.md](./docs/architecture/MODULE_CREATION_GUIDE.md) - Guía para crear módulos
- [docs/architecture/DEPENDENCY_RULES.md](./docs/architecture/DEPENDENCY_RULES.md) - Reglas de dependencias
- [docs/architecture/ADR_GUIDELINES.md](./docs/architecture/ADR_GUIDELINES.md) - Directrices para ADRs

**Políticas**
- [docs/ai/responsible-ai-policy.md](./docs/ai/responsible-ai-policy.md) - Política de IA Responsable

## Contribución

Este proyecto sigue una metodología de desarrollo rigurosa. Antes de contribuir:

1. Leer [TECH_BIBLE.md](./TECH_BIBLE.md)
2. Revisar [docs/adr/](./docs/adr/) para decisiones arquitectónicas
3. Seguir convenciones de commits y código
4. Escribir tests para nuevas funcionalidades
5. Documentar cambios relevantes

## Licencia

MIT License - Ver [LICENSE](./LICENSE) para detalles

## Contacto

- **Lead Architect**: Cascade (Claude Code)
- **Product Owner**: [Usuario]
- **Repository**: [GitHub URL]

---

**EREN - Cognitive Operating System para Ingeniería Clínica**
