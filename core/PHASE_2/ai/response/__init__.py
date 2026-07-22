"""EREN AI Response - Response Composer Module.

Módulo de construcción de respuestas del AI Core.

## Componentes

- **models**: Modelos de respuesta
- **composer**: Componedor de respuestas

## Características

- Texto y Markdown
- Código con syntax highlighting
- Tablas
- Referencias
- Listas
- Warnings e información
- Streaming
- Respuestas parciales y completas

## Uso

```python
from core.PHASE_2.ai.response import (
    ResponseComposer,
    StreamingResponseComposer,
    ResponseConfig,
    ResponseType,
)

# Crear composer
composer = ResponseComposer()

# Crear respuesta
response = composer.create_response(
    response_type=ResponseType.MARKDOWN,
    conversation_id="conv-123",
)

# Agregar elementos
composer.add_markdown("# Título")
composer.add_text("Contenido de la respuesta.")
composer.add_code("python", "print('hello')")
composer.add_table(
    headers=["Nombre", "Edad"],
    rows=[["Ana", 25], ["Juan", 30]],
    caption="Tabla de ejemplo",
)
composer.add_reference(
    id="1",
    title="Documentación",
    url="https://example.com",
)
composer.add_warning("Precaución: esto es importante")
composer.add_info("Información adicional")

# Completar
response = composer.complete()
markdown = composer.to_markdown()
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                  RESPONSE COMPOSER                                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Response Elements                          │ │
│  │  Text │ Code │ Table │ Image │ Reference │ List │ etc.  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Response Composer                           │ │
│  │        (Build, Complete, Format, Stream)                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Output Formats                             │ │
│  │            Markdown │ JSON │ HTML │ Text                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

from core.PHASE_2.ai.response.models import (
    ChartConfig,
    CodeBlock,
    Reference,
    Response,
    ResponseConfig,
    ResponseElement,
    ResponseElementType,
    ResponseStatus,
    ResponseType,
    StreamChunk,
    TableColumn,
    TableData,
)
from core.PHASE_2.ai.response.composer import (
    ResponseComposer,
    ResponseFormatter,
    StreamingResponseComposer,
)

__version__ = "1.0.0"

__all__ = [
    # Models
    "Response",
    "ResponseElement",
    "ResponseElementType",
    "ResponseStatus",
    "ResponseType",
    "ResponseConfig",
    "StreamChunk",
    "CodeBlock",
    "Reference",
    "TableColumn",
    "TableData",
    "ChartConfig",
    # Composer
    "ResponseComposer",
    "StreamingResponseComposer",
    "ResponseFormatter",
]
