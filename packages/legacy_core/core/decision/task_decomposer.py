"""Task Decomposer for EREN Cognitive Decision Engine.

Decomposes goals into executable tasks.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.decision.types import (
    DecisionTask,
    Goal,
    GoalAnalysis,
    GoalType,
    RiskLevel,
    TaskPriority,
)

if TYPE_CHECKING:
    pass


class TaskDecomposer:
    """Decomposes goals into executable tasks.

    The Task Decomposer does NOT:
    - Execute tasks
    - Query providers

    It ONLY:
    - Breaks down goals
    - Creates task definitions
    - Assigns priorities
    """

    def __init__(self):
        """Initialize task decomposer."""
        self._task_templates = self._load_templates()

    def decompose(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose goal into tasks.

        Args:
            goal: Goal to decompose.
            analysis: Goal analysis results.

        Returns:
            List of tasks.
        """
        tasks = []

        if goal.goal_type == GoalType.DIAGNOSIS:
            tasks = self._decompose_diagnosis(goal, analysis)
        elif goal.goal_type == GoalType.TROUBLESHOOTING:
            tasks = self._decompose_troubleshooting(goal, analysis)
        elif goal.goal_type == GoalType.TREATMENT:
            tasks = self._decompose_treatment(goal, analysis)
        elif goal.goal_type == GoalType.RESEARCH:
            tasks = self._decompose_research(goal, analysis)
        elif goal.goal_type == GoalType.MONITORING:
            tasks = self._decompose_monitoring(goal, analysis)
        elif goal.goal_type == GoalType.ANALYSIS:
            tasks = self._decompose_analysis(goal, analysis)
        elif goal.goal_type == GoalType.REPORT:
            tasks = self._decompose_report(goal, analysis)
        else:
            tasks = self._decompose_custom(goal, analysis)

        # Set priorities
        tasks = self._assign_priorities(tasks)

        # Set risk levels
        tasks = self._assign_risk_levels(tasks)

        return tasks

    def _decompose_diagnosis(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose diagnosis goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Gather device history",
                description=f"Consult device history for context: {goal.description}",
                task_type="query",
                capability="memory.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=5.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Retrieve relevant knowledge",
                description="Search medical knowledge base for relevant information",
                task_type="retrieval",
                capability="knowledge.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Find similar cases",
                description="Search for similar historical cases",
                task_type="retrieval",
                capability="knowledge.similar_cases",
                estimated_time_seconds=8.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Analyze symptoms and data",
                description="Analyze gathered information for diagnosis",
                task_type="reasoning",
                capability="reasoning.analyze",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=15.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Generate diagnosis",
                description="Formulate diagnosis based on analysis",
                task_type="reasoning",
                capability="reasoning.diagnose",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=10.0,
            ),
        ]

        return tasks

    def _decompose_troubleshooting(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose troubleshooting goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Check device status",
                description="Verify current device status and error states",
                task_type="diagnostic",
                capability="device.status",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=5.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Retrieve device history",
                description="Get device maintenance and incident history",
                task_type="query",
                capability="memory.retrieve",
                estimated_time_seconds=5.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Find technical documentation",
                description="Search for relevant technical manuals and guides",
                task_type="retrieval",
                capability="knowledge.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Search maintenance protocols",
                description="Find applicable maintenance and repair protocols",
                task_type="retrieval",
                capability="knowledge.protocols",
                estimated_time_seconds=8.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Find similar issues",
                description="Search for similar past issues and solutions",
                task_type="retrieval",
                capability="knowledge.similar_cases",
                estimated_time_seconds=8.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Execute technical reasoning",
                description="Apply technical knowledge to analyze root cause",
                task_type="reasoning",
                capability="reasoning.analyze",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=15.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Generate resolution",
                description="Formulate resolution based on analysis",
                task_type="reasoning",
                capability="reasoning.resolve",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=10.0,
            ),
        ]

        return tasks

    def _decompose_treatment(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose treatment goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Gather patient context",
                description="Retrieve patient history and current status",
                task_type="query",
                capability="memory.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=5.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Retrieve clinical guidelines",
                description="Search for applicable clinical guidelines",
                task_type="retrieval",
                capability="knowledge.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Check contraindications",
                description="Verify treatment safety and contraindications",
                task_type="analysis",
                capability="reasoning.analyze",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Generate treatment plan",
                description="Create treatment recommendations",
                task_type="reasoning",
                capability="reasoning.generate",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=15.0,
            ),
        ]

        return tasks

    def _decompose_research(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose research goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Search knowledge base",
                description=f"Search for information about: {goal.description}",
                task_type="retrieval",
                capability="knowledge.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Find related documents",
                description="Find related documents and resources",
                task_type="retrieval",
                capability="knowledge.related",
                estimated_time_seconds=8.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Synthesize information",
                description="Synthesize findings into coherent response",
                task_type="reasoning",
                capability="reasoning.synthesize",
                priority=TaskPriority.MEDIUM,
                estimated_time_seconds=10.0,
            ),
        ]

        return tasks

    def _decompose_monitoring(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose monitoring goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Retrieve current status",
                description="Get current monitoring data",
                task_type="query",
                capability="device.status",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=5.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Check historical trends",
                description="Analyze historical monitoring data",
                task_type="analysis",
                capability="memory.retrieve",
                estimated_time_seconds=8.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Generate monitoring report",
                description="Create monitoring summary",
                task_type="reasoning",
                capability="reasoning.generate",
                priority=TaskPriority.MEDIUM,
                estimated_time_seconds=5.0,
            ),
        ]

        return tasks

    def _decompose_analysis(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose analysis goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Gather relevant data",
                description="Collect all relevant information for analysis",
                task_type="query",
                capability="memory.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Retrieve supporting knowledge",
                description="Find supporting knowledge and guidelines",
                task_type="retrieval",
                capability="knowledge.retrieve",
                priority=TaskPriority.MEDIUM,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Perform analysis",
                description="Conduct detailed analysis",
                task_type="reasoning",
                capability="reasoning.analyze",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=20.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Generate findings",
                description="Summarize analysis findings",
                task_type="reasoning",
                capability="reasoning.generate",
                priority=TaskPriority.MEDIUM,
                estimated_time_seconds=10.0,
            ),
        ]

        return tasks

    def _decompose_report(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose report goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Gather report data",
                description="Collect all data needed for report",
                task_type="query",
                capability="memory.retrieve",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Generate report content",
                description="Create report content",
                task_type="reasoning",
                capability="reasoning.generate",
                priority=TaskPriority.CRITICAL,
                estimated_time_seconds=15.0,
            ),
        ]

        return tasks

    def _decompose_custom(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
    ) -> list[DecisionTask]:
        """Decompose custom goal."""
        tasks = [
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Gather context",
                description=f"Gather context for: {goal.description}",
                task_type="query",
                capability="memory.retrieve",
                priority=TaskPriority.MEDIUM,
                estimated_time_seconds=5.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Retrieve relevant knowledge",
                description="Search knowledge base",
                task_type="retrieval",
                capability="knowledge.retrieve",
                priority=TaskPriority.MEDIUM,
                estimated_time_seconds=10.0,
            ),
            DecisionTask(
                task_id=str(uuid.uuid4()),
                name="Process and respond",
                description="Process information and generate response",
                task_type="reasoning",
                capability="reasoning.generate",
                priority=TaskPriority.HIGH,
                estimated_time_seconds=10.0,
            ),
        ]

        return tasks

    def _assign_priorities(self, tasks: list[DecisionTask]) -> list[DecisionTask]:
        """Assign priorities to tasks based on position and type."""
        for i, task in enumerate(tasks):
            if i == 0:
                task.priority = TaskPriority.HIGH
            elif task.task_type == "reasoning":
                task.priority = TaskPriority.CRITICAL

        return tasks

    def _assign_risk_levels(self, tasks: list[DecisionTask]) -> list[DecisionTask]:
        """Assign risk levels to tasks."""
        for task in tasks:
            if task.task_type == "reasoning":
                task.risk_level = RiskLevel.MEDIUM
            elif task.task_type == "retrieval":
                task.risk_level = RiskLevel.LOW
            else:
                task.risk_level = RiskLevel.LOW

        return tasks

    def _load_templates(self) -> dict:
        """Load task templates."""
        return {}
