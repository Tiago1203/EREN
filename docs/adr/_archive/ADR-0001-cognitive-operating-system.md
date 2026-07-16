# ADR-0001: ¿Por qué EREN es un Cognitive Operating System y no un chatbot?

## Status
Accepted

> **Nota de consistencia (2026-07-13):** La arquitectura actual materializa este
> COS como un **monorepo** con una capa cognitiva `core/` de **ocho motores**
> (orchestrator, planner, reasoning, memory, knowledge, diagnostic, workflow,
> tools) sobre una **capa de contratos** (`core/contracts`). Las
> responsabilidades de permisos, auditoría y aprendizaje descritas más abajo se
> tratan hoy como capacidades transversales/futuras. Ver
> [ARCHITECTURE_OVERVIEW.md](../../ARCHITECTURE_OVERVIEW.md) y
> [CORE_SPECIFICATION.md](../../CORE_SPECIFICATION.md).

## Context

### Problema
El mercado actual está saturado de "chatbots de IA" que prometen revolucionar industrias pero fallan en entregar valor sostenible. La percepción predominante es que EREN es simplemente "otro chatbot para ingeniería biomédica".

Esta percepción es peligrosa porque:

1. **Expectativas Incorrectas**: Los usuarios esperan respuestas rápidas tipo ChatGPT, no un sistema cognitivo profundo
2. **Subestimación de Valor**: Se percibe como una herramienta de Q&A simple, no como infraestructura cognitiva
3. **Limitaciones Percebidas**: Se asume que solo puede responder preguntas, no orquestar procesos complejos
4. **Escalabilidad Dudosas**: Los chatbots no escalan a miles de hospitales con conocimiento institucional
5. **Diferenciación Competitiva**: Difícil diferenciarse de soluciones genéricas de IA

### Contexto de Negocio
EREN debe operar en entornos hospitalarios donde:
- Las decisiones tienen consecuencias reales en seguridad del paciente
- El conocimiento institucional es crítico y debe preservarse
- La escalabilidad a miles de hospitales es un requisito
- La integración profunda con sistemas existentes es esencial
- La confianza y explicabilidad son no negociables

Un chatbot simple no puede satisfacer estos requisitos.

## Decision

**EREN es un Cognitive Operating System (COS), no un chatbot.**

### Definición de Cognitive Operating System

Un Cognitive Operating System es una plataforma que:

1. **Orquesta Motores Cognitivos Especializados**: Gestiona múltiples motores de razonamiento, memoria, aprendizaje, planificación, y ejecución
2. **Gestiona Recursos Cognitivos**: Al igual que un OS gestiona recursos hardware/software, EREN gestiona recursos cognitivos (memoria, conocimiento, procesos)
3. **Provee Múltiples Interfaces**: La conversación es solo una de varias interfaces (visual, programática, móvil, integración)
4. **Ejecuta Workflows Automatizados**: No solo responde preguntas, ejecuta procesos complejos con supervisión humana
5. **Aprende y Evoluciona**: Cada interacción mejora el sistema de forma estructurada y persistente
6. **Se Integra Profundamente**: No es una isla, se integra nativamente con sistemas hospitalarios
7. **Escala Horizontalmente**: Diseñado para operar en miles de hospitales con conocimiento distribuido

### Arquitectura de Tres Capas

EREN se compone de tres capas fundamentales:

**Capa 1: EREN CORE (Cognitive Operating System)**

Motores cognitivos canónicos actuales (`core/`), sobre `core/contracts`:
- Orchestrator Engine: Coordina los motores y el ciclo de vida de la petición cognitiva
- Planner Engine: Descompone objetivos en planes ordenados y re-planifica
- Reasoning Engine: Razonamiento explicable sobre evidencia
- Memory Engine: Memoria a corto y largo plazo
- Knowledge Engine: Gestión y recuperación de conocimiento institucional
- Diagnostic Engine: Análisis de fallas de equipos clínicos
- Workflow Engine: Procesos operativos duraderos multi-paso
- Tool Engine: Registro/adaptadores para capacidades externas controladas

> Capacidades transversales/futuras (no motores canónicos hoy): aprendizaje
> (Learning), permisos/autorización (Permission) y auditoría (Audit).

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

### La Conversación es Solo una Interfaz

La interfaz conversacional (chat) es el punto de entrada inicial, pero NO define el sistema. EREN puede:

- Responder preguntas (interfaz conversacional)
- Visualizar datos y tendencias (interfaz visual)
- Ejecutar workflows automatizados (interfaz programática)
- Integrarse con sistemas hospitalarios (interfaz de integración)
- Proveer APIs para desarrolladores (interfaz de desarrolladores)

## Consequences

### Impacto Positivo

1. **Diferenciación Clara**: EREN se posiciona como infraestructura cognitiva, no como otro chatbot
2. **Valor Sosten**: El valor es en la infraestructura, no en respuestas individuales
3. **Escalabilidad**: Arquitectura diseñada para miles de hospitales
4. **Integración Profunda**: Capacidad de integración nativa con sistemas hospitalarios
5. **Evolución Orgánica**: Plataforma que evoluciona con cada hospital
6. **Marketplace de Aplicaciones**: Posibilidad de construir aplicaciones sobre EREN CORE
7. **ROI Medible**: Valor en optimización de procesos, no solo en respuestas rápidas

