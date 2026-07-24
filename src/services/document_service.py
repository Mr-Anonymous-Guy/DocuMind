"""
document_service.py - Orchestrates document upload, chunking, and embedding.
"""

import os
from sqlalchemy.orm import Session
from src.storage.database import Document as DBDocument
from src.storage.faiss_manager import FaissManager
from src.document.loader import DocumentLoader
from src.document.chunker import DocumentChunker
from src.config import DATA_DIR
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: Session, faiss_manager: FaissManager):
        self.db = db
        self.faiss = faiss_manager
        self.chunker = DocumentChunker()
        
    def process_and_add_document(self, collection_id: int, file_bytes: bytes, filename: str, file_type: str) -> bool:
        """Saves file to disk, parses it, chunks it, embeds it, and saves metadata."""
        
        # 1. Save file to disk
        collection_dir = os.path.join(DATA_DIR, f"coll_{collection_id}")
        os.makedirs(collection_dir, exist_ok=True)
        
        filepath = os.path.join(collection_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(file_bytes)
            
        # 2. Parse and load
        try:
            docs = DocumentLoader.load_file(filepath, filename)
        except Exception as e:
            logger.error(f"Failed to parse document: {e}")
            return False
            
        # 3. Chunk
        chunks = self.chunker.chunk_documents(docs)
        if not chunks:
            logger.warning(f"No text found in {filename}")
            return False
            
        # 4. Embed and store in FAISS
        try:
            self.faiss.add_documents(collection_id, chunks)
        except Exception as e:
            logger.error(f"Failed to embed document chunks: {e}")
            return False
            
        # 5. Save to Metadata DB
        db_doc = DBDocument(
            collection_id=collection_id,
            filename=filename,
            filepath=filepath,
            file_type=file_type,
            num_chunks=len(chunks)
        )
        self.db.add(db_doc)
        self.db.commit()
        
        return True
