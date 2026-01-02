"""Tests for RAG service"""
import pytest
from app.services.enhanced_rag_service import EnhancedRAGService
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_rag_initialization(db_session: Session):
    """Test RAG service initialization"""
    rag_service = EnhancedRAGService(db_session)
    assert rag_service is not None
    assert rag_service.embeddings is not None
    assert rag_service.vectorstore is not None


@pytest.mark.asyncio
async def test_rag_add_documents(db_session: Session):
    """Test adding documents to RAG"""
    rag_service = EnhancedRAGService(db_session)
    
    texts = ["This is a test document.", "Another test document."]
    metadatas = [{"user_id": 1, "document_id": 1}, {"user_id": 1, "document_id": 1}]
    
    await rag_service.add_documents(texts, metadatas)
    
    # Verify documents were added
    assert rag_service.vectorstore is not None


@pytest.mark.asyncio
async def test_rag_retrieval(db_session: Session):
    """Test RAG retrieval"""
    rag_service = EnhancedRAGService(db_session)
    
    # Add test documents first
    texts = ["Python is a programming language.", "FastAPI is a web framework."]
    metadatas = [{"user_id": 1}, {"user_id": 1}]
    await rag_service.add_documents(texts, metadatas)
    
    # Retrieve context
    context = await rag_service.get_relevant_context(
        query="What is Python?",
        user_id=1,
        top_k=2
    )
    
    assert context is not None
    assert len(context) > 0


@pytest.fixture
def db_session():
    """Fixture for database session"""
    from app.database import SessionLocal
    session = SessionLocal()
    yield session
    session.close()

