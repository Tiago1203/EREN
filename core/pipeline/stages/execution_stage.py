"""Execution Stage for EREN OS Cognitive Pipeline.

Executes the planned actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.pipeline.stages.cognitive_stage import CognitiveStage
from core.pipeline.context import PipelineContext

if TYPE_CHECKING:
    from core.pipeline.cognitive_events import CognitiveEventPublisher


class TaskExecutionStage(CognitiveStage):
    """Stage for executing planned actions.
    
    Responsibilities:
    - Execute tasks in order
    - Handle failures
    - Track progress
    """
    
    def __init__(
        self,
        event_publisher: CognitiveEventPublisher | None = None,
    ):
        """Initialize the execution stage."""
        super().__init__(
            name="execution",
            event_publisher=event_publisher,
        )
    
    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "Execution"
    
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Execute planned tasks.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Execution result.
        """
        plan = context.get("plan", {})
        tasks = plan.get("tasks", [])
        dependencies = plan.get("dependencies", {})
        
        # Execute tasks
        results = self._execute_tasks(tasks, dependencies)
        
        # Record telemetry
        self._record_telemetry(
            actions_executed=results["executed"],
            success_count=results["success"],
            failure_count=results["failed"],
        )
        
        # Store in context
        context["execution_result"] = results
        
        return results
    
    def _execute_tasks(
        self,
        tasks: list,
        dependencies: dict,
    ) -> dict[str, Any]:
        """Execute tasks in dependency order.
        
        Args:
            tasks: Tasks to execute.
            dependencies: Task dependencies.
            
        Returns:
            Execution results.
        """
        executed = 0
        success = 0
        failed = 0
        task_results = []
        
        for task in tasks:
            task_name = task["name"]
            
            # Check dependencies
            deps = dependencies.get(task_name, [])
            deps_satisfied = all(
                r.get("status") == "completed" and r.get("success")
                for r in task_results
                if r.get("task") in deps
            )
            
            if not deps_satisfied:
                failed += 1
                task_results.append({
                    "task": task_name,
                    "status": "skipped",
                    "reason": "dependencies_not_met",
                })
                continue
            
            # Execute task (simplified)
            result = self._execute_single_task(task)
            task_results.append(result)
            
            executed += 1
            if result.get("success"):
                success += 1
            else:
                failed += 1
        
        return {
            "executed": executed,
            "success": success,
            "failed": failed,
            "task_results": task_results,
        }
    
    def _execute_single_task(self, task: dict) -> dict[str, Any]:
        """Execute a single task.
        
        Args:
            task: Task definition.
            
        Returns:
            Task result.
        """
        # Placeholder - real implementation would execute actual tasks
        return {
            "task": task["name"],
            "status": "completed",
            "success": True,
            "output": f"Task {task['name']} executed successfully",
        }
    
    def _create_event(self, context, success=True, error=""):
        """Create execution completed event."""
        from core.pipeline.cognitive_events import ExecutionCompletedEvent, CognitiveEventType
        
        result = context.get("execution_result", {})
        
        return ExecutionCompletedEvent(
            event_type=CognitiveEventType.EXECUTION_COMPLETED,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            actions_executed=result.get("executed", 0),
            success_count=result.get("success", 0),
            failure_count=result.get("failed", 0),
            data=self._telemetry.metadata,
        )
