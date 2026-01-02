# Architecture Documentation

## Overview

This document describes the architecture of the AI Backend platform, focusing on the agentic workflows, RAG system, and multi-provider LLM integration.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  (REST API, WebSocket, Frontend Applications)           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Auth Router  │  │ Doc Router   │  │ Chat Router  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Service Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Agent      │  │     RAG      │  │    Tools     │ │
│  │   Service    │  │   Service    │  │   Service    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     LLM      │  │  Guardrails  │  │   Prompts    │ │
│  │   Service    │  │   Service   │  │   Service   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              LangGraph Workflow Engine                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  State Graph:                                    │  │
│  │  1. Guardrails → 2. RAG → 3. Agent →           │  │
│  │  4. Tools → 5. Response                         │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              External Services                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ OpenAI   │  │ Vertex AI│  │ Bedrock  │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│  ┌──────────┐  ┌──────────┐                          │
│  │  FAISS   │  │  Chroma  │                          │
│  └──────────┘  └──────────┘                          │
│  ┌──────────┐                                         │
│  │LangSmith │                                         │
│  └──────────┘                                         │
└─────────────────────────────────────────────────────────┘
```

## Agentic Workflow Architecture

### LangGraph State Graph

The agentic workflow is built using LangGraph's state graph pattern:

```python
StateGraph(AgentState)
  ├─> guardrails_node
  │     └─> rag_retrieval_node
  │           └─> agent_node
  │                 ├─> tool_execution_node (if tools needed)
  │                 └─> response_generation_node
  │                       └─> END
```

### State Management

```python
class AgentState(TypedDict):
    messages: List[BaseMessage]      # Conversation history
    user_id: int                      # User identifier
    document_id: Optional[int]        # Document context
    iteration_count: int              # Iteration tracking
    context: Optional[str]            # RAG context
    tool_results: List[Dict]          # Tool execution results
```

### Workflow Nodes

1. **Guardrails Node**
   - Validates user input
   - Checks for toxicity, PII
   - Applies content filters

2. **RAG Retrieval Node**
   - Generates query embeddings
   - Searches vector store
   - Retrieves relevant context
   - Applies compression if enabled

3. **Agent Node**
   - Main reasoning engine
   - Decides on tool usage
   - Generates responses
   - Manages iteration limits

4. **Tool Execution Node**
   - Executes function calls
   - Handles MCP/A2A tools
   - Returns tool results

5. **Response Generation Node**
   - Applies output guardrails
   - Formats final response
   - Handles errors with fallback

## RAG System Architecture

### Document Processing Pipeline

```
Document Upload
    │
    ├─> Text Extraction (PDF, DOCX, TXT, MD)
    │
    ├─> Text Chunking (RecursiveCharacterTextSplitter)
    │   └─> Chunk Size: 1000, Overlap: 200
    │
    ├─> Embedding Generation
    │   └─> Provider-specific embeddings
    │       ├─> OpenAI: text-embedding-3-large (3072 dim)
    │       ├─> Vertex AI: text-embedding-004 (768 dim)
    │       └─> Bedrock: amazon.titan-embed (1536 dim)
    │
    └─> Vector Storage
        ├─> FAISS (IndexFlatL2)
        └─> ChromaDB (persistent)
```

### Retrieval Pipeline

```
User Query
    │
    ├─> Query Embedding
    │
    ├─> Similarity Search
    │   └─> Top-K retrieval (default: 5)
    │
    ├─> Filtering (optional)
    │   └─> By user_id, document_id
    │
    ├─> Compression (optional)
    │   └─> LLMChainExtractor
    │
    └─> Context Assembly
        └─> Combined context for LLM
```

## LLM Service Architecture

### Multi-Provider Support

The LLM service abstracts provider differences:

```python
LLMService
    ├─> OpenAI Provider
    │   └─> ChatOpenAI (gpt-4o, gpt-3.5-turbo)
    │
    ├─> Vertex AI Provider
    │   └─> ChatVertexAI (gemini-1.5-pro)
    │
    └─> AWS Bedrock Provider
        └─> ChatBedrock (claude-3-5-sonnet)
