# EREN Epic 5 — Tool Orchestrator

*Version 1.0 - 2026-07-20*

**Registro y ejecución de herramientas.**

Epic 5 implementa el sistema de herramientas del AI Core.

---

## Objetivo

Permitir que EREN utilize herramientas para ejecutar acciones.

---

## Dependencias

- **EPIC 0** (AI Foundation) - ✅ COMPLETO
- **EPIC 1** (Conversation) - ✅ COMPLETO
- **EPIC 2** (Context) - ✅ COMPLETO
- **EPIC 3** (Prompt) - ✅ COMPLETO
- **EPIC 4** (Memory) - ✅ COMPLETO

---

## Herramientas Soportadas

| Categoría | Herramientas |
|-----------|--------------|
| DATABASE | PostgreSQL, MySQL, SQLite |
| VECTOR_STORE | Qdrant, Pinecone, Weaviate |
| MESSAGE_QUEUE | RabbitMQ, Kafka |
| API | REST, GraphQL |
| CODE | Python, JavaScript |
| WEB | HTTP, Fetch |
| FILE | Sistema de archivos |
| SYSTEM | Shell commands |
| MCP | Model Context Protocol |

---

## Componentes Implementados ✅

### ToolRegistry ✅
- Registro de herramientas
- Búsqueda por categoría, tags, nombre
- Habilitar/deshabilitar

### ToolExecutor ✅
- Ejecución async con timeout
- Reintentos automáticos
- Control de concurrencia
- Tracking de ejecuciones

### ToolRouter ✅
- Routing automático por keywords
- Detección de categoría
- Puntuación de relevancia

### ToolSandbox ✅
- Validación de paths
- Bloqueo de comandos peligrosos
- Ejecución Python aislada

### ToolOrchestrator ✅
- API unificada

---

## Ubicación de Implementación

```
core/ai/tools/
├── __init__.py           # Exports y ToolOrchestrator
├── models.py             # ToolDefinition, ToolExecution
├── registry.py          # ToolRegistry
├── executor.py          # ToolExecutor
├── router.py            # ToolRouter
└── sandbox.py          # ToolSandbox
```

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2500 | Tool Architecture | ✅ Accepted |
| ADR-2501 | Tool Execution | ✅ Accepted |
| ADR-2502 | Tool Routing | ✅ Accepted |

---

## Uso

```python
from core.PHASE_2.ai.tools import (
    ToolOrchestrator,
    ToolDefinition,
    ToolCategory,
)

# Crear orchestrator
orchestrator = ToolOrchestrator()

# Registrar herramienta
tool = ToolDefinition(
    id="db-query",
    name="Database Query",
    description="Ejecuta queries SQL",
    category=ToolCategory.DATABASE,
)
orchestrator.register(tool, implementation)

# Ejecutar
result = await orchestrator.execute(
    tool_id="db-query",
    parameters={"sql": "SELECT * FROM users"},
)

# Enrutar automáticamente
tool = orchestrator.router.route("buscar en base de datos")
if tool:
    result = await orchestrator.route_and_execute(
        "buscar usuario",
        parameters={"query": "email"},
    )
```

---

## Status

**Epic 5 Status:** ✅ COMPLETE

---

## Auditoría de Implementación

### ✅ Checklist de Verificación

| Componente | Módulo | Clase Principal | Líneas | Estado |
|------------|--------|-----------------|--------|--------|
| Models | `models.py` | ToolDefinition, ToolExecution | 198 | ✅ |
| Registry | `registry.py` | ToolRegistry | 145 | ✅ |
| Executor | `executor.py` | ToolExecutor | 178 | ✅ |
| Router | `router.py` | ToolRouter | 157 | ✅ |
| Sandbox | `sandbox.py` | ToolSandbox | 153 | ✅ |

**Total: ~831 líneas de código**

### ✅ ADRs Verificados

| ADR | Título | Archivo |
|-----|--------|---------|
| ADR-2500 | Tool Architecture | epic5/ADR-2500.md |
| ADR-2501 | Tool Execution | epic5/ADR-2501.md |
| ADR-2502 | Tool Routing | epic5/ADR-2502.md |

**Total: 3 ADRs - Todos ✅ Accepted**

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status | Descripción |
|------|--------|-------------|
| EPIC 0 (AI Foundation) | ✅ COMPLETE | Kernel, Contracts, Interfaces |
| EPIC 1 (Conversation) | ✅ COMPLETE | Conversation management |
| EPIC 2 (Context) | ✅ COMPLETE | Context building |
| EPIC 3 (Prompt) | ✅ COMPLETE | Prompt engineering |
| EPIC 4 (Memory) | ✅ COMPLETE | Memory system |
| **EPIC 5 (Tools)** | ✅ COMPLETE | Tool registry |
| **EPIC 6 (Response)** | 🚧 NEXT | Response building |
| EPIC 7 (Providers) | PENDING | LLM providers |
| EPIC 8 (Sessions) | PENDING | Session management |
| EPIC 9 (AI Integration) | PENDING | Full integration |

---

*EREN Epic 5 v1.0 - Tool Orchestrator*
*Architecture Board - 2026-07-20*
