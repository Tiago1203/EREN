# FASE 2: AI Core 🔜 PRÓXIMO

**Estado:** 🔜 En progreso

---

## 📋 Épicas

| Épica | Descripción | Status |
|-------|-------------|--------|
| **EPIC 4** | AI Core | 🔜 Próximo |
| **EPIC 5** | Conversational AI | ⏳ Pendiente |
| **EPIC 6** | Reasoning Engine | ⏳ Pendiente |

---

## 🎯 Componentes a Implementar

### Conversation Controller
- Chat interface
- Session management
- Multi-turn conversations

### Context Builder
- Context aggregation
- Memory integration
- Relevance scoring

### Prompt Builder
- Dynamic prompt construction
- Template management
- Token budget

### Memory Manager
- Short-term memory
- Long-term memory
- Working memory
- Episodic memory

### Tool Orchestrator
- Tool registry
- Tool execution
- Parallel execution

### Response Composer
- Response generation
- Citation builder
- Formatting

---

## 📁 Documentación

### Épicas
📂 `epics/`
- `epic4/` - AI Core
- `epic5/` - Conversational AI
- `epic6/` - Reasoning Engine

### ADRs
📂 `adr/`
- `adr/epic4/` - AI Core decisions
- `adr/epic5/` - Conversational AI decisions
- `adr/epic6/` - Reasoning decisions

---

## 📦 Carpeta de Código

```
apps/api/app/ai/
├── conversation/     # Conversation controller
├── context/         # Context builder
├── prompts/         # Prompt builder
├── memory/          # Memory manager
├── tools/          # Tool orchestrator
├── response/        # Response composer
├── reasoning/       # Reasoning engine
└── safety/         # Safety engine
```

---

## 🔗 Enlaces

- [PHASE_2_AI_CORE.md](../PHASE_2_AI_CORE.md) - Plan detallado
- [Anterior: FASE 1](../PHASE_1/) - Foundation
- [Siguiente: FASE 3](../PHASE_3/) - Clinical Intelligence
