# Re-export AgentService from ai.agents for backward compatibility
from app.ai.agents import AgentService

__all__ = ["AgentService"]
