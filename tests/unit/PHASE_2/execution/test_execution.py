"""Tests for Execution Runtime (PR-054)."""

import pytest
from core.PHASE_2.execution.cognitive_execution_integration import (
    ExecutionRuntime,
    ExecutableTask,
    ExecutionStatus,
    ExecutionEvent,
    ExecutionEventType,
)


class TestExecutionRuntime:
    def test_register_task(self):
        runtime = ExecutionRuntime()
        task = ExecutableTask(
            id="task1",
            name="Test Task",
            handler=lambda: "result",
        )
        runtime.register_task(task)
        assert "task1" in runtime._tasks

    def test_execute_task_success(self):
        runtime = ExecutionRuntime()
        runtime.register_task(ExecutableTask(
            id="task1",
            name="Test",
            handler=lambda: "success",
        ))
        result = runtime.execute_task("task1")
        assert result["success"] is True
        assert result["result"] == "success"

    def test_execute_task_with_args(self):
        runtime = ExecutionRuntime()
        runtime.register_task(ExecutableTask(
            id="add",
            name="Add",
            handler=lambda a, b: a + b,
            args=(2, 3),
        ))
        result = runtime.execute_task("add")
        assert result["success"] is True
        assert result["result"] == 5

    def test_execute_task_not_found(self):
        runtime = ExecutionRuntime()
        result = runtime.execute_task("nonexistent")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_execute_task_failure(self):
        runtime = ExecutionRuntime()
        runtime.register_task(ExecutableTask(
            id="fail",
            name="Fail",
            handler=lambda: 1/0,
        ))
        result = runtime.execute_task("fail")
        assert result["success"] is False
        assert "division" in result["error"].lower()

    def test_cancel_task(self):
        runtime = ExecutionRuntime()
        runtime.register_task(ExecutableTask(
            id="task1",
            name="Test",
            handler=lambda: "result",
        ))
        runtime.cancel_task("task1")
        assert runtime.get_status("task1") == ExecutionStatus.CANCELLED

    def test_events(self):
        runtime = ExecutionRuntime()
        events = []
        runtime.subscribe(lambda e: events.append(e))
        runtime.register_task(ExecutableTask(
            id="task1",
            name="Test",
            handler=lambda: "result",
        ))
        runtime.execute_task("task1")
        assert len(events) >= 1
