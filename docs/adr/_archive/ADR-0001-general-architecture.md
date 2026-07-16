# ADR-0001: Arquitectura General de EREN

## Status
Accepted

> **Nota de numeración (2026-07-13):** existen dos archivos con el prefijo
> `ADR-0001` en este directorio (este, sobre arquitectura general, y
> `ADR-0001-cognitive-operating-system.md`). Se conservan ambos por historial; el
> índice ([README.md](./README.md)) documenta la duplicidad. Este ADR debe leerse
> como el **destino arquitectónico** aceptado.
>
> **Nota de consistencia (2026-07-13):** el repositorio implementa hoy la *base*
> de esta arquitectura como un **monorepo** (apps thin, `core/` con ocho motores
> + `core/contracts`, `packages/`, `infrastructure/`). Los elementos distribuidos
> (event bus, CQRS, microservicios, Qdrant, Redis, runtime multiagente) siguen
> siendo dirección objetivo, **no implementada aún**. Ver
> [ARCHITECTURE_OVERVIEW.md](../../ARCHITECTURE_OVERVIEW.md),
> [SYSTEM_DESIGN.md](../../SYSTEM_DESIGN.md) y
> [MASTER_ROADMAP.md](../../MASTER_ROADMAP.md).

## Contexto

EREN es una plataforma de Inteligencia Artificial para Ingeniería Clínica que debe:

1. **Escalar horizontalmente** para soportar múltiples hospitales con miles de usuarios
2. **Proveer IA responsable** con explicabilidad, trazabilidad y auditoría
3. **Manejar datos sensibles** de salud con seguridad robusta
4. **Soportar sistema multiagente** con orquestación compleja
5. **Preservar conocimiento institucional** a largo plazo
6. **Operar en entornos hospitalarios** con alta disponibilidad

El proyecto debe evolucionar durante 10+ años, desde un MVP hasta una plataforma clínica completa. La arquitectura debe soportar esta evolución sin reescrituras mayores.

## Problema

¿Qué arquitectura general debe adoptar EREN para cumplir con los requisitos de:

- Escalabilidad horizontal (10x crecimiento en usuarios y datos)
- Seguridad robusta (cumplimiento normativas de salud)
- IA responsable (explicabilidad, auditoría, trazabilidad)
- Multi-tenancy (aislamiento entre hospitales)
- Sistema multiagente (orquestación compleja)
- Observabilidad completa (toda acción trazable)
- Mantenibilidad a largo plazo (10+ años)

## Decisión

EREN adoptará una **Arquitectura Hexagonal con Vertical Slice Architecture**, combinando:

1. **Clean Architecture** - Separación de capas estricta
2. **Domain Driven Design (DDD)** - Dominio como centro del diseño
3. **Vertical Slice Architecture** - Organización por características
4. **Arquitectura Hexagonal** - Puertos y adaptadores
5. **CQRS** - Separación de lectura/escritura cuando aporte valor
6. **Event-Driven Architecture** - Comunicación asíncrona entre componentes
7. **Microservices-ready** - Monolito modular preparado para microservicios

### Estructura de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  (Next.js Frontend + FastAPI HTTP/WebSocket Interfaces)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (Use Cases, Commands, Queries, DTOs, Orchestrator)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  (Entities, Value Objects, Domain Services, Events)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  (Repositories, External Services, DB, Vector DB, Storage)  │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. Frontend (Next.js)
- **App Router** - Organización por rutas
- **Server Components** - Renderizado en servidor cuando posible
- **Client Components** - Interactividad cuando necesario
- **API Routes** - Endpoints server-side
- **Middleware** - Autenticación y autorización

#### 2. Backend (FastAPI)
- **Domain Layer** - Lógica de negocio pura
- **Application Layer** - Casos de uso
- **Infrastructure Layer** - Implementaciones concretas
- **Interfaces Layer** - HTTP/WebSocket endpoints
- **Agents Layer** - Sistema multiagente
- **Knowledge Layer** - Sistema de conocimiento

#### 3. Sistema Multiagente
- **Orchestrator** - Coordina agentes y decide cuál invocar
- **Specialist Agents** - Agentes especializados por dominio
- **Tool Registry** - Registro de herramientas disponibles
- **Permission System** - Permisos por agente y herramienta
- **Memory System** - Memoria de conversaciones y contexto

#### 4. Sistema de Conocimiento
- **Knowledge Base (KB)** - Manuales técnicos y documentación
- **Case Base (CB)** - Casos de mantenimiento resueltos
- **Memory Base (MB)** - Memoria de conversaciones
- **Learning Base (LB)** - Aprendizaje automático (futuro)
- **Document Base (DB)** - Protocolos y normativas

#### 5. Base de Datos
- **Supabase (PostgreSQL)** - Datos relacionales
- **Qdrant** - Base vectorial para búsqueda semántica
- **Redis** - Caching y colas (futuro)

#### 6. Infraestructura
- **Docker** - Contenedores para todos los servicios
- **Docker Compose** - Orquestación local
- **Observability Stack** - Logging, metrics, tracing

## Consecuencias

### Positivas

1. **Escalabilidad Horizontal**
   - Cada capa puede escalar independientemente
   - Preparado para microservicios si necesario
   - Stateless components facilitan scaling

2. **Mantenibilidad**
   - Separación de responsabilidades clara
   - Cambios localizados no afectan otras capas
   - Testing más fácil y aislado

3. **Testeabilidad**
   - Domain layer testeable sin dependencias
   - Mocking simple de infrastructure
   - Integration tests por vertical slice

4. **Flexibilidad**
   - Fácil cambiar implementaciones de infrastructure
   - Nuevos agentes sin modificar core
   - Nuevas bases de conocimiento sin afectar dominio

