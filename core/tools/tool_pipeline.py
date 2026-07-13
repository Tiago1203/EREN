"""Tool pipeline for the Cognitive Tool Engine.

Executes multiple tools in sequence or parallel with dependency management.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .exceptions import PipelineExecutionError
from .tool_executor import ToolExecutor
from .tool_types import (
    ExecutionStatus,
    PipelineDefinition,
    PipelineResult,
    PipelineStep,
    ToolResult,
)

if TYPE_CHECKING:
    pass


class ToolPipeline:
    """Executes multiple tools in a pipeline.

    Pipelines support:
    - Sequential execution
    - Parallel execution
    - Step dependencies
    - Conditional execution
    - Error handling and recovery
    - Result aggregation
    """

    def __init__(
        self,
        executor: ToolExecutor,
    ) -> None:
        """Initialize tool pipeline.

        Args:
            executor: The tool executor.
        """
        self._executor = executor
        self._pipelines: dict[str, PipelineDefinition] = {}
        self._lock = threading.Lock()

    def register_pipeline(
        self,
        pipeline: PipelineDefinition,
    ) -> None:
        """Register a pipeline.

        Args:
            pipeline: The pipeline definition.
        """
        with self._lock:
            self._pipelines[pipeline.pipeline_id] = pipeline

    def get_pipeline(self, pipeline_id: str) -> PipelineDefinition | None:
        """Get a pipeline definition.

        Args:
            pipeline_id: The pipeline ID.

        Returns:
            The pipeline definition or None.
        """
        return self._pipelines.get(pipeline_id)

    def execute(
        self,
        pipeline_id: str,
        initial_parameters: dict,
    ) -> PipelineResult:
        """Execute a pipeline.

        Args:
            pipeline_id: The pipeline to execute.
            initial_parameters: Initial parameters for the pipeline.

        Returns:
            PipelineResult with all step results.

        Raises:
            PipelineExecutionError: If execution fails.
        """
        if pipeline_id not in self._pipelines:
            raise PipelineExecutionError(pipeline_id, "Pipeline not found")

        pipeline = self._pipelines[pipeline_id]
        execution_id = f"pipe_{uuid.uuid4().hex[:16]}"
        start_time = time.time()

        # Build dependency graph
        step_outputs: dict[str, Any] = {}
        step_results: list[ToolResult] = []
        failed_steps: set[str] = set()

        # Create step execution order
        execution_order = self._topological_sort(pipeline)

        for step_id in execution_order:
            step = self._get_step(pipeline, step_id)
            if not step:
                continue

            # Check if step dependencies are satisfied
            deps_satisfied = all(
                sid not in failed_steps
                for sid in step.depends_on
            )

            if not deps_satisfied:
                # Skip step due to failed dependency
                continue

            # Evaluate condition if present
            if step.condition and not self._evaluate_condition(
                step.condition, step_outputs
            ):
                # Skip step due to condition
                continue

            # Merge parameters
            step_params = self._merge_parameters(
                step.parameters,
                step_outputs,
                initial_parameters,
            )

            # Execute step
            try:
                result = self._executor.execute(
                    step.tool_id,
                    step_params,
                )
                step_results.append(result)

                # Store output
                if result.is_success():
                    step_outputs[step_id] = result.output
                else:
                    failed_steps.add(step_id)

                    if not pipeline.continue_on_error:
                        break

            except Exception as e:
                failed_steps.add(step_id)
                step_results.append(ToolResult(
                    tool_id=step.tool_id,
                    execution_id=f"{execution_id}_{step_id}",
                    status=ExecutionStatus.FAILED,
                    error=str(e),
                ))

                if not pipeline.continue_on_error:
                    break

        total_time_ms = (time.time() - start_time) * 1000

        # Determine overall status
        if failed_steps:
            status = ExecutionStatus.FAILED
        else:
            status = ExecutionStatus.SUCCESS

        return PipelineResult(
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            status=status,
            step_results=tuple(step_results),
            total_time_ms=total_time_ms,
        )

    def execute_parallel(
        self,
        pipeline_id: str,
        parameters_by_step: dict[str, dict],
    ) -> PipelineResult:
        """Execute a pipeline with parallel execution.

        Steps without dependencies run in parallel.

        Args:
            pipeline_id: The pipeline to execute.
            parameters_by_step: Parameters for each step.

        Returns:
            PipelineResult with all step results.
        """
        if pipeline_id not in self._pipelines:
            raise PipelineExecutionError(pipeline_id, "Pipeline not found")

        pipeline = self._pipelines[pipeline_id]
        execution_id = f"pipe_{uuid.uuid4().hex[:16]}"
        start_time = time.time()

        step_outputs: dict[str, Any] = {}
        step_results: dict[str, ToolResult] = {}
        results_lock = threading.Lock()

        def execute_step(step: PipelineStep) -> None:
            """Execute a single step."""
            try:
                params = parameters_by_step.get(step.step_id, {})
                params = self._merge_parameters(
                    step.parameters,
                    step_outputs,
                    params,
                )

                result = self._executor.execute(
                    step.tool_id,
                    params,
                )

                with results_lock:
                    step_results[step.step_id] = result
                    if result.is_success():
                        step_outputs[step.step_id] = result.output

            except Exception as e:
                with results_lock:
                    step_results[step.step_id] = ToolResult(
                        tool_id=step.tool_id,
                        execution_id=f"{execution_id}_{step.step_id}",
                        status=ExecutionStatus.FAILED,
                        error=str(e),
                    )

        # Group steps by dependency level
        levels = self._group_by_level(pipeline)

        for level_steps in levels:
            threads = []
            for step in level_steps:
                thread = threading.Thread(
                    target=execute_step,
                    args=(step,),
                )
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        total_time_ms = (time.time() - start_time) * 1000

        # Check for failures
        has_failures = any(
            r.status == ExecutionStatus.FAILED
            for r in step_results.values()
        )

        return PipelineResult(
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            status=ExecutionStatus.FAILED if has_failures else ExecutionStatus.SUCCESS,
            step_results=tuple(step_results.values()),
            total_time_ms=total_time_ms,
        )

    def _get_step(
        self,
        pipeline: PipelineDefinition,
        step_id: str,
    ) -> PipelineStep | None:
        """Get a step by ID."""
        for step in pipeline.steps:
            if step.step_id == step_id:
                return step
        return None

    def _topological_sort(
        self,
        pipeline: PipelineDefinition,
    ) -> list[str]:
        """Perform topological sort on pipeline steps.

        Args:
            pipeline: The pipeline definition.

        Returns:
            Ordered list of step IDs.
        """
        # Build adjacency list
        in_degree: dict[str, int] = {}
        dependents: dict[str, list[str]] = defaultdict(list)

        for step in pipeline.steps:
            if step.step_id not in in_degree:
                in_degree[step.step_id] = 0

            for dep in step.depends_on:
                dependents[dep].append(step.step_id)
                in_degree[step.step_id] += 1

        # Kahn's algorithm
        queue = [sid for sid, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for dependent in dependents[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return result

    def _group_by_level(
        self,
        pipeline: PipelineDefinition,
    ) -> list[list[PipelineStep]]:
        """Group steps by dependency level for parallel execution.

        Args:
            pipeline: The pipeline definition.

        Returns:
            List of step groups (each group can run in parallel).
        """
        levels: list[list[PipelineStep]] = []
        remaining = set(s.step_id for s in pipeline.steps)
        executed: set[str] = set()

        while remaining:
            current_level = []

            for step_id in list(remaining):
                step = self._get_step(pipeline, step_id)
                if not step:
                    remaining.discard(step_id)
                    continue

                # Check if all dependencies are satisfied
                deps_done = all(dep in executed for dep in step.depends_on)
                if deps_done:
                    current_level.append(step)
                    remaining.discard(step_id)

            if current_level:
                levels.append(current_level)
            else:
                # Circular dependency or error
                break

        return levels

    def _evaluate_condition(
        self,
        condition: str,
        outputs: dict[str, Any],
    ) -> bool:
        """Evaluate a condition expression.

        Args:
            condition: The condition expression.
            outputs: Available step outputs.

        Returns:
            True if condition is satisfied.
        """
        # Simple condition evaluation
        # In a real implementation, this would use a proper expression evaluator
        try:
            # Check for presence of outputs
            for key in outputs:
                if key in condition:
                    return True
            return False
        except Exception:
            return False

    def _merge_parameters(
        self,
        step_params: dict,
        step_outputs: dict[str, Any],
        initial_params: dict,
    ) -> dict:
        """Merge parameters from various sources.

        Args:
            step_params: Parameters defined in step.
            step_outputs: Outputs from previous steps.
            initial_params: Initial pipeline parameters.

        Returns:
            Merged parameters.
        """
        merged = dict(initial_params)

        # Add step parameters
        merged.update(step_params)

        # Add step outputs (keyed by step_id)
        for step_id, output in step_outputs.items():
            merged[f"step_{step_id}_output"] = output

        return merged
