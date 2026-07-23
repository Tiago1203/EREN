# ADR-2118: ContextBuilder Integration Pattern

**Estado:** ACEPTADO  
**Fecha:** Julio 2026  
**Decisor:** Arquitectura EREN  
**Epic:** EPIC 11.1

---

## 📋 Resumen

Definir el patrón de integración entre `ContextBuilder` y `BaseContextProvider` para que los providers de dominio participen en la construcción de contexto del AI Core.

---

## 🎯 Contexto

Después de la auditoría de EPIC 11, se identificó que:

1. `ContextBuilder.__init__` acepta `sources: dict[ContextSource, ContextSourceGetter]`
2. `AICoreController` pasa `providers=providers` a `ContextBuilder`
3. **Python ignora el argumento** porque no coincide con `sources`
4. `ContextBuilder.build()` nunca se ejecuta en el flujo principal

### Impacto

El contexto de dominio (devices, incidents, knowledge, recommendations) **nunca llegaba al LLM**.

---

## 🔄 Patrón Actual (INCORRECTO)

```python
# controller.py - INCORRECTO
providers = get_providers_with_gateways(...)
self._context = ContextBuilder(providers=providers)  # ❌ Ignorado

# ContextBuilder solo recibe sources vacíos
context = ContextBuilder(sources={})  # ✅ Correcto internamente
```

---

## ✅ Decisión

Implementar un **adapter bidireccional** entre `BaseContextProvider` y `ContextSourceGetter`.

### Opción 1: Adapter (ELEGIDA)

```python
# providers/__init__.py
from typing import Callable

def provider_to_source_getter(
    provider: BaseContextProvider,
    source: ContextSource,
) -> tuple[ContextSource, Callable]:
    """
    Convierte un BaseContextProvider a ContextSourceGetter.
    
    Returns:
        Tuple de (ContextSource, ContextSourceGetter)
    """
    async def getter(query: ContextQuery) -> list[ContextItem]:
        return await provider.get_context(query)
    
    return source, getter
```

**Ventajas:**
- ✅ Mantiene `BaseContextProvider` como abstracción principal
- ✅ Reutiliza lógica existente de providers
- ✅ No modifica `ContextBuilder`
- ✅ Compatible con DI

**Desventajas:**
- ❌ Añade capa de conversión

### Opción 2: Modificar ContextBuilder

Modificar `ContextBuilder` para aceptar `providers` directamente.

**Ventajas:**
- ✅ Más simple conceptualmente

**Desventajas:**
- ❌ Rompe responsabilidad única
- ❌ Acopla ContextBuilder a providers
- ❌ Duplica responsabilidad

### Opción 3: Eliminar ContextBuilder

Usar providers directamente en el controller.

**Ventajas:**
- ✅ Elimina abstracción

**Desventajas:**
- ❌ Pierde funcionalidad de ContextBuilder (prioritization, compression)
- ❌ Rompe arquitectura existente

---

## 🔧 Implementación

### 1. Crear Adapter en providers/__init__.py

```python
def provider_to_source_getter(
    provider: BaseContextProvider,
) -> tuple[ContextSource, "ContextSourceGetter"]:
    """
    Convierte un BaseContextProvider a ContextSourceGetter.
    
    Args:
        provider: Provider a convertir
        
    Returns:
        Tuple de (ContextSource, ContextSourceGetter)
    """
    async def getter(query: "ContextQuery") -> list["ContextItem"]:
        return await provider.get_context(query)
    
    return ContextSource(provider.name.upper()), getter


def providers_to_sources(
    providers: list["BaseContextProvider"],
) -> dict[ContextSource, "ContextSourceGetter"]:
    """
    Convierte una lista de providers a sources dict.
    
    Args:
        providers: Lista de providers
        
    Returns:
        Dict compatible con ContextBuilder.sources
    """
    sources = {}
    for provider in providers:
        source, getter = provider_to_source_getter(provider)
        sources[source] = getter
    return sources
```

### 2. Modificar AICoreController.initialize()

