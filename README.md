# AI Backend - Production LLM/GenAI Platform

A production-grade AI backend built with FastAPI, LangChain, LangGraph, and modern GenAI technologies. This platform supports agentic workflows, RAG systems, multi-provider LLM support (OpenAI, Vertex AI, AWS Bedrock), and comprehensive observability.

## 🚀 Features

### Core Capabilities
- **Agentic Workflows**: Stateful agent graphs using LangGraph
- **RAG System**: Advanced retrieval-augmented generation with vector databases
- **Multi-Provider LLM Support**: OpenAI, Google Vertex AI, AWS Bedrock
- **Tool/Function Calling**: MCP, A2A, and custom tool support
- **WebSocket Support**: Real-time streaming chat
- **Guardrails & Safety**: Content filtering and fallback logic
- **Prompt Management**: Version-controlled prompts with Git integration
- **Observability**: LangSmith integration for tracing and monitoring
- **Testing**: Comprehensive test suite with pytest and LLM evaluation

### Technology Stack
- **Framework**: FastAPI with async Python, Pydantic v2
- **LLM Framework**: LangChain, LangGraph
- **Vector Stores**: FAISS, ChromaDB
- **LLM Providers**: OpenAI, Vertex AI, AWS Bedrock
- **Observability**: LangSmith
- **Testing**: pytest, langchain-evaluation
- **Deployment**: Docker, Kubernetes-ready

## 📋 Prerequisites

- Python 3.10+ (3.11+ recommended)
- PostgreSQL 12+
- OpenAI API key (or Vertex AI / AWS Bedrock credentials)
- LangSmith API key (optional, for observability)

## 🛠️ Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/ai_backend

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Provider (choose one)
LLM_PROVIDER=openai  # or vertex_ai or aws_bedrock

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Vertex AI Configuration (if using)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro

# AWS Bedrock Configuration (if using)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0

# LangSmith Observability
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=ai-backend
LANGSMITH_TRACING=true

# Vector Store
VECTOR_STORE_TYPE=faiss  # or chroma
FAISS_INDEX_PATH=./vector_store/faiss_index

# Agent Configuration
AGENT_MAX_ITERATIONS=10
AGENT_ENABLE_TOOLS=true
AGENT_ENABLE_MCP=false
AGENT_ENABLE_A2A=false

# Guardrails
GUARDRAILS_ENABLED=true
GUARDRAILS_MAX_TOXICITY_SCORE=0.5
GUARDRAILS_FALLBACK_ENABLED=true
```

### 3. Database Setup

```bash
# Initialize database
make init-db
# or
python init_db.py
```

### 4. Run the Application

```bash
# Development mode
make dev

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🐳 Docker Setup

```bash
# Build and start
docker-compose up --build

# Stop
docker-compose down
```

## 📚 Architecture

### System Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (REST/WS)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│ Agent │ │   RAG   │
│Service│ │ Service │
└───┬───┘ └──┬──────┘
    │        │
┌───▼────────▼───┐
│  LangGraph     │
│  State Graph   │
└───┬────────────┘
    │
┌───▼──────────────┐
│  LLM Service     │
│  (Multi-Provider)│
└───┬──────────────┘
    │
┌───▼──────────────┐
│  Vector Store    │
│  (FAISS/Chroma)  │
└──────────────────┘
```

### Agentic Workflow

The system uses LangGraph to create stateful agent workflows:

1. **Guardrails Node**: Validates input
2. **RAG Retrieval Node**: Retrieves relevant context
3. **Agent Node**: Main reasoning and decision-making
4. **Tool Execution Node**: Executes tools/functions
5. **Response Generation Node**: Generates final response

### RAG Pipeline

1. Document ingestion and chunking
2. Embedding generation (provider-specific)
3. Vector storage (FAISS or ChromaDB)
4. Similarity search and retrieval
5. Context compression (optional)
6. LLM generation with context

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/` - List user documents
- `GET /api/documents/{id}` - Get document
- `DELETE /api/documents/{id}` - Delete document

### Chat
- `POST /api/chat/` - Create chat (agentic workflow)
- `POST /api/chat/agent` - Full agent workflow
- `GET /api/chat/` - List chats
- `GET /api/chat/{id}` - Get chat
- `WS /api/chat/ws/{user_id}` - WebSocket chat

