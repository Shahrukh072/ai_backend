from openai import AsyncOpenAI
from app.config import settings, LLMProvider
from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        # For embeddings, we use OpenAI API (works with Groq setup since Groq doesn't have embeddings)
        # If using Groq, we still need OPENAI_API_KEY for embeddings
        embedding_api_key = settings.OPENAI_API_KEY
        if not embedding_api_key and settings.LLM_PROVIDER == LLMProvider.GROQ:
            # For Groq, we can optionally use Groq API key with OpenAI-compatible endpoint
            # But OpenAI embeddings are recommended for now
            embedding_api_key = getattr(settings, 'GROQ_API_KEY', None)
        
        if not embedding_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for embeddings. "
                "Even when using Groq, you need OpenAI API key for embeddings. "
                "Or set GROQ_API_KEY and we'll use it with OpenAI-compatible endpoint."
            )
        
        self.client = AsyncOpenAI(api_key=embedding_api_key)
        # Use general embedding settings (works for all providers)
        self.model = getattr(settings, 'EMBEDDING_MODEL', settings.OPENAI_EMBEDDING_MODEL)
        self.dimension = getattr(settings, 'EMBEDDING_DIMENSION', settings.OPENAI_EMBEDDING_DIMENSION)
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        if not response or not response.data or len(response.data) == 0:
            logger.error(f"Empty response from embeddings API for model {self.model}, input: {text[:100]}...")
            raise ValueError(f"Empty response from embeddings API. Model: {self.model}, Input length: {len(text)}")
        return response.data[0].embedding
    
    async def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = await self.create_embedding(text)
            embeddings.append(embedding)
        return np.array(embeddings)

