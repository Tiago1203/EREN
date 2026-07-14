"""Goal Analyzer for EREN Cognitive Planning Engine.

Analyzes user intent and extracts goals.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.planning.types import (
    Goal,
    GoalAnalysis,
    GoalType,
)

if TYPE_CHECKING:
    pass


class GoalAnalyzer:
    """Analyzes user intent and extracts goals.

    The Goal Analyzer does NOT:
    - Execute tasks
    - Query providers
    - Use OpenAI directly

    It ONLY:
    - Analyzes intent
    - Extracts objectives
    - Identifies required capabilities
    """

    def __init__(self):
        """Initialize goal analyzer."""
        self._goal_type_keywords = {
            GoalType.DIAGNOSIS: [
                "diagnose", "diagnosis", "analyze", "identify problem",
                "what is wrong", "cause", "reason",
            ],
            GoalType.TREATMENT: [
                "treat", "treatment", "therapy", "prescribe",
                "recommend", "solution", "manage",
            ],
            GoalType.MONITORING: [
                "monitor", "track", "watch", "observe",
                "check status", "follow up",
            ],
            GoalType.ANALYSIS: [
                "analyze", "analysis", "examine", "evaluate",
                "assess", "review", "study",
            ],
            GoalType.RESEARCH: [
                "research", "find", "search", "lookup",
                "information", "details", "learn",
            ],
            GoalType.TROUBLESHOOTING: [
                "troubleshoot", "fix", "repair", "resolve",
                "not working", "issue", "problem", "error",
            ],
            GoalType.CONSULTATION: [
                "consult", "advice", "opinion", "second opinion",
                "recommendation", "suggest",
            ],
            GoalType.REPORT: [
                "report", "summary", "document", "generate report",
                "create report", "export",
            ],
        }

    def analyze(
        self,
        user_intent: str,
        context: dict | None = None,
    ) -> GoalAnalysis:
        """Analyze user intent.

        Args:
            user_intent: User's intent/question.
            context: Additional context.

        Returns:
            GoalAnalysis with extracted goals.
        """
        context = context or {}

        # Create goal
        goal = Goal(
            goal_id=self._generate_id(),
            goal_type=GoalType.CUSTOM,
            description=user_intent,
            user_intent=user_intent,
            context=context,
        )

        # Analyze intent
        analysis = GoalAnalysis(
            goal=goal,
            intent=user_intent,
            goal_type=self._detect_goal_type(user_intent),
            primary_objective=self._extract_primary_objective(user_intent),
            sub_objectives=self._extract_sub_objectives(user_intent),
            required_capabilities=self._identify_capabilities(user_intent),
            constraints=self._extract_constraints(user_intent, context),
        )

        # Update goal type
        goal.goal_type = analysis.goal_type

        # Calculate estimates
        analysis.estimated_complexity = self._estimate_complexity(user_intent)
        analysis.estimated_tasks = self._estimate_task_count(user_intent, analysis.estimated_complexity)
        analysis.estimated_time_seconds = self._estimate_time(analysis.estimated_tasks)

        # Update goal estimates
        goal.complexity = analysis.estimated_complexity
        goal.estimated_tasks = analysis.estimated_tasks
        goal.estimated_time_seconds = analysis.estimated_time_seconds

        return analysis

    def _detect_goal_type(self, intent: str) -> GoalType:
        """Detect goal type from intent."""
        intent_lower = intent.lower()

        scores = {}
        for goal_type, keywords in self._goal_type_keywords.items():
            score = sum(1 for kw in keywords if kw in intent_lower)
            if score > 0:
                scores[goal_type] = score

        if scores:
            return max(scores, key=scores.get)

        return GoalType.CUSTOM

    def _extract_primary_objective(self, intent: str) -> str:
        """Extract primary objective from intent."""
        # Simple extraction: remove common question words
        intent_lower = intent.lower()

        # Remove question prefixes
        prefixes = [
            "what is", "what are", "how do", "how does", "how can",
            "why is", "why does", "can you", "could you",
            "tell me", "show me", "find", "analyze", "help me",
        ]

        for prefix in prefixes:
            if intent_lower.startswith(prefix):
                return intent[len(prefix):].strip()

        return intent

    def _extract_sub_objectives(self, intent: str) -> list[str]:
        """Extract sub-objectives from intent."""
        sub_objectives = []

        # Look for conjunctions that might indicate multiple objectives
        conjunction_keywords = [
            "and then", "also", "additionally", "plus",
            "first", "second", "finally", "also",
        ]

        intent_lower = intent.lower()
        for keyword in conjunction_keywords:
            if keyword in intent_lower:
                sub_objectives.append(f"Handle {keyword} part of request")

        return sub_objectives

    def _identify_capabilities(self, intent: str) -> list[str]:
        """Identify required capabilities from intent."""
        capabilities = []

        intent_lower = intent.lower()

        # Device-related
        if any(kw in intent_lower for kw in ["device", "monitor", "equipment"]):
            capabilities.append("device_management")
            capabilities.append("device_diagnostics")

        # Medical knowledge
        if any(kw in intent_lower for kw in ["medical", "clinical", "patient", "diagnosis"]):
            capabilities.append("medical_knowledge")
            capabilities.append("clinical_protocols")

        # Technical
        if any(kw in intent_lower for kw in ["technical", "specification", "manual"]):
            capabilities.append("technical_documentation")
            capabilities.append("knowledge_retrieval")

        # Analysis
        if any(kw in intent_lower for kw in ["analyze", "analysis", "evaluate"]):
            capabilities.append("reasoning")

        # Troubleshooting
        if any(kw in intent_lower for kw in ["troubleshoot", "fix", "repair", "not working"]):
            capabilities.append("troubleshooting")
            capabilities.append("diagnostics")

        return capabilities

    def _extract_constraints(self, intent: str, context: dict) -> dict:
        """Extract constraints from intent and context."""
        constraints = {}

        # Time constraints
        intent_lower = intent.lower()
        if "urgent" in intent_lower or "asap" in intent_lower:
            constraints["priority"] = "high"
        elif "when possible" in intent_lower or "when you can" in intent_lower:
            constraints["priority"] = "low"

        # Device constraints
        if context.get("device_id"):
            constraints["device_id"] = context["device_id"]

        # User constraints
        if context.get("user_role"):
            constraints["user_role"] = context["user_role"]

        return constraints

    def _estimate_complexity(self, intent: str) -> int:
        """Estimate goal complexity (1-5)."""
        complexity = 1

        # Increase for longer intents
        if len(intent) > 100:
            complexity += 1
        if len(intent) > 200:
            complexity += 1

        # Increase for multiple objectives
        conjunction_count = sum(
            intent.lower().count(kw)
            for kw in [" and ", " also ", " plus "]
        )
        complexity += min(conjunction_count, 2)

        # Increase for specific keywords
        specific_keywords = [
            "detailed", "comprehensive", "complete analysis",
            "thorough", "in-depth",
        ]
        for kw in specific_keywords:
            if kw in intent.lower():
                complexity += 1

        return min(complexity, 5)

    def _estimate_task_count(self, intent: str, complexity: int) -> int:
        """Estimate number of tasks needed."""
        base_tasks = {
            GoalType.RESEARCH: 3,
            GoalType.DIAGNOSIS: 5,
            GoalType.TROUBLESHOOTING: 6,
            GoalType.TREATMENT: 4,
            GoalType.MONITORING: 3,
            GoalType.ANALYSIS: 4,
            GoalType.CONSULTATION: 3,
            GoalType.REPORT: 2,
            GoalType.CUSTOM: 3,
        }

        goal_type = self._detect_goal_type(intent)
        tasks = base_tasks.get(goal_type, 3)

        # Adjust for complexity
        if complexity > 3:
            tasks += 2
        elif complexity > 1:
            tasks += 1

        return tasks

    def _estimate_time(self, task_count: int) -> float:
        """Estimate total time in seconds."""
        # Average 30 seconds per task
        return task_count * 30.0

    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())
