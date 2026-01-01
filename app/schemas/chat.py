from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatBase(BaseModel):
    question: str
    document_id: Optional[int] = None


class ChatCreate(ChatBase):
    pass


class ChatResponse(ChatBase):
    id: int
    answer: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    question: str
    document_id: Optional[int] = None

