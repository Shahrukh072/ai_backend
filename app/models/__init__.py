# Import all models so they're registered with SQLAlchemy
from app.models.user import User
from app.models.document import Document
from app.models.chat import Chat

__all__ = ["User", "Document", "Chat"]