### Impacto Negativo

1. **Complejidad Inicial**: Arquitectura más compleja que un chatbot simple
2. **Curva de Aprendizaje**: Requiere más tiempo para entender el sistema completo
3. **Expectativas de Usuarios**: Necesidad de educar usuarios sobre la naturaleza de COS
4. **Desarrollo Inicial**: Más tiempo para construir la infraestructura base
5. **Documentación Extensiva**: Requiere documentación arquitectónica exhaustiva

## Benefits

1. **Escalabilidad a 10,000+ Hospitales**: Arquitectura diseñada para escala masiva
2. **Valor Acumulativo**: El conocimiento se acumula y mejora con el tiempo
3. **Multi-Interfaz**: Flexibilidad para diferentes use cases
4. **Integración Nativa**: No es una capa sobre sistemas existentes, se integra profundamente
5. **Ecosistema Evolutivo**: Posibilidad de marketplace de aplicaciones
6. **Diferenciación Competitiva**: Posicionamiento único en el mercado
7. **Sostenibilidad a Largo Plazo**: Arquitectura diseñada para 15+ años

## Risks

1. **Riesgo de Percepción**: Usuarios pueden no entender la diferencia entre COS y chatbot
   - **Mitigación**: Educación exhaustiva, documentación clara, demos de capacidades avanzadas

2. **Complejidad Técnica**: Arquitectura de COS es más compleja que chatbot
   - **Mitigación**: Equipo técnico experimentado, arquitectura modular, documentación exhaustiva

3. **Tiempo de Desarrollo**: Más tiempo para construir infraestructura base
   - **Mitigación**: MVP enfocado en motores fundamentales, iteración rápida

4. **Adopción de Usuarios**: Usuarios pueden resistir la complejidad
   - **Mitigación**: Interfaz conversacional como punto de entrada simple, onboarding gradual

5. **Competencia con Chatbots**: Competidores pueden posicionarse como "más simples"
   - **Mitigación**: Diferenciación clara en valor, no en simplicidad; ROI medible

## Alternatives Considered

### Alternativa 1: Chatbot Simple con RAG
**Descripción**: Chatbot simple con Retrieval Augmented Generation sobre documentos técnicos.

**Por qué fue rechazada**:
- No escala a miles de hospitales
- No gestiona conocimiento institucional estructurado
- No ejecuta workflows complejos
- No se integra profundamente con sistemas
- Valor limitado a respuestas, no a procesos
- Diferenciación competitiva mínima

### Alternativa 2: Sistema de Gestión de Conocimiento (KMS)
**Descripción**: Sistema tipo Confluence/Notion con búsqueda avanzada.

**Por qué fue rechazada**:
- Sin inteligencia cognitiva
- Sin razonamiento o aprendizaje
- Sin workflows automatizados
- Sin integración profunda
- Repositorio estático, no sistema vivo
- No amplifica capacidad humana

### Alternativa 3: CMMS con IA
**Descripción**: Computerized Maintenance Management System con capa de IA.

**Por qué fue rechazada**:
- Enfoque en gestión de procesos, no cognición
- IA como add-on, no como núcleo
- Limitado a mantenimiento, no a conocimiento general
- Sin motores cognitivos especializados
- Sin escalabilidad de conocimiento

### Alternativa 4: Plataforma de Agentes (Multi-Agent System)
**Descripción**: Sistema de múltiples agentes conversacionales especializados.

**Por qué fue rechazada**:
- Aún percibido como chatbot mejorado
- Sin arquitectura de OS subyacente
- Sin gestión de recursos cognitivos
- Sin interfaces múltiples
- Limitado a conversación como interfaz principal

## Future Work

1. **Desarrollo de Motores Cognitivos**: Implementar los 8 motores fundamentales de EREN CORE
2. **Documentación de Arquitectura**: Documentación exhaustiva de cada motor y su interacción
3. **Demos de Capacidades**: Demostraciones de workflows automatizados más allá de chat
4. **Educación de Usuarios**: Material educativo sobre diferencia entre COS y chatbot
5. **Marketplace de Aplicaciones**: Diseño de marketplace para aplicaciones sobre EREN CORE
6. **Integraciones Profundas**: Demostraciones de integración con sistemas hospitalarios
7. **Métricas de Éxito**: Definir métricas específicas para valor de COS vs chatbot

## References

- [VISION.md](../../VISION.md) - Máxima autoridad del proyecto
- [EREN_MANIFESTO.md](../../EREN_MANIFESTO.md) - Filosofía y principios
- Cognitive Computing: A Brief Guide and Glossary - IBM Research
- Cognitive Systems: The Next Wave of AI - MIT Technology Review
- Operating System Concepts - Silberschatz, Galvin, Gagne
- Domain-Driven Design - Eric Evans

---

**ADR-0001**  
**Status**: Accepted  
**Fecha**: 2026-07-10  
**Autor**: Chief Software Architect / Principal AI Engineer / CTO  
**Aprobado por**: Product Owner  
**Alineado con**: VISION.md v1.0.0
