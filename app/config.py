from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Literal, Optional
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    VERTEX_AI = "vertex_ai"
    AWS_BEDROCK = "aws_bedrock"


class Settings(BaseSettings):
    # Database - Use psycopg3 driver explicitly
    DATABASE_URL: str = "postgresql+psycopg://postgres:root@localhost:5432/ai_backend"
    
    # Security
    SECRET_KEY: str = "dmANvXXGHE4_JNwYI0sI7NLMCbxQpsv-H6ip5sEP1to"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days (30 * 24 * 60)
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Environment
    ENV: str = "development"
    
    # Google OAuth Configuration
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    GOOGLE_OAUTH_REDIRECT_URI: Optional[str] = None
    APP_BASE_URL: Optional[str] = None  # Base URL for constructing redirect URI
    
    # LLM Provider Selection
    LLM_PROVIDER: LLMProvider = LLMProvider.OPENAI
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_EMBEDDING_DIMENSION: int = 3072
    
    # Vertex AI Configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    VERTEX_AI_MODEL: str = "gemini-1.5-pro"
    VERTEX_AI_EMBEDDING_MODEL: str = "text-embedding-004"
    VERTEX_AI_EMBEDDING_DIMENSION: int = 768
    
    # AWS Bedrock Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    BEDROCK_MODEL: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_EMBEDDING_MODEL: str = "amazon.titan-embed-text-v1"
    BEDROCK_EMBEDDING_DIMENSION: int = 1536
    
    # LangSmith Observability
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "ai-backend"
    LANGSMITH_TRACING: bool = True
    
    # LangGraph Configuration
    LANGGRAPH_CHECKPOINT_DIR: str = "./checkpoints"
    LANGGRAPH_DEBUG: bool = False
    
    # Vector Store Configuration
    VECTOR_STORE_TYPE: Literal["faiss", "chroma"] = "faiss"
    FAISS_INDEX_PATH: str = "./vector_store/faiss_index"
    CHROMA_PERSIST_DIR: str = "./vector_store/chroma"
    
    # RAG Configuration
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_RERANK: bool = False
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_MAX_EXECUTION_TIME: int = 300  # seconds
    AGENT_ENABLE_TOOLS: bool = True
    AGENT_ENABLE_MCP: bool = False
    AGENT_ENABLE_A2A: bool = False
    
    # Guardrails Configuration
    GUARDRAILS_ENABLED: bool = True
    GUARDRAILS_MAX_TOXICITY_SCORE: float = 0.5
    GUARDRAILS_MAX_PII_DETECTION: bool = True
    GUARDRAILS_FALLBACK_ENABLED: bool = True
    
    # Prompt Management
    PROMPT_VERSIONING_ENABLED: bool = True
    PROMPT_STORAGE_PATH: str = "./prompts"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".docx", ".md"]
    
    # WebSocket Configuration
    WEBSOCKET_MAX_CONNECTIONS: int = 100
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Testing & Evaluation
    LLM_EVAL_ENABLED: bool = True
    LLM_EVAL_MODEL: str = "gpt-4o-mini"
    
    @model_validator(mode='after')
    def validate_redirect_uri(self):
        """Validate and set GOOGLE_OAUTH_REDIRECT_URI based on ENV and APP_BASE_URL"""
        if not self.GOOGLE_OAUTH_REDIRECT_URI or not self.GOOGLE_OAUTH_REDIRECT_URI.strip():
            if self.APP_BASE_URL:
                self.GOOGLE_OAUTH_REDIRECT_URI = f"{self.APP_BASE_URL.rstrip('/')}/api/auth/google/callback"
            else:
                # Only allow localhost in development
                if self.ENV == "development":
                    self.GOOGLE_OAUTH_REDIRECT_URI = "http://localhost:3000/api/auth/google/callback"
                else:
                    raise ValueError(
                        "GOOGLE_OAUTH_REDIRECT_URI must be set in production. "
                        "Set it via environment variable or APP_BASE_URL."
                    )
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

