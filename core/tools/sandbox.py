"""Tool Sandbox for EREN OS Universal Tool Calling Engine.

Provides secure execution environment for tool execution.
"""

from __future__ import annotations

import asyncio
import os
import resource
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

if True:
    pass


# =============================================================================
# Sandbox Types
# =============================================================================


class SandboxType(str, Enum):
    """Types of sandboxed execution."""

    PROCESS = "process"  # Separate process
    THREAD = "thread"  # Separate thread (limited isolation)
    CONTAINER = "container"  # Container-based (future)
    VM = "vm"  # Virtual machine (future)


class SandboxState(str, Enum):
    """State of sandbox."""

    READY = "ready"
    RUNNING = "running"
    TERMINATED = "terminated"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class SandboxConfig:
    """Configuration for sandbox."""

    sandbox_type: SandboxType = SandboxType.PROCESS
    timeout_seconds: float = 30.0
    memory_limit_mb: int = 512
    cpu_limit_percent: float = 50.0
    network_enabled: bool = True
    filesystem_readonly: bool = False
    allow_subprocess: bool = False
    environment_vars: dict = field(default_factory=dict)


@dataclass
class SandboxMetrics:
    """Metrics for sandbox execution."""

    execution_id: str
    start_time: datetime
    end_time: datetime | None = None
    peak_memory_mb: float = 0.0
    cpu_time_seconds: float = 0.0
    wall_time_seconds: float = 0.0
    syscalls: int = 0
    state: SandboxState = SandboxState.READY


# =============================================================================
# Sandbox Base
# =============================================================================


class ToolSandbox(ABC):
    """Abstract base for tool sandbox."""

    def __init__(self, config: SandboxConfig | None = None):
        """Initialize sandbox.

        Args:
            config: Sandbox configuration.
        """
        self._config = config or SandboxConfig()
        self._state = SandboxState.READY
        self._metrics: SandboxMetrics | None = None

    @property
    def config(self) -> SandboxConfig:
        """Get sandbox configuration."""
        return self._config

    @property
    def state(self) -> SandboxState:
        """Get current state."""
        return self._state

    @abstractmethod
    async def execute(self, func, *args, **kwargs) -> Any:
        """Execute function in sandbox.

        Args:
            func: Function to execute.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Function result.

        Raises:
            SandboxError: If execution fails.
        """
        pass

    @abstractmethod
    async def terminate(self) -> None:
        """Terminate sandbox execution."""
        pass


class ProcessSandbox(ToolSandbox):
    """Sandbox using separate process."""

    def __init__(self, config: SandboxConfig | None = None):
        """Initialize process sandbox."""
        super().__init__(config)
        self._process: asyncio.subprocess.Process | None = None
        self._task: asyncio.Task | None = None

    async def execute(self, func, *args, **kwargs) -> Any:
        """Execute function in separate process."""
        self._state = SandboxState.RUNNING

        try:
            # Create execution payload
            import pickle
            import base64

            payload = base64.b64encode(pickle.dumps((func, args, kwargs))).decode()

            # Execute in subprocess
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    "python",
                    "-c",
                    f"import pickle,base64, marshal; "
                    f"d=pickle.loads(base64.b64decode('{payload}')); "
                    f"r=marshal.loads(marshal.dumps(d[0](*d[1],**d[2]))); "
                    f"print(base64.b64encode(pickle.dumps(r)).decode())",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                ),
                timeout=self._config.timeout_seconds,
            )

            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                raise Exception(f"Execution failed: {stderr.decode()}")

            return pickle.loads(base64.b64decode(stdout.decode()))

        except asyncio.TimeoutError:
            self._state = SandboxState.TIMEOUT
            raise TimeoutError(f"Sandbox execution timed out after {self._config.timeout_seconds}s")
        except Exception as e:
            self._state = SandboxState.ERROR
            raise Exception(f"Sandbox execution error: {e}")
        finally:
            self._state = SandboxState.READY

    async def terminate(self) -> None:
        """Terminate process."""
        if self._process:
            self._process.terminate()
            await self._process.wait()


