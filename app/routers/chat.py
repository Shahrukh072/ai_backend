"""Chat router with agentic workflows and WebSocket support"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import AgentService
from app.services.rag_service import RAGService
from app.config import settings
import json
import uuid

router = APIRouter()


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a chat interaction using agentic workflow"""
    try:
        agent_service = AgentService(db_session=db)
        
        result = await agent_service.run(
            query=chat_request.question,
            user_id=current_user.id,
            document_id=chat_request.document_id,
            thread_id=str(uuid.uuid4())
        )
        
        # Create chat record
        from app.models.chat import Chat
        chat = Chat(
            question=chat_request.question,
            answer=result["response"],
            user_id=current_user.id,
            document_id=chat_request.document_id
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        
        return chat
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@router.get("/", response_model=List[ChatResponse])
async def get_chats(
    document_id: Optional[int] = None,
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


@router.websocket("/ws/{user_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: int,
    document_id: Optional[int] = None
):
    """WebSocket endpoint for real-time chat with agentic workflows"""
    await websocket.accept()
    
    # Get database session (simplified - in production, use proper dependency injection)
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        agent_service = AgentService(db_session=db)
        thread_id = str(uuid.uuid4())
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            query = message_data.get("message", "")
            if not query:
                await websocket.send_json({
                    "type": "error",
                    "message": "Empty message"
                })
                continue
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "status",
                "message": "Processing..."
            })
            
            # Stream agent response
            try:
                async for event in agent_service.stream(
                    query=query,
                    user_id=user_id,
                    document_id=document_id or message_data.get("document_id"),
                    thread_id=thread_id
                ):
                    # Send streaming updates
                    await websocket.send_json({
                        "type": "stream",
                        "data": json.dumps(event, default=str)
                    })
                
                # Get final result
                result = await agent_service.run(
                    query=query,
                    user_id=user_id,
                    document_id=document_id or message_data.get("document_id"),
                    thread_id=thread_id
                )
                
                # Save chat
                from app.models.chat import Chat
                chat = Chat(
                    question=query,
                    answer=result["response"],
                    user_id=user_id,
                    document_id=document_id or message_data.get("document_id")
                )
                db.add(chat)
                db.commit()
                
                # Send final response
                await websocket.send_json({
                    "type": "complete",
                    "response": result["response"],
                    "tool_results": result.get("tool_results", []),
                    "iterations": result.get("iterations", 0)
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error: {str(e)}"
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Connection error: {str(e)}"
        })
    finally:
        db.close()


@router.post("/agent", status_code=status.HTTP_201_CREATED)
async def create_agent_chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a chat using the full agentic workflow"""
    try:
        agent_service = AgentService(db_session=db)
        
        result = await agent_service.run(
            query=chat_request.question,
            user_id=current_user.id,
            document_id=chat_request.document_id
        )
        
        return {
            "response": result["response"],
            "tool_results": result.get("tool_results", []),
            "iterations": result.get("iterations", 0),
            "context_used": result.get("context_used", False)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in agent workflow: {str(e)}"
        )
