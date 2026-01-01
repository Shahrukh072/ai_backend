from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    file_type: str


class DocumentCreate(DocumentBase):
    file_path: str
    file_size: int
    content: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = None  # Renamed from 'metadata' to match model


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = None  # Renamed from 'metadata' to match model


class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_size: int
    content: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = None  # Renamed from 'metadata' to match model
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

