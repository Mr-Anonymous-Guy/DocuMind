"""
collection_service.py - Orchestrates Collection CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.storage.database import Collection, Document, ChatSession
from src.storage.faiss_manager import FaissManager
import logging

logger = logging.getLogger(__name__)

class CollectionService:
    def __init__(self, db: Session, faiss_manager: FaissManager):
        self.db = db
        self.faiss = faiss_manager
        
    def create_collection(self, name: str, description: str = "") -> Collection:
        collection = Collection(name=name, description=description)
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        return collection
        
    def get_collections(self) -> List[Collection]:
        return self.db.query(Collection).all()
        
    def get_collection(self, collection_id: int) -> Optional[Collection]:
        return self.db.query(Collection).filter(Collection.id == collection_id).first()
        
    def delete_collection(self, collection_id: int) -> bool:
        collection = self.get_collection(collection_id)
        if not collection:
            return False
            
        try:
            # Delete FAISS index
            self.faiss.delete_collection(collection_id)
            # Delete DB entry (cascades to docs and chats)
            self.db.delete(collection)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_id}: {e}")
            self.db.rollback()
            return False
