from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from app.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService
from app.utils.file_utils import save_upload_file, extract_text_from_file
from app.utils.text_splitter import TextSplitter
from app.config import settings
import os


class DocumentLoaderService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.faiss_service = FAISSService()
        self.text_splitter = TextSplitter()
    
    async def upload_and_process(self, file: UploadFile, user_id: int) -> Document:
        """Upload file, extract text, create embeddings, and store in vector DB"""
        # Validate file
        if not self._validate_file(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type or size"
            )
        
        # Save file
        file_path = await save_upload_file(file, user_id)
        
        try:
            # Extract text
            content = await extract_text_from_file(file_path, file.filename)
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Create document record
            document = Document(
                title=file.filename,
                file_path=file_path,
                file_type=os.path.splitext(file.filename)[1],
                file_size=file.size or 0,
                content=content,
                user_id=user_id
            )
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            # Generate embeddings and store in FAISS
            embeddings = await self.embedding_service.create_embeddings(chunks)
            self.faiss_service.add_documents(document.id, chunks, embeddings)
            
            return document
        
        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing document: {str(e)}"
            )
    
    def _validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        if not file.filename:
            return False
        
        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False
        
        # Check file size (if available)
        if file.size and file.size > settings.MAX_FILE_SIZE:
            return False
        
        return True

