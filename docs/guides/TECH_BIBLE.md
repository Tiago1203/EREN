# TECH_BIBLE - Constitución Técnica de EREN

> **Este documento es la CONSTITUCIÓN TÉCNICA de EREN.**
> Todas las decisiones técnicas inmutables están definidas aquí.
> Cualquier cambio requiere discusión consciente, ADR documentado, y aprobación explícita del Lead Architect.
> Este documento es OBLIGATORIO para cualquier desarrollador que trabaje en EREN.

---

## Declaración de Autoridad

Este documento es la autoridad técnica suprema del proyecto. En caso de conflicto entre este documento y cualquier otro documento técnico, TECH_BIBLE prevalece.

**Alineado con**: [VISION.md](./VISION.md) - Máxima autoridad del proyecto

---

## Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [Paradigmas Arquitecturales](#paradigmas-arquitecturales)
3. [Convenciones de Nombres](#convenciones-de-nombres)
4. [Estructura de Carpetas](#estructura-de-carpetas)
5. [Estándares de Código](#estándares-de-código)
6. [Estrategia Git](#estrategia-git)
7. [Estrategia de Branches](#estrategia-de-branches)
8. [Convenciones de Commits](#convenciones-de-commits)
9. [Testing](#testing)
10. [Documentación](#documentación)
11. [Seguridad](#seguridad)
12. [IA Responsable](#ia-responsable)
13. [Architecture Decision Records (ADR)](#architecture-decision-records-adr)
14. [Model Context Protocol (MCP)](#model-context-protocol-mcp)
15. [Supabase](#supabase)
16. [Docker](#docker)
17. [WSL2](#wsl2)
18. [Checklist de Pull Request](#checklist-de-pull-request)
19. [Cambios a este Documento](#cambios-a-este-documento)

---

## Arquitectura General

### Paradigmas Arquitecturales

EREN sigue los siguientes paradigmas arquitectónicos de forma OBLIGATORIA:

- **Clean Architecture**: Separación de capas estricta (Domain, Application, Infrastructure, Interfaces)
- **SOLID**: Principios de diseño orientado a objetos (Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion)
- **Domain Driven Design (DDD)**: Dominio como centro del diseño con bounded contexts, aggregates, y domain services
- **Vertical Slice Architecture**: Organización por características cuando Clean Architecture no aporte valor claro
- **CQRS**: Separación de lectura/escritura cuando aporte valor en queries complejas
- **Arquitectura Hexagonal**: Puertos y adaptadores para desacoplamiento de infraestructura
- **Event-Driven Architecture**: Comunicación asíncrona entre motores cognitivos
- **KISS & YAGNI**: Simplicidad y evitar sobre-ingeniería, especialmente en MVP
- **Security by Design**: Seguridad desde el diseño, no como parche
- **AI by Design**: IA como ciudadano de primera clase en arquitectura
- **Escalabilidad Horizontal**: Preparado para crecer a 10,000+ hospitales
- **Observabilidad**: Todo debe ser observable (logging, tracing, metrics)

### Patrones Prohibidos

Los siguientes patrones están PROHIBIDOS en EREN:

- ❌ God Objects
- ❌ Spaghetti Code
- ❌ Tight Coupling sin interfaces
- ❌ Magic Numbers/Strings (usar constantes)
- ❌ Global State (usar dependency injection)
- ❌ Direct Database Access from UI/Controllers
- ❌ Business Logic in Controllers (usar domain services)
- ❌ Direct API calls from Domain Layer
- ❌ Circular Dependencies
- ❌ Silent Failures (siempre loggear errores)

### Arquitectura de Tres Capas

EREN se compone de tres capas fundamentales:

**Capa 1: EREN CORE (Cognitive Operating System)**
- Motores cognitivos especializados
- Orquestación de procesos
- Gestión de recursos cognitivos

**Capa 2: Dominios de Negocio**
- Equipment, Maintenance, Case, Knowledge, User, Hospital domains
- Lógica de negocio pura
- Independiente de infraestructura

**Capa 3: Interfaces de Usuario**
- Conversational, Visual, Mobile, Programmatic, Integration interfaces
- Presentación pura
- Sin lógica de negocio

---

## Paradigmas Arquitecturales (Detallado)

### Clean Architecture

**Capas**:
1. **Domain Layer**: Entidades, value objects, domain services, repositories interfaces
2. **Application Layer**: Use cases, commands, queries, DTOs
3. **Infrastructure Layer**: Implementaciones concretas de repositories, external services
4. **Interface Layer**: HTTP controllers, WebSocket handlers

**Reglas**:
- Dependencies point inward (Infrastructure → Application → Domain)
- Domain layer NO dependencies de otras capas
- Business logic en Domain layer, NO en controllers
- Interfaces en Domain layer, implementaciones en Infrastructure

### Domain Driven Design (DDD)

**Bounded Contexts**:
- Equipment Context
- Maintenance Context
- Case Context
- Knowledge Context
- User Context
- Hospital Context

**Elementos**:
- **Entities**: Objetos con identidad única
- **Value Objects**: Objetos sin identidad, inmutables
- **Aggregates**: Raíz de consistencia transaccional
- **Repositories**: Interfaces para persistencia
- **Domain Services**: Lógica de negocio que no pertenece a entidades
- **Domain Events**: Eventos que ocurren en el dominio

### Event-Driven Architecture

**Event Types**:
- **Domain Events**: Eventos de negocio
- **Integration Events**: Eventos entre bounded contexts
- **System Events**: Eventos de sistema (audit, logging)

**Message Queue**: RabbitMQ o Kafka para comunicación asíncrona

---

## Convenciones de Nombres

### Python (Backend)

```python
# Variables y funciones: snake_case
user_name = "Juan"
calculate_maintenance_cost()

# Clases: PascalCase
class MaintenanceOrder:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3

# Módulos: snake_case
# maintenance_order_service.py

# Paquetes: snake_case
# services/
# repositories/
```

### TypeScript/JavaScript (Frontend)

```typescript
// Variables y funciones: camelCase
const userName = "Juan";
function calculateMaintenanceCost() {}

// Clases/Interfaces/Types: PascalCase
interface MaintenanceOrder {}
class MaintenanceService {}

// Constantes: UPPER_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3;

// Componentes React: PascalCase
const MaintenanceCard = () => {};

// Archivos: kebab-case
// maintenance-order.service.ts
// maintenance-card.tsx
```

### Base de Datos

```sql
-- Tablas: snake_case, plural
maintenance_orders
equipment_failures

-- Columnas: snake_case
created_at
updated_at
user_id

-- Índices: idx_tabla_columnas
idx_maintenance_orders_status

-- Foreign keys: fk_tabla_columna_referencia
fk_maintenance_orders_equipment_id
```

### Git

```bash
# Ramas: kebab-case con prefijo
feature/new-maintenance-module
fix/authentication-bug
hotfix/security-patch

# Tags: vX.Y.Z
v1.0.0
v0.1.0-alpha
```

---

## Estructura de Carpetas

```
eren/
├── docs/                          # Documentación
│   ├── adr/                      # Architecture Decision Records
│   ├── api/                      # Documentación de APIs
│   ├── guides/                   # Guías de usuario
│   └── architecture/             # Diagramas y arquitectura
├── frontend/                     # Next.js Frontend
│   ├── src/
│   │   ├── app/                  # App Router
│   │   ├── components/           # Componentes React
│   │   ├── lib/                  # Utilidades
│   │   ├── hooks/                # Custom Hooks
│   │   ├── services/             # Servicios API
│   │   ├── types/                # TypeScript types
│   │   └── styles/               # Estilos globales
│   ├── public/                   # Assets estáticos
│   └── tests/                    # Tests frontend
├── backend/                      # Python FastAPI Backend
│   ├── src/
│   │   ├── domain/               # Dominio (DDD)
│   │   │   ├── entities/
│   │   │   ├── value_objects/
│   │   │   ├── repositories/
│   │   │   └── services/
│   │   ├── application/          # Casos de uso
│   │   │   ├── commands/
│   │   │   ├── queries/
│   │   │   └── dto/
│   │   ├── infrastructure/      # Infraestructura
│   │   │   ├── persistence/
│   │   │   ├── external/
│   │   │   └ messaging/
│   │   ├── interfaces/          # Interfaces HTTP
│   │   │   ├── api/
│   │   │   └ websocket/
│   │   ├── agents/               # Sistema multiagente
│   │   │   ├── orchestrator/
│   │   │   ├── specialists/
│   │   │   └── tools/
│   │   ├── knowledge/           # Sistema de conocimiento
│   │   │   ├── kb/
│   │   │   ├── cb/
│   │   │   ├── mb/
│   │   │   ├── lb/
│   │   │   └── db/
│   │   └── shared/              # Código compartido
│   │       ├── config/
│   │       ├── exceptions/
│   │       └── utils/
│   ├── tests/                   # Tests backend
│   └── pyproject.toml
├── docker/                       # Configuraciones Docker
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── docker-compose.yml
├── scripts/                      # Scripts de utilidad
├── .github/                      # GitHub Actions
│   └── workflows/
├── .env.example                  # Variables de entorno ejemplo
├── .gitignore
├── README.md
├── EREN_MANIFESTO.md
├── TECH_BIBLE.md
├── PROJECT_BOOTSTRAP.md
└── LICENSE
```

---

## Estándares de Código

### Python

```python
# Type hints obligatorios
def create_maintenance_order(
    equipment_id: str,
    priority: MaintenancePriority,
    assigned_to: Optional[str] = None
) -> MaintenanceOrder:
    """Crea una orden de mantenimiento."""
    pass

# Docstrings estilo Google
class MaintenanceService:
    """Servicio para gestión de órdenes de mantenimiento."""
    
    def create_order(
        self,
        equipment_id: str,
        priority: MaintenancePriority
    ) -> MaintenanceOrder:
        """Crea una nueva orden de mantenimiento.
        
        Args:
            equipment_id: ID del equipo a mantener.
            priority: Prioridad de la orden.
            
        Returns:
            La orden de mantenimiento creada.
            
        Raises:
            EquipmentNotFoundError: Si el equipo no existe.
        """
        pass

# Máximo 80 caracteres por línea
# Máximo 4 niveles de indentación
# Máximo 50 líneas por función
# Máximo 200 líneas por clase
```

### TypeScript

```typescript
// Type hints obligatorios
interface MaintenanceOrder {
  id: string;
  equipmentId: string;
  priority: MaintenancePriority;
  assignedTo?: string;
  createdAt: Date;
}

// JSDoc para funciones públicas
/**
 * Crea una orden de mantenimiento.
 * @param equipmentId - ID del equipo a mantener.
 * @param priority - Prioridad de la orden.
 * @returns La orden de mantenimiento creada.
 */
async function createMaintenanceOrder(
  equipmentId: string,
  priority: MaintenancePriority
): Promise<MaintenanceOrder> {
  // ...
}

// Máximo 80 caracteres por línea
// Máximo 4 niveles de indentación
// Máximo 50 líneas por función
// Máximo 200 líneas por componente
```

---

## Estrategia Git

### Estrategia de Branches

### Ramas Principales

- **main**: Producción. Solo merges desde develop.
- **develop**: Desarrollo. Integración continua.

### Ramas de Feature

```
feature/<nombre-descriptivo>
Ejemplo: feature/maintenance-workflow
```

### Ramas de Fix

```
fix/<nombre-descriptivo>
Ejemplo: fix/authentication-timeout
```

### Ramas de Hotfix

```
hotfix/<nombre-descriptivo>
Ejemplo: hotfix/security-vulnerability
```

### Flujo de Trabajo

1. Crear rama desde `develop`
2. Desarrollar y commitear
3. Crear Pull Request a `develop`
4. Code review obligatorio
5. Tests deben pasar
7. Merge a `develop`
8. Delete rama de feature

---

## Convenciones para Commits

### Formato

```
<tipo>(<alcance>): <descripción>

[opcional: cuerpo]

[opcional: footer]
```

### Tipos

- **feat**: Nueva funcionalidad
- **fix**: Corrección de bug
- **docs**: Cambios en documentación
- **style**: Formato, missing semicolons, etc.
- **refactor**: Refactorización
- **test**: Agregar/modificar tests
- **chore**: Actualizar deps, config, etc.
- **_perf**: Mejoras de performance
- **_security**: Mejoras de seguridad

### Ejemplos

```bash
feat(maintenance): add preventive scheduling workflow

fix(auth): resolve token expiration edge case

docs(api): update maintenance endpoints documentation

refactor(agent): extract tool registry to separate module

test(knowledge): add vector similarity tests

_security(auth): implement rate limiting
```

---

## Testing

### Estrategia de Testing

EREN sigue una pirámide de testing:

**70% Unit Tests**
- Tests de funciones y clases individuales
- Tests de domain logic
- Tests de utilities
- Sin dependencias externas (mocks)

**20% Integration Tests**
- Tests de integración entre componentes
- Tests de repositories con DB de test
- Tests de APIs externas con mocks
- Tests de message queues

**10% E2E Tests**
- Tests de flujo completo
- Tests de integración con sistemas externos
- Tests de UI críticos

### Frameworks

**Python**:
- pytest para unit tests
- pytest-asyncio para async tests
- pytest-cov para coverage
- factory-boy para fixtures
- moto para AWS mocks

**TypeScript**:
- Jest para unit tests
- React Testing Library para componentes
- Playwright para E2E tests
- MSW para API mocking

### Coverage

- **Mínimo 80% coverage** para código crítico
- **Mínimo 60% coverage** para código no crítico
- **100% coverage** para domain layer

### Reglas

- Todo nuevo código DEBE tener tests
- Tests deben ser independientes
- Tests deben ser rápidos (< 5s para suite unit)
- Tests deben ser reproducibles
- Tests deben tener nombres descriptivos

---

## Documentación

### Tipos de Documentación

**Documentación de Código**:
- Docstrings obligatorios para funciones públicas
- Type hints obligatorios
- Comments para lógica compleja
- README en cada módulo

**Documentación de Arquitectura**:
- ADRs para decisiones arquitectónicas
- Diagramas Mermaid para arquitectura
- Documentación de dominios (DDD)
- Documentación de motores cognitivos

**Documentación de API**:
- OpenAPI 3.0 spec auto-generada
- Ejemplos de request/response
- Códigos de error documentados
- Rate limits documentados

**Documentación de Usuario**:
- Guías de usuario
- Guías de instalación
- Guías de troubleshooting
- Videos tutoriales (futuro)

### Herramientas

- **Python**: Sphinx o MkDocs
- **TypeScript**: TypeDoc
- **API**: FastAPI auto-docs
- **Diagrams**: Mermaid

---

## Seguridad

### Principios de Seguridad

1. **Defense in Depth**: Múltiples capas de seguridad
2. **Principle of Least Privilege**: Mínimo privilegio necesario
3. **Zero Trust**: No confiar en nada por defecto
4. **Security by Design**: Seguridad desde el diseño
5. **Fail Secure**: Fallar de forma segura

### Implementación

**Autenticación**:
- Supabase Auth como provider
- MFA opcional para usuarios enterprise
- Session management robusto
- Token refresh automático

**Autorización**:
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Row Level Security (RLS) en PostgreSQL
- Permission checks en cada endpoint

**Encryption**:
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Field-level encryption para datos sensibles
- Key management con KMS

**Input Validation**:
- Validación de todos los inputs
- Sanitización de datos
- Type checking estricto
- Length limits

**Output Encoding**:
- Escaping de outputs
- Content Security Policy (CSP)
- XSS prevention
- SQL injection prevention

**Rate Limiting**:
- Distributed rate limiting (Redis)
- Per-user rate limits
- Per-endpoint rate limits
- Tiered limits por plan

**Secrets Management**:
- Secrets en variables de entorno
- No secrets en código
- Secrets rotation automática
- Audit de accesos a secrets

**Security Headers**:
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Content-Security-Policy

**Auditing**:
- Logging de todos los accesos
- Logging de cambios sensibles
- Alertas de actividad sospechosa
- Regular security audits

---

## IA Responsable

### Principios

1. **Explicabilidad**: Cada respuesta debe ser explicada
2. **Auditoría**: Toda acción debe ser auditable
3. **Trazabilidad**: Origen de cada decisión
4. **Anti-Halucinación**: Verificar antes de responder
5. **Confianza**: Admitir incertidumbre
6. **Privacidad**: No exponer datos sensibles
7. **Permisos**: Respetar permisos de usuario
8. **Humano en el circuito**: Decisiones críticas requieren aprobación

### Implementación

**Explicabilidad**:
- Chain of thought logging
- Citas de fuentes
- Razonamiento detallado
- Confidence scores

**Auditoría**:
- Logging de todas las decisiones de IA
- Logging de inputs/outputs de LLM
- Logging de herramientas usadas
- Logging de permisos verificados

**Anti-Halucinación**:
- Verificación de hechos antes de responder
- Citas obligatorias para afirmaciones fácticas
- Admisión de ignorancia cuando no se sabe
- Validación con fuentes confiables

**Confianza**:
- Confidence scores basados en evidencia
- Admisión de incertidumbre
- Distinción entre hecho y probabilidad
- Limitaciones conocidas documentadas

**Privacidad**:
- Anonimización de datos antes de enviar a LLM
- No enviar PII sin consentimiento
- Row Level Security para datos sensibles
- Compliance con HIPAA/GDPR

**Humano en el Circuito**:
- Decisiones críticas requieren aprobación
- Recomendaciones, no órdenes
- Capacidad de override por humano
- Feedback loop para aprendizaje

---

## Architecture Decision Records (ADR)

### Propósito

Los ADRs documentan decisiones arquitectónicas importantes, su contexto, consecuencias y alternativas consideradas.

### Formato

Ver [docs/adr/README.md](./docs/adr/README.md) para formato oficial.

### Proceso

1. Identificar necesidad de ADR
2. Asignar número según categoría
3. Crear archivo en docs/adr/
4. Seguir formato oficial
5. Documentar contexto, decisión, consecuencias
6. Incluir alternativas consideradas
7. Actualizar índice
8. Solicitar aprobación del Lead Architect
9. Crear PR para revisión

### Categorías

- Arquitectura (ADR-000X)
- Backend (ADR-001X)
- Frontend (ADR-002X)
- IA (ADR-003X)
- Seguridad (ADR-005X)
- Datos (ADR-006X)
- Infraestructura (ADR-007X)
- Cloud (ADR-008X)
- Normativas (ADR-009X)
- DevOps (ADR-010X)
- Hospitales (ADR-011X)
- Integraciones (ADR-012X)
- Dominios (ADR-013X)

---

## Model Context Protocol (MCP)

### Propósito

MCP es el protocolo de comunicación entre EREN CORE y los motores cognitivos.

### Implementación

**Message Types**:
- REQUEST: Solicitar acción a motor
- RESPONSE: Respuesta de motor
- ERROR: Error en ejecución
- EVENT: Evento asíncrono

**Message Format**:
```json
{
  "id": "uuid",
  "type": "REQUEST|RESPONSE|ERROR|EVENT",
  "source": "motor_name",
  "target": "motor_name",
  "content": {},
  "timestamp": "ISO8601",
  "metadata": {}
}
```

**Communication**:
- Async message passing
- Message queue (RabbitMQ/Kafka)
- Circuit breakers
- Timeout handling
- Retry logic

---

## Supabase

### Uso

Supabase se utiliza para:
- PostgreSQL como base de datos principal
- Autenticación de usuarios
- Storage de archivos
- Realtime (WebSockets)
- Row Level Security (RLS)

### Configuración

**Database**:
- PostgreSQL 15+
- Connection pooling
- Read replicas (futuro)
- Backup automático

**Auth**:
- Supabase Auth
- Email/password auth
- OAuth providers (Google, GitHub)
- MFA (futuro)

**Storage**:
- Supabase Storage
- Buckets por tipo de archivo
- CDN automático
- RLS en storage

**Realtime**:
- WebSockets para updates en tiempo real
- Subscriptions a cambios
- Presence tracking (futuro)

### Reglas

- NO usar Supabase como vendor lock-in
- Preparar migración a PostgreSQL nativo
- Usar RLS para aislamiento de datos
- NO lógica de negocio en Supabase Functions
- NO triggers complejos en DB

---

## Docker

### Uso

Docker se utiliza para:
- Contenedores de desarrollo
- Contenedores de producción
- Orquestación con Docker Compose (desarrollo)
- Orquestación con Kubernetes (producción)

### Dockerfiles

**Backend Dockerfile**:
- Base image: python:3.11-slim
- Multi-stage build
- Non-root user
- Health check
- Optimización de tamaño

**Frontend Dockerfile**:
- Base image: node:20-alpine
- Multi-stage build
- Static assets optimization
- Health check

### Docker Compose

**Servicios**:
- backend
- frontend
- postgres
- qdrant
- redis
- rabbitmq (futuro)

### Reglas

- NO hardcoded values en Dockerfiles
- Usar .env files
- Health checks obligatorios
- Resource limits definidos
- Security scanning obligatorio

---

## WSL2

### Configuración

EREN se desarrolla en WSL2 Ubuntu 24.04 en Windows.

### Requisitos

- Windows 11 con WSL2 habilitado
- Ubuntu 24.04 LTS
- Docker Desktop con WSL2 integration
- Git configurado

### Reglas

- Desarrollo en WSL2, NO en Windows nativo
- Docker Desktop con WSL2 integration
- Filesystem en WSL2 para performance
- NO cross-platform paths en código

---

## Filosofía de Diseño

### Principios

1. **Dominio Primero**: El código debe reflejar el dominio de negocio de ingeniería clínica
2. **Explicito sobre Implícito**: Nada de magia, todo debe ser claro y documentado
3. **Composibilidad**: Componentes pequeños que se componen para formar sistemas complejos
4. **Testeabilidad**: Todo debe ser testeable desde el diseño
5. **Observabilidad**: Todo debe ser observable (logging, tracing, metrics)
6. **Seguridad por Defecto**: Seguro por defecto, no por parche
7. **Arquitectura para 15 Años**: Cada decisión considera horizonte de 15 años
8. **Amplificación Humana**: Diseñado para amplificar, no reemplazar capacidad humana

### Anti-Patterns

- ❌ Lógica de negocio en controladores
- ❌ Acoplamiento directo a infraestructura
- ❌ Código no testeable
- ❌ Falta de logging estructurado
- ❌ Secrets en código
- ❌ Hardcoded values
- ❌ Silent failures
- ❌ God objects
- ❌ Tight coupling sin interfaces
- ❌ Global state

---

## Checklist de Pull Request

### Antes de crear PR

- [ ] Código sigue TECH_BIBLE
- [ ] Tests escritos y pasando (unit + integration)
- [ ] Coverage mínimo alcanzado
- [ ] Documentación actualizada
- [ ] ADR creado si es decisión arquitectónica
- [ ] Commits siguen convención
- [ ] No hay secrets en código
- [ ] Logging estructurado agregado
- [ ] Error handling implementado
- [ ] Seguridad considerada
- [ ] IA responsable considerada

### Durante Review

- [ ] Al menos 1 approval de senior developer
- [ ] CI/CD pasa
- [ ] Security scan pasa
- [ ] Performance no degradada
- [ ] No introduce tech debt significativo
- [ ] ADR aprobado si aplica

### Antes de Merge

- [ ] Squash commits (si es feature branch)
- [ ] Delete rama remota
- [ ] Tag si es release
- [ ] Changelog actualizado

---

## Cambios a este Documento

Cualquier cambio a TECH_BIBLE.md requiere:

1. **Discusión en issue**: Discusión consciente del cambio propuesto
2. **ADR documentando el cambio**: ADR específico documentando la decisión
3. **Aprobación del Lead Architect**: Aprobación explícita del Lead Architect
4. **Actualización de este documento**: Actualización de TECH_BIBLE.md
5. **Comunicación al equipo**: Comunicación del cambio al equipo completo
6. **Versión incrementada**: Incrementar versión de TECH_BIBLE.md

### Proceso de Cambio

1. Crear issue proponiendo el cambio
2. Discutir con equipo y Lead Architect
3. Crear ADR documentando la decisión
4. Obtener aprobación del Lead Architect
5. Actualizar TECH_BIBLE.md
6. Incrementar versión
7. Comunicar al equipo
8. Crear PR con el cambio

---

**Última actualización**: 2026-07-10  
**Versión**: 2.0.0  
**Autor**: Chief Software Architect / Principal AI Engineer / CTO  
**Alineado con**: VISION.md v1.0.0, ADR-0001, ADR-0002
