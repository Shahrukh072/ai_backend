import faiss
import numpy as np
import pickle
import os
import logging
import json
from app.config import settings, LLMProvider
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class FAISSService:
    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        # Get dimension based on provider
        provider = settings.LLM_PROVIDER
        if provider == LLMProvider.GROQ:
            # Groq uses OpenAI embeddings
            self.dimension = getattr(settings, 'EMBEDDING_DIMENSION', settings.OPENAI_EMBEDDING_DIMENSION)
        elif provider == LLMProvider.OPENAI:
            self.dimension = settings.OPENAI_EMBEDDING_DIMENSION
        elif provider == LLMProvider.VERTEX_AI:
            self.dimension = settings.VERTEX_AI_EMBEDDING_DIMENSION
        elif provider == LLMProvider.AWS_BEDROCK:
            self.dimension = settings.BEDROCK_EMBEDDING_DIMENSION
        else:
            self.dimension = settings.OPENAI_EMBEDDING_DIMENSION  # default
        self.index = None
        self.id_to_text = {}
        self.id_to_doc_id = {}
        self._load_index()
    
    def _load_index(self):
        """Load or create FAISS index"""
        os.makedirs(self.index_path, exist_ok=True)
        index_file = os.path.join(self.index_path, "index.faiss")
        metadata_file = os.path.join(self.index_path, "metadata.pkl")
        
        try:
            if os.path.exists(index_file) and os.path.exists(metadata_file):
                self.index = faiss.read_index(index_file)
                
                # Validate dimension
                index_dim = getattr(self.index, "d", None)
                if index_dim is None:
                    # Try alternative attribute
                    index_dim = self.index.dimension() if hasattr(self.index, "dimension") else None
                
                if index_dim != self.dimension:
                    logger.warning(
                        f"Index dimension mismatch: expected {self.dimension}, got {index_dim}. "
                        "Creating new index."
                    )
                    self.index = None
                else:
                    # Load metadata with safer approach
                    try:
                        # Try JSON first (safer)
                        json_metadata_file = os.path.join(self.index_path, "metadata.json")
                        if os.path.exists(json_metadata_file):
                            with open(json_metadata_file, "r") as f:
                                metadata = json.load(f)
                        else:
                            # Fallback to pickle with validation
                            with open(metadata_file, "rb") as f:
                                metadata = pickle.load(f)
                        
                        self.id_to_text = metadata.get("id_to_text", {})
                        self.id_to_doc_id = metadata.get("id_to_doc_id", {})
                    except Exception as e:
                        logger.error(f"Error loading metadata: {e}")
                        self.id_to_text = {}
                        self.id_to_doc_id = {}
            else:
                self.index = None
        except Exception as e:
            logger.exception(f"Error loading FAISS index: {e}")
            self.index = None
        
        # Create new index if loading failed
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.id_to_text = {}
            self.id_to_doc_id = {}
            self._save_index()
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        index_file = os.path.join(self.index_path, "index.faiss")
        metadata_file = os.path.join(self.index_path, "metadata.pkl")
        json_metadata_file = os.path.join(self.index_path, "metadata.json")
        
        try:
            faiss.write_index(self.index, index_file)
            
            # Save metadata as JSON (safer) and pickle (for backward compatibility)
            metadata = {
                "id_to_text": self.id_to_text,
                "id_to_doc_id": self.id_to_doc_id
            }
            
            # Save as JSON
            with open(json_metadata_file, "w") as f:
                json.dump(metadata, f)
            
            # Also save as pickle for backward compatibility
            with open(metadata_file, "wb") as f:
                pickle.dump(metadata, f)
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            raise
    
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
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if self.index.ntotal == 0:
            return []
        
        query_vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_vector, min(k * 2, self.index.ntotal))
        
        results = []
        # Use enumerate to track position in indices[0] for correct distance indexing
        for pos, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            
            # Filter by document_id if specified
            if document_id and self.id_to_doc_id.get(idx) != document_id:
                continue
            
            if idx in self.id_to_text:
                # Use pos to index into distances[0]
                results.append({
                    "text": self.id_to_text[idx],
                    "document_id": self.id_to_doc_id.get(idx),
                    "distance": float(distances[0][pos])
                })
            
            if len(results) >= k:
                break
        
        return results

