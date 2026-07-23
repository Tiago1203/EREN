"""
PHASE 5 - EPIC 1: Multi-Agent Orchestrator

Orquestador multiagente que conecta todos los EPICs en un flujo funcional.
Este componente implementa la concatenación real entre EPICs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional
import logging
import uuid

if TYPE_CHECKING:
    from core.PHASE_5.foundation import Agent
    from core.PHASE_5.foundation.domain import AgentTask, AgentResult

from core.PHASE_5.foundation import (
    BaseAgent,
    AgentState,
    AgentType,
    AgentCapability,
    AgentCapabilityVO,
    AgentBus,
    AgentBusConfig,
    AgentRegistry,
    AgentLookup,
    InMemoryAgentRepository,
)
from core.PHASE_5.foundation.types import (
    AgentPriority,
    MessageType,
)
from core.PHASE_5.foundation.gateways.real import (
    MultiPhaseGateway,
)

logger = logging.getLogger(__name__)


# =============================================================================
# EPIC CONNECTION - Conexión a un EPIC
# =============================================================================

@dataclass
class EpicConnection:
    """Conexión a un EPIC."""
    epic_id: str
    epic_name: str
    agent_type: str
    agent_instance: "Agent | None" = None
    enabled: bool = True
    priority: int = 5
    capability: AgentCapability | None = None


# =============================================================================
# EPIC REGISTRY - Registro de EPICs
# =============================================================================

class EpicRegistry:
    """Registro de EPICs conectados al orquestador."""
    
    def __init__(self):
        self.connections: dict[str, EpicConnection] = {}
        self._agent_registry = AgentRegistry()
        self._lookup = AgentLookup(self._agent_registry)
    
    def register(
        self,
        epic_id: str,
        epic_name: str,
        agent_type: str,
        capability: AgentCapability | None = None,
        priority: int = 5,
    ) -> None:
        """Registra un EPIC."""
        self.connections[epic_id] = EpicConnection(
            epic_id=epic_id,
            epic_name=epic_name,
            agent_type=agent_type,
            capability=capability,
            priority=priority,
        )
        logger.info(f"Registered EPIC: {epic_name} ({epic_id})")
    
    def get_enabled(self) -> list[EpicConnection]:
        """Obtiene EPICs habilitados."""
        return [c for c in self.connections.values() if c.enabled]
    
    def get_by_priority(self) -> list[EpicConnection]:
        """Obtiene EPICs ordenados por prioridad."""
        return sorted(self.get_enabled(), key=lambda c: c.priority, reverse=True)
    
    async def register_agent(self, agent: "Agent") -> bool:
        """Registra un agente en el AgentRegistry."""
        return await self._agent_registry.register(agent)
    
    async def discover_agent(self, capability: AgentCapability) -> list["Agent"]:
        """Descubre agentes por capability."""
        return await self._agent_registry.get_by_capability(capability)


# =============================================================================
# EXECUTION RESULT - Resultado de ejecución
# =============================================================================

@dataclass
class ExecutionResult:
    """Resultado de ejecución de un EPIC."""
    epic_id: str
    epic_name: str
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# MULTI-AGENT ORCHESTRATOR - Orquestador multiagente
# =============================================================================

class MultiAgentOrchestrator:
    """
    Orquestador multiagente que conecta todos los EPICs en un flujo funcional.
    
    Responsabilidades:
    - Registrar todos los EPICs
    - Dirigir tareas al EPIC correcto
    - Coordinar flujo entre EPICs
    - Agregar resultados
    
    Flujo:
    ```
    MultiAgentOrchestrator
            │
            ├── EPIC 2 (Biomedical Agent) ──► Resultado
            │         │
            │         └── EPIC 3 (Diagnostic Agent) ──► Resultado
            │                   │
            │                   └── EPIC 4 (Knowledge Agent) ──► Resultado
            │                             │
            │                             └── EPIC 5 (Research Agent) ──► Resultado
            │                                       │
            │                                       └── EPIC 6 (Planning Agent) ──► Resultado
            │                                                 │
            │                                                 └── EPIC 7 (Collaboration) ──► Resultado
            │                                                           │
            │                                                           └── EPIC 8 (Consensus) ──► Resultado
            │                                                                     │
            │                                                                     └── EPIC 9 (Memory) ──► Resultado
            │                                                                               │
            │                                                                               └── EPIC 10 (Learning) ──► Resultado
            │                                                                                         │
            │                                                                                         └── EPIC 11 (Governance) ──► Resultado Final
    ```
    """
    
    def __init__(self, name: str = "MultiAgentOrchestrator"):
        self.name = name
        self.orchestrator_id = str(uuid.uuid4())
        
        # EPIC Registry
        self._epic_registry = EpicRegistry()
        
        # Agent Bus para comunicación
        self._bus = AgentBus(AgentBusConfig(enable_routing=True))
        
        # Repository para persistencia
        self._repository = InMemoryAgentRepository()
        
        # Gateway para integración con otras fases
        self._gateway = MultiPhaseGateway()
        
        # Resultados de ejecución
        self._execution_results: dict[str, list[ExecutionResult]] = {}
        
        # Inicializar EPICs
        self._initialize_epics()
        
        # Estado
        self._initialized = False
    
    def _initialize_epics(self) -> None:
        """Inicializa el registro de EPICs."""
        # EPIC 1 - Orchestrator (este componente)
        self._epic_registry.register(
            "epic_1",
            "Agent Orchestrator",
            "orchestrator",
            capability=AgentCapability.COORDINATE,
            priority=10,
        )
        
        # EPIC 2 - Biomedical Agent
        self._epic_registry.register(
            "epic_2",
            "Biomedical Agent",
            "biomedical",
            capability=AgentCapability.ANALYZE,
            priority=8,
        )
        
        # EPIC 3 - Diagnostic Agent
        self._epic_registry.register(
            "epic_3",
            "Diagnostic Agent",
            "diagnostic",
            capability=AgentCapability.DIAGNOSE,
            priority=7,
        )
        
        # EPIC 4 - Knowledge Agent
        self._epic_registry.register(
            "epic_4",
            "Knowledge Agent",
            "knowledge",
            capability=AgentCapability.REASON,
            priority=7,
        )
        
        # EPIC 5 - Research Agent
        self._epic_registry.register(
            "epic_5",
            "Research Agent",
            "research",
            capability=AgentCapability.RESEARCH,
            priority=6,
        )
        
        # EPIC 6 - Planning Agent
        self._epic_registry.register(
            "epic_6",
            "Planning Agent",
            "planning",
            capability=AgentCapability.PLAN,
            priority=6,
        )
        
        # EPIC 7 - Collaboration Engine
        self._epic_registry.register(
            "epic_7",
            "Collaboration Engine",
            "collaboration",
            capability=AgentCapability.COLLABORATE,
            priority=5,
        )
        
        # EPIC 8 - Consensus Engine
        self._epic_registry.register(
            "epic_8",
            "Consensus Engine",
            "consensus",
            capability=AgentCapability.NEGOTIATE,
            priority=5,
        )
        
        # EPIC 9 - Agent Memory Engine
        self._epic_registry.register(
            "epic_9",
            "Agent Memory Engine",
            "memory",
            capability=AgentCapability.MEMORIZE,
            priority=4,
        )
        
        # EPIC 10 - Agent Learning & Optimization
        self._epic_registry.register(
            "epic_10",
            "Agent Learning",
            "learning",
            capability=AgentCapability.LEARN,
            priority=4,
        )
        
        # EPIC 11 - Multi-Agent Governance
        self._epic_registry.register(
            "epic_11",
            "Multi-Agent Governance",
            "governance",
            capability=AgentCapability.GOVERN,
            priority=3,
        )
        
        logger.info(f"Initialized {len(self._epic_registry.connections)} EPICs")
    
    async def initialize(self) -> None:
        """Inicializa el orquestador."""
        if self._initialized:
            return
        
        # Inicializar gateway
        await self._gateway.initialize_all()
        
        self._initialized = True
        logger.info("MultiAgentOrchestrator initialized")
    
    async def execute_task(
        self,
        task_type: str,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ejecuta una tarea orquestando los EPICs.
        
        Args:
            task_type: Tipo de tarea
            input_data: Datos de entrada
        
        Returns:
            Resultado combinado de todos los EPICs
        """
        if not self._initialized:
            await self.initialize()
        
        # Determinar flujo de EPICs
        epic_flow = self._determine_epic_flow(task_type)
        
        logger.info(f"Executing task '{task_type}' with EPICs: {epic_flow}")
        
        results: list[ExecutionResult] = []
        context = input_data.copy()
        
        # Ejecutar cada EPIC en secuencia
        for epic_id in epic_flow:
            epic = self._epic_registry.connections.get(epic_id)
            if not epic or not epic.enabled:
                continue
            
            logger.info(f"Executing EPIC: {epic.epic_name}")
            
            # Ejecutar el EPIC (simulado)
            result = await self._execute_epic(epic, context)
            results.append(result)
            
            # Agregar resultado al contexto para el siguiente EPIC
            context[f"{epic_id}_result"] = result.output
            context[f"{epic_id}_success"] = result.success
            
            if not result.success:
                logger.warning(f"EPIC {epic.epic_name} failed: {result.error}")
        
        # Guardar resultados
        session_id = str(uuid.uuid4())
        self._execution_results[session_id] = results
        
        # Combinar resultados
        final_output = self._combine_results(results, context)
        
        return {
            "session_id": session_id,
            "task_type": task_type,
            "epics_executed": [r.epic_id for r in results],
            "success": all(r.success for r in results),
            "results": {
                r.epic_id: r.output for r in results
            },
            "final_output": final_output,
            "execution_count": len(results),
        }
    
    async def _execute_epic(
        self,
        epic: EpicConnection,
        context: dict[str, Any],
    ) -> ExecutionResult:
        """Ejecuta un EPIC individual."""
        start_time = datetime.now(UTC)
        
        try:
            # Enviar mensaje al EPIC via bus
            await self._bus.send(
                sender=self.orchestrator_id,
                receiver=epic.epic_id,
                action="execute",
                payload={
                    "context": context,
                    "epic_id": epic.epic_id,
                },
            )
            
            # Simular procesamiento
            output = await self._process_epic(epic, context)
            
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            
            return ExecutionResult(
                epic_id=epic.epic_id,
                epic_name=epic.epic_name,
                success=True,
                output=output,
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            return ExecutionResult(
                epic_id=epic.epic_id,
                epic_name=epic.epic_name,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
            )
    
    async def _process_epic(
        self,
        epic: EpicConnection,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Procesa un EPIC específico."""
        # Simular procesamiento basado en el tipo de EPIC
        epic_id = epic.epic_id
        
        if epic_id == "epic_2":  # Biomedical
            return {
                "analysis": "Biomedical analysis completed",
                "devices_found": 5,
                "recommendations": ["Check calibration", "Schedule maintenance"],
            }
        
        elif epic_id == "epic_3":  # Diagnostic
            return {
                "diagnosis": "Diagnostic analysis completed",
                "confidence": 0.85,
                "possible_causes": ["Wear", "Calibration drift"],
            }
        
        elif epic_id == "epic_4":  # Knowledge
            return {
                "knowledge_found": True,
                "articles": ["Article 1", "Article 2"],
                "standards": ["IEC 60601", "ISO 13485"],
            }
        
        elif epic_id == "epic_5":  # Research
            return {
                "research_completed": True,
                "papers_found": 10,
                "evidence_level": "high",
            }
        
        elif epic_id == "epic_6":  # Planning
            return {
                "plan_created": True,
                "actions": ["Action 1", "Action 2"],
                "schedule": "2026-07-24",
            }
        
        elif epic_id == "epic_7":  # Collaboration
            return {
                "collaboration_done": True,
                "agents_involved": ["Agent A", "Agent B"],
            }
        
        elif epic_id == "epic_8":  # Consensus
            return {
                "consensus_reached": True,
                "agreement_level": 0.9,
                "votes": {"Agent A": "yes", "Agent B": "yes"},
            }
        
        elif epic_id == "epic_9":  # Memory
            return {
                "memory_stored": True,
                "memory_type": "episodic",
                "recall_confidence": 0.85,
            }
        
        elif epic_id == "epic_10":  # Learning
            return {
                "learning_completed": True,
                "improvements": ["Better accuracy", "Faster response"],
                "metrics_improved": 2,
            }
        
        elif epic_id == "epic_11":  # Governance
            return {
                "governance_applied": True,
                "policies_compliant": True,
                "audit_trail": ["Step 1", "Step 2"],
            }
        
        return {"status": "processed"}
    
    def _determine_epic_flow(self, task_type: str) -> list[str]:
        """Determina el flujo de EPICs basado en el tipo de tarea."""
        task_type = task_type.lower()
        
        # Flujo completo para tareas complejas
        full_flow = [
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
        
        # Flujos específicos
        if "biomedical" in task_type or "equipment" in task_type:
            return ["epic_2", "epic_11"]
        
        if "diagnostic" in task_type or "diagnosis" in task_type:
            return ["epic_2", "epic_3", "epic_11"]
        
        if "knowledge" in task_type or "search" in task_type:
            return ["epic_4", "epic_11"]
        
        if "research" in task_type or "evidence" in task_type:
            return ["epic_4", "epic_5", "epic_11"]
        
        if "planning" in task_type or "schedule" in task_type:
            return ["epic_6", "epic_11"]
        
        if "collaboration" in task_type or "consensus" in task_type:
            return ["epic_7", "epic_8", "epic_11"]
        
        if "memory" in task_type or "learning" in task_type:
            return ["epic_9", "epic_10", "epic_11"]
        
        if "governance" in task_type or "policy" in task_type:
            return ["epic_11"]
        
        # Flujo completo por defecto
        return full_flow
    
    def _combine_results(
        self,
        results: list[ExecutionResult],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Combina resultados de múltiples EPICs."""
        return {
            "total_epics": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "total_time_ms": sum(r.execution_time_ms for r in results),
            "context": context,
        }
    
    def get_epic_status(self) -> dict[str, Any]:
        """Obtiene estado de todos los EPICs."""
        return {
            epic_id: {
                "name": epic.epic_name,
                "enabled": epic.enabled,
                "priority": epic.priority,
                "capability": epic.capability.value if epic.capability else None,
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
    
    def get_execution_history(self, session_id: str) -> list[ExecutionResult]:
        """Obtiene historial de ejecución."""
        return self._execution_results.get(session_id, [])
    
    async def discover_agents(self, capability: str) -> list[dict[str, Any]]:
        """Descubre agentes por capability."""
        try:
            cap = AgentCapability(capability.lower())
            agents = await self._epic_registry.discover_agent(cap)
            return [
                {
                    "agent_id": a.agent_id,
                    "type": a.agent_type.value,
                    "state": a.state.value,
                }
                for a in agents
            ]
        except ValueError:
            return []
    
    def get_bus_stats(self) -> dict[str, Any]:
        """Obtiene estadísticas del bus."""
        return self._bus.get_stats()
    
    def get_stats(self) -> dict[str, Any]:
        """Obtiene estadísticas del orquestador."""
        return {
            "orchestrator_id": self.orchestrator_id,
            "epics_count": len(self._epic_registry.connections),
            "enabled_epics": len(self._epic_registry.get_enabled()),
            "bus_stats": self._bus.get_stats(),
            "initialized": self._initialized,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MultiAgentOrchestrator",
    "EpicRegistry",
    "EpicConnection",
    "ExecutionResult",
]
