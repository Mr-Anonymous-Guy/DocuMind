"""
productivity_service.py - Orchestrates AI productivity tools (Summaries, Flashcards).
"""

from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from src.ai.llm_manager import LLMManager
from src.storage.faiss_manager import FaissManager
import logging

logger = logging.getLogger(__name__)

class ProductivityService:
    def __init__(self, llm_manager: LLMManager, faiss_manager: FaissManager):
        self.llm = llm_manager
        self.faiss = faiss_manager
        
    def _get_collection_text(self, collection_id: int, k: int = 20) -> str:
        """Retrieves a large chunk of text from the collection for summarization."""
        vectorstore = self.faiss.load_vectorstore(collection_id)
        if not vectorstore:
            return ""
            
        # We can simulate getting a broad overview by doing a generic search
        # or getting random chunks if FAISS supports it.
        # For simplicity in this implementation, we do a generic query:
        docs = vectorstore.as_retriever(search_kwargs={"k": k}).invoke("summary overview core concepts")
        return "\n".join([doc.page_content for doc in docs])

    def generate_summary(self, collection_id: int) -> str:
        """Generates an executive summary of the collection."""
        context = self._get_collection_text(collection_id)
        if not context:
            return "No documents available in this collection to summarize."
            
        system = "You are a professional analyst. Provide a clear, structured executive summary of the following documents."
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Context:\n{context}\n\nPlease summarize.")
        ]
        
        try:
            return self.llm.generate(messages).content
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Failed to generate summary."

    def generate_flashcards(self, collection_id: int) -> str:
        """Generates flashcards based on the collection."""
        context = self._get_collection_text(collection_id, k=15)
        if not context:
            return "No documents available."
            
        system = "You are a teacher. Create 5 comprehensive flashcards (Question/Answer format) based on the provided text. Format as Markdown."
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Context:\n{context}\n\nGenerate Flashcards.")
        ]
        
        try:
            return self.llm.generate(messages).content
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return "Failed to generate flashcards."
            
    def generate_quiz(self, collection_id: int) -> str:
        """Generates a multiple choice quiz based on the collection."""
        context = self._get_collection_text(collection_id, k=15)
        if not context:
            return "No documents available."
            
        system = "You are a teacher. Create a 3-question multiple choice quiz with answers at the end, based on the provided text."
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Context:\n{context}\n\nGenerate Quiz.")
        ]
        
        try:
            return self.llm.generate(messages).content
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return "Failed to generate quiz."
