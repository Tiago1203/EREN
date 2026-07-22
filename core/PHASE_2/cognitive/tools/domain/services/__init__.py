"""Tools domain services."""
from typing import Protocol
from dataclasses import dataclass

from core.PHASE_2.cognitive.tools.domain.entities import Tool, ToolCall, ToolResult


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())
    
    def get_by_type(self, tool_type: str) -> list[Tool]:
        """Get tools by type."""
        return [t for t in self._tools.values() if t.tool_type.value == tool_type]


class ExecutionContext:
    """Context for tool execution."""
    user_id: str
    tenant_id: str
    conversation_id: str
    approval: bool = False
    
    def __init__(self, user_id: str, tenant_id: str, conversation_id: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.conversation_id = conversation_id


class ToolExecutor(Protocol):
    """Protocol for tool executor."""
    
    async def execute(
        self,
        tool: Tool,
        parameters: dict,
        context: ExecutionContext,
    ) -> ToolResult:
        """Execute a tool."""
        ...


class ToolOrchestrator:
    """Orchestrates tool execution."""
    
    def __init__(
        self,
        registry: ToolRegistry,
        executor: ToolExecutor,
    ):
        self.registry = registry
        self.executor = executor
    
    async def execute_tool(
        self,
        tool_call: ToolCall,
        context: ExecutionContext,
    ) -> ToolResult:
        """Execute a single tool."""
        tool = self.registry.get(tool_call.tool_name)
        if not tool:
            return ToolResult.error(f"Unknown tool: {tool_call.tool_name}")
        
        valid, errors = tool.validate_parameters(tool_call.parameters)
        if not valid:
            return ToolResult.error(f"Invalid parameters: {errors}")
        
        if tool.requires_approval and not context.approval:
            return ToolResult.pending_approval(
                f"Approval required for {tool.name}"
            )
        
        return await self.executor.execute(tool, tool_call.parameters, context)
    
    async def execute_plan(
        self,
        plan: list[ToolCall],
        context: ExecutionContext,
    ) -> list[ToolResult]:
        """Execute a plan with multiple tool calls."""
        results = []
        for tool_call in plan:
            result = await self.execute_tool(tool_call, context)
            results.append(result)
            if not result.success:
                break
        return results
