from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database - Use psycopg3 driver explicitly
    DATABASE_URL: str = "postgresql+psycopg://postgres:root@localhost:5432/ai_backend"
    
    # Security
    SECRET_KEY: str = "dmANvXXGHE4_JNwYI0sI7NLMCbxQpsv-H6ip5sEP1to"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Embedding
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536
    
    # Vector Store
    FAISS_INDEX_PATH: str = "./vector_store/faiss_index"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".docx", ".md"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

