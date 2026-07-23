"""
PHASE 5 - EPIC 1: Orchestrator Engine

Motor principal de orquestación de agentes.
Recibe solicitudes clínicas y coordina la ejecución de agentes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM PHASE 5 FOUNDATION
# =============================================================================

from core.PHASE_5.foundation import (
    AgentRegistry,
    AgentLifecycleManager,
    MessageBroker,
    EventBus,
    AgentLookup,
    BaseAgent,
    AgentTask,
    AgentResult,
    AgentType,
    AgentCapability,
    AgentState,
)
from core.PHASE_5.foundation.domain import AgentContext, AgentSession
from core.PHASE_5.foundation.events import EventFactory, AgentEventType

# =============================================================================
# IMPORTS FROM DOMAIN
# =============================================================================

from core.PHASE_5.epic1_orchestrator.domain import (
    OrchestrationPlan,
    PlanStep,
    Workflow,
    WorkflowStep,
    AgentExecution,
    ExecutionResult,
    ExecutionStatus,
    PlanStatus,
    WorkflowStatus,
    OrchestrationStrategy,
    ExecutionMode,
    AggregationMethod,
)

# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

from core.PHASE_5.epic1_orchestrator.dispatcher import (
    TaskDispatcher,
    DispatchStrategy,
)
from core.PHASE_5.epic1_orchestrator.scheduler import (
    TaskScheduler,
    ScheduleStrategy,
)
from core.PHASE_5.epic1_orchestrator.aggregator import (
    ResponseAggregator,
    AggregationConfig,
)


# =============================================================================
# ORCHESTRATOR CONFIG
# =============================================================================

@dataclass
class OrchestratorConfig:
    """Configuración del orquestador."""
    # Timeouts
    default_timeout_seconds: int = 300
    workflow_timeout_seconds: int = 3600
    
    # Retry
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Execution
    max_concurrent_executions: int = 10
    default_strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL
    default_execution_mode: ExecutionMode = ExecutionMode.SYNC
    default_aggregation: AggregationMethod = AggregationMethod.BEST
    
    # Agent Selection
    enable_agent_fallback: bool = True
    min_confidence_threshold: float = 0.5
    
    # Context
    enable_context_sharing: bool = True
    context_ttl_seconds: int = 3600
    
    # Events
    emit_events: bool = True
    event_bus: EventBus | None = None


# =============================================================================
# ORCHESTRATOR ENGINE - Motor principal
# =============================================================================

class OrchestratorEngine:
    """
    Motor de orquestación de agentes.
    
    Responsabilidades:
    1. Recibir solicitudes clínicas
    2. Crear planes de orquestación
    3. Seleccionar agentes apropiados
    4. Coordinar ejecución
    5. Agregar resultados
    6. Devolver respuesta final
    """
    
    def __init__(
        self,
        config: OrchestratorConfig | None = None,
        registry: AgentRegistry | None = None,
        lifecycle: AgentLifecycleManager | None = None,
        broker: MessageBroker | None = None,
        event_bus: EventBus | None = None,
    ):
        self.config = config or OrchestratorConfig()
        self.registry = registry or AgentRegistry()
        self.lifecycle = lifecycle or AgentLifecycleManager(event_bus)
        self.broker = broker or MessageBroker()
        self.event_bus = event_bus or EventBus()
        self.lookup = AgentLookup(self.registry)
        
        # Sub-componentes
        self.dispatcher = TaskDispatcher(
            registry=self.registry,
            broker=self.broker,
            config=self.config,
        )
        self.scheduler = TaskScheduler(
            config=self.config,
        )
        self.aggregator = ResponseAggregator(
            config=self.config,
        )
        
        # Estado
        self._active_workflows: dict[str, Workflow] = {}
        self._active_plans: dict[str, OrchestrationPlan] = {}
        self._executions: dict[str, AgentExecution] = {}
        
        logger.info("OrchestratorEngine initialized")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def process_request(
        self,
        query: str,
        context: dict | None = None,
        strategy: OrchestrationStrategy | None = None,
    ) -> dict:
        """
        Procesa una solicitud clínica.
        
        Flujo:
        1. Crear plan de orquestación
        2. Seleccionar agentes
        3. Crear workflow
        4. Ejecutar workflow
        5. Agregar resultados
        6. Devolver respuesta
        """
        from datetime import UTC, datetime
        
        request_id = str(datetime.now(UTC).timestamp())
        
        logger.info(f"Processing request {request_id}: {query[:100]}")
        
        try:
            # 1. Crear plan
            plan = await self.create_plan(
                request_id=request_id,
                query=query,
                context=context or {},
                strategy=strategy or self.config.default_strategy,
            )
            
            # 2. Validar plan
            if not await self.validate_plan(plan):
                raise ValueError(f"Plan validation failed: {plan.validation_errors}")
            
            # 3. Seleccionar agentes
            await self.select_agents(plan)
            
            # 4. Crear workflow
            workflow = await self.create_workflow(plan)
            
            # 5. Ejecutar workflow
            workflow_result = await self.execute_workflow(workflow)
            
            # 6. Agregar resultados
            final_result = await self.aggregate_results(workflow_result)
            
            # Publicar evento
            if self.config.emit_events:
                await self.event_bus.publish(
                    EventFactory.task_completed(
                        task_id=request_id,
                        agent_id="orchestrator",
                    )
                )
            
            return {
                "request_id": request_id,
                "success": True,
                "result": final_result,
                "workflow_id": workflow.workflow_id,
                "execution_time_ms": workflow_result.get("execution_time_ms", 0),
            }
            
        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
            
            if self.config.emit_events:
                await self.event_bus.publish(
                    EventFactory.agent_failed("orchestrator", str(e))
                )
            
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
            }
    
    async def create_plan(
        self,
        request_id: str,
        query: str,
        context: dict,
        strategy: OrchestrationStrategy,
    ) -> OrchestrationPlan:
        """Crea un plan de orquestación para la solicitud."""
        
        # Analizar query para determinar intent
        intent = self._analyze_intent(query)
        
        # Crear plan base
        plan = OrchestrationPlan(
            plan_id=str(datetime.now(UTC).timestamp()),
            request_id=request_id,
            original_query=query,
            intent=intent,
            strategy=strategy,
            execution_mode=self.config.default_execution_mode,
        )
        
        # Determinar pasos según intent
        steps = self._determine_steps(intent, context)
        
        for step in steps:
            plan.add_step(step)
        
        self._active_plans[plan.plan_id] = plan
        
        logger.info(f"Created plan {plan.plan_id} with {len(steps)} steps")
        
        return plan
    
    async def validate_plan(self, plan: OrchestrationPlan) -> bool:
        """Valida un plan de orquestación."""
        
        validation_errors = []
        
        # Validar que hay pasos
        if not plan.steps:
            validation_errors.append("Plan has no steps")
        
        # Validar dependencias
        step_ids = {s.step_id for s in plan.steps}
        for step in plan.steps:
            for dep_id in step.depends_on if hasattr(step, 'depends_on') else []:
                if dep_id not in step_ids:
                    validation_errors.append(f"Step {step.step_id} depends on unknown step {dep_id}")
        
        # Validar capacidades requeridas vs disponibles
        required_caps = set()
        for step in plan.steps:
            required_caps.update(step.required_capabilities)
        
        # Verificar que hay agentes disponibles
        for cap in required_caps:
            agents = await self.registry.get_by_capabilities(
                [AgentCapability(cap)],
                match_all=True,
            )
            if not agents:
                validation_errors.append(f"No agent available with capability: {cap}")
        
        plan.validation_errors = validation_errors
        plan.is_validated = len(validation_errors) == 0
        plan.status = PlanStatus.VALIDATED if plan.is_validated else PlanStatus.CREATED
        
        if plan.is_validated:
            plan.validated_at = datetime.now(UTC)
        
        return plan.is_validated
    
    async def select_agents(self, plan: OrchestrationPlan) -> None:
        """Selecciona agentes para ejecutar el plan."""
        
        for step in plan.steps:
            # Obtener agentes con las capabilities requeridas
            capabilities = [AgentCapability(cap) for cap in step.required_capabilities]
            
            agents = await self.registry.get_by_capabilities(
                capabilities,
                match_all=True,
            )
            
            # Filtrar disponibles
            available = [a for a in agents if a.is_available]
            
            if not available:
                if self.config.enable_agent_fallback:
                    # Tomar cualquier agente del tipo requerido
                    agents = await self.registry.get_by_type(AgentType(step.agent_type))
                    available = [a for a in agents if a.is_available]
            
            if available:
                # Seleccionar el mejor (primero disponible por ahora)
                plan.selected_agents[step.agent_type] = available[0].agent_id
                step.assigned_agent_id = available[0].agent_id
            else:
                logger.warning(f"No agent available for step {step.step_id}")
    
    async def create_workflow(self, plan: OrchestrationPlan) -> Workflow:
        """Crea un workflow desde un plan."""
        
        workflow = Workflow(
            workflow_id=f"wf_{plan.plan_id}",
            name=f"Workflow for {plan.request_id}",
            description=f"Orchestration workflow for request {plan.request_id}",
            strategy=plan.strategy,
            execution_mode=plan.execution_mode,
            aggregation_method=self.config.default_aggregation,
            input_context=plan.original_query,
        )
        
        # Crear pasos del workflow desde el plan
        for plan_step in plan.steps:
            workflow_step = WorkflowStep(
                step_id=plan_step.step_id,
                agent_type=plan_step.agent_type,
                agent_id=plan_step.assigned_agent_id,
                input_mapping={"source": "context"},
                output_mapping={"target": "shared_context"},
                depends_on=[],  # Se establece según estrategia
                timeout_seconds=plan_step.timeout_seconds,
                required_capabilities=plan_step.required_capabilities,
            )
            workflow.add_step(workflow_step)
        
        # Establecer dependencias según estrategia
        self._establish_dependencies(workflow, plan.strategy)
        
        self._active_workflows[workflow.workflow_id] = workflow
        
        logger.info(f"Created workflow {workflow.workflow_id} with {len(workflow.steps)} steps")
        
        return workflow
    
    async def execute_workflow(
        self,
        workflow: Workflow,
    ) -> dict:
        """Ejecuta un workflow completo."""
        
        from datetime import UTC, datetime
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now(UTC)
        
        start_time = datetime.now(UTC)
        
        try:
            if workflow.strategy == OrchestrationStrategy.SEQUENTIAL:
                await self._execute_sequential(workflow)
            elif workflow.strategy == OrchestrationStrategy.PARALLEL:
                await self._execute_parallel(workflow)
            elif workflow.strategy == OrchestrationStrategy.PIPELINE:
                await self._execute_pipeline(workflow)
            else:
                await self._execute_sequential(workflow)
            
            workflow.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Workflow {workflow.workflow_id} failed: {e}")
            workflow.status = WorkflowStatus.FAILED
        
        finally:
            workflow.completed_at = datetime.now(UTC)
            end_time = datetime.now(UTC)
        
        # Compilar resultados
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value,
            "step_results": workflow.step_results,
            "shared_context": workflow.shared_context,
            "execution_time_ms": execution_time_ms,
            "progress": workflow.progress,
        }
    
    async def aggregate_results(
        self,
        workflow_result: dict,
    ) -> dict:
        """Agrega resultados de un workflow."""
        
        return await self.aggregator.aggregate(
            results=workflow_result.get("step_results", {}),
            shared_context=workflow_result.get("shared_context", {}),
            method=self.config.default_aggregation,
        )
    
    # =============================================================================
    # EXECUTION STRATEGIES
    # =============================================================================
    
    async def _execute_sequential(self, workflow: Workflow) -> None:
        """Ejecuta pasos secuencialmente."""
        
        for step in workflow.steps:
            if workflow.status == WorkflowStatus.FAILED:
                break
            
            result = await self._execute_step(step, workflow)
            workflow.step_results[step.step_id] = result
            
            # Actualizar contexto compartido
            if result.get("success"):
                workflow.shared_context[step.step_id] = result.get("output", {})
    
    async def _execute_parallel(self, workflow: Workflow) -> None:
        """Ejecuta pasos en paralelo."""
        
        import asyncio
        
        ready_steps = workflow.get_ready_steps()
        
        # Ejecutar todos los pasos listos en paralelo
        tasks = [
            self._execute_step(step, workflow)
            for step in ready_steps
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for step, result in zip(ready_steps, results):
            if isinstance(result, Exception):
                workflow.step_results[step.step_id] = {
                    "success": False,
                    "error": str(result),
                }
            else:
                workflow.step_results[step.step_id] = result
                
                if result.get("success"):
                    workflow.shared_context[step.step_id] = result.get("output", {})
    
    async def _execute_pipeline(self, workflow: Workflow) -> None:
        """Ejecuta pasos en pipeline (salida de uno es entrada de otro)."""
        
        await self._execute_sequential(workflow)
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict:
        """Ejecuta un paso individual."""
        
        from datetime import UTC, datetime
        
        step.status = ExecutionStatus.RUNNING
        step.started_at = datetime.now(UTC)
        
        try:
            # Crear ejecución
            execution = AgentExecution(
                execution_id=f"exec_{step.step_id}_{datetime.now(UTC).timestamp()}",
                workflow_id=workflow.workflow_id,
                step_id=step.step_id,
                agent_id=step.agent_id or "",
                agent_type=step.agent_type,
                task_type="orchestrated_task",
                task_input=workflow.input_context,
                input_context=workflow.shared_context,
                timeout_seconds=step.timeout_seconds,
            )
            
            self._executions[execution.execution_id] = execution
            
            # Obtener agente
            agent = await self.registry.get(execution.agent_id)
            
            if not agent:
                raise ValueError(f"Agent {execution.agent_id} not found")
            
            # Ejecutar
            result = await self.dispatcher.dispatch(execution, agent)
            
            step.status = ExecutionStatus.COMPLETED
            step.completed_at = datetime.now(UTC)
            
            return {
                "success": True,
                "output": result.output if result else {},
                "confidence": result.confidence if result else 0.0,
                "execution_time_ms": result.execution_time_ms if result else 0,
            }
            
        except Exception as e:
            logger.error(f"Step {step.step_id} failed: {e}")
            step.status = ExecutionStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now(UTC)
            
            return {
                "success": False,
                "error": str(e),
            }
    
    def _establish_dependencies(
        self,
        workflow: Workflow,
        strategy: OrchestrationStrategy,
    ) -> None:
        """Establece dependencias entre pasos según estrategia."""
        
        if strategy == OrchestrationStrategy.SEQUENTIAL:
            # Cada paso depende del anterior
            for i, step in enumerate(workflow.steps):
                if i > 0:
                    step.depends_on = [workflow.steps[i - 1].step_id]
        
        elif strategy == OrchestrationStrategy.PARALLEL:
            # No hay dependencias (todos pueden ejecutarse juntos)
            pass
        
        elif strategy == OrchestrationStrategy.PIPELINE:
            # Cada paso depende del anterior
            for i, step in enumerate(workflow.steps):
                if i > 0:
                    step.depends_on = [workflow.steps[i - 1].step_id]
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _analyze_intent(self, query: str) -> str:
        """Analiza el query para determinar el intent."""
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["diagnostic", "diagnose", "diagnosis", "problema", "fallo"]):
            return "diagnostic"
        elif any(word in query_lower for word in ["device", "equipo", "activo"]):
            return "device_analysis"
        elif any(word in query_lower for word in ["maintenance", "mantenimiento", "preventivo"]):
            return "maintenance"
        elif any(word in query_lower for word in ["incident", "incidente", "alerta"]):
            return "incident"
        elif any(word in query_lower for word in ["knowledge", "knowledge_base", "articulo"]):
            return "knowledge"
        elif any(word in query_lower for word in ["research", "investigat", "investigar", "buscar"]):
            return "research"
        elif any(word in query_lower for word in ["plan", "planning", "planificar"]):
            return "planning"
        else:
            return "general"
    
    def _determine_steps(self, intent: str, context: dict) -> list[PlanStep]:
        """Determina los pasos del plan según el intent."""
        
        steps = []
        order = 0
        
        if intent == "diagnostic":
            # Diagnóstico requiere: biomedical -> diagnostic -> reasoning
            steps.extend([
                PlanStep(
                    step_id=f"step_{order}",
                    order=order,
                    agent_type="biomedical",
                    required_capabilities=["analyze", "reason"],
                    timeout_seconds=300,
                    priority=10,
                ),
                PlanStep(
                    step_id=f"step_{order + 1}",
                    order=order + 1,
                    agent_type="diagnostic",
                    required_capabilities=["diagnose", "validate"],
                    timeout_seconds=300,
                    priority=9,
                ),
            ])
        
        elif intent == "device_analysis":
            # Análisis de dispositivo: knowledge -> biomedical -> diagnostic
            steps.extend([
                PlanStep(
                    step_id=f"step_{order}",
                    order=order,
                    agent_type="knowledge",
                    required_capabilities=["research", "analyze"],
                    timeout_seconds=300,
                    priority=10,
                ),
                PlanStep(
                    step_id=f"step_{order + 1}",
                    order=order + 1,
                    agent_type="biomedical",
                    required_capabilities=["analyze"],
                    timeout_seconds=300,
                    priority=8,
                ),
            ])
        
        elif intent == "maintenance":
            # Mantenimiento: knowledge -> planning
            steps.extend([
                PlanStep(
                    step_id=f"step_{order}",
                    order=order,
                    agent_type="knowledge",
                    required_capabilities=["research"],
                    timeout_seconds=300,
                    priority=10,
                ),
                PlanStep(
                    step_id=f"step_{order + 1}",
                    order=order + 1,
                    agent_type="planning",
                    required_capabilities=["plan", "coordinate"],
                    timeout_seconds=300,
                    priority=9,
                ),
            ])
        
        elif intent == "research":
            steps.append(
                PlanStep(
                    step_id=f"step_{order}",
                    order=order,
                    agent_type="research",
                    required_capabilities=["research", "analyze"],
                    timeout_seconds=300,
                    priority=10,
                )
            )
        
        elif intent == "planning":
            steps.append(
                PlanStep(
                    step_id=f"step_{order}",
                    order=order,
                    agent_type="planning",
                    required_capabilities=["plan"],
                    timeout_seconds=300,
                    priority=10,
                )
            )
        
        else:
            # General: usar el orquestador directamente
            steps.append(
                PlanStep(
                    step_id=f"step_{order}",
                    order=order,
                    agent_type="orchestrator",
                    required_capabilities=["coordinate"],
                    timeout_seconds=300,
                    priority=10,
                )
            )
        
        return steps
    
    # =============================================================================
    # STATUS METHODS
    # =============================================================================
    
    def get_workflow_status(self, workflow_id: str) -> dict | None:
        """Obtiene estado de un workflow."""
        
        workflow = self._active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value,
            "progress": workflow.progress,
            "current_step": workflow.current_step_index,
            "total_steps": len(workflow.steps),
        }
    
    def get_execution_status(self, execution_id: str) -> dict | None:
        """Obtiene estado de una ejecución."""
        
        execution = self._executions.get(execution_id)
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "agent_id": execution.agent_id,
            "duration_ms": execution.duration_ms,
        }
    
    def list_active_workflows(self) -> list[dict]:
        """Lista workflows activos."""
        
        return [
            self.get_workflow_status(wf.workflow_id)
            for wf in self._active_workflows.values()
            if wf.status in [WorkflowStatus.RUNNING, WorkflowStatus.PENDING]
        ]
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del orquestador."""
        
        return {
            "active_workflows": len(self._active_workflows),
            "active_plans": len(self._active_plans),
            "active_executions": len(self._executions),
            "registered_agents": 0,  # Call count() in async context
        }
    
    async def get_stats_async(self) -> dict:
        """Obtiene estadísticas del orquestador (async)."""
        
        return {
            "active_workflows": len(self._active_workflows),
            "active_plans": len(self._active_plans),
            "active_executions": len(self._executions),
            "registered_agents": await self.registry.count(),
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OrchestratorEngine",
    "OrchestratorConfig",
]
