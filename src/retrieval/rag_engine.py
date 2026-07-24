"""
rag_engine.py - Core Retrieval-Augmented Generation logic.
"""

import json
from typing import List, Dict, Any, Tuple
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from src.ai.llm_manager import LLMManager
from src.storage.faiss_manager import FaissManager
import logging

logger = logging.getLogger(__name__)

# Base Prompts
RAG_SYSTEM_PROMPT = """You are DocuMind, an intelligent and highly accurate AI research assistant.
Your goal is to answer the user's question based strictly on the provided context documents.

Rules:
1. If the answer is not contained in the context, politely state that you cannot answer based on the provided documents.
2. Use markdown formatting to make your answer easy to read (bullet points, bold text).
3. Do NOT make up facts or use outside knowledge.
"""

class RAGEngine:
    """Coordinates retrieval and generation for RAG."""
    
    def __init__(self, llm_manager: LLMManager, faiss_manager: FaissManager):
        self.llm = llm_manager
        self.faiss = faiss_manager
        
    def retrieve(self, collection_id: int, query: str, k: int = 5) -> List[Document]:
        """Retrieves top k most similar documents from a collection."""
        vectorstore = self.faiss.load_vectorstore(collection_id)
        if not vectorstore:
            logger.warning(f"No vector store found for collection {collection_id}")
            return []
            
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(query)
        return docs
        
    def build_context_string(self, docs: List[Document]) -> Tuple[str, List[Dict]]:
        """Builds a formatted context string and citation list."""
        context_parts = []
        citations = []
        
        for idx, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown Document')
            text = doc.page_content.strip()
            
            context_parts.append(f"--- Document [{idx+1}]: {source} ---\n{text}\n")
            citations.append({
                "id": idx + 1,
                "source": source,
                "snippet": text[:150] + "..."
            })
            
        return "\n".join(context_parts), citations

    def ask(self, collection_id: int, query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Performs a RAG query and returns the full response object with citations."""
        # 1. Retrieve
        docs = self.retrieve(collection_id, query)
        context_str, citations = self.build_context_string(docs)
        
        # 2. Construct Prompt
        user_prompt = f"Context Information:\n{context_str}\n\nUser Question: {query}"
        
        messages = [SystemMessage(content=RAG_SYSTEM_PROMPT)]
        
        # Add history if available
        if history:
            for msg in history:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    # Simplified for now, in Langchain it's AIMessage
                    from langchain_core.messages import AIMessage
                    messages.append(AIMessage(content=msg['content']))
                    
        messages.append(HumanMessage(content=user_prompt))
        
        # 3. Generate
        try:
            response = self.llm.generate(messages)
            return {
                "answer": response.content,
                "citations": citations
            }
        except Exception as e:
            logger.error(f"Error during RAG generation: {e}")
            return {
                "answer": f"Sorry, I encountered an error generating the response: {str(e)}",
                "citations": []
            }
