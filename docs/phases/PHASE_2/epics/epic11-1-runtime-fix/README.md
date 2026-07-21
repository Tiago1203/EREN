# EPIC 11.1 — Runtime Integration Fix

## 🎯 Objetivo

Corregir la integración entre FASE 1 (Business Domain) y FASE 2 (AI Core) para que el flujo completo de contexto funcione correctamente.

## 📊 Estado Previo

Después de la auditoría arquitectónica, se identificaron los siguientes problemas:

| # | Problema | Severidad | Evidencia |
|---|----------|----------|-----------|
| 1 | `ContextBuilder(providers=providers)` ignora el argumento | 🔴 CRÍTICO | Parámetro es `sources`, no `providers` |
| 2 | `self._context.build()` nunca se llama | 🔴 CRÍTICO | No hay uso de `self._context` en controller |
| 3 | 11 `NotImplementedError` en gateways | 🟡 MODERADO | Métodos avanzados no implementados |

### Impacto

El contexto de dominio (devices, incidents, knowledge, recommendations) **NUNCA llegaba al LLM**.

**Flujo ACTUAL (INCORRECTO):**
```
Usuario → Controller.process()
    ↓
_build_context() ← IGNORA self._context.build()
    ↓
Sesión + Memoria + Tools (NO dominio)
    ↓
Prompt (SIN contexto de dominio)
    ↓
LLM MOCK (SIN información de devices/incidents/etc)
```

## 📋 Alcance

### Incluido
- [x] Corregir conexión ContextBuilder ↔ Providers
- [x] Implementar `self._context.build()` en flujo principal
- [x] Implementar 11 métodos faltantes en gateways
- [x] Validar flujo completo con tests
- [x] Actualizar documentación

### Excluido
- [ ] Providers LLM reales (OpenAI, Anthropic)
- [ ] Nuevos bounded contexts
- [ ] Cambios en arquitectura general

## 🔧 Problema 1: ContextBuilder no recibe providers

### Análisis

**Ubicación:** `core/ai/integration/controller.py:164`

```python
# ❌ INCORRECTO
providers = get_providers_with_gateways(...)
self._context = ContextBuilder(providers=providers)  # Argumento ignorado
```

**Causa:** `ContextBuilder.__init__` espera `sources: dict[ContextSource, ContextSourceGetter]`, no `providers`.

### Solución

Necesitamos un adapter que convierta `BaseContextProvider` → `ContextSourceGetter`.

```python
def provider_to_source_getter(provider: BaseContextProvider) -> ContextSourceGetter:
    """Convierte un provider a source getter."""
    async def getter(query: ContextQuery) -> list[ContextItem]:
        return await provider.get_context(query)
    return getter
```

## 🔧 Problema 2: _build_context no usa ContextBuilder

### Análisis

**Ubicación:** `core/ai/integration/controller.py:35-55`

```python
async def _build_context(self, ...):
    context_data = {}
    # Solo añade sesión, memoria, tools
    if session.context:
        context_data["session"] = {...}
    if self._memory:
        context_data["memories"] = ...
    # ❌ NUNCA llama a self._context.build()
    return context_data
```

### Solución

Integrar `ContextBuilder.build()` en el flujo:

```python
async def _build_context(self, user_input, session, extra_context):
    context_data = {}
    
    # 1. Contexto de sesión
    if session.context:
        context_data["session"] = {...}
    
    # 2. MEMORY - existente
    if self._memory:
        context_data["memories"] = await self._memory.retrieve(...)
    
    # 3. CONTEXT BUILDER - AGREGAR
    context_query = ContextQuery(
        query=user_input,
        tenant_id=session.tenant_id,
        max_tokens=4000,
    )
    context_result = await self._context.build(context_query)
    context_data["domain_context"] = context_result
    
    # 4. Tools
    if self._tools:
        context_data["tools"] = ...
    
    return context_data
```

## 🔧 Problema 3: NotImplementedError en gateways

### Análisis

| Gateway | Método | Criticidad |
|---------|--------|------------|
| IncidentGateway | get_history | 🟡 MODERADO |
| IncidentGateway | analyze | 🟡 MODERADO |
| KnowledgeGateway | get_related | 🟢 BAJA |
| KnowledgeGateway | get_by_confidence | 🟢 BAJA |
| RecommendationGateway | generate | 🟡 MODERADO |
| RecommendationGateway | get_by_device | 🟢 BAJA |
| HospitalGateway | get_by_id | 🔴 ALTA |
| HospitalGateway | get_capacity | 🔴 ALTA |
| HospitalGateway | get_available_beds | 🟡 MODERADA |
| WorkOrderGateway | get_sla_breached | 🟡 MODERADA |

### Solución

Para métodos de **alta/moderada criticidad**: Implementar.
Para métodos de **baja criticidad**: Mantener NotImplementedError con justificación.

## 📁 Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `core/ai/context_builder/providers/__init__.py` | Agregar `provider_to_source_getter()` |
| `core/ai/integration/controller.py` | Usar `self._context.build()` |
| `core/ai/integration/domain_adapter.py` | Implementar métodos faltantes |

## ✅ Criterios de Éxito

1. `ContextBuilder` recibe providers correctamente
2. `_build_context()` incluye resultado de `context.build()`
3. Todos los providers participan en construcción de contexto
4. Gateways devuelven datos reales
5. Tests validan flujo completo

## 🔄 Flujo Esperado (CORRECTO)

```
USUARIO → Controller.process()
    ↓
_build_context()
    ↓
┌─────────────────────────────────────┐
│ 1. Session Context                  │
│ 2. Memory Manager → retrieve()      │
│ 3. ContextBuilder.build()           │
│    ↓                               │
│    DeviceContextProvider.get_context()   → DeviceGateway
│    IncidentContextProvider.get_context() → IncidentGateway
│    KnowledgeContextProvider.get_context()→ KnowledgeGateway
│    RecommendationContextProvider    → RecommendationGateway
│    HospitalContextProvider           → HospitalGateway
│    ↓                               │
│    ContextResult con domain_context │
└─────────────────────────────────────┘
    ↓
Prompt Builder (con contexto completo)
    ↓
LLM Provider
    ↓
USUARIO (respuesta enriquecida)
```

## 📅 Timeline

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Documentación y ADR | 🚧 IN PROGRESS |
| 2 | Implementar adapter provider→source | 📋 PLANNED |
| 3 | Modificar AICoreController | 📋 PLANNED |
| 4 | Implementar gateways faltantes | 📋 PLANNED |
| 5 | Tests de validación | 📋 PLANNED |
| 6 | Documentación final | 📋 PLANNED |

## 📚 Referencias

- [ADR-2118: ContextBuilder Integration](./adr/ADR-2118-context-builder-integration.md)
- [Auditoría EREN](./AUDIT.md)
- [EPIC 11 original](../epic11-runtime-integration/README.md)