```python
async def initialize(self) -> None:
    # ... setup de otros componentes ...
    
    # EPIC 11.1: Conectar providers a ContextBuilder
    from core.PHASE_2.ai.context_builder.providers import get_providers_with_gateways
    from core.PHASE_2.ai.context_builder import providers_to_sources
    
    providers = get_providers_with_gateways(
        device_gateway=self._gateways.get("device"),
        incident_gateway=self._gateways.get("incident"),
        knowledge_gateway=self._gateways.get("knowledge"),
        recommendation_gateway=self._gateways.get("recommendation"),
        hospital_gateway=self._gateways.get("hospital"),
    )
    
    # ✅ Convertir providers a sources
    sources = providers_to_sources(providers)
    self._context = ContextBuilder(sources=sources)
```

### 3. Modificar AICoreController._build_context()

```python
async def _build_context(
    self,
    user_input: str,
    session: Session,
    extra_context: dict[str, Any] | None,
) -> dict[str, Any]:
    context_data = {}
    
    # 1. Contexto de sesión
    if session.context:
        context_data["session"] = {
            "topic": session.context.topic,
            "domain": session.context.domain,
        }
    
    # 2. Memoria
    if self._memory:
        memories = await self._memory.retrieve(user_input, limit=5)
        context_data["memories"] = [m.content for m in memories]
    
    # 3. ✅ CONTEXT BUILDER - Ejecutar providers
    context_query = ContextQuery(
        query=user_input,
        tenant_id=session.tenant_id or "default",
        max_tokens=4000,
        include_sources=[
            ContextSource.DEVICE,
            ContextSource.INCIDENT,
            ContextSource.KNOWLEDGE,
            ContextSource.RECOMMENDATION,
            ContextSource.HOSPITAL,
        ],
    )
    context_result = await self._context.build(context_query)
    context_data["domain_context"] = context_result
    
    # 4. Tools
    if self._tools:
        tools = self._tools.list_tools()
        context_data["tools"] = [
            {"id": t.id, "name": t.name} for t in tools
        ]
    
    # 5. Extra context
    if extra_context:
        context_data.update(extra_context)
    
    return context_data
```

---

## 🔄 Estado Actual vs Nuevo

### Antes (INCORRECTO)

```
providers → ContextBuilder(providers={}) → IGNORADO
_build_context() → {session, memory, tools} → SIN dominio
```

### Después (CORRECTO)

```
providers → providers_to_sources() → sources dict
sources → ContextBuilder(sources={}) → ✅ FUNCIONA
_build_context() → {session, memory, tools, domain_context} → CON dominio
```

---

## 📊 Consecuencias

### Positivas
- ✅ Contexto de dominio llega al LLM
- ✅ Providers existentes son reutilizados
- ✅ ContextBuilder funciona como diseñado
- ✅ Arquitectura se respeta

### Negativas
- ❌ Nueva capa de conversión
- ❌ Requiere modificar initialize()
- ❌ Requiere modificar _build_context()

### Riesgos
- ⚠️ Performance: providers se ejecutan en cada request
- ⚠️ Errores: providers pueden fallar silenciosamente

---

## 📝 Notas

### Sobre ContextSourceMapping

Cada provider tiene un `name` que debe mapear a `ContextSource`:

| Provider | ContextSource |
|----------|---------------|
| DeviceContextProvider | DEVICE |
| IncidentContextProvider | INCIDENT |
| KnowledgeContextProvider | KNOWLEDGE |
| RecommendationContextProvider | RECOMMENDATION |
| HospitalContextProvider | HOSPITAL |
| ConversationContextProvider | CONVERSATION |
| MemoryContextProvider | MEMORY |
| SessionContextProvider | SESSION |

### Sobre Error Handling

Los providers deben ser fault-tolerant:

```python
async def getter(query: ContextQuery) -> list[ContextItem]:
    try:
        return await provider.get_context(query)
    except Exception:
        return []  # Fail silently, no contexto
```

---

## ✅ Verificación

```python
# Verificar que ContextBuilder tiene sources
assert len(controller._context.sources) > 0

# Verificar que sources incluyen dominio
sources = set(controller._context.sources.keys())
assert ContextSource.DEVICE in sources
assert ContextSource.INCIDENT in sources

# Verificar que _build_context incluye domain_context
context = await controller._build_context(...)
assert "domain_context" in context
```

---

## 🔗 Referencias

- [ContextBuilder Implementation](../../../../core/ai/context_builder/builder.py)
- [BaseContextProvider Implementation](../../../../core/ai/context_builder/providers/base.py)
- [AICoreController Implementation](../../../../core/ai/integration/controller.py)
