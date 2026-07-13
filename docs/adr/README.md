# Architecture Decision Records (ADR)

Este directorio contiene los Architecture Decision Records de EREN. Los ADRs documentan decisiones arquitectónicas importantes, su contexto, consecuencias y alternativas consideradas.

## Índice Oficial por Categorías

### Arquitectura

- **ADR-0001**: ¿Por qué EREN es un Cognitive Operating System y no un chatbot?
- **ADR-0002**: Arquitectura General de EREN CORE
- **ADR-0003**: Arquitectura de Tres Capas (CORE, Dominios, Interfaces)
- **ADR-0004**: Estrategia de Escalabilidad Horizontal
- **ADR-0005**: Arquitectura de Microservicios vs Monolito Modular

### Backend

- **ADR-0010**: Selección de FastAPI como Framework Backend
- **ADR-0011**: Arquitectura Limpia en Python
- **ADR-0012**: Estrategia de Async/Await en Backend
- **ADR-0013**: Gestión de Dependencias con uv
- **ADR-0014**: Estrategia de API REST vs GraphQL
- **ADR-0015**: Versionado de APIs

### Frontend

- **ADR-0020**: Selección de Next.js 14 como Framework Frontend
- **ADR-0021**: Estrategia de TypeScript Strict Mode
- **ADR-0022**: Arquitectura de Componentes con shadcn/ui
- **ADR-0023**: Gestión de Estado con Zustand
- **ADR-0024**: Estrategia de Server Components vs Client Components
- **ADR-0025**: Optimización de Performance y Bundle Size

### IA

- **ADR-0030**: Arquitectura de Motores Cognitivos
- **ADR-0031**: Reasoning Engine Design
- **ADR-0032**: Knowledge Engine Design
- **ADR-0033**: Memory Engine Design
- **ADR-0034**: Learning Engine Design
- **ADR-0035**: Planning Engine Design
- **ADR-0036**: Tool Engine Design
- **ADR-0037**: Permission Engine Design
- **ADR-0038**: Audit Engine Design
- **ADR-0039**: Estrategia de Multi-LLM Abstraction
- **ADR-0040**: Estrategia de Embeddings y Búsqueda Vectorial

### Seguridad

- **ADR-0050**: Estrategia de Security by Design
- **ADR-0051**: Estrategia de Autenticación Multi-Hospital
- **ADR-0052**: Row Level Security (RLS) Strategy
- **ADR-0053**: Estrategia de Encryption (at rest, in transit, field-level)
- **ADR-0054**: Estrategia de Key Management (KMS)
- **ADR-0055**: Estrategia de Rate Limiting
- **ADR-0056**: Estrategia de Auditoría de Seguridad
- **ADR-0057**: Estrategia de Compliance (HIPAA, GDPR)

### Datos

- **ADR-0060**: Estrategia de Base de Datos (Supabase + PostgreSQL)
- **ADR-0061**: Estrategia de Vector Database (Qdrant)
- **ADR-0062**: Knowledge Base Architecture
- **ADR-0063**: Case Base Architecture
- **ADR-0064**: Memory Base Architecture
- **ADR-0065**: Document Base Architecture
- **ADR-0066**: Estrategia de Data Retention
- **ADR-0067**: Estrategia de Data Archival
- **ADR-0068**: Estrategia de Backup y Disaster Recovery

### Infraestructura

- **ADR-0070**: Estrategia de Contenedores (Docker)
- **ADR-0071**: Estrategia de Orquestación (Docker Compose → Kubernetes)
- **ADR-0072**: Estrategia de Multi-Layer Caching
- **ADR-0073**: Estrategia de Message Queues (RabbitMQ/Kafka)
- **ADR-0074**: Estrategia de Service Mesh (Istio)
- **ADR-0075**: Estrategia de CDN

### Cloud

- **ADR-0080**: Estrategia de Multi-Cloud vs Single Cloud
- **ADR-0081**: Estrategia de Multi-Region Deployment
- **ADR-0082**: Estrategia de Auto-Scaling
- **ADR-0083**: Estrategia de Cost Optimization
- **ADR-0084**: Estrategia de Data Residency

### Normativas

