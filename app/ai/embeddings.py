from openai import AsyncOpenAI
from app.config import settings
from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = settings.OPENAI_EMBEDDING_DIMENSION
    
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

