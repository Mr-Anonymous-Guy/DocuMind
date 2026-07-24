"""
chunker.py - Document chunking logic using RecursiveCharacterTextSplitter.
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentChunker:
    """Handles splitting LangChain Documents into smaller chunks."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or CHUNK_OVERLAP
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of documents into chunks.
        
        Args:
            documents: List of LangChain Documents.
            
        Returns:
            List of chunked LangChain Documents.
        """
        return self.splitter.split_documents(documents)
