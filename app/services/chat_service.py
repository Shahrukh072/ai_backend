from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.ai.agents import AgentService
from typing import Optional, List
from app.models.user import User


class ChatService:
    """Service for managing chat interactions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService(db_session=db)
    
    async def create_chat(
        self,
        question: str,
        user_id: int,
        document_id: Optional[int] = None
    ) -> Chat:
        """Create a new chat interaction"""
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            result = await self.agent_service.run(
                query=question,
                user_id=user_id,
                document_id=document_id
            )
        except Exception as e:
            logger.exception(f"Error in agent_service.run: {e}, question: {question[:100]}, user_id: {user_id}, document_id: {document_id}")
            raise
        
        # Validate result
        if not isinstance(result, dict) or "response" not in result:
            logger.error(f"Invalid result from agent_service.run: {result}")
            raise ValueError("Invalid response from agent service")
        
        chat = Chat(
            question=question,
            answer=result["response"],
            user_id=user_id,
            document_id=document_id
        )
        
        # Run DB operations in thread pool to avoid blocking
        try:
            self.db.add(chat)
            await asyncio.to_thread(self.db.commit)
            await asyncio.to_thread(self.db.refresh, chat)
        except Exception as e:
            await asyncio.to_thread(self.db.rollback)
            logger.exception(f"Error saving chat to database: {e}")
            raise
        
        return chat
    
    def get_chats(
        self,
        user_id: int,
        document_id: Optional[int] = None
    ) -> List[Chat]:
        """Get all chats for a user"""
        query = self.db.query(Chat).filter(Chat.user_id == user_id)
        
        if document_id:
            query = query.filter(Chat.document_id == document_id)
        
        return query.order_by(Chat.created_at.desc()).all()
    
    def get_chat(self, chat_id: int, user_id: int) -> Optional[Chat]:
        """Get a specific chat"""
        return self.db.query(Chat).filter(
            Chat.id == chat_id,
            Chat.user_id == user_id
        ).first()

