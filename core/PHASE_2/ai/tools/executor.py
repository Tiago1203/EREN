"""Tool Executor - Ejecutor de herramientas."""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from core.PHASE_2.ai.tools.models import (
    ToolConfig,
    ToolDefinition,
    ToolExecution,
    ToolResult,
    ToolStatus,
)
from core.PHASE_2.ai.tools.registry import ToolRegistry, get_registry


class ToolExecutor:
    """
    Ejecutor de herramientas.
    
    Ejecuta herramientas de forma segura y maneja
    timeouts, reintentos y errores.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        config: ToolConfig | None = None,
    ) -> None:
        self._registry = registry or get_registry()
        self._config = config or ToolConfig()
        self._executions: dict[str, ToolExecution] = {}
        self._semaphore: asyncio.Semaphore | None = None

    @property
    def config(self) -> ToolConfig:
        return self._config

    async def execute(
        self,
        tool_id: str,
        parameters: dict[str, Any],
        user_id: str | None = None,
        session_id: str | None = None,
        tenant_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> ToolResult:
        """
        Ejecuta una herramienta.
        
        Args:
            tool_id: ID de la herramienta
            parameters: Parámetros de ejecución
            user_id: ID del usuario
            session_id: ID de la sesión
            tenant_id: ID del tenant
            context: Contexto adicional
            
        Returns:
            Resultado de la ejecución
        """
        # Obtener herramienta
        tool = self._registry.get(tool_id)
        if not tool:
            return ToolResult(
                execution_id="",
                tool_id=tool_id,
                status=ToolStatus.FAILED,
                error=f"Herramienta {tool_id} no encontrada",
            )
        
        if not tool.enabled:
            return ToolResult(
                execution_id="",
                tool_id=tool_id,
                status=ToolStatus.FAILED,
                error=f"Herramienta {tool_id} está deshabilitada",
            )
        
        # Validar parámetros
        valid, errors = tool.validate_parameters(parameters)
        if not valid:
            return ToolResult(
                execution_id="",
                tool_id=tool_id,
                status=ToolStatus.FAILED,
                error=f"Validación fallida: {errors}",
            )
        
        # Crear ejecución
        execution_id = str(uuid.uuid4())
        execution = ToolExecution(
            id=execution_id,
            tool_id=tool_id,
            tool_name=tool.name,
            parameters=parameters,
            user_id=user_id,
            session_id=session_id,
            tenant_id=tenant_id,
            context=context or {},
        )
        
        self._executions[execution_id] = execution
        
        # Ejecutar con reintentos
        return await self._execute_with_retries(execution, tool)

    async def _execute_with_retries(
        self,
        execution: ToolExecution,
        tool: ToolDefinition,
    ) -> ToolResult:
        """Ejecuta con reintentos."""
        last_error = None
        
        for attempt in range(self._config.max_retries):
            try:
                return await self._do_execute(execution, tool)
            except Exception as e:
                last_error = str(e)
                if attempt < self._config.max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Backoff
        
        # Todos los intentos fallaron
        execution.status = ToolStatus.FAILED
        execution.error = last_error
        
        return ToolResult(
            execution_id=execution.id,
            tool_id=tool.id,
            status=ToolStatus.FAILED,
            error=last_error,
        )

    async def _do_execute(
        self,
        execution: ToolExecution,
        tool: ToolDefinition,
    ) -> ToolResult:
        """Ejecuta la herramienta."""
        start_time = time.time()
        execution.status = ToolStatus.RUNNING
        
        try:
            # Verificar límite de concurrencia
            if self._semaphore is None:
                self._semaphore = asyncio.Semaphore(self._config.max_concurrent)
            
            async with self._semaphore:
                # Obtener implementación
                impl = self._registry.get_implementation(tool.id)
                
                if impl:
                    # Ejecutar implementación async
                    if asyncio.iscoroutinefunction(impl.execute):
                        result = await impl.execute(execution.parameters)
                    else:
                        result = await asyncio.to_thread(impl.execute, execution.parameters)
                else:
                    # Sin implementación - usar handler genérico
                    result = await self._execute_handler(tool, execution.parameters)
                
                execution.status = ToolStatus.COMPLETED
                execution.result = result
                execution.completed_at = execution.started_at
                
                execution_time = (time.time() - start_time) * 1000
                execution.execution_time_ms = execution_time
                
                return ToolResult(
                    execution_id=execution.id,
                    tool_id=tool.id,
                    status=ToolStatus.COMPLETED,
                    data=result,
                    execution_time_ms=execution_time,
                )
        
        except asyncio.TimeoutError:
            execution.status = ToolStatus.TIMEOUT
            execution.error = "Timeout de ejecución"
            execution.completed_at = execution.started_at
            execution.execution_time_ms = (time.time() - start_time) * 1000
            
            return ToolResult(
                execution_id=execution.id,
                tool_id=tool.id,
                status=ToolStatus.TIMEOUT,
                error="Timeout de ejecución",
                execution_time_ms=execution.execution_time_ms,
            )
        
        except Exception as e:
            execution.status = ToolStatus.FAILED
            execution.error = str(e)
            execution.completed_at = execution.started_at
            execution.execution_time_ms = (time.time() - start_time) * 1000
            
            return ToolResult(
                execution_id=execution.id,
                tool_id=tool.id,
                status=ToolStatus.FAILED,
                error=str(e),
                execution_time_ms=execution.execution_time_ms,
            )

    async def _execute_handler(
        self,
        tool: ToolDefinition,
        parameters: dict[str, Any],
    ) -> Any:
        """Ejecuta un handler genérico."""
        handler = tool.handler
        
        if handler is None:
            return {"message": f"Herramienta {tool.name} ejecutada", "params": parameters}
        
        if asyncio.iscoroutinefunction(handler):
            return await handler(parameters)
        else:
            return await asyncio.to_thread(handler, parameters)

    def get_execution(self, execution_id: str) -> ToolExecution | None:
        """Obtiene una ejecución por ID."""
        return self._executions.get(execution_id)

    def list_executions(
        self,
        tool_id: str | None = None,
        status: ToolStatus | None = None,
        limit: int = 100,
    ) -> list[ToolExecution]:
        """Lista ejecuciones."""
        executions = list(self._executions.values())
        
        if tool_id:
            executions = [e for e in executions if e.tool_id == tool_id]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        # Ordenar por más reciente
        executions.sort(key=lambda e: e.started_at, reverse=True)
        
        return executions[:limit]

    def cancel(self, execution_id: str) -> bool:
        """Cancela una ejecución."""
        execution = self._executions.get(execution_id)
        if execution and execution.status == ToolStatus.RUNNING:
            execution.status = ToolStatus.CANCELLED
            return True
        return False


class SyncToolExecutor:
    """Versión síncrona del ejecutor."""

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        config: ToolConfig | None = None,
    ) -> None:
        self._registry = registry or get_registry()
        self._config = config or ToolConfig()

    def execute(
        self,
        tool_id: str,
        parameters: dict[str, Any],
        **kwargs: Any,
    ) -> ToolResult:
        """Ejecuta una herramienta síncronamente."""
        return asyncio.run(
            self._async_execute(tool_id, parameters, **kwargs)
        )

    async def _async_execute(
        self,
        tool_id: str,
        parameters: dict[str, Any],
        **kwargs: Any,
    ) -> ToolResult:
        """Ejecuta de forma async."""
        executor = ToolExecutor(self._registry, self._config)
        return await executor.execute(tool_id, parameters, **kwargs)
