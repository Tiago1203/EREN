"""
PHASE 5 - EPIC 1: Task Dispatcher

Componente que dispatcha tareas a agentes.
Gestiona la distribución de trabajo y selección de agentes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM PHASE 5 FOUNDATION
# =============================================================================

from core.PHASE_5.foundation import (
    AgentRegistry,
    MessageBroker,
    AgentLookup,
    BaseAgent,
    AgentTask,
    AgentResult,
    AgentCapability,
    AgentState,
)

# =============================================================================
# IMPORTS FROM DOMAIN
# =============================================================================

from core.PHASE_5.epic1_orchestrator.domain import (
    AgentExecution,
    ExecutionResult,
    ExecutionStatus,
)


# =============================================================================
# DISPATCH STRATEGY
# =============================================================================

class DispatchStrategy(str, Enum):
    """Estrategia de dispatch."""
    DIRECT = "direct"                 # Envía directamente al agente
    QUEUE = "queue"                   # Cola el mensaje
    BALANCED = "balanced"             # Balancea carga
    AFFINITY = "affinity"             # Afinidad con agente específico


# =============================================================================
# TASK DISPATCHER
# =============================================================================

class TaskDispatcher:
    """
    Dispatcher de tareas a agentes.
    
    Responsabilidades:
    1. Seleccionar agente apropiado
    2. Crear tarea para el agente
    3. Enviar a través del message broker
    4. Manejar retry y timeout
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        broker: MessageBroker,
        config: Any | None = None,
    ):
        self.registry = registry
        self.broker = broker
        self.config = config
        self.lookup = AgentLookup(registry)
        
        # Estado
        self._dispatch_count = 0
        self._success_count = 0
        self._failure_count = 0
    
    async def dispatch(
        self,
        execution: AgentExecution,
        agent: BaseAgent,
        strategy: DispatchStrategy = DispatchStrategy.DIRECT,
    ) -> ExecutionResult | None:
        """
        Dispatcha una ejecución a un agente.
        
        Args:
            execution: Definición de la ejecución
            agent: Agente seleccionado
            strategy: Estrategia de dispatch
        
        Returns:
            ExecutionResult con el resultado de la ejecución
        """
        from datetime import UTC, datetime
        
        self._dispatch_count += 1
        
        logger.info(f"Dispatching execution {execution.execution_id} to agent {agent.agent_id}")
        
        execution.agent_id = agent.agent_id
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now(UTC)
        
        try:
            if strategy == DispatchStrategy.DIRECT:
                result = await self._dispatch_direct(execution, agent)
            elif strategy == DispatchStrategy.QUEUE:
                result = await self._dispatch_queue(execution, agent)
            elif strategy == DispatchStrategy.BALANCED:
                result = await self._dispatch_balanced(execution, agent)
            else:
                result = await self._dispatch_direct(execution, agent)
            
            if result and result.success:
                self._success_count += 1
            else:
                self._failure_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Dispatch failed for {execution.execution_id}: {e}")
            self._failure_count += 1
            
            return ExecutionResult(
                execution_id=execution.execution_id,
                success=False,
                error=str(e),
            )
    
    async def _dispatch_direct(
        self,
        execution: AgentExecution,
        agent: BaseAgent,
    ) -> ExecutionResult | None:
        """Dispatch directo - ejecuta inmediatamente."""
        
        from datetime import UTC, datetime
        
        # Crear tarea
        task = AgentTask(
            task_id=execution.execution_id,
            agent_id=agent.agent_id,
            task_type=execution.task_type,
            description=f"Task from orchestrator for {execution.task_type}",
            input_data=execution.task_input,
            timeout_seconds=execution.timeout_seconds,
        )
        
        # Ejecutar
        try:
            result = await agent.execute(task)
            
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.now(UTC)
            execution.result = result
            
            return ExecutionResult(
                execution_id=execution.execution_id,
                success=result.success,
                output=result.output,
                execution_time_ms=result.execution_time_ms,
                confidence=result.confidence,
                tokens_used=result.tokens_used,
            )
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            
            execution.status = ExecutionStatus.FAILED
            execution.completed_at = datetime.now(UTC)
            
            return ExecutionResult(
                execution_id=execution.execution_id,
                success=False,
                error=str(e),
            )
    
    async def _dispatch_queue(
        self,
        execution: AgentExecution,
        agent: BaseAgent,
    ) -> ExecutionResult | None:
        """Dispatch a través de cola de mensajes."""
        
        from datetime import UTC, datetime
        from core.PHASE_5.foundation import AgentMessage, MessageType, AgentPriority
        
        # Crear mensaje de tarea
        message = AgentMessage(
            message_id=str(datetime.now(UTC).timestamp()),
            sender="orchestrator",
            receiver=agent.agent_id,
            type=MessageType.REQUEST,
            action="execute_task",
            payload={
                "execution_id": execution.execution_id,
                "task_type": execution.task_type,
                "input": execution.task_input,
                "timeout": execution.timeout_seconds,
            },
            priority=AgentPriority.MEDIUM,
            ttl=execution.timeout_seconds,
        )
        
        # Enviar a cola
        await self.broker.send(message)
        
        # Esperar respuesta
        response = await self.broker.send_and_wait(
            message,
            timeout=execution.timeout_seconds,
        )
        
        if response:
            return ExecutionResult(
                execution_id=execution.execution_id,
                success=response.payload.get("success", True),
                output=response.payload.get("output", {}),
                error=response.payload.get("error"),
            )
        
        return ExecutionResult(
            execution_id=execution.execution_id,
            success=False,
            error="Timeout waiting for response",
        )
    
    async def _dispatch_balanced(
        self,
        execution: AgentExecution,
        agent: BaseAgent,
    ) -> ExecutionResult | None:
        """Dispatch con balanceo de carga."""
        
        # Por ahora, usar dispatch directo
        # En el futuro,可以选择 agente con menor carga
        return await self._dispatch_direct(execution, agent)
    
    async def dispatch_batch(
        self,
        executions: list[AgentExecution],
        strategy: DispatchStrategy = DispatchStrategy.DIRECT,
    ) -> list[ExecutionResult]:
        """Dispatch múltiples executions."""
        
        import asyncio
        
        tasks = []
        for execution in executions:
            # Obtener agente para cada ejecución
            agents = await self.registry.get_by_type(execution.agent_type)
            if agents:
                agent = agents[0]
                tasks.append(self.dispatch(execution, agent, strategy))
            else:
                tasks.append(
                    self._create_failed_result(
                        execution,
                        f"No agent of type {execution.agent_type}",
                    )
                )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if not isinstance(r, Exception) else self._create_failed_result(ex, str(r))
            for r, ex in zip(results, executions)
        ]
    
    async def select_best_agent(
        self,
        execution: AgentExecution,
    ) -> BaseAgent | None:
        """Selecciona el mejor agente para una ejecución."""
        
        # Intentar por capability
        capabilities = [
            AgentCapability(cap)
            for cap in execution.task_input.get("required_capabilities", [])
        ]
        
        if capabilities:
            agent = await self.lookup.find_best_for_task(capabilities)
            if agent:
                return agent
        
        # Fallback: cualquier agente del tipo
        agents = await self.registry.get_by_type(execution.agent_type)
        available = [a for a in agents if a.is_available]
        
        if available:
            return available[0]
        
        return None
    
    def _create_failed_result(
        self,
        execution: AgentExecution,
        error: str,
    ) -> ExecutionResult:
        """Crea un resultado fallido."""
        
        return ExecutionResult(
            execution_id=execution.execution_id,
            success=False,
            error=error,
        )
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del dispatcher."""
        
        return {
            "total_dispatches": self._dispatch_count,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "success_rate": (
                self._success_count / self._dispatch_count
                if self._dispatch_count > 0
                else 0.0
            ),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TaskDispatcher",
    "DispatchStrategy",
]
