from typing import List
try:
    # Try new langchain import (0.2.0+)
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback to old import (0.1.x)
    from langchain.text_splitter import RecursiveCharacterTextSplitter


class TextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        return self.splitter.split_text(text)

