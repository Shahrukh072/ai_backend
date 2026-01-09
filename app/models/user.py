from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    provider = Column(String, default="email")  # 'email' or 'google'
    google_id = Column(String, nullable=True, unique=True, index=True)  # Google user ID
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    chats = relationship("Chat", back_populates="user")

