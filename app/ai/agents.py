"""LangGraph-based agentic workflow service with stateful graphs"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
import uuid
from langchain_core.tools import BaseTool
from app.ai.llm import LLMService
from app.ai.rag import EnhancedRAGService
from app.ai.tools import ToolService
from app.services.guardrails_service import GuardrailsService
from app.config import settings, LLMProvider
import operator
import asyncio


class AgentState(TypedDict):
    """State for the agentic workflow"""
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: int
    document_id: Optional[int]
    iteration_count: int
    context: Optional[str]
    tool_results: List[Dict[str, Any]]
    guardrails_rejected: bool


class AgentService:
    """LangGraph-based agentic workflow service"""
    
    def __init__(self, db_session=None):
        self.llm_service = LLMService()
        self.rag_service = EnhancedRAGService(db_session) if db_session else None
        self.tool_service = ToolService()
        self.guardrails = GuardrailsService()
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("guardrails", self._guardrails_node)
        workflow.add_node("rag_retrieval", self._rag_retrieval_node)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tool_execution", self._tool_execution_node)
        workflow.add_node("response_generation", self._response_generation_node)
        
        # Set entry point
        workflow.set_entry_point("guardrails")
        
        # Add edges
        workflow.add_conditional_edges(
            "guardrails",
            self._should_continue_after_guardrails,
            {
                "continue": "rag_retrieval",
                "reject": END
            }
        )
        workflow.add_conditional_edges(
            "rag_retrieval",
            self._should_use_rag,
            {
                "use_rag": "agent",
                "skip_rag": "agent"
            }
        )
        workflow.add_conditional_edges(
            "agent",
            self._should_use_tools,
            {
                "use_tools": "tool_execution",
                "no_tools": "response_generation"
            }
        )
        workflow.add_edge("tool_execution", "agent")
        workflow.add_edge("response_generation", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _guardrails_node(self, state: AgentState) -> AgentState:
        """Apply guardrails to user input"""
        state["guardrails_rejected"] = False
        if not settings.GUARDRAILS_ENABLED:
            return state
        
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            is_safe, reason = await self.guardrails.check_input(last_message.content)
            if not is_safe:
                state["messages"].append(
                    AIMessage(content=f"Input rejected: {reason}")
                )
                state["guardrails_rejected"] = True
                return state
        
        return state
    
    def _should_continue_after_guardrails(self, state: AgentState) -> str:
        """Determine if execution should continue after guardrails check"""
        if state.get("guardrails_rejected", False):
            return "reject"
        return "continue"
    
    async def _rag_retrieval_node(self, state: AgentState) -> AgentState:
        """Retrieve relevant context using RAG"""
        if not self.rag_service:
            return state
        
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            try:
                context = await self.rag_service.get_relevant_context(
                    query=last_message.content,
                    user_id=state["user_id"],
                    document_id=state.get("document_id"),
                    top_k=settings.RAG_TOP_K
                )
                state["context"] = context
            except Exception as e:
                state["context"] = f"Error retrieving context: {str(e)}"
        
        return state
    
    def _should_use_rag(self, state: AgentState) -> str:
        """Determine if RAG context should be used"""
        return "use_rag" if state.get("context") else "skip_rag"
    
    async def _agent_node(self, state: AgentState) -> AgentState:
        """Main agent reasoning node"""
        messages = state["messages"].copy()
        
        # Add RAG context if available
        if state.get("context"):
            context_msg = SystemMessage(
                content=f"Relevant context from documents:\n{state['context']}"
            )
            messages.insert(-1, context_msg)
        
        # Add system prompt
        system_prompt = SystemMessage(
            content=self._get_system_prompt()
        )
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages.insert(0, system_prompt)
        
        # Check iteration limit
        if state.get("iteration_count", 0) >= settings.AGENT_MAX_ITERATIONS:
            messages.append(
                AIMessage(content="Maximum iterations reached. Please try a simpler query.")
            )
            return state
        
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        
        # Get tools if enabled (but not for Groq - it doesn't support function calling)
        tools = []
        if settings.AGENT_ENABLE_TOOLS and self.llm_service.provider != LLMProvider.GROQ:
            tools = await self.tool_service.get_available_tools()
        
        # Generate response with or without tools
        if tools:
            try:
                response = await self.llm_service.generate_with_tools(messages, tools)
            except Exception as tool_error:
                # If tool calling fails (e.g., Groq doesn't support it), fall back to regular generation
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(f"Tool calling failed, falling back to regular generation: {tool_error}")
                response = await self.llm_service.generate(messages)
                response = AIMessage(content=response)
        else:
            response = await self.llm_service.generate(messages)
            response = AIMessage(content=response)
        
        state["messages"].append(response)
        return state
    
    def _should_use_tools(self, state: AgentState) -> str:
        """Determine if tools should be executed"""
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls"):
            if last_message.tool_calls:
                return "use_tools"
        return "no_tools"
    
    async def _tool_execution_node(self, state: AgentState) -> AgentState:
        """Execute tools called by the agent"""
        last_message = state["messages"][-1]
        tool_results = []
        
        if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls"):
            for tool_call in last_message.tool_calls:
                try:
                    result = await self.tool_service.execute_tool(
                        tool_call["name"],
                        tool_call.get("args", {})
                    )
                    tool_results.append({
                        "tool": tool_call["name"],
                        "result": result
                    })
                    state["messages"].append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        )
                    )
                except Exception as e:
                    state["messages"].append(
                        ToolMessage(
                            content=f"Error executing tool: {str(e)}",
                            tool_call_id=tool_call["id"]
                        )
                    )
        
        state["tool_results"] = tool_results
        return state
    
    async def _response_generation_node(self, state: AgentState) -> AgentState:
        """Generate final response"""
        # Apply guardrails to output
        if settings.GUARDRAILS_ENABLED:
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage):
                is_safe, reason = await self.guardrails.check_output(last_message.content)
                if not is_safe:
                    # Create new message instead of mutating
                    filtered_message = AIMessage(
                        content=f"Response filtered: {reason}",
                        **{k: v for k, v in last_message.__dict__.items() if k != 'content'}
                    )
                    state["messages"][-1] = filtered_message
        
        return state
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are a helpful AI assistant with access to document knowledge and tools.
        
Your capabilities:
- Answer questions based on retrieved document context
- Use tools to perform actions when needed
- Provide clear, accurate, and helpful responses

Guidelines:
- If you don't know something, say so
- Use retrieved context when available
- Execute tools when appropriate
- Be concise but thorough"""
    
    async def run(
        self,
        query: str,
        user_id: int,
        document_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run the agentic workflow"""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "user_id": user_id,
            "document_id": document_id,
            "iteration_count": 0,
            "context": None,
            "tool_results": [],
            "guardrails_rejected": False
        }
        
        config = config or {}
        # Checkpointer requires thread_id - generate one if not provided
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        config["configurable"] = {"thread_id": thread_id}
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state, config)
        
        # Extract final response
        last_message = final_state["messages"][-1]
        response_text = last_message.content if isinstance(last_message, AIMessage) else ""
        
        return {
            "response": response_text,
            "messages": final_state["messages"],
            "tool_results": final_state.get("tool_results", []),
            "iterations": final_state.get("iteration_count", 0),
            "context_used": final_state.get("context") is not None
        }
    
    async def stream(
        self,
        query: str,
        user_id: int,
        document_id: Optional[int] = None,
        thread_id: Optional[str] = None
    ):
        """Stream the agentic workflow execution"""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "user_id": user_id,
            "document_id": document_id,
            "iteration_count": 0,
            "context": None,
            "tool_results": [],
            "guardrails_rejected": False
        }
        
        config = {}
        # Checkpointer requires thread_id - generate one if not provided
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        config["configurable"] = {"thread_id": thread_id}
        
        async for event in self.graph.astream(initial_state, config):
            yield event

