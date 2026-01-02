"""Tool/Function calling service with MCP and A2A support"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool, tool
from app.config import settings
from pydantic import BaseModel, Field
import json
import httpx
from datetime import datetime

# Optional community tools - may have compatibility issues with Python 3.14
DUCKDUCKGO_AVAILABLE = False
WIKIPEDIA_AVAILABLE = False
DuckDuckGoSearchRun = None
WikipediaQueryRun = None
WikipediaAPIWrapper = None

try:
    from langchain_community.tools import DuckDuckGoSearchRun
    DUCKDUCKGO_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    pass

try:
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper
    WIKIPEDIA_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    pass


class CalculatorInput(BaseModel):
    """Input for calculator tool"""
    expression: str = Field(description="Mathematical expression to evaluate")


class WebSearchInput(BaseModel):
    """Input for web search tool"""
    query: str = Field(description="Search query")


class ToolService:
    """Service for managing and executing tools/functions for agents"""
    
    def __init__(self):
        self.tools: List[BaseTool] = []
        self.mcp_tools: Dict[str, Any] = {}
        self.a2a_tools: Dict[str, Any] = {}
        self._initialize_default_tools()
    
    def _initialize_default_tools(self):
        """Initialize default tools"""
        # Calculator tool
        @tool("calculator", args_schema=CalculatorInput)
        async def calculator(expression: str) -> str:
            """Evaluate a mathematical expression safely"""
            try:
                # Safe evaluation - only allow basic math operations
                allowed_chars = set("0123456789+-*/.() ")
                if not all(c in allowed_chars for c in expression):
                    return "Error: Invalid characters in expression"
                result = eval(expression, {"__builtins__": {}})
                return str(result)
            except Exception as e:
                return f"Error: {str(e)}"
        
        self.tools.append(calculator)
        
        # Web search tool (optional)
        if DUCKDUCKGO_AVAILABLE and DuckDuckGoSearchRun:
            @tool("web_search", args_schema=WebSearchInput)
            async def web_search(query: str) -> str:
                """Search the web for current information"""
                try:
                    search = DuckDuckGoSearchRun()
                    result = await search.ainvoke(query)
                    return result
                except Exception as e:
                    return f"Search error: {str(e)}"
            
            self.tools.append(web_search)
        else:
            # Fallback web search tool
            @tool("web_search", args_schema=WebSearchInput)
            async def web_search(query: str) -> str:
                """Search the web for current information (limited functionality)"""
                return f"Web search is not available. Query: {query}"
            
            self.tools.append(web_search)
        
        # Wikipedia tool (optional)
        if WIKIPEDIA_AVAILABLE and WikipediaQueryRun and WikipediaAPIWrapper:
            @tool("wikipedia_search")
            async def wikipedia_search(query: str) -> str:
                """Search Wikipedia for information"""
                try:
                    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
                    result = await wiki.ainvoke(query)
                    return result
                except Exception as e:
                    return f"Wikipedia error: {str(e)}"
            
            self.tools.append(wikipedia_search)
        else:
            # Fallback Wikipedia tool
            @tool("wikipedia_search")
            async def wikipedia_search(query: str) -> str:
                """Search Wikipedia for information (limited functionality)"""
                return f"Wikipedia search is not available. Query: {query}"
            
            self.tools.append(wikipedia_search)
        
        # Current time tool
        @tool("get_current_time")
        async def get_current_time() -> str:
            """Get the current date and time"""
            return datetime.now().isoformat()
        
        self.tools.append(get_current_time)
    
    async def get_available_tools(self) -> List[BaseTool]:
        """Get all available tools"""
        all_tools = self.tools.copy()
        
        # Add MCP tools if enabled
        if settings.AGENT_ENABLE_MCP:
            all_tools.extend(list(self.mcp_tools.values()))
        
        # Add A2A tools if enabled
        if settings.AGENT_ENABLE_A2A:
            all_tools.extend(list(self.a2a_tools.values()))
        
        return all_tools
    
    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool by name"""
        # Find tool
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool and tool_name in self.mcp_tools:
            tool = self.mcp_tools[tool_name]
        
        if not tool and tool_name in self.a2a_tools:
            tool = self.a2a_tools[tool_name]
        
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Execute tool
        if hasattr(tool, "ainvoke"):
            result = await tool.ainvoke(args)
        else:
            result = await tool.invoke(args)
        
        return result
    
    def register_mcp_tool(self, name: str, tool: BaseTool):
        """Register an MCP (Model Context Protocol) tool"""
        self.mcp_tools[name] = tool
    
    def register_a2a_tool(self, name: str, tool: BaseTool):
        """Register an A2A (Agent-to-Agent) tool"""
        self.a2a_tools[name] = tool
    
    def create_custom_tool(
        self,
        name: str,
        description: str,
        func: callable,
        args_schema: Optional[BaseModel] = None
    ) -> BaseTool:
        """Create a custom tool"""
        return tool(name, description=description, args_schema=args_schema)(func)


# Example custom tools for document operations
@tool("get_document_summary")
async def get_document_summary(document_id: int) -> str:
    """Get a summary of a document"""
    # This would integrate with your document service
    return f"Summary for document {document_id}"


@tool("search_documents")
async def search_documents(query: str, user_id: int) -> str:
    """Search user's documents"""
    # This would integrate with your document service
    return f"Search results for '{query}' in user {user_id}'s documents"
