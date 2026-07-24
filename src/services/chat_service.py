"""
chat_service.py - Orchestrates Chat sessions and RAG interactions.
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.storage.database import ChatSession, ChatMessage
from src.retrieval.rag_engine import RAGEngine
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: Session, rag_engine: RAGEngine):
        self.db = db
        self.rag = rag_engine
        
    def create_session(self, collection_id: int, title: str = "New Chat") -> ChatSession:
        session = ChatSession(collection_id=collection_id, title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
        
    def get_sessions(self, collection_id: int) -> List[ChatSession]:
        return self.db.query(ChatSession).filter(ChatSession.collection_id == collection_id).order_by(ChatSession.created_at.desc()).all()
        
    def get_messages(self, session_id: int) -> List[ChatMessage]:
        return self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()

    def send_message(self, session_id: int, collection_id: int, content: str) -> Dict[str, Any]:
        """Handles a user message, queries RAG, and saves both to DB."""
        
        # 1. Save User Message
        user_msg = ChatMessage(session_id=session_id, role="user", content=content)
        self.db.add(user_msg)
        
        # 2. Get History (last 4 messages to preserve context but limit tokens)
        history = self.get_messages(session_id)[-4:]
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in history]
        
        # 3. Query RAG
        response_data = self.rag.ask(collection_id=collection_id, query=content, history=history_dicts)
        
        # 4. Save Assistant Message
        citations_json = json.dumps(response_data.get("citations", []))
        asst_msg = ChatMessage(
            session_id=session_id, 
            role="assistant", 
            content=response_data["answer"],
            citations=citations_json
        )
        self.db.add(asst_msg)
        self.db.commit()
        
        return response_data
