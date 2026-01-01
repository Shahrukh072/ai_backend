import os
import aiofiles
from fastapi import UploadFile
from typing import Optional
from app.config import settings


async def save_upload_file(file: UploadFile, user_id: int) -> str:
    """Save uploaded file to disk"""
    upload_dir = f"./uploads/user_{user_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return file_path


async def extract_text_from_file(file_path: str, filename: str) -> str:
    """Extract text from various file formats"""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".txt":
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()
    
    elif ext == ".pdf":
        try:
            import PyPDF2
            text = ""
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except ImportError:
            raise Exception("PyPDF2 is required for PDF processing")
    
    elif ext == ".docx":
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            raise Exception("python-docx is required for DOCX processing")
    
    elif ext == ".md":
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()
    
    else:
        raise Exception(f"Unsupported file type: {ext}")

