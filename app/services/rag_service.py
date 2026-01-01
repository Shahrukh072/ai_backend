from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService
from app.services.llm_service import LLMService
from typing import Optional


class RAGService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.faiss_service = FAISSService()
        self.llm_service = LLMService()
    
    async def process_query(
        self,
        question: str,
        user_id: int,
        document_id: Optional[int] = None
    ) -> Chat:
        """Process a query using RAG"""
        # Create chat record
        chat = Chat(
            question=question,
            user_id=user_id,
            document_id=document_id
        )
        self.db.add(chat)
        self.db.commit()
        
        try:
            # Get relevant context
            context = await self._get_relevant_context(question, document_id)
            
            # Generate answer using LLM
            answer = await self.llm_service.generate_answer(question, context)
            
            # Update chat with answer
            chat.answer = answer
            self.db.commit()
            self.db.refresh(chat)
            
            return chat
        
        except Exception as e:
            chat.answer = f"Error processing query: {str(e)}"
            self.db.commit()
            self.db.refresh(chat)
            return chat
    
    async def _get_relevant_context(self, question: str, document_id: Optional[int] = None) -> str:
        """Get relevant context from vector store"""
        # Create embedding for question
        question_embedding = await self.embedding_service.create_embedding(question)
        
        # Search in FAISS
        if document_id:
            # Search within specific document
            results = self.faiss_service.search(question_embedding, document_id, k=5)
        else:
            # Search across all documents
            results = self.faiss_service.search(question_embedding, None, k=5)
        
        # Combine results into context
        context = "\n\n".join([result["text"] for result in results])
        return context

