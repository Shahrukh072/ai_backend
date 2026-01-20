from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from typing import Optional
from app.models.document import Document
from app.ai.embeddings import EmbeddingService
from app.vectorstore.faiss_store import FAISSService
from app.utils.file_utils import save_upload_file, extract_text_from_file
from app.utils.text_splitter import TextSplitter
from app.config import settings
import os
import logging

# Module-level logger - use this throughout the file
_logger = logging.getLogger(__name__)


class DocumentLoaderService:
    def __init__(self, db: Session):
        self.db = db
        # Initialize embedding service - will fail gracefully if API key is missing
        try:
            self.embedding_service = EmbeddingService()
            self.embeddings_available = True
        except (ValueError, Exception) as e:
            _logger.warning(f"Embedding service not available: {e}. Documents can still be uploaded but RAG will not work.")
            self.embedding_service = None
            self.embeddings_available = False
        self.faiss_service = FAISSService()
        self.text_splitter = TextSplitter()
    
    async def upload_and_process(self, file: UploadFile, user_id: int) -> Document:
        """Upload file, extract text, create embeddings, and store in vector DB"""
        # Validate file
        validation_error = self._validate_file(file)
        if validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_error
            )
        
        # Save file
        file_path = await save_upload_file(file, user_id)
        
        try:
            # Extract text
            content = await extract_text_from_file(file_path, file.filename)
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Get file size from saved file if not available from upload
            file_size = file.size
            if file_size is None:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Create document record
            document = Document(
                title=file.filename,
                file_path=file_path,
                file_type=os.path.splitext(file.filename)[1],
                file_size=file_size,
                content=content,
                user_id=user_id
            )
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            # Generate embeddings and store in FAISS (optional - continue even if it fails)
            if self.embeddings_available and self.embedding_service:
                try:
                    embeddings = await self.embedding_service.create_embeddings(chunks)
                    self.faiss_service.add_documents(document.id, chunks, embeddings)
                    _logger.info(f"Successfully created embeddings for document {document.id}")
                except Exception as embedding_error:
                    # Log error but don't fail the upload - document is saved, just no RAG yet
                    error_msg = str(embedding_error)
                    if "quota" in error_msg.lower() or "429" in error_msg:
                        _logger.warning(
                            f"OpenAI API quota exceeded. Document {document.id} uploaded successfully "
                            f"but embeddings could not be created. RAG features will not be available. "
                            f"To enable RAG, add a valid OPENAI_API_KEY with available quota."
                        )
                    else:
                        _logger.warning(
                            f"Failed to create embeddings for document {document.id}: {embedding_error}. "
                            f"Document uploaded successfully but RAG features will not be available."
                        )
                    # Document is still saved and can be used, just without vector search
            else:
                _logger.info(
                    f"Embedding service not available. Document {document.id} uploaded successfully "
                    f"but RAG features will not be available. To enable RAG, configure OPENAI_API_KEY."
                )
            
            return document
        
        except HTTPException:
            # Re-raise HTTPExceptions (validation errors, etc.)
            raise
        except Exception as e:
            # Clean up on error
            _logger.exception(f"Error processing document: {e}")
            
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            # Provide more helpful error messages
            error_detail = str(e)
            if "quota" in error_detail.lower() or "429" in error_detail:
                error_detail = (
                    "OpenAI API quota exceeded. Document was saved but embeddings could not be created. "
                    "To enable RAG features, please add a valid OPENAI_API_KEY with available quota, "
                    "or wait for your quota to reset."
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing document: {error_detail}"
            )
    
    def _validate_file(self, file: UploadFile) -> Optional[str]:
        """Validate uploaded file. Returns error message if invalid, None if valid."""
        if not file or not file.filename:
            return "No file or filename provided"
        
        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if not ext or ext not in settings.ALLOWED_EXTENSIONS:
            allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
            return f"Invalid file type. Allowed types: {allowed}. Received: {ext or 'unknown'}"
        
        # Check file size (if available)
        # Note: file.size might be None for streaming uploads
        if file.size is not None and file.size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            file_size_mb = file.size / (1024 * 1024)
            return f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
        
        if file.size is not None and file.size == 0:
            return "File is empty"
        
        return None

