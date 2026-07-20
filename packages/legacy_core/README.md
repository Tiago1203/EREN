# Legacy Core - Archived Code

**⚠️ ESTE CÓDIGO ESTÁ ARCHIVADO - NO SE USA**

---

## Contenido

Este directorio contiene código legacy que fue desarrollado durante el diseño inicial de EREN pero **NUNCA fue integrado con la API**.

### Módulos Archivados

| Módulo | Descripción | Estado |
|--------|-------------|--------|
| `core/cognitive/` | AI Layer (Memory, Reasoning, RAG, Safety) | Legacy |
| `core/clinical/` | Clinical Intelligence | Legacy |
| `core/knowledge/` | Knowledge Engine | Legacy |
| `core/rag/` | RAG Pipeline | Legacy |
| `core/memory/` | Memory Manager | Legacy |
| `core/reasoning/` | Reasoning Engine | Legacy |
| `core/biomedical/` | Biomedical Engine | Legacy |
| `core/device/` | Device Domain | Legacy |
| `core/incident/` | Incident Domain | Legacy |
| `core/recommendation/` | Recommendation Domain | Legacy |
| `core/shared/` | Shared Kernel | Legacy |

---

## Por qué está archivado

1. **Código incompleto** - Fue desarrollado parcialmente y abandonado
2. **Nunca se integró** - No está conectado a la API
3. **Stubs duplicados** - Existían stubs en `apps/api/app/` que tampoco se usaban
4. **Decisión: Reescribir** - Se decidió reescribir el código durante FASE 2-4

---

## FASE 2+ Plan

Cuando se implemente FASE 2 (AI Core), el código se reescribirá desde cero:

- EPIC 10: Conversation Controller
- EPIC 11: Context Builder
- EPIC 12: Prompt Builder
- EPIC 13: Memory Manager
- EPIC 14: Tool Orchestrator
- EPIC 15: Response Composer

---

**Fecha de archivado:** 2026-07-20
