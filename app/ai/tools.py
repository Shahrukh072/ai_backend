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
                # Validate input - reject dangerous operations
                if "**" in expression or "pow(" in expression.lower() or "exec(" in expression.lower() or "eval(" in expression.lower():
                    return "Error: Power operator and function calls are not allowed"
                
                if len(expression) > 100:
                    return "Error: Expression too long"
                
                # Only allow basic math operations
                allowed_chars = set("0123456789+-*/.() ")
                if not all(c in allowed_chars for c in expression):
                    return "Error: Invalid characters in expression"
                
                # Use operator module for safe evaluation
                import operator
                import ast
                
                # Parse AST and validate
                tree = ast.parse(expression, mode='eval')
                for node in ast.walk(tree):
                    # Only allow basic operations
                    if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Constant)):
                        continue
                    elif isinstance(node, ast.BinOp):
                        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                            continue
                        else:
                            return "Error: Only +, -, *, / operations are allowed"
                    else:
                        return "Error: Only basic arithmetic operations are allowed"
                
                # Safe evaluation using operator module
                ops = {
                    ast.Add: operator.add,
                    ast.Sub: operator.sub,
                    ast.Mult: operator.mul,
                    ast.Div: operator.truediv,
                    ast.USub: operator.neg,
                }
                
                def eval_node(node):
                    if isinstance(node, ast.Constant):
                        return node.value
                    elif isinstance(node, ast.BinOp):
                        return ops[type(node.op)](eval_node(node.left), eval_node(node.right))
                    elif isinstance(node, ast.UnaryOp):
                        return ops[type(node.op)](eval_node(node.operand))
                    else:
                        raise ValueError("Unsupported operation")
                
                result = eval_node(tree.body)
                return str(result)
            except SyntaxError:
                return "Error: Invalid expression syntax"
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
        
        if not tool and settings.AGENT_ENABLE_MCP and tool_name in self.mcp_tools:
            tool = self.mcp_tools[tool_name]
        
        if not tool and settings.AGENT_ENABLE_A2A and tool_name in self.a2a_tools:
            tool = self.a2a_tools[tool_name]
        
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Execute tool
        import inspect
        import asyncio
        
        if hasattr(tool, "ainvoke"):
            result = await tool.ainvoke(args)
        else:
            result = tool.invoke(args)
            # Check if result is awaitable and await if needed
            if inspect.isawaitable(result):
                result = await result
        
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
