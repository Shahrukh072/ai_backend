"""Prompt management service with versioning support"""
from typing import Dict, Optional, List
from pathlib import Path
import json
import yaml
from datetime import datetime
from app.config import settings
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
import os


class PromptVersion:
    """Represents a versioned prompt"""
    def __init__(
        self,
        name: str,
        content: str,
        version: str,
        metadata: Optional[Dict] = None
    ):
        self.name = name
        self.content = content
        self.version = version
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "content": self.content,
            "version": self.version,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


class PromptService:
    """Service for managing prompts with versioning"""
    
    def __init__(self):
        self.storage_path = Path(settings.PROMPT_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.prompts: Dict[str, List[PromptVersion]] = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompts from storage"""
        if not settings.PROMPT_VERSIONING_ENABLED:
            return
        
        prompts_file = self.storage_path / "prompts.json"
        if prompts_file.exists():
            with open(prompts_file, "r") as f:
                data = json.load(f)
                for name, versions in data.items():
                    self.prompts[name] = [
                        PromptVersion(**v) for v in versions
                    ]
    
    def _save_prompts(self):
        """Save prompts to storage"""
        if not settings.PROMPT_VERSIONING_ENABLED:
            return
        
        prompts_file = self.storage_path / "prompts.json"
        data = {
            name: [v.to_dict() for v in versions]
            for name, versions in self.prompts.items()
        }
        with open(prompts_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def create_prompt(
        self,
        name: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> PromptVersion:
        """Create a new prompt version"""
        versions = self.prompts.get(name, [])
        version = f"v{len(versions) + 1}.0.0"
        
        prompt_version = PromptVersion(
            name=name,
            content=content,
            version=version,
            metadata=metadata
        )
        
        if name not in self.prompts:
            self.prompts[name] = []
        self.prompts[name].append(prompt_version)
        
        self._save_prompts()
        self._commit_to_git(name, version)
        
        return prompt_version
    
    def get_prompt(
        self,
        name: str,
        version: Optional[str] = None
    ) -> Optional[PromptVersion]:
        """Get a prompt by name and optional version"""
        if name not in self.prompts:
            return None
        
        versions = self.prompts[name]
        if not versions:
            return None
        
        if version:
            for v in versions:
                if v.version == version:
                    return v
            return None
        
        # Return latest version
        return versions[-1]
    
    def list_prompts(self) -> List[str]:
        """List all prompt names"""
        return list(self.prompts.keys())
    
    def list_versions(self, name: str) -> List[str]:
        """List all versions for a prompt"""
        if name not in self.prompts:
            return []
        return [v.version for v in self.prompts[name]]
    
    def _commit_to_git(self, name: str, version: str):
        """Commit prompt changes to git if in a git repository"""
        if not GIT_AVAILABLE:
            return
        try:
            repo = git.Repo(search_parent_directories=True)
            if not repo.is_dirty():
                return
            
            # Stage prompt files
            repo.index.add([str(self.storage_path / "prompts.json")])
            
            # Commit
            repo.index.commit(f"Update prompt: {name} {version}")
        except (git.InvalidGitRepositoryError, git.GitCommandError):
            # Not a git repo or git not available
            pass
    
    def get_system_prompt(self, agent_type: str = "default") -> str:
        """Get system prompt for different agent types"""
        prompt_name = f"system_{agent_type}"
        prompt = self.get_prompt(prompt_name)
        
        if prompt:
            return prompt.content
        
        # Default prompts
        default_prompts = {
            "default": """You are a helpful AI assistant with access to document knowledge and tools.
Your goal is to provide accurate, helpful, and safe responses.""",
            "rag": """You are a RAG-powered assistant. Use the provided context to answer questions accurately.
If the context doesn't contain enough information, say so.""",
            "agent": """You are an autonomous agent with access to tools and document knowledge.
You can reason, plan, and execute actions to help users achieve their goals.""",
        }
        
        return default_prompts.get(agent_type, default_prompts["default"])
    
    def format_prompt(
        self,
        template: str,
        **kwargs
    ) -> str:
        """Format a prompt template with variables"""
        return template.format(**kwargs)


# Pre-defined prompt templates
PROMPT_TEMPLATES = {
    "rag_qa": """Based on the following context, answer the question. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {question}

Answer:""",
    
    "react": """You are a helpful assistant that can use tools to answer questions.

Question: {question}

Think step by step:
1. Understand the question
2. Determine if you need to use tools
3. Use tools if needed
4. Synthesize the answer

Let's begin:""",
    
    "plan_execute": """You are a planning agent. Break down the task into steps and execute them.

Task: {task}

First, create a plan:
1. 
2. 
3. 

Then execute each step.""",
    
    "tree_of_thought": """You are solving: {problem}

Consider multiple approaches:
- Approach 1: 
- Approach 2: 
- Approach 3: 

Evaluate each approach and choose the best one."""
}