class ThreadSandbox(ToolSandbox):
    """Sandbox using separate thread with resource limits."""

    def __init__(self, config: SandboxConfig | None = None):
        """Initialize thread sandbox."""
        super().__init__(config)
        self._result: tuple[Any, Exception | None] = (None, None)
        self._thread: threading.Thread | None = None
        self._event = threading.Event()

    async def execute(self, func, *args, **kwargs) -> Any:
        """Execute function in limited thread."""
        self._state = SandboxState.RUNNING

        def worker():
            try:
                # Apply resource limits if on Unix
                try:
                    # Memory limit
                    memory_bytes = self._config.memory_limit_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

                    # CPU limit
                    cpu_percent = self._config.cpu_limit_percent / 100
                    resource.setrlimit(resource.RLIMIT_CPU, (int(cpu_percent * 100), int(cpu_percent * 100)))
                except Exception:
                    pass  # Limits not supported on this platform

                result = func(*args, **kwargs)
                self._result = (result, None)
            except Exception as e:
                self._result = (None, e)
            finally:
                self._event.set()

        self._thread = threading.Thread(target=worker)
        self._thread.start()

        # Wait with timeout
        try:
            await asyncio.wait_for(
                asyncio.wrap_future(asyncio.Future(loop=asyncio.get_event_loop())),
                timeout=self._config.timeout_seconds,
            )
            # Check event manually
            while not self._event.is_set() and self._thread.is_alive():
                await asyncio.sleep(0.1)

            if self._thread.is_alive():
                self._state = SandboxState.TIMEOUT
                raise TimeoutError(f"Sandbox execution timed out after {self._config.timeout_seconds}s")

            self._thread.join()

            result, error = self._result
            if error:
                raise error

            return result

        except asyncio.TimeoutError:
            self._state = SandboxState.TIMEOUT
            if self._thread:
                self._thread.join(timeout=0.1)
            raise TimeoutError(f"Sandbox execution timed out after {self._config.timeout_seconds}s")
        finally:
            self._state = SandboxState.READY

    async def terminate(self) -> None:
        """Terminate thread (best effort)."""
        self._state = SandboxState.TERMINATED


# =============================================================================
# Sandbox Manager
# =============================================================================


class SandboxManager:
    """Manages sandbox instances for tool execution."""

    def __init__(self):
        """Initialize sandbox manager."""
        self._sandboxes: dict[str, ToolSandbox] = {}
        self._lock = threading.RLock()

    def get_sandbox(
        self,
        sandbox_id: str,
        sandbox_type: SandboxType = SandboxType.PROCESS,
        config: SandboxConfig | None = None,
    ) -> ToolSandbox:
        """Get or create sandbox.

        Args:
            sandbox_id: Unique sandbox identifier.
            sandbox_type: Type of sandbox.
            config: Sandbox configuration.

        Returns:
            Sandbox instance.
        """
        with self._lock:
            if sandbox_id in self._sandboxes:
                return self._sandboxes[sandbox_id]

            if sandbox_type == SandboxType.PROCESS:
                sandbox = ProcessSandbox(config)
            elif sandbox_type == SandboxType.THREAD:
                sandbox = ThreadSandbox(config)
            else:
                sandbox = ThreadSandbox(config)  # Default

            self._sandboxes[sandbox_id] = sandbox
            return sandbox

    def release_sandbox(self, sandbox_id: str) -> None:
        """Release sandbox.

        Args:
            sandbox_id: Sandbox identifier.
        """
        with self._lock:
            if sandbox_id in self._sandboxes:
                sandbox = self._sandboxes[sandbox_id]
                try:
                    asyncio.run(sandbox.terminate())
                except Exception:
                    pass
                del self._sandboxes[sandbox_id]

    async def execute_in_sandbox(
        self,
        sandbox_id: str,
        func,
        *args,
        sandbox_type: SandboxType = SandboxType.PROCESS,
        config: SandboxConfig | None = None,
        **kwargs,
    ) -> Any:
        """Execute function in sandbox.

        Args:
            sandbox_id: Sandbox identifier.
            func: Function to execute.
            *args: Positional arguments.
            sandbox_type: Type of sandbox.
            config: Sandbox configuration.
            **kwargs: Keyword arguments.

        Returns:
            Function result.
        """
        sandbox = self.get_sandbox(sandbox_id, sandbox_type, config)
        return await sandbox.execute(func, *args, **kwargs)

    def list_sandboxes(self) -> list[str]:
        """List active sandbox IDs."""
        with self._lock:
            return list(self._sandboxes.keys())

    def shutdown(self) -> None:
        """Shutdown all sandboxes."""
        with self._lock:
            for sandbox_id in list(self._sandboxes.keys()):
                self.release_sandbox(sandbox_id)
