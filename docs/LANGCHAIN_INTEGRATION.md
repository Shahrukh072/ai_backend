# LangChain Integration Documentation

This document provides a comprehensive overview of how LangChain is integrated and used throughout this AI backend project.

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [LLM Service Integration](#llm-service-integration)
4. [RAG Service Integration](#rag-service-integration)
5. [Agent Service (LangGraph)](#agent-service-langgraph)
6. [Tool Service](#tool-service)
7. [Text Splitting](#text-splitting)
8. [Vector Stores](#vector-stores)
9. [LangSmith Observability](#langsmith-observability)
10. [Configuration](#configuration)
11. [Usage Examples](#usage-examples)
12. [Architecture Flow](#architecture-flow)

---

## Overview

LangChain is the core framework powering this AI backend, providing:

- **Multi-provider LLM support**: OpenAI, Google Vertex AI, AWS Bedrock
- **RAG (Retrieval-Augmented Generation)**: Document retrieval and context injection
- **Agentic workflows**: LangGraph-based stateful agent systems
- **Tool/Function calling**: Extensible tool system for agent capabilities
- **Vector stores**: FAISS and Chroma integration for semantic search
- **Text processing**: Document chunking and splitting
- **Observability**: LangSmith tracing and monitoring

### Key LangChain Packages Used

```python
# Core LangChain
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.4.0

# Provider-specific integrations
langchain-openai>=0.2.0
langchain-google-vertexai>=2.0.0  # Optional
langchain-aws>=0.2.0  # Optional

# Text processing
langchain-text-splitters>=0.3.0

# LangGraph for agentic workflows
langgraph>=0.2.0  # Implicit via agent service
```

---

## Core Components

### 1. LLM Service (`app/services/llm_service.py`)

The LLM Service provides a unified interface to multiple LLM providers through LangChain's abstraction layer.

#### Key Features

- **Multi-provider support**: Seamlessly switch between OpenAI, Vertex AI, and AWS Bedrock
- **Unified API**: Same interface regardless of provider
- **Streaming support**: Real-time response streaming
- **Tool binding**: Function calling capabilities
- **LangSmith integration**: Automatic tracing and observability

#### Implementation Details

```python
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_aws import ChatBedrock
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
```

**Provider Initialization:**

```python
# OpenAI
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    streaming=True,
    api_key=settings.OPENAI_API_KEY
)

# Vertex AI
llm = ChatVertexAI(
    model_name="gemini-1.5-pro",
    temperature=0.7,
    streaming=True,
    project=settings.GOOGLE_CLOUD_PROJECT
)

# AWS Bedrock
llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="us-east-1",
    streaming=True
)
```

**Message Handling:**

LangChain uses a standardized message format:

```python
messages = [
    SystemMessage(content="You are a helpful assistant"),
    HumanMessage(content="What is the capital of France?")
]

response = await llm.ainvoke(messages)
answer = response.content
```

**Streaming:**

```python
async for chunk in llm.astream(messages):
    yield chunk.content
```

**Tool/Function Calling:**

```python
llm_with_tools = llm.bind_tools(tools)
response = await llm_with_tools.ainvoke(messages)
# Response contains tool_calls if LLM decides to use tools
```

---

### 2. RAG Service Integration

#### Basic RAG Service (`app/services/rag_service.py`)

Uses LangChain's LLM service for answer generation:

```python
from app.services.llm_service import LLMService

class RAGService:
    def __init__(self, db: Session):
        self.llm_service = LLMService()
    
    async def process_query(self, question: str, user_id: int):
        # Get relevant context from vector store
        context = await self._get_relevant_context(question, document_id)
        
        # Generate answer using LangChain LLM
        answer = await self.llm_service.generate_answer(question, context)
        return answer
```

#### Enhanced RAG Service (`app/services/enhanced_rag_service.py`)

Full LangChain integration with advanced retrieval patterns:

**Key Components:**

1. **Embeddings**: Multi-provider embedding support
   ```python
   from langchain_openai import OpenAIEmbeddings
   from langchain_google_vertexai import VertexAIEmbeddings
   from langchain_aws import BedrockEmbeddings
   ```

2. **Vector Stores**: FAISS and Chroma via LangChain
   ```python
   from langchain_community.vectorstores import FAISS, Chroma
   ```

3. **Text Splitting**: LangChain's recursive text splitter
   ```python
   from langchain_text_splitters import RecursiveCharacterTextSplitter
   ```

4. **Retrievers**: Advanced retrieval with compression
   ```python
   from langchain.retrievers import ContextualCompressionRetriever
   from langchain.retrievers.document_compressors import LLMChainExtractor
   ```

**Document Processing Flow:**

```python
# 1. Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_text(text)

# 2. Create LangChain Document objects
from langchain_core.documents import Document
documents = [
    Document(page_content=chunk, metadata={"user_id": user_id})
    for chunk in chunks
]

# 3. Add to vector store
vectorstore.add_documents(documents)
vectorstore.save_local(index_path)

# 4. Retrieve relevant documents
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5, "filter": {"user_id": user_id}}
)
docs = await retriever.aget_relevant_documents(query)
```

**Advanced Retrieval with Compression:**

```python
# Apply contextual compression to reduce noise
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)
docs = await compression_retriever.aget_relevant_documents(query)
```

---

### 3. Agent Service (LangGraph)

The Agent Service implements stateful agentic workflows using LangGraph.

**Location:** `app/services/agent_service.py`

#### Architecture

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
```

**State Definition:**

```python
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: int
    document_id: Optional[int]
    iteration_count: int
    context: Optional[str]
    tool_results: List[Dict[str, Any]]
```

**Graph Structure:**

```
┌─────────────┐
│ Guardrails  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ RAG Retrieval│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Agent     │◄────┐
└──────┬──────┘     │
       │            │
       ├────────────┤
       │            │
       ▼            │
┌─────────────┐     │
│Tool Execution│────┘
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Response   │
│ Generation  │
└──────┬──────┘
       │
       ▼
      END
```

**Node Implementation:**

```python
async def _agent_node(self, state: AgentState) -> AgentState:
    """Main agent reasoning node"""
    messages = state["messages"].copy()
    
    # Add RAG context if available
    if state.get("context"):
        context_msg = SystemMessage(
            content=f"Relevant context:\n{state['context']}"
        )
        messages.insert(-1, context_msg)
    
    # Generate response with tools
    tools = await self.tool_service.get_available_tools()
    response = await self.llm_service.generate_with_tools(messages, tools)
    
    state["messages"].append(response)
    return state
```

**Conditional Edges:**

```python
def _should_use_tools(self, state: AgentState) -> str:
    """Determine if tools should be executed"""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls"):
        if last_message.tool_calls:
            return "use_tools"
    return "no_tools"

workflow.add_conditional_edges(
    "agent",
    self._should_use_tools,
    {
        "use_tools": "tool_execution",
        "no_tools": "response_generation"
    }
)
```

**Execution:**

```python
# Run the graph
final_state = await self.graph.ainvoke(initial_state, config)

# Stream execution
async for event in self.graph.astream(initial_state, config):
    yield event
```

---

### 4. Tool Service

The Tool Service manages LangChain tools for agent function calling.

**Location:** `app/services/tool_service.py`

#### Tool Definition

```python
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression")

@tool("calculator", args_schema=CalculatorInput)
async def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely"""
    # Implementation
    return str(result)
```

#### Community Tools

```python
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
```

#### Tool Execution

```python
# Get available tools
tools = await tool_service.get_available_tools()

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# LLM decides to call tool
response = await llm_with_tools.ainvoke(messages)
# response.tool_calls contains tool invocation details

# Execute tool
result = await tool_service.execute_tool(
    tool_name=tool_call["name"],
    args=tool_call["args"]
)

# Add tool result to conversation
tool_message = ToolMessage(
    content=str(result),
    tool_call_id=tool_call["id"]
)
messages.append(tool_message)
```

---

### 5. Text Splitting

LangChain's text splitter is used for document chunking.

**Location:** `app/utils/text_splitter.py`

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
    
    def split_text(self, text: str) -> List[str]:
        return self.splitter.split_text(text)
```

**Also used in Enhanced RAG Service:**

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
chunks = text_splitter.split_text(text)
```

---

### 6. Vector Stores

LangChain provides unified interfaces to vector stores.

#### FAISS Integration

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(
    texts=["Document 1", "Document 2"],
    embedding=embeddings
)

# Save and load
vectorstore.save_local("./faiss_index")
vectorstore = FAISS.load_local(
    "./faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# Search
docs = await vectorstore.asimilarity_search(query, k=5)
```

#### Chroma Integration

```python
from langchain_community.vectorstores import Chroma

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# Persist
vectorstore.persist()

# Search
docs = await vectorstore.asimilarity_search(query, k=5, filter={"user_id": 1})
```

#### Retriever Interface

```python
# Create retriever from vectorstore
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"user_id": user_id, "document_id": doc_id}
    }
)

# Retrieve documents
docs = await retriever.aget_relevant_documents(query)
```

---

### 7. LangSmith Observability

LangSmith provides tracing and monitoring for LangChain operations.

**Setup:**

```python
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
```

**Automatic Tracing:**

Once configured, all LangChain operations are automatically traced:
- LLM calls
- Tool executions
- RAG retrievals
- Agent workflow steps

**View Traces:**

Visit: https://smith.langchain.com

---

## Configuration

### Environment Variables

```bash
# LLM Provider
LLM_PROVIDER=openai  # or vertex_ai, aws_bedrock

# OpenAI
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Vertex AI
GOOGLE_CLOUD_PROJECT=your_project
VERTEX_AI_MODEL=gemini-1.5-pro

# AWS Bedrock
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# LangSmith
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=ai-backend
LANGSMITH_TRACING=true

# Vector Store
VECTOR_STORE_TYPE=faiss  # or chroma
FAISS_INDEX_PATH=./vector_store/faiss_index

# RAG
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_RERANK=false

# Agent
AGENT_MAX_ITERATIONS=10
AGENT_ENABLE_TOOLS=true
```

---

## Usage Examples

### Example 1: Simple LLM Query

```python
from app.services.llm_service import LLMService
from langchain_core.messages import HumanMessage

llm_service = LLMService()
messages = [HumanMessage(content="What is AI?")]
response = await llm_service.generate(messages)
print(response)
```

### Example 2: RAG Query

```python
from app.services.enhanced_rag_service import EnhancedRAGService

rag_service = EnhancedRAGService(db)
context = await rag_service.get_relevant_context(
    query="What is the main topic?",
    user_id=1,
    document_id=123,
    top_k=5
)

# Use context with LLM
from app.services.llm_service import LLMService
llm_service = LLMService()
messages = [
    SystemMessage(content=f"Context: {context}"),
    HumanMessage(content="What is the main topic?")
]
response = await llm_service.generate(messages)
```

### Example 3: Agent Workflow

```python
from app.services.agent_service import AgentService

agent_service = AgentService(db_session=db)
result = await agent_service.run(
    query="What is the weather in Paris?",
    user_id=1,
    document_id=None,
    thread_id="thread-123"
)

print(result["response"])
print(f"Tools used: {result['tool_results']}")
print(f"Iterations: {result['iterations']}")
```

### Example 4: Streaming Agent Response

```python
async for event in agent_service.stream(
    query="Calculate 123 * 456",
    user_id=1
):
    print(event)
```

### Example 5: Custom Tool

```python
from app.services.tool_service import ToolService
from langchain_core.tools import tool

@tool("custom_action")
async def custom_action(param: str) -> str:
    """Perform a custom action"""
    return f"Action result: {param}"

tool_service = ToolService()
tool_service.tools.append(custom_action)
```

---

## Architecture Flow

### Complete Request Flow

```
1. User Request
   │
   ▼
2. Chat Router (app/routers/chat.py)
   │
   ▼
3. Agent Service (LangGraph)
   │
   ├─► Guardrails Node
   │   │
   ├─► RAG Retrieval Node
   │   │   ├─► Enhanced RAG Service
   │   │   │   ├─► Vector Store (FAISS/Chroma)
   │   │   │   ├─► Embeddings (LangChain)
   │   │   │   └─► Retriever (LangChain)
   │   │   │
   │   │   └─► Context Retrieved
   │   │
   ├─► Agent Node
   │   │   ├─► LLM Service (LangChain)
   │   │   │   ├─► ChatOpenAI / ChatVertexAI / ChatBedrock
   │   │   │   └─► Tool Binding
   │   │   │
   │   │   └─► Response with potential tool calls
   │   │
   ├─► Tool Execution Node (if tools called)
   │   │   ├─► Tool Service
   │   │   │   ├─► LangChain Tools
   │   │   │   └─► Community Tools
   │   │   │
   │   │   └─► Tool Results
   │   │
   └─► Response Generation Node
       │
       ▼
4. Final Response
```

### Document Processing Flow

```
1. Document Upload
   │
   ▼
2. Document Loader
   │
   ▼
3. Text Extraction
   │
   ▼
4. Text Splitter (LangChain)
   │   └─► RecursiveCharacterTextSplitter
   │
   ▼
5. Create Embeddings (LangChain)
   │   └─► OpenAIEmbeddings / VertexAIEmbeddings / BedrockEmbeddings
   │
   ▼
6. Create Documents (LangChain)
   │   └─► Document(page_content, metadata)
   │
   ▼
7. Add to Vector Store (LangChain)
   │   └─► FAISS / Chroma
   │
   ▼
8. Persist Vector Store
```

---

## Key LangChain Concepts Used

### 1. Messages

LangChain uses a standardized message format:

- `SystemMessage`: System instructions
- `HumanMessage`: User input
- `AIMessage`: LLM responses
- `ToolMessage`: Tool execution results

### 2. Documents

```python
from langchain_core.documents import Document

document = Document(
    page_content="Text content",
    metadata={"user_id": 1, "document_id": 123}
)
```

### 3. Retrievers

Unified interface for document retrieval:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)
docs = await retriever.aget_relevant_documents(query)
```

### 4. Tools

Extensible function calling:

```python
@tool("tool_name")
async def tool_function(param: str) -> str:
    """Tool description"""
    return result
```

### 5. Callbacks

For observability and custom handling:

```python
from langchain_core.callbacks import AsyncCallbackHandler

class CustomHandler(AsyncCallbackHandler):
    async def on_llm_start(self, serialized, prompts, **kwargs):
        # Custom logic
        pass
```

---

## Best Practices

1. **Provider Abstraction**: Always use LangChain's base classes (`BaseChatModel`, `BaseTool`) for flexibility

2. **Error Handling**: Wrap LangChain calls in try-except blocks

3. **Streaming**: Use streaming for better UX in production

4. **Tool Validation**: Validate tool inputs using Pydantic schemas

5. **Context Management**: Properly manage context windows and chunk sizes

6. **Observability**: Enable LangSmith tracing in production

7. **Vector Store Persistence**: Regularly save vector stores to disk

8. **Async Operations**: Use async methods (`ainvoke`, `astream`) for better performance

---

## Troubleshooting

### Import Errors

If you see import errors, ensure all packages are installed:

```bash
pip install langchain langchain-core langchain-community langchain-openai
```

### Provider-Specific Issues

- **Vertex AI**: Requires `langchain-google-vertexai` and proper GCP authentication
- **AWS Bedrock**: Requires `langchain-aws` and AWS credentials
- **OpenAI**: Requires `langchain-openai` and API key

### Vector Store Issues

- **FAISS**: Ensure `faiss-cpu` or `faiss-gpu` is installed
- **Chroma**: Ensure `chromadb` is installed
- **Persistence**: Check file permissions for save/load operations

### LangSmith Tracing

If tracing doesn't work:
1. Verify `LANGSMITH_API_KEY` is set
2. Check network connectivity
3. Verify project name matches LangSmith project

---

## References

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith](https://smith.langchain.com/)
- [LangChain Community Tools](https://python.langchain.com/docs/integrations/tools/)

---

## Summary

LangChain is deeply integrated throughout this project, providing:

1. **Unified LLM Interface**: Multi-provider support with consistent API
2. **RAG Capabilities**: Advanced retrieval and context injection
3. **Agentic Workflows**: Stateful, tool-enabled agents via LangGraph
4. **Vector Operations**: FAISS and Chroma integration
5. **Text Processing**: Document chunking and splitting
6. **Observability**: LangSmith tracing and monitoring

This architecture enables a production-grade AI backend with flexibility, scalability, and observability.

