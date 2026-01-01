from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Chat(BaseModel):
    __tablename__ = "chats"
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    document = relationship("Document", back_populates="chats")

