from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.rag import DocumentCreate, DocumentResponse, DocumentUpdate
from app.vectorstore.loader import DocumentLoaderService

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Upload request received: filename={file.filename}, size={file.size}, user_id={current_user.id}")
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        document_service = DocumentLoaderService(db)
        document = await document_service.upload_and_process(file, current_user.id)
        
        logger.info(f"Document uploaded successfully: id={document.id}, title={document.title}")
        return document
    except HTTPException:
        # Re-raise HTTPExceptions (validation errors, etc.)
        raise
    except Exception as e:
        logger.exception(f"Error uploading document: {e}")
        error_msg = str(e)
        # Provide user-friendly error messages
        if "quota" in error_msg.lower() or "429" in error_msg:
            detail = (
                "Document uploaded successfully, but embeddings could not be created due to OpenAI API quota limit. "
                "The document is saved and can be viewed, but RAG (document search) features will not work. "
                "To enable RAG, please add a valid OPENAI_API_KEY with available quota."
            )
        else:
            detail = f"Error processing document: {error_msg}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user"""
    from app.models.document import Document
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    from app.models.document import Document
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    from app.models.document import Document
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db.delete(document)
    db.commit()
    return None

