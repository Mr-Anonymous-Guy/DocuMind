"""
faiss_manager.py - Manage FAISS vector store operations for RAG.
"""

import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document as LC_Document
from src.config import FAISS_INDEX_PATH
import logging

logger = logging.getLogger(__name__)

class FaissManager:
    """Manages the FAISS vector database."""
    
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        
    def _get_collection_path(self, collection_id: int) -> str:
        """Returns the FAISS path for a specific collection."""
        path = os.path.join(FAISS_INDEX_PATH, f"collection_{collection_id}")
        return path

    def load_vectorstore(self, collection_id: int) -> Optional[FAISS]:
        """Loads a FAISS index from disk for a specific collection."""
        path = self._get_collection_path(collection_id)
        if os.path.exists(path):
            try:
                return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                logger.error(f"Failed to load FAISS index at {path}: {e}")
                return None
        return None

    def add_documents(self, collection_id: int, documents: List[LC_Document]) -> int:
        """Adds embedded documents to a collection's FAISS index."""
        path = self._get_collection_path(collection_id)
        
        # Load existing or create new
        vectorstore = self.load_vectorstore(collection_id)
        
        if vectorstore is None:
            vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            vectorstore.add_documents(documents)
            
        vectorstore.save_local(path)
        logger.info(f"Saved {len(documents)} chunks to FAISS at {path}")
        return len(documents)

    def delete_collection(self, collection_id: int) -> bool:
        """Deletes the FAISS index for a collection."""
        import shutil
        path = self._get_collection_path(collection_id)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                return True
            except Exception as e:
                logger.error(f"Failed to delete FAISS index at {path}: {e}")
                return False
        return True
