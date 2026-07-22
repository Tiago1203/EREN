"""Tool Sandbox - Sandboxing de herramientas."""

from __future__ import annotations

import asyncio
import os
import subprocess
from typing import Any


class ToolSandbox:
    """
    Sandbox para ejecución segura de herramientas.
    
    Proporciona aislamiento y restricciones de seguridad
    para la ejecución de herramientas.
    """

    def __init__(
        self,
        allowed_paths: list[str] | None = None,
        blocked_commands: list[str] | None = None,
        max_memory_mb: int = 512,
        max_cpu_percent: int = 80,
    ) -> None:
        self._allowed_paths = allowed_paths or []
        self._blocked_commands = blocked_commands or [
            "rm", "del", "format", "shutdown", "reboot",
            "curl", "wget", "nc", "netcat", "ssh",
            "sudo", "su", "chmod", "chown",
        ]
        self._max_memory_mb = max_memory_mb
        self._max_cpu_percent = max_cpu_percent

    def validate_path(self, path: str) -> bool:
        """
        Valida que un path esté permitido.
        
        Args:
            path: Path a validar
            
        Returns:
            True si está permitido
        """
        if not self._allowed_paths:
            return True
        
        abs_path = os.path.abspath(path)
        
        for allowed in self._allowed_paths:
            allowed_abs = os.path.abspath(allowed)
            if abs_path.startswith(allowed_abs):
                return True
        
        return False

    def validate_command(self, command: list[str]) -> tuple[bool, str]:
        """
        Valida que un comando sea seguro.
        
        Args:
            command: Comando a validar (lista de strings)
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not command:
            return False, "Comando vacío"
        
        base_cmd = command[0].lower()
        
        # Verificar comandos bloqueados
        for blocked in self._blocked_commands:
            if base_cmd == blocked or base_cmd.endswith(blocked):
                return False, f"Comando bloqueado: {blocked}"
        
        # Verificar path traversal
        for arg in command:
            if ".." in arg or arg.startswith("~/"):
                if not self.validate_path(arg):
                    return False, f"Path no permitido: {arg}"
        
        return True, ""

    async def execute_python(
        self,
        code: str,
        timeout: int = 30,
    ) -> tuple[str, str, int]:
        """
        Ejecuta código Python en sandbox.
        
        Args:
            code: Código Python a ejecutar
            timeout: Timeout en segundos
            
        Returns:
            Tupla (stdout, stderr, return_code)
        """
        # Validaciones básicas
        blocked_patterns = [
            "import os",
            "import sys",
            "import subprocess",
            "import socket",
            "open(",
            "__import__",
            "eval(",
            "exec(",
            "os.system",
            "os.popen",
            "subprocess.run",
            "subprocess.Popen",
        ]
        
        for pattern in blocked_patterns:
            if pattern in code:
                return "", f"Código bloqueado: {pattern}", 1
        
        try:
            # Ejecutar en proceso separado
            proc = await asyncio.create_subprocess_exec(
                "python3", "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout,
                )
                return (
                    stdout.decode() if stdout else "",
                    stderr.decode() if stderr else "",
                    proc.returncode or 0,
                )
            except asyncio.TimeoutError:
                proc.kill()
                return "", "Timeout de ejecución", 1
        
        except Exception as e:
            return "", str(e), 1

    async def execute_shell(
        self,
        command: str,
        timeout: int = 30,
    ) -> tuple[str, str, int]:
        """
        Ejecuta un comando shell en sandbox.
        
        Args:
            command: Comando a ejecutar
            timeout: Timeout en segundos
            
        Returns:
            Tupla (stdout, stderr, return_code)
        """
        # Parsear comando
        parts = command.split()
        if not parts:
            return "", "Comando vacío", 1
        
        # Validar
        valid, error = self.validate_command(parts)
        if not valid:
            return "", error, 1
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "PATH": "/usr/bin:/bin"},
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout,
                )
                return (
                    stdout.decode() if stdout else "",
                    stderr.decode() if stderr else "",
                    proc.returncode or 0,
                )
            except asyncio.TimeoutError:
                proc.kill()
                return "", "Timeout de ejecución", 1
        
        except Exception as e:
            return "", str(e), 1

    def check_permission(
        self,
        action: str,
        resource: str,
    ) -> bool:
        """
        Verifica permisos para una acción.
        
        Args:
            action: Acción (read, write, execute, delete)
            resource: Recurso afectado
            
        Returns:
            True si está permitido
        """
        # Verificar paths de archivo
        if action in ("read", "write", "delete"):
            return self.validate_path(resource)
        
        # Verificar comandos
        if action == "execute":
            # Validar que no sea un ejecutable del sistema
            blocked_paths = [
                "/bin", "/sbin", "/usr/bin", "/usr/sbin",
            ]
            for blocked in blocked_paths:
                if resource.startswith(blocked):
                    return False
            return True
        
        return True


class SandboxContext:
    """Contexto de sandbox para una ejecución."""

    def __init__(self, sandbox: ToolSandbox) -> None:
        self._sandbox = sandbox
        self._violations: list[str] = []

    def record_violation(self, message: str) -> None:
        """Registra una violación de sandbox."""
        self._violations.append(message)

    @property
    def violations(self) -> list[str]:
        """Obtiene todas las violaciones."""
        return self._violations.copy()

    @property
    def is_secure(self) -> bool:
        """Verifica si el contexto es seguro."""
        return len(self._violations) == 0