5. **Seguridad**
   - Auth/authorization en presentation layer
   - Domain rules inmutables
   - Infrastructure layer controla acceso a datos

6. **IA Responsable**
   - Orchestrator centraliza decisiones
   - Cada agente con permisos explícitos
   - Toda acción auditada en infrastructure

### Negativas

1. **Complejidad Inicial**
   - Más boilerplate que arquitectura simple
   - Curva de aprendizaje para equipo
   - Overhead en desarrollo inicial

2. **Overhead de Performance**
   - Múltiples capas pueden añadir latencia
   - Requiere optimización cuidadosa
   - Caching crítico para performance

3. **Decisiones Arquitecturales**
   - Requiere pensamiento cuidadoso en cada feature
   - Fácil sobre-ingeniería si no se disciplina
   - Necesita arquitecto experimentado

## Alternativas Consideradas

### 1. Monolito Tradicional (MVC)

**Descripción:** Arquitectura MVC simple con controllers, models, views.

**Pros:**
- Más simple de implementar
- Menos boilerplate
- Más rápido para MVP

**Contras:**
- Difícil escalar horizontalmente
- Acoplamiento alto entre componentes
- Difícil testear en aislamiento
- No preparado para evolución a largo plazo

**Decisión:** Rechazado. No cumple requisitos de escalabilidad y mantenibilidad a 10 años.

### 2. Microservicios desde el Inicio

**Descripción:** Cada componente como microservicio independiente.

**Pros:**
- Escalabilidad máxima
- Independencia de despliegue
- Tecnología por servicio

**Contras:**
- Complejidad operacional alta
- Overhead de comunicación
- Difícil para equipo pequeño
- Distributed transactions complejas

**Decisión:** Rechazado. Overkill para MVP. Monolito modular preparado para microservicios es mejor.

### 3. Serverless Architecture

**Descripción:** Funciones serverless en AWS Lambda o similares.

**Pros:**
- Sin gestión de infraestructura
- Auto-scaling
- Pay-per-use

**Contras:**
- Cold starts
- Vendor lock-in
- Difícil para long-running processes (agentes)
- Complejidad en estado local

**Decisión:** Rechazado. Agentes IA requieren procesos long-running. Serverless no apropiado.

### 4. Event Sourcing + CQRS Completo

**Descripción:** Todos los cambios como eventos, CQRS para todas las queries.

**Pros:**
- Audit trail completo
- Escalabilidad de lectura
- Time travel

**Contras:**
- Complejidad alta
- Overhead para muchos casos
- Curva de aprendizaje steep

**Decisión:** Parcialmente aceptado. CQRS solo donde aporte valor (queries complejas). Event sourcing para eventos de dominio críticos.

## Riesgos

### Riesgo 1: Over-Engineering

**Probabilidad:** Alta  
**Impacto:** Medio  
**Mitigación:**
- YAGNI原则: No implementar features no necesarios
- KISS原则: Mantener simple cuando posible
- Revisión arquitectónica regular
- MVP con features esenciales solo

### Riesgo 2: Curva de Aprendizaje

**Probabilidad:** Media  
**Impacto:** Alto  
**Mitigación:**
- Documentación exhaustiva (TECH_BIBLE)
- Pair programming inicial
- Training formal en DDD, Clean Arch
- Mentoría de arquitecto senior

### Riesgo 3: Performance

**Probabilidad:** Media  
**Impacto:** Alto  
**Mitigación:**
- Caching agresivo (Redis)
- Optimización de queries
- Monitoring de performance desde día 1
- Load testing antes de producción

### Riesgo 4: Complejidad de Multi-Agentes

**Probabilidad:** Alta  
**Impacto:** Alto  
**Mitigación:**
- Start con 3 agentes simples
- Iterar gradualmente
- Testing exhaustivo de orquestador
- Fallback a agentes individuales si falla orquestador

## Trabajo Futuro

### Corto Plazo (v0.1.0 - v0.2.0)

1. **Implementar capas básicas**
   - Domain layer para entidades principales
   - Application layer para use cases MVP
   - Infrastructure layer con Supabase y Qdrant

2. **Implementar orquestador básico**
   - 3 agentes especializados simples
   - Tool registry básico
   - Permission system inicial

3. **Implementar sistema de conocimiento MVP**
   - KB + CB + MB
   - Búsqueda vectorial básica
   - Memoria de conversaciones

### Medio Plazo (v0.3.0 - v1.0.0)

1. **Optimizar arquitectura**
   - CQRS para queries complejas
   - Event sourcing para eventos críticos
   - Caching con Redis

2. **Expander sistema multiagente**
   - Más agentes especializados
   - Herramientas más complejas
   - Memoria distribuida

3. **Mejorar observabilidad**
   - OpenTelemetry tracing
   - Prometheus metrics
   - Grafana dashboards

### Largo Plazo (v2.0.0+)

1. **Evaluar microservicios**
   - Si monolito se vuelve muy grande
   - Separar componentes críticos
   - Service mesh si necesario

2. **Expander conocimiento**
   - Learning Base con ML
   - Knowledge graphs
   - Advanced embeddings

3. **Optimizar performance**
   - Sharding de Qdrant
   - Read replicas de PostgreSQL
   - CDN global

## Referencias

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- [Vertical Slice Architecture by Jimmy Bogard](https://jimmybogard.com/vertical-slice-architecture/)
- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [CQRS Pattern by Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [Event Sourcing by Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)
- [TECH_BIBLE.md](../../TECH_BIBLE.md)
- [EREN_MANIFESTO.md](../../EREN_MANIFESTO.md)

---

**ADR Aprobado por:** Lead Architect (Cascade)  
**Fecha:** 2026-07-10  
**Revisión Próxima:** v1.0.0 (Q2 2027)
