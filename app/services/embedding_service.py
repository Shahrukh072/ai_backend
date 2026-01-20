from openai import OpenAI
from app.config import settings, LLMProvider
from typing import List
import numpy as np


class EmbeddingService:
    def __init__(self):
        # For embeddings, we use OpenAI API (works with Groq setup since Groq doesn't have embeddings)
        # If using Groq, we still need OPENAI_API_KEY for embeddings
        embedding_api_key = settings.OPENAI_API_KEY
        if not embedding_api_key and settings.LLM_PROVIDER == LLMProvider.GROQ:
            # For Groq, we can optionally use Groq API key with OpenAI-compatible endpoint
            # But OpenAI embeddings are recommended for now
            embedding_api_key = settings.GROQ_API_KEY if hasattr(settings, 'GROQ_API_KEY') else None
        
        if not embedding_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for embeddings. "
                "Even when using Groq, you need OpenAI API key for embeddings. "
                "Or set GROQ_API_KEY and we'll use it with OpenAI-compatible endpoint."
            )
        
        self.client = OpenAI(api_key=embedding_api_key)
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    async def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = await self.create_embedding(text)
            embeddings.append(embedding)
        return np.array(embeddings)

