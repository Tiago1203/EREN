# EREN Epic 3 — Prompt Builder

*Version 1.0 - 2026-07-20*

**Ingeniería de prompts.**

Epic 3 implementa el sistema de construcción y optimización de prompts.

---

## Objetivo

Construir prompts dinámicos para múltiples modelos de LLM.

---

## Dependencias

- **EPIC 0** (AI Foundation) - ✅ COMPLETO
- **EPIC 1** (Conversation) - ✅ COMPLETO
- **EPIC 2** (Context) - ✅ COMPLETO

---

## Modelos Soportados

| Proveedor | Modelos |
|-----------|---------|
| OpenAI | GPT-4, GPT-4-Turbo, GPT-3.5-Turbo |
| Anthropic | Claude-3-Opus, Claude-3-Sonnet, Claude-3-Haiku |
| Google | Gemini-Pro, Gemini-Ultra |
| Locales | Llama-2, Mistral |

---

## Componentes Implementados ✅

### PromptTemplate ✅
- Templates reutilizables con variables
- Sistema de variables: `{{variable}}` y `{{variable|default}}`
- Few-shot examples integrados
- Metadatos completos

### PromptStrategy ✅
- DirectStrategy: Pregunta directa
- ChainOfThoughtStrategy: Razonamiento paso a paso
- FewShotStrategy: Con ejemplos
- TreeOfThoughtStrategy: Múltiples caminos
- ReActStrategy: Reason + Act
- SelfAskStrategy: Preguntas intermedias

### PromptRenderer ✅
- Renderizado con interpolación de variables
- Adaptadores para diferentes modelos
- Estimación de tokens
- Múltiples formatos de salida

### PromptOptimizer ✅
- Optimización de texto
- Análisis de claridad y complejidad
- Generación de sugerencias
- Modo agresivo opcional

### PromptVersioning ✅
- Control de versiones
- Estados: DRAFT, ACTIVE, DEPRECATED, ARCHIVED
- Métricas de uso y éxito
- Comparación de versiones

---

## Ubicación de Implementación

```
core/ai/prompt/
├── __init__.py           # Exports y PromptBuilder
├── models.py             # PromptTemplate, RenderedPrompt, etc.
├── renderer.py           # PromptRenderer, ModelAdapters
├── optimizer.py          # PromptOptimizer, PromptAnalyzer
├── versioning.py         # PromptVersioningManager
└── strategy.py          # Estrategias de prompt
```

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2300 | Prompt Architecture | ✅ Accepted |
| ADR-2301 | Template System | ✅ Accepted |
| ADR-2302 | Prompt Strategies | ✅ Accepted |

---

## Uso

```python
from core.ai.prompt import (
    PromptBuilder,
    PromptTemplate,
    PromptStrategyType,
    PromptModel,
)

# Crear template
template = PromptTemplate(
    id="support-assistant",
    name="Support Assistant",
    system_template="Eres un asistente de soporte técnico.",
    user_template="Usuario pregunta: {{question}}",
)

# Construir prompt
builder = PromptBuilder()
prompt = builder.build(
    template=template,
    variables={"question": "¿Cómo reseteo mi contraseña?"},
    strategy=PromptStrategyType.CHAIN_OF_THOUGHT,
)

# Analizar
analysis = builder.analyze(prompt.user_message)
```

---

## Status

**Epic 3 Status:** ✅ COMPLETE

---

## Auditoría de Implementación

### ✅ Checklist de Verificación

| Componente | Módulo | Clase Principal | Líneas | Estado |
|------------|--------|-----------------|--------|--------|
| Models | `models.py` | PromptTemplate, RenderedPrompt | 245 | ✅ |
| Renderer | `renderer.py` | PromptRenderer, ModelAdapter | 268 | ✅ |
| Optimizer | `optimizer.py` | PromptOptimizer, PromptAnalyzer | 208 | ✅ |
| Versioning | `versioning.py` | PromptVersioningManager | 267 | ✅ |
| Strategy | `strategy.py` | StrategyFactory, estrategias | 210 | ✅ |

**Total: ~1,198 líneas de código**

### ✅ ADRs Verificados

| ADR | Título | Archivo |
|-----|--------|---------|
| ADR-2300 | Prompt Architecture | epic3/ADR-2300.md |
| ADR-2301 | Template System | epic3/ADR-2301.md |
| ADR-2302 | Prompt Strategies | epic3/ADR-2302.md |

**Total: 3 ADRs - Todos ✅ Accepted**

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status | Descripción |
|------|--------|-------------|
| EPIC 0 (AI Foundation) | ✅ COMPLETE | Kernel, Contracts, Interfaces |
| EPIC 1 (Conversation) | ✅ COMPLETE | Conversation management |
| EPIC 2 (Context) | ✅ COMPLETE | Context building |
| **EPIC 3 (Prompt)** | ✅ COMPLETE | Prompt engineering |
| **EPIC 4 (Memory)** | 🚧 NEXT | Memory system |
| EPIC 5 (Tools) | PENDING | Tool registry |
| EPIC 6 (Response) | PENDING | Response building |
| EPIC 7 (Providers) | PENDING | LLM providers |
| EPIC 8 (Sessions) | PENDING | Session management |
| EPIC 9 (AI Integration) | PENDING | Full integration |

---

*EREN Epic 3 v1.0 - Prompt Builder*
*Architecture Board - 2026-07-20*
