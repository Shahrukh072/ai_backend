"""Tests for agent service"""
import pytest
from app.ai.agents import AgentService, AgentState
from langchain_core.messages import HumanMessage


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent service initialization"""
    agent = AgentService()
    assert agent is not None
    assert agent.llm_service is not None
    assert agent.tool_service is not None
    assert agent.guardrails is not None


@pytest.mark.asyncio
async def test_agent_run_basic():
    """Test basic agent run"""
    agent = AgentService()
    
    result = await agent.run(
        query="What is 2+2?",
        user_id=1
    )
    
    assert "response" in result
    assert result["response"] is not None
    assert "iterations" in result


@pytest.mark.asyncio
async def test_agent_guardrails():
    """Test guardrails in agent"""
    agent = AgentService()
    
    # This would test guardrails - adjust based on implementation
    state: AgentState = {
        "messages": [HumanMessage(content="Test message")],
        "user_id": 1,
        "document_id": None,
        "iteration_count": 0,
        "context": None,
        "tool_results": []
    }
    
    result_state = await agent._guardrails_node(state)
    assert result_state is not None

