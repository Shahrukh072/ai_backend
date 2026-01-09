"""Chat router with agentic workflows and WebSocket support"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db, SessionLocal
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.agents import AgentService
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
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
    
    # Authenticate via token in query params
    authenticated_user_id = None
    try:
        # Get token from query params
        token = websocket.query_params.get("token")
        if token:
            from app.core.security import verify_token
            payload = verify_token(token)
            if payload:
                authenticated_user_id = int(payload.get("sub"))
        
        if not authenticated_user_id or authenticated_user_id != user_id:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Get database session (simplified - in production, use proper dependency injection)
    db = SessionLocal()
    
    try:
        agent_service = AgentService(db_session=db)
        thread_id = str(uuid.uuid4())
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Invalid JSON in websocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message format"
                })
                continue
            
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
                final_result = None
                async for event in agent_service.stream(
                    query=query,
                    user_id=authenticated_user_id,
                    document_id=document_id or message_data.get("document_id"),
                    thread_id=thread_id
                ):
                    # Send streaming updates
                    try:
                        await websocket.send_json({
                            "type": "stream",
                            "data": json.dumps(event, default=str)
                        })
                    except Exception as send_error:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Failed to send websocket message: {send_error}")
                    
                    # Extract final result from stream events
                    if isinstance(event, dict):
                        # Look for final state in event
                        for node_name, node_state in event.items():
                            if isinstance(node_state, dict) and "messages" in node_state:
                                messages = node_state.get("messages", [])
                                if messages:
                                    last_msg = messages[-1]
                                    if hasattr(last_msg, "content"):
                                        final_result = {
                                            "response": last_msg.content,
                                            "tool_results": node_state.get("tool_results", []),
                                            "iterations": node_state.get("iteration_count", 0)
                                        }
                
                # Use final result from stream, or run if not found
                if final_result is None:
                    result = await agent_service.run(
                        query=query,
                        user_id=authenticated_user_id,
                        document_id=document_id or message_data.get("document_id"),
                        thread_id=thread_id
                    )
                else:
                    result = final_result
                
                # Save chat
                from app.models.chat import Chat
                chat = Chat(
                    question=query,
                    answer=result["response"],
                    user_id=authenticated_user_id,
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
                import logging
                logger = logging.getLogger(__name__)
                logger.exception(f"Error in agent workflow: {e}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": "An error occurred processing your request"
                    })
                except Exception:
                    # Connection may already be closed
                    pass
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"WebSocket connection error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Connection error"
            })
        except Exception:
            # Connection may already be closed
            pass
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
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error in agent workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
