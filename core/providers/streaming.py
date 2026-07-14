"""Streaming support for EREN OS Multi-Provider Layer (PR-056).

Provides streaming capabilities for LLM responses.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable, Generator, AsyncGenerator


# =============================================================================
# Streaming Types
# =============================================================================


@dataclass
class StreamChunk:
    """A single chunk of a streamed response."""
    content: str
    is_final: bool = False
    chunk_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamMetrics:
    """Metrics for streaming operations."""
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None
    chunks_received: int = 0
    total_tokens: int = 0
    first_token_latency_ms: float = 0.0
    last_chunk_latency_ms: float = 0.0

    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    @property
    def tokens_per_second(self) -> float:
        """Get tokens per second."""
        duration = self.duration_ms / 1000
        if duration > 0:
            return self.total_tokens / duration
        return 0.0


# =============================================================================
# Stream Handlers
# =============================================================================


class StreamHandler(ABC):
    """Abstract stream handler."""

    @abstractmethod
    def on_chunk(self, chunk: StreamChunk) -> None:
        """Handle a chunk."""
        pass

    @abstractmethod
    def on_complete(self) -> None:
        """Handle completion."""
        pass

    @abstractmethod
    def on_error(self, error: Exception) -> None:
        """Handle error."""
        pass


class CallbackStreamHandler(StreamHandler):
    """Stream handler that calls a callback."""

    def __init__(
        self,
        on_chunk: Callable[[StreamChunk], None] | None = None,
        on_complete: Callable[[], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ):
        """Initialize handler."""
        self._on_chunk = on_chunk
        self._on_complete = on_complete
        self._on_error = on_error

    def on_chunk(self, chunk: StreamChunk) -> None:
        """Handle chunk."""
        if self._on_chunk:
            self._on_chunk(chunk)

    def on_complete(self) -> None:
        """Handle completion."""
        if self._on_complete:
            self._on_complete()

    def on_error(self, error: Exception) -> None:
        """Handle error."""
        if self._on_error:
            self._on_error(error)


class CollectingStreamHandler(StreamHandler):
    """Stream handler that collects all chunks."""

    def __init__(self):
        """Initialize handler."""
        self._chunks: list[StreamChunk] = []
        self._lock = threading.Lock()
        self._complete = False
        self._error: Exception | None = None
        self._metrics = StreamMetrics()

    def on_chunk(self, chunk: StreamChunk) -> None:
        """Handle chunk."""
        with self._lock:
            if self._metrics.chunks_received == 0:
                from time import time
                self._metrics.first_token_latency_ms = (
                    time() - self._metrics.start_time.timestamp()
                ) * 1000
            
            self._chunks.append(chunk)
            self._metrics.chunks_received += 1

    def on_complete(self) -> None:
        """Handle completion."""
        with self._lock:
            self._complete = True
            from time import time
            self._metrics.end_time = datetime.now(UTC)

    def on_error(self, error: Exception) -> None:
        """Handle error."""
        with self._lock:
            self._error = error
            self._metrics.end_time = datetime.now(UTC)

    def get_content(self) -> str:
        """Get collected content."""
        with self._lock:
            return "".join(c.content for c in self._chunks)

    def get_chunks(self) -> list[StreamChunk]:
        """Get all chunks."""
        with self._lock:
            return list(self._chunks)

    def is_complete(self) -> bool:
        """Check if complete."""
        with self._lock:
            return self._complete

    def get_error(self) -> Exception | None:
        """Get error if any."""
        with self._lock:
            return self._error

    @property
    def metrics(self) -> StreamMetrics:
        """Get metrics."""
        with self._lock:
            return self._metrics


class GeneratorStreamHandler(StreamHandler):
    """Stream handler that yields chunks."""

    def __init__(self):
        """Initialize handler."""
        self._queue: list[StreamChunk] = []
        self._lock = threading.Lock()
        self._complete = threading.Event()
        self._error: Exception | None = None

    def on_chunk(self, chunk: StreamChunk) -> None:
        """Handle chunk."""
        with self._lock:
            self._queue.append(chunk)
        if not chunk.is_final:
            self._complete.set()

    def on_complete(self) -> None:
        """Handle completion."""
        self._complete.set()

    def on_error(self, error: Exception) -> None:
        """Handle error."""
        with self._lock:
            self._error = error
        self._complete.set()

    def stream(self) -> Generator[StreamChunk, None, None]:
        """Stream chunks."""
        while not self._complete.is_set():
            with self._lock:
                if self._queue:
                    chunk = self._queue.pop(0)
                else:
                    chunk = None
            if chunk:
                yield chunk
            elif self._error:
                raise self._error
            elif not self._complete.is_set():
                self._complete.wait(0.1)
        
        with self._lock:
            while self._queue:
                yield self._queue.pop(0)


# =============================================================================
# Stream Adapter (for different provider formats)
# =============================================================================


class StreamAdapter(ABC):
    """Abstract stream adapter for different provider formats."""

    @abstractmethod
    def adapt(self, raw_stream: Any) -> Generator[StreamChunk, None, None]:
        """Adapt raw stream to standard chunks."""
        pass


class OpenAIStreamAdapter(StreamAdapter):
    """Adapter for OpenAI streaming format."""

    def adapt(self, raw_stream: Any) -> Generator[StreamChunk, None, None]:
        """Adapt OpenAI stream."""
        for chunk in raw_stream:
            if hasattr(chunk, "choices") and chunk.choices:
                choice = chunk.choices[0]
                if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                    content = choice.delta.content or ""
                    yield StreamChunk(
                        content=content,
                        is_final=choice.finish_reason is not None,
                        chunk_type="text",
                    )


class AnthropicStreamAdapter(StreamAdapter):
    """Adapter for Anthropic streaming format."""

    def adapt(self, raw_stream: Any) -> Generator[StreamChunk, None, None]:
        """Adapt Anthropic stream."""
        for chunk in raw_stream:
            if hasattr(chunk, "type"):
                if chunk.type == "content_block_delta":
                    content = getattr(chunk.delta, "text", "") or ""
                    yield StreamChunk(content=content)
                elif chunk.type == "message_delta":
                    yield StreamChunk(content="", is_final=True)


class MockStreamAdapter(StreamAdapter):
    """Adapter for mock/simple streaming."""

    def adapt(self, raw_stream: Any) -> Generator[StreamChunk, None, None]:
        """Adapt mock stream."""
        for content in raw_stream:
            yield StreamChunk(content=content)
        yield StreamChunk(content="", is_final=True)
