from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a chat interaction with AI"""
    rag_service = RAGService(db)
    chat = await rag_service.process_query(
        question=chat_request.question,
        user_id=current_user.id,
        document_id=chat_request.document_id
    )
    return chat


@router.get("/", response_model=List[ChatResponse])
async def get_chats(
    document_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chats for the current user, optionally filtered by document"""
    from app.models.chat import Chat
    query = db.query(Chat).filter(Chat.user_id == current_user.id)
    
    if document_id:
        query = query.filter(Chat.document_id == document_id)
    
    chats = query.order_by(Chat.created_at.desc()).all()
    return chats


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat"""
    from app.models.chat import Chat
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    return chat

