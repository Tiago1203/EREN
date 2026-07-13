# EREN - Cognitive Operating System for Clinical Engineering

> **Sistema Operativo Cognitivo especializado en Ingeniería Clínica**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)

---

## ¿Qué es EREN?

EREN es un **Cognitive Operating System (COS)** especializado en Ingeniería Clínica. No es una aplicación, no es un chatbot, no es un asistente. Es un sistema operativo cognitivo que orquesta procesos de pensamiento, gestiona conocimiento institucional, y amplifica la capacidad humana.

**Para la máxima autoridad del proyecto, ver [VISION.md](./VISION.md).**

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
2. **Motores Cognitivos Especializados**: Reasoning, Knowledge, Memory, Learning, Planning
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

**Capa 1: EREN CORE (Cognitive Operating System)**
- Reasoning Engine: Razonamiento lógico y deductivo
- Knowledge Engine: Gestión y recuperación de conocimiento
- Memory Engine: Memoria a corto y largo plazo
- Learning Engine: Aprendizaje automático
- Planning Engine: Planificación de tareas complejas
- Tool Engine: Ejecución de herramientas externas
- Permission Engine: Control de permisos y autorización
- Audit Engine: Auditoría completa de acciones

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

## Alcance de v0.1.0 (MVP)

### Motores Cognitivos Fundamentales

**EREN CORE v0.1.0 incluye 5 motores cognitivos:**
1. **Reasoning Engine**: Razonamiento lógico básico
2. **Knowledge Engine**: Gestión y recuperación de conocimiento
3. **Memory Engine**: Memoria de conversaciones y contexto
4. **Tool Engine**: Ejecución de herramientas externas
5. **Permission Engine**: Control de permisos y autorización

### Funcionalidades Incluidas

#### Core
- Sistema de autenticación multi-hospital
- Gestión de inventario de equipos médicos
- Registro de órdenes de mantenimiento
- Sistema de casos resueltos
- Búsqueda vectorial de conocimiento técnico
- Interfaz conversacional (chat)

#### Bases de Conocimiento
- Knowledge Base: Manuales técnicos y documentación
- Case Base: Casos de mantenimiento resueltos
- Memory Base: Memoria de conversaciones y contexto
- Document Base: Protocolos y normativas

#### Infraestructura
- Backend FastAPI con arquitectura limpia
- Frontend Next.js con TypeScript
- Base de datos Supabase (PostgreSQL)
- Vector database Qdrant
- Docker para contenedores
- Logging estructurado
- Tests básicos

### Funcionalidades NO Incluidas (Futuro)

- Learning Engine (aprendizaje automático) - v2.0.0
- Planning Engine (planificación compleja) - v2.0.0
- Diagnostic Engine (diagnóstico avanzado) - v3.0.0
- Workflow Engine (workflows automatizados) - v2.0.0
- Audit Engine (auditoría avanzada) - v2.0.0
- Multi-hospital colaborativo - v3.0.0
- Integración con sistemas hospitalarios (HL7, DICOM) - v3.0.0
- Móvil (app nativa) - v2.0.0

## Tecnologías

### Frontend
- **Next.js 14**: Framework React con App Router
- **TypeScript 5.0**: Type safety
- **TailwindCSS**: Estilos utility-first
- **shadcn/ui**: Componentes UI modernos
- **Lucide React**: Iconos

### Backend
- **Python 3.11+**: Lenguaje principal
- **FastAPI**: Framework web asíncrono
- **uv**: Gestión de paquetes Python
- **Pydantic**: Validación de datos
- **LangChain**: Framework para agentes de IA

### Base de Datos
- **Supabase**: PostgreSQL como servicio
  - Autenticación
  - Base de datos relacional
  - Storage (archivos)
  - Realtime (WebSockets)

### Vector Database
- **Qdrant**: Base de datos vectorial
  - Búsqueda semántica
  - Similitud de documentos
  - Escalabilidad horizontal

### IA/ML
- **OpenAI GPT-4**: Modelos de lenguaje (inicial)
- **LangGraph**: Orquestación de agentes
- **Embeddings**: OpenAI text-embedding-3

### Infraestructura
- **Docker**: Contenedores
- **Docker Compose**: Orquestación local
- **GitHub**: Control de versiones
- **GitHub Actions**: CI/CD (futuro)

### Desarrollo
- **uv**: Gestión de entornos Python
- **pnpm**: Gestión de paquetes Node.js
- **WSL2**: Entorno de desarrollo en Windows
- **VS Code/Cursor/DevIn**: Editores de código

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

### v0.1.0 - MVP (Q3 2026)
- EREN CORE con 5 motores cognitivos fundamentales
- Interfaz conversacional como punto de entrada
- 4 bases de conocimiento (KB, CB, MB, DB)
- 50 hospitales piloto

### v0.2.0 - Core (Q4 2026)
- Learning Engine y Planning Engine
- Workflow Engine y Audit Engine
- Mejoras en UI/UX
- Tests completos

### v0.3.0 - Advanced (Q1 2027)
- Diagnostic Engine
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

**Arquitectura**
- [docs/adr/](./docs/adr/) - Architecture Decision Records (índice por categorías)
- [docs/core/](./docs/core/) - EREN CORE: diseño de motores cognitivos
- [docs/domain/](./docs/domain/) - Dominios de negocio (DDD)
- [docs/knowledge/](./docs/knowledge/) - Arquitectura del conocimiento

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
