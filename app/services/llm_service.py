"""Enhanced LLM Service with multi-provider support (OpenAI, Vertex AI, AWS Bedrock)"""
from typing import Optional, List, Dict, Any, AsyncIterator
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.callbacks import AsyncCallbackHandler
from app.config import settings, LLMProvider
import os

# Optional imports for providers
try:
    from langchain_google_vertexai import ChatVertexAI
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    ChatVertexAI = None

try:
    from langchain_aws import ChatBedrock
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    ChatBedrock = None


class LLMService:
    """Multi-provider LLM service supporting OpenAI, Vertex AI, and AWS Bedrock"""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.llm = self._initialize_llm()
        self._setup_langsmith()
    
    def _setup_langsmith(self):
        """Configure LangSmith tracing if enabled"""
        if settings.LANGSMITH_TRACING and settings.LANGSMITH_API_KEY:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
    
    def _initialize_llm(self) -> BaseChatModel:
        """Initialize LLM based on provider"""
        if self.provider == LLMProvider.OPENAI:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.7,
                streaming=True,
                api_key=settings.OPENAI_API_KEY
            )
        
        elif self.provider == LLMProvider.VERTEX_AI:
            if not VERTEX_AI_AVAILABLE:
                raise ImportError(
                    "langchain-google-vertexai is not installed. "
                    "Install it with: pip install langchain-google-vertexai"
                )
            if not settings.GOOGLE_CLOUD_PROJECT:
                raise ValueError("GOOGLE_CLOUD_PROJECT is required for Vertex AI provider")
            return ChatVertexAI(
                model_name=settings.VERTEX_AI_MODEL,
                temperature=0.7,
                streaming=True,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
        
        elif self.provider == LLMProvider.AWS_BEDROCK:
            if not BEDROCK_AVAILABLE:
                raise ImportError(
                    "langchain-aws is not installed. "
                    "Install it with: pip install langchain-aws"
                )
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                raise ValueError("AWS credentials are required for Bedrock provider")
            return ChatBedrock(
                model_id=settings.BEDROCK_MODEL,
                region_name=settings.AWS_REGION,
                credentials_profile_name=None,
                streaming=True
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from the LLM"""
        response = await self.llm.ainvoke(
            messages,
            temperature=temperature or 0.7,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.content
    
    async def stream(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream responses from the LLM"""
        async for chunk in self.llm.astream(
            messages,
            temperature=temperature or 0.7,
            **kwargs
        ):
            yield chunk.content
    
    async def generate_with_tools(
        self,
        messages: List[BaseMessage],
        tools: List[Any],
        **kwargs
    ) -> Any:
        """Generate response with tool/function calling support"""
        llm_with_tools = self.llm.bind_tools(tools)
        response = await llm_with_tools.ainvoke(messages, **kwargs)
        return response
    
    def get_model_name(self) -> str:
        """Get the current model name"""
        if self.provider == LLMProvider.OPENAI:
            return settings.OPENAI_MODEL
        elif self.provider == LLMProvider.VERTEX_AI:
            return settings.VERTEX_AI_MODEL
        elif self.provider == LLMProvider.AWS_BEDROCK:
            return settings.BEDROCK_MODEL
        return "unknown"
