"""Response Composer - Componedor de respuestas."""

from __future__ import annotations

import uuid
from typing import Any, AsyncIterator

from core.ai.response.models import (
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


class ResponseComposer:
    """
    Componedor de respuestas.
    
    Construye respuestas estructuradas con múltiples
    elementos (texto, código, tablas, etc.).
    """

    def __init__(self, config: ResponseConfig | None = None) -> None:
        self._config = config or ResponseConfig()
        self._response: Response | None = None

    @property
    def config(self) -> ResponseConfig:
        return self._config

    def create_response(
        self,
        response_type: ResponseType = ResponseType.TEXT,
        conversation_id: str | None = None,
        message_id: str | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> Response:
        """Crea una nueva respuesta."""
        self._response = Response(
            id=str(uuid.uuid4()),
            response_type=response_type,
            conversation_id=conversation_id,
            message_id=message_id,
            user_id=user_id,
            tenant_id=tenant_id,
            streaming_enabled=self._config.enable_streaming,
        )
        return self._response

    def get_response(self) -> Response | None:
        """Obtiene la respuesta actual."""
        return self._response

    # ========== Agregar Elementos ==========

    def add_text(self, text: str) -> ResponseComposer:
        """Agrega texto plano."""
        if self._response:
            self._response.add_text(text)
        return self

    def add_markdown(self, markdown: str) -> ResponseComposer:
        """Agrega contenido markdown."""
        if self._response:
            self._response.add_markdown(markdown)
        return self

    def add_code(
        self,
        language: str,
        code: str,
        filename: str | None = None,
        line_numbers: bool = False,
    ) -> ResponseComposer:
        """Agrega bloque de código."""
        if self._response:
            self._response.add_element(ResponseElement(
                type=ResponseElementType.CODE,
                code=CodeBlock(
                    language=language,
                    code=code,
                    filename=filename,
                    line_numbers=line_numbers,
                ),
            ))
        return self

    def add_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        caption: str | None = None,
        align: str = "left",
    ) -> ResponseComposer:
        """Agrega tabla."""
        if self._response:
            columns = [
                TableColumn(name=h.lower().replace(" ", "_"), header=h, align=align)
                for h in headers
            ]
            self._response.add_table(columns, rows, caption)
        return self

    def add_list(
        self,
        items: list[str],
        ordered: bool = False,
    ) -> ResponseComposer:
        """Agrega lista."""
        if self._response:
            if ordered:
                for i, item in enumerate(items, 1):
                    self._response.add_element(ResponseElement(
                        type=ResponseElementType.TEXT,
                        content=f"{i}. {item}",
                    ))
            else:
                self._response.add_element(ResponseElement(
                    type=ResponseElementType.LIST,
                    list_items=items,
                ))
        return self

    def add_reference(
        self,
        id: str,
        title: str,
        url: str | None = None,
        snippet: str | None = None,
    ) -> ResponseComposer:
        """Agrega referencia."""
        if self._response:
            self._response.add_reference(id, title, url, snippet)
        return self

    def add_warning(self, message: str) -> ResponseComposer:
        """Agrega advertencia."""
        if self._response:
            self._response.add_element(ResponseElement(
                type=ResponseElementType.WARNING,
                content=message,
            ))
        return self

    def add_info(self, message: str) -> ResponseComposer:
        """Agrega información."""
        if self._response:
            self._response.add_element(ResponseElement(
                type=ResponseElementType.INFO,
                content=message,
            ))
        return self

    def add_error(self, message: str) -> ResponseComposer:
        """Agrega error."""
        if self._response:
            self._response.add_element(ResponseElement(
                type=ResponseElementType.ERROR,
                content=message,
            ))
        return self

    def add_divider(self) -> ResponseComposer:
        """Agrega divisor."""
        if self._response:
            self._response.add_element(ResponseElement(
                type=ResponseElementType.DIVIDER,
            ))
        return self

    def add_quote(self, text: str) -> ResponseComposer:
        """Agrega cita."""
        if self._response:
            self._response.add_element(ResponseElement(
                type=ResponseElementType.QUOTE,
                content=text,
            ))
        return self

    def add_image(
        self,
        url: str,
        alt: str | None = None,
        caption: str | None = None,
    ) -> ResponseComposer:
        """Agrega imagen."""
        if self._response:
            content = f"![{alt or 'image'}]({url})"
            if caption:
                content += f"\n*{caption}*"
            self._response.add_element(ResponseElement(
                type=ResponseElementType.IMAGE,
                content=content,
            ))
        return self

    # ========== Completar ==========

    def complete(self) -> Response | None:
        """Marca la respuesta como completada."""
        if self._response:
            self._response.status = ResponseStatus.COMPLETE
            self._response.completed_at = self._response.created_at
        return self._response

    def fail(self, error: str) -> Response | None:
        """Marca la respuesta como fallida."""
        if self._response:
            self._response.status = ResponseStatus.ERROR
            self._response.error = error
        return self._response

    # ========== Utilidades ==========

    def to_markdown(self) -> str:
        """Convierte a markdown."""
        if self._response:
            return self._response.to_markdown()
        return ""

    def reset(self) -> None:
        """Reinicia el composer."""
        self._response = None


class StreamingResponseComposer(ResponseComposer):
    """Versión con soporte de streaming."""

    def __init__(self, config: ResponseConfig | None = None) -> None:
        super().__init__(config)

    async def stream_text(
        self,
        text: str,
    ) -> AsyncIterator[StreamChunk]:
        """Stream de texto."""
        chunk_size = self._config.stream_chunk_size
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            is_final = i + chunk_size >= len(text)
            
            yield StreamChunk(
                content=chunk,
                is_final=is_final,
                chunk_type="text",
            )
            
            # Actualizar respuesta
            if self._response:
                self._response.raw_content += chunk

    async def stream_markdown(
        self,
        markdown: str,
    ) -> AsyncIterator[StreamChunk]:
        """Stream de markdown."""
        # Dividir por tokens significativos
        tokens = self._split_markdown(markdown)
        
        buffer = ""
        for token in tokens:
            buffer += token
            
            # Enviar cuando hay suficientes caracteres o es el final
            if len(buffer) >= self._config.stream_chunk_size:
                yield StreamChunk(
                    content=buffer,
                    is_final=False,
                    chunk_type="text",
                )
                buffer = ""
        
        # Enviar lo que queda
        if buffer:
            yield StreamChunk(
                content=buffer,
                is_final=True,
                chunk_type="text",
            )

    def _split_markdown(self, markdown: str) -> list[str]:
        """Divide markdown en tokens."""
        tokens = []
        
        # Split por espacios pero mantener estructura
        current = ""
        in_code_block = False
        
        for char in markdown:
            current += char
            
            # Detectar inicio/fin de code block
            if current.endswith("```"):
                if in_code_block:
                    in_code_block = False
                else:
                    in_code_block = True
                tokens.append(current)
                current = ""
        
        if current:
            tokens.append(current)
        
        return tokens

    async def stream_response(
        self,
        response: Response,
    ) -> AsyncIterator[StreamChunk]:
        """Stream de respuesta completa."""
        markdown = response.to_markdown()
        
        async for chunk in self.stream_markdown(markdown):
            yield chunk
        
        yield StreamChunk(
            content="",
            is_final=True,
            chunk_type="complete",
        )


class ResponseFormatter:
    """Formateador de respuestas."""

    def __init__(self, config: ResponseConfig | None = None) -> None:
        self._config = config or ResponseConfig()

    def format_code(
        self,
        language: str,
        code: str,
        line_numbers: bool = False,
    ) -> str:
        """Formatea bloque de código."""
        lines = [f"```{language}"]
        
        if line_numbers:
            for i, line in enumerate(code.split("\n"), 1):
                lines.append(f"{i:4d} {line}")
        else:
            lines.append(code)
        
        lines.append("```")
        return "\n".join(lines)

    def format_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        align: str = "left",
    ) -> str:
        """Formatea tabla markdown."""
        lines = []
        
        # Header
        lines.append("| " + " | ".join(headers) + " |")
        
        # Separator
        sep = "|" + "|".join("---" for _ in headers) + "|"
        lines.append(sep)
        
        # Rows
        for row in rows:
            lines.append("| " + " | ".join(str(c) for c in row) + " |")
        
        return "\n".join(lines)

    def format_list(
        self,
        items: list[str],
        ordered: bool = False,
    ) -> str:
        """Formatea lista."""
        if ordered:
            return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))
        return "\n".join(f"- {item}" for item in items)
