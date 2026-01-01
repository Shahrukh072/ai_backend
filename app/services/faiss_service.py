import faiss
import numpy as np
import pickle
import os
from app.config import settings
from typing import List, Dict, Optional


class FAISSService:
    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.dimension = settings.EMBEDDING_DIMENSION
        self.index = None
        self.id_to_text = {}
        self.id_to_doc_id = {}
        self._load_index()
    
    def _load_index(self):
        """Load or create FAISS index"""
        os.makedirs(self.index_path, exist_ok=True)
        index_file = os.path.join(self.index_path, "index.faiss")
        metadata_file = os.path.join(self.index_path, "metadata.pkl")
        
        if os.path.exists(index_file) and os.path.exists(metadata_file):
            self.index = faiss.read_index(index_file)
            with open(metadata_file, "rb") as f:
                metadata = pickle.load(f)
                self.id_to_text = metadata.get("id_to_text", {})
                self.id_to_doc_id = metadata.get("id_to_doc_id", {})
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)
            self._save_index()
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        index_file = os.path.join(self.index_path, "index.faiss")
        metadata_file = os.path.join(self.index_path, "metadata.pkl")
        
        faiss.write_index(self.index, index_file)
        with open(metadata_file, "wb") as f:
            pickle.dump({
                "id_to_text": self.id_to_text,
                "id_to_doc_id": self.id_to_doc_id
            }, f)
    
    def add_documents(self, document_id: int, texts: List[str], embeddings: np.ndarray):
        """Add documents to the index"""
        start_id = len(self.id_to_text)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        for i, text in enumerate(texts):
            idx = start_id + i
            self.id_to_text[idx] = text
            self.id_to_doc_id[idx] = document_id
        
        self._save_index()
    
    def search(
        self,
        query_embedding: List[float],
        document_id: Optional[int] = None,
        k: int = 5
    ) -> List[Dict[str, any]]:
        """Search for similar documents"""
        if self.index.ntotal == 0:
            return []
        
        query_vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_vector, min(k * 2, self.index.ntotal))
        
        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            
            # Filter by document_id if specified
            if document_id and self.id_to_doc_id.get(idx) != document_id:
                continue
            
            if idx in self.id_to_text:
                results.append({
                    "text": self.id_to_text[idx],
                    "document_id": self.id_to_doc_id.get(idx),
                    "distance": float(distances[0][len(results)])
                })
            
            if len(results) >= k:
                break
        
        return results

