"""LLM evaluation tests using langsmith"""
import pytest
from app.ai.llm import LLMService
from langchain_core.messages import HumanMessage, SystemMessage


@pytest.mark.asyncio
async def test_llm_response_quality():
    """Test LLM response quality using evaluation"""
    llm_service = LLMService()
    
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is the capital of France?")
    ]
    
    response = await llm_service.generate(messages)
    
    # Basic assertions
    assert response is not None
    assert len(response) > 0
    assert "Paris" in response or "paris" in response.lower()


@pytest.mark.asyncio
async def test_llm_with_tools():
    """Test LLM with tool calling"""
    llm_service = LLMService()
    
    # This would test tool calling - adjust based on implementation
    messages = [HumanMessage(content="Calculate 5 + 3")]
    
    # If tools are available
    # response = await llm_service.generate_with_tools(messages, tools)
    # assert response is not None


@pytest.mark.asyncio
async def test_llm_streaming():
    """Test LLM streaming"""
    llm_service = LLMService()
    
    messages = [HumanMessage(content="Say hello")]
    
    chunks = []
    async for chunk in llm_service.stream(messages):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    assert "".join(chunks) is not None