### Example: Chat Request

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is in my documents?",
    "document_id": 1
  }'
```

### Example: WebSocket Chat

```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws/1');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
ws.send(JSON.stringify({
  message: "Hello!",
  document_id: 1
}));
```

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_agent_service.py

# With coverage
pytest --cov=app --cov-report=html

# LLM evaluation tests (requires API keys)
pytest tests/test_llm_eval.py -m llm
```

### Test Structure

```
tests/
├── conftest.py           # Pytest fixtures
├── test_agent_service.py # Agent workflow tests
├── test_rag_service.py   # RAG system tests
└── test_llm_eval.py      # LLM evaluation tests
```

## 🔧 Configuration

### LLM Provider Selection

Switch between providers in `.env`:

```bash
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key

# Vertex AI
LLM_PROVIDER=vertex_ai
GOOGLE_CLOUD_PROJECT=your-project

# AWS Bedrock
LLM_PROVIDER=aws_bedrock
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### Vector Store Selection

```bash
# FAISS (default)
VECTOR_STORE_TYPE=faiss
FAISS_INDEX_PATH=./vector_store/faiss_index

# ChromaDB
VECTOR_STORE_TYPE=chroma
CHROMA_PERSIST_DIR=./vector_store/chroma
```

### Agent Configuration

```bash
# Maximum iterations
AGENT_MAX_ITERATIONS=10

# Enable tools
AGENT_ENABLE_TOOLS=true

# Enable MCP (Model Context Protocol)
AGENT_ENABLE_MCP=false

# Enable A2A (Agent-to-Agent)
AGENT_ENABLE_A2A=false
```

## 📖 Advanced Features

### Prompt Management

```python
from app.services.prompt_service import PromptService

prompt_service = PromptService()

# Create a new prompt version
prompt = prompt_service.create_prompt(
    name="system_agent",
    content="You are a helpful assistant...",
    metadata={"version": "1.0", "author": "team"}
)

# Get prompt
prompt = prompt_service.get_prompt("system_agent", version="v1.0.0")
```

### Custom Tools

```python
from app.services.tool_service import ToolService

tool_service = ToolService()

# Create custom tool
@tool_service.create_custom_tool(
    name="custom_action",
    description="Performs a custom action",
    func=my_custom_function
)
async def my_custom_function(param: str) -> str:
    return f"Processed: {param}"
```

### Guardrails

```python
from app.services.guardrails_service import GuardrailsService

guardrails = GuardrailsService()

# Check input
is_safe, reason = await guardrails.check_input(user_input)

# Check output
is_safe, reason = await guardrails.check_output(llm_output)

# Apply fallback
fallback_response = await guardrails.apply_fallback(error, context)
```

## 🚢 Deployment

### Docker

```bash
docker build -t ai-backend .
docker run -p 8000:8000 --env-file .env ai-backend
```

### Kubernetes

See `k8s/` directory for Kubernetes manifests (create as needed):

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Environment Variables

Ensure all required environment variables are set in your deployment environment.

## 📊 Observability

### LangSmith Integration

The system automatically traces all LLM calls when LangSmith is configured:

```bash
LANGSMITH_API_KEY=your-key
LANGSMITH_PROJECT=ai-backend
LANGSMITH_TRACING=true
```

View traces at: https://smith.langchain.com

### Monitoring

- All agent workflows are traced
- Tool executions are logged
- RAG retrieval metrics
- Error tracking and fallback usage

## 🔐 Security

- JWT-based authentication
- Input/output guardrails
- PII detection
- Content filtering
- Rate limiting (implement as needed)

## 📝 Development

### Code Style

```bash
# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

### Project Structure

```
ai_backend/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── database.py             # Database setup
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── routers/                # API routes
│   ├── services/               # Business logic
│   │   ├── agent_service.py    # LangGraph agent
│   │   ├── llm_service.py      # Multi-provider LLM
│   │   ├── enhanced_rag_service.py  # RAG system
│   │   ├── tool_service.py     # Tool management
│   │   ├── guardrails_service.py    # Safety checks
│   │   └── prompt_service.py  # Prompt versioning
│   └── utils/                  # Utilities
├── tests/                      # Test suite
├── vector_store/               # Vector DB storage
├── prompts/                    # Prompt storage
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review LangChain/LangGraph docs

## 🔗 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangSmith](https://smith.langchain.com/)