```

### Features

- **Streaming**: Async streaming support
- **Tool Calling**: Function/tool binding
- **Temperature Control**: Configurable creativity
- **Token Limits**: Max token configuration
- **Error Handling**: Provider-specific error handling

## Tool System Architecture

### Tool Types

1. **Built-in Tools**
   - Calculator
   - Web Search (DuckDuckGo)
   - Wikipedia Search
   - Current Time

2. **MCP Tools** (Model Context Protocol)
   - External tool integration
   - Protocol-based communication

3. **A2A Tools** (Agent-to-Agent)
   - Inter-agent communication
   - Agent orchestration

4. **Custom Tools**
   - User-defined functions
   - Domain-specific tools

### Tool Execution Flow

```
Agent Request
    │
    ├─> Tool Selection
    │   └─> Based on function calling
    │
    ├─> Tool Validation
    │   └─> Check availability, permissions
    │
    ├─> Tool Execution
    │   └─> Async execution
    │
    └─> Result Processing
        └─> Format and return to agent
```

## Guardrails Architecture

### Safety Layers

1. **Input Guardrails**
   - Toxicity detection
   - PII detection
   - Content filtering

2. **Output Guardrails**
   - Response validation
   - Content filtering
   - PII redaction

3. **Fallback Logic**
   - Error handling
   - Graceful degradation
   - User-friendly error messages

## Prompt Management Architecture

### Versioning System

```
prompts/
├── prompts.json          # Version metadata
├── system_default_v1.0.0.txt
├── system_rag_v1.0.0.txt
└── system_agent_v1.0.0.txt
```

### Git Integration

- Automatic commits on prompt updates
- Version tracking
- Rollback capability

## Observability Architecture

### LangSmith Integration

- **Tracing**: All LLM calls traced
- **Monitoring**: Agent workflow monitoring
- **Debugging**: Step-by-step execution logs
- **Metrics**: Performance metrics

### Logging

- Structured logging
- Error tracking
- Performance metrics
- Tool execution logs

## Database Schema

### Core Models

- **User**: Authentication and user data
- **Document**: Uploaded documents
- **Chat**: Conversation history
- **Embedding**: Vector embeddings (optional)

## Security Architecture

### Authentication

- JWT-based authentication
- Token expiration
- Refresh tokens (implement as needed)

### Authorization

- User-based access control
- Document-level permissions
- API key management

### Data Protection

- Input sanitization
- Output filtering
- PII detection and redaction
- Encryption at rest (implement as needed)

## Deployment Architecture

### Container Architecture

```
Docker Container
├── FastAPI Application
├── Python Dependencies
└── Application Code
```

### Kubernetes Architecture

```
Kubernetes Cluster
├── Deployment
│   ├── Replicas: 3
│   └── Resource Limits
├── Service
│   └── Load Balancer
└── ConfigMap/Secrets
    └── Environment Variables
```

## Scalability Considerations

### Horizontal Scaling

- Stateless application design
- Shared vector store
- Database connection pooling

### Performance Optimization

- Async operations
- Caching (implement as needed)
- Vector index optimization
- Batch processing

## Error Handling

### Error Types

1. **LLM Errors**: Rate limits, timeouts, API errors
2. **Vector Store Errors**: Index errors, retrieval failures
3. **Tool Errors**: Execution failures, timeouts
4. **Guardrail Errors**: Content violations

### Fallback Strategies

- Graceful degradation
- User-friendly error messages
- Retry logic
- Circuit breakers (implement as needed)

## Future Enhancements

- [ ] Advanced caching layer
- [ ] Multi-modal support
- [ ] Fine-tuning capabilities
- [ ] Advanced guardrails (ML-based)
- [ ] Real-time collaboration
- [ ] Advanced monitoring dashboard

