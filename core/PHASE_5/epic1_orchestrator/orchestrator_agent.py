"""
PHASE 5 - EPIC 1: Orchestrator Agent

Agente orquestador que conecta todos los EPICs en un flujo unificado.
Este componente resuelve el problema de concatenación entre EPICs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging
import uuid

from core.PHASE_5.foundation import (
    BaseAgent,
    AgentState,
    AgentType,
    AgentCapability,
    AgentCapabilityVO,
    AgentTask,
    AgentResult,
    AgentBus,
    AgentBusConfig,
    AgentRegistry,
)
from core.PHASE_5.foundation.types import (
    AgentPriority,
    MessageType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# EPIC REGISTRY - Registro de EPICs conectados
# =============================================================================

@dataclass
class EpicConnection:
    """Conexión a un EPIC."""
    epic_id: str
    epic_name: str
    agent_class: type[BaseAgent] | None = None
    instance: BaseAgent | None = None
    enabled: bool = True
    priority: int = 5  # 1-10


@dataclass
class EpicRegistry:
    """Registro de EPICs conectados al orquestador."""
    connections: dict[str, EpicConnection] = field(default_factory=dict)
    
    def register(
        self,
        epic_id: str,
        epic_name: str,
        agent_class: type[BaseAgent] | None = None,
        priority: int = 5,
    ) -> None:
        """Registra un EPIC."""
        self.connections[epic_id] = EpicConnection(
            epic_id=epic_id,
            epic_name=epic_name,
            agent_class=agent_class,
            priority=priority,
        )
        logger.info(f"Registered EPIC: {epic_name} ({epic_id})")
    
    def get_enabled(self) -> list[EpicConnection]:
        """Obtiene EPICs habilitados."""
        return [c for c in self.connections.values() if c.enabled]
    
    def get_by_priority(self) -> list[EpicConnection]:
        """Obtiene EPICs ordenados por prioridad."""
        return sorted(
            self.get_enabled(),
            key=lambda c: c.priority,
            reverse=True,
        )


# =============================================================================
# ORCHESTRATOR AGENT - Agente principal de orquestación
# =============================================================================

class OrchestratorAgent(BaseAgent):
    """
    Agente orquestador que conecta todos los EPICs.
    
    Responsabilidades:
    - Registrar todos los EPICs (1-11)
    - Dirigir tareas al EPIC correcto
    - Coordinar flujo entre EPICs
    - Agregar resultados
    
    Flujo:
    ```
    EPIC 1 (Orchestrator) 
        │
        ├──► EPIC 2 (Biomedical Agent)
        │         │
        │         └──► EPIC 3 (Diagnostic Agent)
        │                   │
        │                   └──► EPIC 4 (Knowledge Agent)
        │                             │
        │                             └──► EPIC 5 (Research Agent)
        │                                       │
        │                                       └──► EPIC 6 (Planning Agent)
        │                                                 │
        │                                                 └──► EPIC 7 (Collaboration)
        │                                                           │
        │                                                           └──► EPIC 8 (Consensus)
        │                                                                     │
        │                                                                     └──► EPIC 9 (Memory)
        │                                                                               │
        │                                                                               └──► EPIC 10 (Learning)
        │                                                                                         │
        │                                                                                         └──► EPIC 11 (Governance)
    ```
    """
    
    def __init__(self, agent_id: str = ""):
        super().__init__(
            agent_id=agent_id or str(uuid.uuid4()),
            agent_type=AgentType.ORCHESTRATOR,
            name="OrchestratorAgent",
            description="Agente orquestador que coordina todos los EPICs",
            capabilities=[
                AgentCapabilityVO(capability=AgentCapability.COORDINATE, level=1.0),
                AgentCapabilityVO(capability=AgentCapability.MONITOR, level=0.9),
            ],
        )
        
        # EPIC Registry
        self._epic_registry = EpicRegistry()
        
        # Agent Bus para comunicación
        self._bus = AgentBus()
        
        # Agent Registry (Foundation)
        self._agent_registry: AgentRegistry | None = None
        
        # Task queue
        self._pending_tasks: list[AgentTask] = []
        
        # Results aggregation
        self._aggregation_enabled = True
        
        # Flujo habilitado
        self._flow_enabled = True
        
        # Inicializar EPICs
        self._initialize_epics()
    
    def _initialize_epics(self) -> None:
        """Inicializa el registro de EPICs."""
        # EPIC 0 - Foundation (ya incluido en BaseAgent)
        
        # EPIC 1 - Orchestrator (este agente)
        self._epic_registry.register("epic_1", "Agent Orchestrator", priority=10)
        
        # EPIC 2 - Biomedical Agent
        self._epic_registry.register("epic_2", "Biomedical Agent", priority=8)
        
        # EPIC 3 - Diagnostic Agent
        self._epic_registry.register("epic_3", "Diagnostic Agent", priority=7)
        
        # EPIC 4 - Knowledge Agent
        self._epic_registry.register("epic_4", "Knowledge Agent", priority=7)
        
        # EPIC 5 - Research Agent
        self._epic_registry.register("epic_5", "Research Agent", priority=6)
        
        # EPIC 6 - Planning Agent
        self._epic_registry.register("epic_6", "Planning Agent", priority=6)
        
        # EPIC 7 - Collaboration Engine
        self._epic_registry.register("epic_7", "Collaboration Engine", priority=5)
        
        # EPIC 8 - Consensus Engine
        self._epic_registry.register("epic_8", "Consensus Engine", priority=5)
        
        # EPIC 9 - Agent Memory Engine
        self._epic_registry.register("epic_9", "Agent Memory Engine", priority=4)
        
        # EPIC 10 - Agent Learning & Optimization
        self._epic_registry.register("epic_10", "Agent Learning & Optimization", priority=4)
        
        # EPIC 11 - Multi-Agent Governance
        self._epic_registry.register("epic_11", "Multi-Agent Governance", priority=3)
        
        logger.info(f"Initialized {len(self._epic_registry.connections)} EPICs")
    
    async def initialize(self) -> None:
        """Inicializa el orquestador."""
        await super().initialize()
        
        # Registrar en Agent Registry si existe
        if self._agent_registry:
            await self._agent_registry.register(self)
        
        # Registrar handler en bus
        self._bus.register_handler(self.agent_id, self._handle_bus_message)
        
        self._state = AgentState.IDLE
        logger.info("OrchestratorAgent initialized")
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea orquestando los EPICs."""
        self._state = AgentState.RUNNING
        self.current_task_id = task.task_id
        
        results = {}
        
        try:
            # Determinar flujo de EPICs basado en el tipo de tarea
            epic_flow = self._determine_epic_flow(task)
            
            # Ejecutar cada EPIC en secuencia
            for epic_id in epic_flow:
                epic = self._epic_registry.connections.get(epic_id)
                if not epic or not epic.enabled:
                    continue
                
                logger.info(f"Executing EPIC: {epic.epic_name}")
                
                # Enviar tarea al EPIC via bus
                await self._bus.send(
                    sender=self.agent_id,
                    receiver=f"{epic_id}_agent",
                    action="execute_task",
                    payload={
                        "task": task.to_dict() if hasattr(task, 'to_dict') else {"task_id": task.task_id},
                        "previous_results": results,
                    },
                )
                
                # Placeholder: En producción, esperar resultado
                # result = await self._wait_for_result(epic_id)
                # results[epic_id] = result
                results[epic_id] = {"status": "executed"}
            
            # Agregar resultados si está habilitado
            if self._aggregation_enabled:
                aggregated = await self._aggregate_results(results)
                output = aggregated
            else:
                output = results
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=output,
            )
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
            )
        finally:
            self._state = AgentState.IDLE
            self.current_task_id = None
    
    def _determine_epic_flow(self, task: AgentTask) -> list[str]:
        """
        Determina el flujo de EPICs basado en el tipo de tarea.
        
        Flujo predeterminado:
        1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11
        """
        task_type = task.task_type.lower()
        
        # Flujo completo para tareas complejas
        full_flow = [
            "epic_1",   # Orchestrator
            "epic_2",   # Biomedical
            "epic_3",   # Diagnostic
            "epic_4",   # Knowledge
            "epic_5",   # Research
            "epic_6",   # Planning
            "epic_7",   # Collaboration
            "epic_8",   # Consensus
            "epic_9",   # Memory
            "epic_10",  # Learning
            "epic_11",  # Governance
        ]
        
        # Flujo parcial para tareas específicas
        if "biomedical" in task_type or "equipment" in task_type:
            return ["epic_1", "epic_2", "epic_11"]
        
        if "diagnostic" in task_type or "diagnosis" in task_type:
            return ["epic_1", "epic_2", "epic_3", "epic_11"]
        
        if "knowledge" in task_type or "search" in task_type:
            return ["epic_1", "epic_4", "epic_11"]
        
        if "research" in task_type or "evidence" in task_type:
            return ["epic_1", "epic_4", "epic_5", "epic_11"]
        
        if "planning" in task_type or "schedule" in task_type:
            return ["epic_1", "epic_6", "epic_11"]
        
        if "collaboration" in task_type or "consensus" in task_type:
            return ["epic_1", "epic_7", "epic_8", "epic_11"]
        
        if "memory" in task_type or "learning" in task_type:
            return ["epic_1", "epic_9", "epic_10", "epic_11"]
        
        if "governance" in task_type or "policy" in task_type:
            return ["epic_1", "epic_11"]
        
        # Flujo completo por defecto
        return full_flow
    
    async def _aggregate_results(self, results: dict) -> dict:
        """Agrega resultados de múltiples EPICs."""
        return {
            "aggregated": True,
            "epic_count": len(results),
            "results": results,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    
    async def _handle_bus_message(self, message: Any) -> None:
        """Maneja mensajes del bus."""
        logger.info(f"Orchestrator received message: {message}")
    
    def get_epic_status(self) -> dict:
        """Obtiene estado de todos los EPICs."""
        return {
            epic_id: {
                "name": epic.epic_name,
                "enabled": epic.enabled,
                "priority": epic.priority,
            }
            for epic_id, epic in self._epic_registry.connections.items()
        }
    
    def enable_epic(self, epic_id: str) -> bool:
        """Habilita un EPIC."""
        if epic_id in self._epic_registry.connections:
            self._epic_registry.connections[epic_id].enabled = True
            return True
        return False
    
    def disable_epic(self, epic_id: str) -> bool:
        """Deshabilita un EPIC."""
        if epic_id in self._epic_registry.connections:
            self._epic_registry.connections[epic_id].enabled = False
            return True
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "EpicConnection",
    "EpicRegistry",
    "OrchestratorAgent",
]
