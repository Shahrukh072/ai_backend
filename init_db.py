"""
Database initialization script
Creates all database tables from models
"""
from app.db.session import engine
from app.db.base import Base
# Import all models to register them with SQLAlchemy
from app.models import User, Document, Chat

def init_database():
    """Create all database tables"""
    print("🗄️  Initializing database...")
    print("Creating tables: users, documents, chats")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - documents")
        print("  - chats")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL in .env is correct")
        print("  3. Database exists (create it if needed)")
        return False
    
    return True

if __name__ == "__main__":
    init_database()

