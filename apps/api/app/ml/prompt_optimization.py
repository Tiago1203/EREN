"""
Prompt Optimization Module

Library, versioning, and optimization of prompts.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class PromptType(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class PromptVersion(BaseModel):
    """Versioned prompt."""
    id: str
    prompt_id: str
    version: int
    content: str
    created_at: datetime
    created_by: str
    metrics: Dict[str, float] = {}
    is_active: bool = False


class Prompt(BaseModel):
    """Prompt with versioning."""
    id: str
    name: str
    type: PromptType
    description: str
    current_version: int = 1
    versions: List[PromptVersion] = []


class PromptLibrary:
    """Library of optimized prompts."""
    
    def __init__(self):
        self.prompts: Dict[str, Prompt] = {}
        self._init_default_prompts()
    
    def _init_default_prompts(self):
        """Initialize default prompts."""
        self.prompts["clinical_reasoning"] = Prompt(
            id="clinical_reasoning",
            name="Clinical Reasoning",
            type=PromptType.SYSTEM,
            description="System prompt for clinical reasoning",
            versions=[
                PromptVersion(
                    id="cr-v1",
                    prompt_id="clinical_reasoning",
                    version=1,
                    content="You are a clinical AI assistant...",
                    created_at=datetime.utcnow(),
                    created_by="system",
                    is_active=True
                )
            ]
        )
    
    async def create_prompt(self, name: str, content: str, prompt_type: PromptType, description: str = "") -> Prompt:
        """Create new prompt."""
        prompt = Prompt(
            id=name.lower().replace(" ", "_"),
            name=name,
            type=prompt_type,
            description=description,
            versions=[
                PromptVersion(
                    id=f"{name}-v1",
                    prompt_id=name,
                    version=1,
                    content=content,
                    created_at=datetime.utcnow(),
                    created_by="user",
                    is_active=True
                )
            ]
        )
        self.prompts[prompt.id] = prompt
        return prompt
    
    async def get_active_prompt(self, prompt_id: str) -> Optional[str]:
        """Get active version of prompt."""
        prompt = self.prompts.get(prompt_id)
        if not prompt:
            return None
        
        for version in prompt.versions:
            if version.is_active:
                return version.content
        return None
    
    async def update_prompt(self, prompt_id: str, content: str, created_by: str) -> PromptVersion:
        """Create new version of prompt."""
        prompt = self.prompts.get(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        # Deactivate current version
        for version in prompt.versions:
            version.is_active = False
        
        # Create new version
        new_version = PromptVersion(
            id=f"{prompt_id}-v{prompt.current_version + 1}",
            prompt_id=prompt_id,
            version=prompt.current_version + 1,
            content=content,
            created_at=datetime.utcnow(),
            created_by=created_by,
            is_active=True
        )
        
        prompt.versions.append(new_version)
        prompt.current_version += 1
        
        return new_version


class PromptVersioning:
    """Prompt versioning and rollback."""
    
    async def rollback(self, prompt_library: PromptLibrary, prompt_id: str, version: int) -> bool:
        """Rollback to previous version."""
        prompt = prompt_library.prompts.get(prompt_id)
        if not prompt:
            return False
        
        for v in prompt.versions:
            v.is_active = (v.version == version)
        
        return True
    
    async def get_version_history(self, prompt_library: PromptLibrary, prompt_id: str) -> List[Dict]:
        """Get version history."""
        prompt = prompt_library.prompts.get(prompt_id)
        if not prompt:
            return []
        
        return [
            {
                "version": v.version,
                "created_at": v.created_at,
                "created_by": v.created_by,
                "is_active": v.is_active,
                "metrics": v.metrics
            }
            for v in prompt.versions
        ]


class PromptMetrics:
    """Metrics for prompt effectiveness."""
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict]] = {}
    
    async def record(self, prompt_id: str, version: int, metrics: Dict[str, float]):
        """Record metrics for prompt."""
        if prompt_id not in self.metrics:
            self.metrics[prompt_id] = []
        
        self.metrics[prompt_id].append({
            "version": version,
            "timestamp": datetime.utcnow(),
            **metrics
        })
    
    async def get_effectiveness(self, prompt_id: str) -> Dict[str, float]:
        """Get effectiveness score for prompt."""
        records = self.metrics.get(prompt_id, [])
        if not records:
            return {}
        
        latest = records[-1]
        return {
            "accuracy": latest.get("accuracy", 0),
            "user_satisfaction": latest.get("user_satisfaction", 0),
            "latency": latest.get("latency", 0)
        }
