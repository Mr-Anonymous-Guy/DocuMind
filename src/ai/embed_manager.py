"""
embed_manager.py - Manages Embedding Models via Ollama and LangChain.
"""

from langchain_ollama import OllamaEmbeddings
from src.config import OLLAMA_BASE_URL, DEFAULT_EMBED_MODEL

class EmbedManager:
    """Wrapper for Ollama Embedding Models."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or DEFAULT_EMBED_MODEL
        self.embeddings = OllamaEmbeddings(
            model=self.model_name,
            base_url=OLLAMA_BASE_URL
        )
        
    def get_embeddings(self) -> OllamaEmbeddings:
        """Returns the LangChain embeddings object to be passed to FAISS."""
        return self.embeddings
