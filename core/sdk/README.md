# core/sdk - Cognitive SDK

## Descripción

SDK oficial para construir capacidades y plugins para EREN OS.

## Responsabilidad

- Definir API pública
- Proveer abstracciones
- Facilitar desarrollo

## Uso

```python
from core.sdk import Capability, CapabilityContext

class MyCapability(Capability):
    async def execute(self, context: CapabilityContext):
        return CapabilityResult(success=True)
```

## Límites

- **Puede depender de:** contracts, events
- **Nunca depende de:** implementaciones específicas

---
*Architecture only*
