"""Planning Stage for EREN OS Cognitive Pipeline.

Creates execution plans based on reasoning results.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from core.PHASE_2.pipeline.stages.cognitive_stage import CognitiveStage
from core.PHASE_2.pipeline.context import PipelineContext

if TYPE_CHECKING:
    from core.PHASE_2.pipeline.cognitive_events import CognitiveEventPublisher


class CognitivePlanningStage(CognitiveStage):
    """Stage for creating execution plans.
    
    Responsibilities:
    - Analyze goals
    - Decompose tasks
    - Create execution plan
    - Estimate duration
    - Assess risks
    """
    
    def __init__(
        self,
        event_publisher: CognitiveEventPublisher | None = None,
    ):
        """Initialize the planning stage."""
        super().__init__(
            name="planning",
            event_publisher=event_publisher,
        )
    
    @property
    def stage_name(self) -> str:
        """Get stage name."""
        return "Planning"
    
    def _execute_impl(self, context: PipelineContext) -> dict[str, Any]:
        """Execute planning.
        
        Args:
            context: Pipeline context.
            
        Returns:
            Planning result.
        """
        intent = context.get("intent", "query")
        reasoning = context.get("reasoning", {})
        
        # Create plan
        plan = self._create_plan(intent, reasoning)
        
        # Record telemetry
        self._record_telemetry(
            plan_id=plan["plan_id"],
            task_count=plan["task_count"],
            risk_level=plan["risk_level"],
        )
        
        # Store in context
        context["plan"] = plan
        context["plan_id"] = plan["plan_id"]
        
        return plan
    
    def _create_plan(
        self,
        intent: str,
        reasoning: dict,
    ) -> dict[str, Any]:
        """Create execution plan.
        
        Args:
            intent: User intent.
            reasoning: Reasoning results.
            
        Returns:
            Execution plan.
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        
        # Create tasks based on intent
        tasks = self._decompose_intent(intent)
        
        # Calculate risk
        risk_level = self._assess_risk(intent, tasks)
        
        return {
            "plan_id": plan_id,
            "intent": intent,
            "tasks": tasks,
            "task_count": len(tasks),
            "estimated_duration_ms": sum(t.get("estimated_ms", 100) for t in tasks),
            "risk_level": risk_level,
            "dependencies": self._build_dependencies(tasks),
        }
    
    def _decompose_intent(self, intent: str) -> list[dict[str, Any]]:
        """Decompose intent into tasks.
        
        Args:
            intent: User intent.
            
        Returns:
            List of tasks.
        """
        # Task templates based on intent type
        task_templates = {
            "query": [
                {"name": "gather_info", "estimated_ms": 50, "parallel": False},
                {"name": "analyze", "estimated_ms": 100, "parallel": False},
                {"name": "respond", "estimated_ms": 30, "parallel": False},
            ],
            "command": [
                {"name": "validate", "estimated_ms": 20, "parallel": False},
                {"name": "execute", "estimated_ms": 200, "parallel": False},
                {"name": "verify", "estimated_ms": 30, "parallel": False},
            ],
            "medical": [
                {"name": "collect_symptoms", "estimated_ms": 50, "parallel": False},
                {"name": "analyze_medical", "estimated_ms": 150, "parallel": False},
                {"name": "generate_recommendation", "estimated_ms": 80, "parallel": False},
            ],
        }
        
        return task_templates.get(intent, task_templates["query"])
    
    def _assess_risk(self, intent: str, tasks: list) -> str:
        """Assess plan risk.
        
        Args:
            intent: User intent.
            tasks: Plan tasks.
            
        Returns:
            Risk level.
        """
        if intent == "medical":
            return "high"
        elif len(tasks) > 5:
            return "medium"
        return "low"
    
    def _build_dependencies(self, tasks: list) -> dict[str, list[str]]:
        """Build task dependencies.
        
        Args:
            tasks: Plan tasks.
            
        Returns:
            Dependency map.
        """
        dependencies = {}
        for i, task in enumerate(tasks):
            if i > 0 and not task.get("parallel"):
                dependencies[task["name"]] = [tasks[i - 1]["name"]]
        return dependencies
    
    def _create_event(self, context, success=True, error=""):
        """Create plan created event."""
        from core.PHASE_2.pipeline.cognitive_events import PlanCreatedEvent, CognitiveEventType
        
        plan = context.get("plan", {})
        
        return PlanCreatedEvent(
            event_type=CognitiveEventType.PLAN_CREATED,
            correlation_id=context.correlation_id,
            session_id=context.session_id,
            pipeline_id=context.pipeline_id,
            stage_name=self.name,
            success=success,
            error=error,
            duration_ms=self._telemetry.duration_ms,
            plan_id=plan.get("plan_id", ""),
            task_count=plan.get("task_count", 0),
            estimated_duration_ms=plan.get("estimated_duration_ms", 0.0),
            risk_level=plan.get("risk_level", "unknown"),
            data=self._telemetry.metadata,
        )