- **ADR-0090**: Política de IA Responsable (IEC 62304, ISO 14971, ISO 13485)
- **ADR-0091**: Estrategia de Explicabilidad Obligatoria
- **ADR-0092**: Estrategia de Trazabilidad de Decisiones
- **ADR-0093**: Estrategia de Control Humano en el Circuito
- **ADR-0094**: Estrategia de Versionado de Modelos
- **ADR-0095**: Estrategia de Clasificación de Riesgo

### DevOps

- **ADR-0100**: Estrategia de CI/CD (GitHub Actions)
- **ADR-0101**: Estrategia de Git Branching
- **ADR-0102**: Estrategia de Code Review
- **ADR-0103**: Estrategia de Testing (Unit, Integration, E2E)
- **ADR-0104**: Estrategia de Feature Flags
- **ADR-0105**: Estrategia de Observability (Logging, Tracing, Metrics)
- **ADR-0106**: Estrategia de Error Tracking (Sentry)
- **ADR-0107**: Estrategia de Chaos Engineering

### Hospitales

- **ADR-0110**: Estrategia de Multi-Tenancy
- **ADR-0111**: Estrategia de Isolation de Datos por Hospital
- **ADR-0112**: Estrategia de Configuración por Hospital
- **ADR-0113**: Estrategia de Onboarding de Hospitales
- **ADR-0114**: Estrategia de Compartición de Conocimiento (Opcional)
- **ADR-0115**: Estrategia de Benchmarking Anónimo

### Integraciones

- **ADR-0120**: Integración con Supabase Auth
- **ADR-0121**: Integración con Qdrant
- **ADR-0122**: Integración con OpenAI API
- **ADR-0123**: Integración con HL7 (Futuro)
- **ADR-0124**: Integración con DICOM (Futuro)
- **ADR-0125**: Integración con FHIR (Futuro)
- **ADR-0126**: Integración con EMR/EHR (Futuro)
- **ADR-0127**: Integración con CMMS (Futuro)

### Dominios (DDD)

- **ADR-0130**: Equipment Domain Design
- **ADR-0131**: Maintenance Domain Design
- **ADR-0132**: Case Domain Design
- **ADR-0133**: Knowledge Domain Design
- **ADR-0134**: User Domain Design
- **ADR-0135**: Hospital Domain Design
- **ADR-0136**: Bounded Contexts y Context Maps

---

## Formato Oficial de ADR

Cada ADR sigue el formato estándar de Architecture Decision Records:

```markdown
# ADR-XXXX: [Título]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYYY]

## Context
[Descripción del contexto y problema]

## Decision
[La decisión tomada]

## Consequences
[Impacto positivo y negativo]

## Benefits
[Beneficios de la decisión]

## Risks
[Riesgos identificados]

## Alternatives Considered
[Otras opciones evaluadas y por qué no fueron seleccionadas]

## Future Work
[Trabajo futuro relacionado]

## References
[Links a recursos relevantes]
```

## Proceso para Crear un ADR

1. **Identificar la necesidad**: Una decisión arquitectónica significativa requiere un ADR
2. **Asignar número**: Usar el siguiente número disponible en la categoría apropiada
3. **Crear archivo**: Crear `ADR-XXXX-titulo.md` en este directorio
4. **Seguir formato**: Usar el formato oficial de ADR
5. **Documentar contexto**: Explicar claramente el problema y contexto
6. **Documentar decisión**: Describir la decisión tomada
7. **Documentar consecuencias**: Beneficios, riesgos y trade-offs
8. **Incluir alternativas**: Documentar alternativas consideradas y por qué fueron rechazadas
9. **Actualizar índice**: Agregar el ADR al índice apropiado
10. **Crear PR**: Solicitar revisión del equipo
11. **Aprobar**: El ADR debe ser aprobado antes de ser implementado

## ADRs Activos

Los siguientes ADRs están actualmente activos:

- ADR-0001: ¿Por qué EREN es un Cognitive Operating System y no un chatbot? (Pending)
- ADR-0002: Arquitectura General de EREN CORE (Pending)

## ADRs Propuestos

Los siguientes ADRs están propuestos pero no aceptados:

- (Ninguno actualmente)

## ADRs Deprecados

Los siguientes ADRs han sido deprecados:

- (Ninguno actualmente)

## ADRs Superseded

Los siguientes ADRs han sido reemplazados por versiones más recientes:

- (Ninguno actualmente)

---

**Última actualización**: 2026-07-10  
**Alineado con**: VISION.md v1.0.0
