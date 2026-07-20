"""Response Models - Modelos de respuesta."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator


class ResponseType(str, Enum):
    """Tipos de respuesta."""
    TEXT = "text"
    MARKDOWN = "markdown"
    TABLE = "table"
    CODE = "code"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    JSON = "json"
    HTML = "html"
    MIXED = "mixed"


class ResponseStatus(str, Enum):
    """Estado de la respuesta."""
    PENDING = "pending"
    STREAMING = "streaming"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


class ResponseElementType(str, Enum):
    """Tipos de elementos en una respuesta."""
    TEXT = "text"
    MARKDOWN = "markdown"
    TABLE = "table"
    CODE = "code"
    IMAGE = "image"
    CHART = "chart"
    REFERENCE = "reference"
    WARNING = "warning"
    INFO = "info"
    ERROR = "error"
    DIVIDER = "divider"
    LIST = "list"
    QUOTE = "quote"


@dataclass
class Reference:
    """Referencia a una fuente."""
    id: str
    title: str
    url: str | None = None
    snippet: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TableColumn:
    """Columna de tabla."""
    name: str
    header: str
    align: str = "left"  # left, center, right
    width: str | None = None


@dataclass
class TableData:
    """Datos de tabla."""
    columns: list[TableColumn]
    rows: list[list[Any]]
    caption: str | None = None


@dataclass
class CodeBlock:
    """Bloque de código."""
    language: str
    code: str
    filename: str | None = None
    line_numbers: bool = False


@dataclass
class ChartConfig:
    """Configuración de gráfico."""
    chart_type: str  # bar, line, pie, scatter
    title: str
    x_label: str | None = None
    y_label: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseElement:
    """Un elemento individual de la respuesta."""
    type: ResponseElementType
    content: str = ""
    
    # Datos estructurados
    table: TableData | None = None
    code: CodeBlock | None = None
    chart: ChartConfig | None = None
    reference: Reference | None = None
    list_items: list[str] | None = None
    
    # Metadatos
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Rendering
    visible: bool = True
    order: int = 0

    def to_markdown(self) -> str:
        """Convierte el elemento a markdown."""
        if self.type == ResponseElementType.TEXT:
            return self.content
        
        elif self.type == ResponseElementType.MARKDOWN:
            return self.content
        
        elif self.type == ResponseElementType.CODE and self.code:
            lines = [f"```{self.code.language}"]
            if self.code.filename:
                lines.append(f"# {self.code.filename}")
            lines.append(self.code.code)
            lines.append("```")
            return "\n".join(lines)
        
        elif self.type == ResponseElementType.TABLE and self.table:
            lines = []
            
            # Header
            header = "| " + " | ".join(c.header for c in self.table.columns) + " |"
            separator = "|" + "|".join("---" for _ in self.table.columns) + "|"
            
            lines.append(header)
            lines.append(separator)
            
            # Rows
            for row in self.table.rows:
                lines.append("| " + " | ".join(str(c) for c in row) + " |")
            
            if self.table.caption:
                lines.append(f"\n*{self.table.caption}*")
            
            return "\n".join(lines)
        
        elif self.type == ResponseElementType.REFERENCE and self.reference:
            return f"[{self.reference.title}]({self.reference.url or '#'})"
        
        elif self.type == ResponseElementType.LIST and self.list_items:
            return "\n".join(f"- {item}" for item in self.list_items)
        
        elif self.type == ResponseElementType.WARNING:
            return f"> ⚠️ {self.content}"
        
        elif self.type == ResponseElementType.INFO:
            return f"> ℹ️ {self.content}"
        
        elif self.type == ResponseElementType.ERROR:
            return f"> ❌ {self.content}"
        
        elif self.type == ResponseElementType.DIVIDER:
            return "---"
        
        elif self.type == ResponseElementType.QUOTE:
            return f"> {self.content}"
        
        return self.content


@dataclass
class Response:
    """Respuesta completa."""
    id: str
    status: ResponseStatus = ResponseStatus.PENDING
    
    # Contenido
    elements: list[ResponseElement] = field(default_factory=list)
    raw_content: str = ""
    
    # Tipo
    response_type: ResponseType = ResponseType.TEXT
    
    # Metadatos
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    model: str | None = None
    tokens_used: int = 0
    
    # Errores
    error: str | None = None
    
    # Contexto
    conversation_id: str | None = None
    message_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    
    # Configuración
    streaming_enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def add_element(self, element: ResponseElement) -> None:
        """Agrega un elemento a la respuesta."""
        element.order = len(self.elements)
        self.elements.append(element)
    
    def add_text(self, text: str) -> None:
        """Agrega texto simple."""
        self.add_element(ResponseElement(
            type=ResponseElementType.TEXT,
            content=text,
        ))
    
    def add_markdown(self, markdown: str) -> None:
        """Agrega contenido markdown."""
        self.add_element(ResponseElement(
            type=ResponseElementType.MARKDOWN,
            content=markdown,
        ))
    
    def add_code(
        self,
        language: str,
        code: str,
        filename: str | None = None,
    ) -> None:
        """Agrega bloque de código."""
        self.add_element(ResponseElement(
            type=ResponseElementType.CODE,
            code=CodeBlock(
                language=language,
                code=code,
                filename=filename,
            ),
        ))
    
    def add_table(
        self,
        columns: list[TableColumn],
        rows: list[list[Any]],
        caption: str | None = None,
    ) -> None:
        """Agrega tabla."""
        self.add_element(ResponseElement(
            type=ResponseElementType.TABLE,
            table=TableData(
                columns=columns,
                rows=rows,
                caption=caption,
            ),
        ))
    
    def add_reference(
        self,
        id: str,
        title: str,
        url: str | None = None,
        snippet: str | None = None,
    ) -> None:
        """Agrega referencia."""
        self.add_element(ResponseElement(
            type=ResponseElementType.REFERENCE,
            reference=Reference(
                id=id,
                title=title,
                url=url,
                snippet=snippet,
            ),
        ))
    
    def to_markdown(self) -> str:
        """Convierte la respuesta a markdown."""
        parts = []
        for element in sorted(self.elements, key=lambda e: e.order):
            if element.visible:
                markdown = element.to_markdown()
                if markdown:
                    parts.append(markdown)
        return "\n\n".join(parts)
    
    @property
    def is_complete(self) -> bool:
        return self.status == ResponseStatus.COMPLETE
    
    @property
    def is_error(self) -> bool:
        return self.status == ResponseStatus.ERROR
    
    @property
    def text_content(self) -> str:
        """Obtiene solo el contenido de texto."""
        return self.raw_content or self.to_markdown()


@dataclass
class StreamChunk:
    """Chunk de streaming."""
    content: str
    is_final: bool = False
    chunk_type: str = "text"  # text, code, table, error
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseConfig:
    """Configuración de respuesta."""
    # Formato
    default_type: ResponseType = ResponseType.MARKDOWN
    enable_markdown: bool = True
    enable_syntax_highlighting: bool = True
    
    # Streaming
    enable_streaming: bool = True
    stream_chunk_size: int = 10
    
    # Límites
    max_tokens: int = 8192
    max_elements: int = 100
    
    # Tablas
    default_table_page_size: int = 10
    
    # Citas
    include_references: bool = True
    max_references: int = 10
