"""Enhanced RAG service using LangChain with advanced retrieval patterns"""
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from langchain_community.vectorstores import FAISS, Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import settings, LLMProvider
import os

# Optional imports for embeddings
try:
    from langchain_google_vertexai import VertexAIEmbeddings
    VERTEX_AI_EMBEDDINGS_AVAILABLE = True
except ImportError:
    VERTEX_AI_EMBEDDINGS_AVAILABLE = False
    VertexAIEmbeddings = None

try:
    from langchain_aws import BedrockEmbeddings
    BEDROCK_EMBEDDINGS_AVAILABLE = True
except ImportError:
    BEDROCK_EMBEDDINGS_AVAILABLE = False
    BedrockEmbeddings = None
# Optional retrievers - may not be available in all LangChain versions
RETRIEVERS_AVAILABLE = False
ContextualCompressionRetriever = None
LLMChainExtractor = None

try:
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    RETRIEVERS_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import paths for different LangChain versions
        from langchain_core.retrievers import BaseRetriever
        # Compression retrievers may not be available
        RETRIEVERS_AVAILABLE = False
    except ImportError:
        pass
from langchain_core.documents import Document
from app.ai.llm import LLMService
from app.config import settings, LLMProvider
import os
import pickle
import numpy as np


class EnhancedRAGService:
    """Enhanced RAG service with LangChain integration and advanced retrieval"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.embeddings = self._initialize_embeddings()
        self.vectorstore = self._initialize_vectorstore()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def _initialize_embeddings(self):
        """Initialize embeddings based on provider"""
        provider = settings.LLM_PROVIDER
        
        if provider == LLMProvider.GROQ:
            # Groq doesn't have embeddings, use OpenAI embeddings
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for embeddings when using Groq provider")
            return OpenAIEmbeddings(
                model=getattr(settings, 'EMBEDDING_MODEL', settings.OPENAI_EMBEDDING_MODEL),
                api_key=settings.OPENAI_API_KEY
            )
        elif provider == LLMProvider.OPENAI:
            return OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY
            )
        elif provider == LLMProvider.VERTEX_AI:
            if not VERTEX_AI_EMBEDDINGS_AVAILABLE:
                raise ImportError(
                    "langchain-google-vertexai is not installed. "
                    "Install it with: pip install langchain-google-vertexai"
                )
            return VertexAIEmbeddings(
                model_name=settings.VERTEX_AI_EMBEDDING_MODEL,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
        elif provider == LLMProvider.AWS_BEDROCK:
            if not BEDROCK_EMBEDDINGS_AVAILABLE:
                raise ImportError(
                    "langchain-aws is not installed. "
                    "Install it with: pip install langchain-aws"
                )
            return BedrockEmbeddings(
                model_id=settings.BEDROCK_EMBEDDING_MODEL,
                region_name=settings.AWS_REGION
            )
        else:
            raise ValueError(f"Unsupported provider for embeddings: {provider}")
    
    def _initialize_vectorstore(self):
        """Initialize vector store"""
        if settings.VECTOR_STORE_TYPE == "faiss":
            return self._load_faiss_store()
        elif settings.VECTOR_STORE_TYPE == "chroma":
            return self._load_chroma_store()
        else:
            raise ValueError(f"Unsupported vector store type: {settings.VECTOR_STORE_TYPE}")
    
    def _load_faiss_store(self):
        """Load or create FAISS vector store"""
        index_path = settings.FAISS_INDEX_PATH
        os.makedirs(index_path, exist_ok=True)
        
        index_file = os.path.join(index_path, "index.faiss")
        pkl_file = os.path.join(index_path, "index.pkl")
        
        if os.path.exists(index_file) and os.path.exists(pkl_file):
            # Only allow deserialization if index_path is trusted (restrict via filesystem permissions)
            # For production, validate index files before loading
            try:
                return FAISS.load_local(
                    index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=False  # Set to False and validate files first
                )
            except Exception:
                # If loading fails, create fresh empty index without API calls
                return self._create_empty_faiss_store()
        else:
            # Create empty store without making API calls
            return self._create_empty_faiss_store()
    
    def _create_empty_faiss_store(self):
        """Create an empty FAISS store without making embedding API calls"""
        import faiss
        
        # Get embedding dimension from settings
        if settings.LLM_PROVIDER == LLMProvider.GROQ:
            dimension = getattr(settings, 'EMBEDDING_DIMENSION', settings.OPENAI_EMBEDDING_DIMENSION)
        elif settings.LLM_PROVIDER == LLMProvider.OPENAI:
            dimension = settings.OPENAI_EMBEDDING_DIMENSION
        elif settings.LLM_PROVIDER == LLMProvider.VERTEX_AI:
            dimension = settings.VERTEX_AI_EMBEDDING_DIMENSION
        elif settings.LLM_PROVIDER == LLMProvider.AWS_BEDROCK:
            dimension = settings.BEDROCK_EMBEDDING_DIMENSION
        else:
            dimension = getattr(settings, 'EMBEDDING_DIMENSION', 3072)
        
        # Create empty FAISS index
        index = faiss.IndexFlatL2(dimension)
        
        # Create index files manually to avoid API calls
        index_path = settings.FAISS_INDEX_PATH
        index_file = os.path.join(index_path, "index.faiss")
        pkl_file = os.path.join(index_path, "index.pkl")
        
        # Save empty index
        faiss.write_index(index, index_file)
        
        # Save empty metadata (FAISS format)
        with open(pkl_file, "wb") as f:
            pickle.dump({"ids": [], "metadatas": []}, f)
        
        # Load it back - this won't make API calls since index is already created
        return FAISS.load_local(
            index_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def _load_chroma_store(self):
        """Load or create Chroma vector store"""
        persist_directory = settings.CHROMA_PERSIST_DIR
        os.makedirs(persist_directory, exist_ok=True)
        
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
    
    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ):
        """Add documents to the vector store"""
        # Split texts into chunks
        documents = []
        for i, text in enumerate(texts):
            chunks = self.text_splitter.split_text(text)
            for chunk in chunks:
                # Safely get metadata with copy to avoid mutating caller's dict
                if metadatas and i < len(metadatas):
                    metadata = dict(metadatas[i])
                else:
                    metadata = {}
                metadata["chunk_index"] = len(documents)
                documents.append(Document(page_content=chunk, metadata=metadata))
        
        # Add to vector store
        if settings.VECTOR_STORE_TYPE == "faiss":
            self.vectorstore.add_documents(documents)
            self.vectorstore.save_local(settings.FAISS_INDEX_PATH)
        else:
            self.vectorstore.add_documents(documents)
            # Chroma persists automatically in recent versions, no need to call persist()
    
    async def get_relevant_context(
        self,
        query: str,
        user_id: int,
        document_id: Optional[int] = None,
        top_k: int = None
    ) -> str:
        """Get relevant context using RAG"""
        top_k = top_k or settings.RAG_TOP_K
        
        # Build filter
        filter_dict = {"user_id": user_id}
        if document_id:
            filter_dict["document_id"] = document_id
        
        # Retrieve documents
        retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": top_k,
                "filter": filter_dict if filter_dict else None
            }
        )
        
        # Apply compression if enabled
        if settings.RAG_RERANK and RETRIEVERS_AVAILABLE and LLMChainExtractor:
            try:
                compressor = LLMChainExtractor.from_llm(self.llm_service.llm)
                compression_retriever = ContextualCompressionRetriever(
                    base_compressor=compressor,
                    base_retriever=retriever
                )
                docs = await compression_retriever.aget_relevant_documents(query)
            except Exception:
                # Fallback to regular retrieval if compression fails
                docs = await retriever.aget_relevant_documents(query)
        else:
            docs = await retriever.aget_relevant_documents(query)
        
        # Filter by similarity threshold
        filtered_docs = []
        for doc in docs:
            # Calculate similarity (simplified - actual implementation depends on vectorstore)
            if hasattr(doc, "metadata") and "score" in doc.metadata:
                if doc.metadata["score"] >= settings.RAG_SIMILARITY_THRESHOLD:
                    filtered_docs.append(doc)
            else:
                filtered_docs.append(doc)
        
        # Combine context
        context = "\n\n".join([doc.page_content for doc in filtered_docs[:top_k]])
        return context
    
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Perform similarity search"""
        return await self.vectorstore.asimilarity_search(
            query,
            k=k,
            filter=filter
        )
    
    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """Perform similarity search with scores"""
        return await self.vectorstore.asimilarity_search_with_score(
            query,
            k=k,
            filter=filter
        )

