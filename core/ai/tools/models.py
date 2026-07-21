"""Tool Models - Modelos de herramientas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, TypeVar


class ToolCategory(str, Enum):
    """Categorías de herramientas."""
    DATABASE = "database"       # PostgreSQL, MySQL, etc.
    VECTOR_STORE = "vector"     # Qdrant, Pinecone, etc.
    MESSAGE_QUEUE = "queue"     # RabbitMQ, Kafka, etc.
    API = "api"                 # Llamadas a APIs
    CODE = "code"               # Ejecución de código
    WEB = "web"                 # Internet, HTTP
    FILE = "file"               # Sistema de archivos
    SYSTEM = "system"           # Comandos del sistema
    MCP = "mcp"                 # Model Context Protocol


class ToolCapability(str, Enum):
    """Capacidades de las herramientas."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SEARCH = "search"
    EXECUTE = "execute"
    STREAM = "stream"
    TRANSACT = "transact"


@dataclass
class ToolParameter:
    """Parámetro de una herramienta."""
    name: str
    type: str  # string, int, float, bool, list, dict, object
    description: str = ""
    required: bool = True
    default: Any = None
    validation: dict[str, Any] | None = None


@dataclass
class ToolDefinition:
    """Definición de una herramienta."""
    id: str
    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    
    # Parámetros
    parameters: list[ToolParameter] = field(default_factory=list)
    
    # Capacidades
    capabilities: list[ToolCapability] = field(default_factory=list)
    
    # Configuración
    enabled: bool = True
    requires_auth: bool = False
    requires_sandbox: bool = False
    
    # Metadatos
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Implementación
    handler: Any = field(default=None, repr=False)
    
    def get_parameter(self, name: str) -> ToolParameter | None:
        """Obtiene un parámetro por nombre."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None
    
    def validate_parameters(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Valida los parámetros proporcionados."""
        errors = []
        
        for param in self.parameters:
            if param.required and param.name not in params:
                errors.append(f"Parámetro requerido: {param.name}")
        
        for name, value in params.items():
            param = self.get_parameter(name)
            if not param:
                continue
            
            # Validación de tipo
            expected_type = param.type
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"{name} debe ser string")
            elif expected_type == "int" and not isinstance(value, int):
                errors.append(f"{name} debe ser int")
            elif expected_type == "float" and not isinstance(value, (int, float)):
                errors.append(f"{name} debe ser float")
            elif expected_type == "bool" and not isinstance(value, bool):
                errors.append(f"{name} debe ser bool")
            elif expected_type == "list" and not isinstance(value, list):
                errors.append(f"{name} debe ser list")
            elif expected_type == "dict" and not isinstance(value, dict):
                errors.append(f"{name} debe ser dict")
        
        return len(errors) == 0, errors


class ToolStatus(str, Enum):
    """Estado de ejecución de herramienta."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ToolExecution:
    """Ejecución de una herramienta."""
    id: str
    tool_id: str
    tool_name: str
    
    # Parámetros de ejecución
    parameters: dict[str, Any]
    
    # Estado
    status: ToolStatus = ToolStatus.PENDING
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    
    # Resultado
    result: Any = None
    error: str | None = None
    
    # Metadatos
    user_id: str | None = None
    session_id: str | None = None
    tenant_id: str | None = None
    execution_time_ms: float = 0.0
    
    # Contexto
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Resultado de una ejecución."""
    execution_id: str
    tool_id: str
    status: ToolStatus
    
    # Datos
    data: Any = None
    error: str | None = None
    
    # Metadatos
    execution_time_ms: float = 0.0
    tokens_used: int = 0
    
    @property
    def success(self) -> bool:
        return self.status == ToolStatus.COMPLETED
    
    @property
    def data_as_text(self) -> str:
        """Convierte los datos a texto."""
        if self.data is None:
            return ""
        if isinstance(self.data, str):
            return self.data
        import json
        return json.dumps(self.data, indent=2, default=str)


@dataclass
class ToolConfig:
    """Configuración del sistema de herramientas."""
    # Límites
    max_concurrent: int = 10
    timeout_seconds: int = 30
    max_retries: int = 3
    
    # Seguridad
    enable_sandbox: bool = True
    allowed_paths: list[str] = field(default_factory=list)
    blocked_commands: list[str] = field(default_factory=list)
    
    # Cache
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000


class ToolInterface(ABC):
    """Interfaz abstracta para herramientas."""
    
    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Definición de la herramienta."""
        ...
    
    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> Any:
        """Ejecuta la herramienta."""
        ...
    
    @abstractmethod
    def validate_params(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Valida los parámetros."""
        ...
