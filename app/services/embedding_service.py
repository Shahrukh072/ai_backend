from openai import OpenAI
from app.config import settings
from typing import List
import numpy as np


class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
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

