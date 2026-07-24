"""
loader.py - Document loading strategies using LangChain document loaders.
"""

import os
import tempfile
import logging
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Handles parsing of PDF, DOCX, TXT, and Markdown files."""
    
    @staticmethod
    def load_file(file_path: str, filename: str = None) -> List[Document]:
        """
        Loads a file from path and extracts its text into LangChain Documents.
        
        Args:
            file_path: Absolute or relative path to the file.
            filename: Original filename to store in metadata (optional).
            
        Returns:
            List of LangChain Document objects.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        if not filename:
            filename = os.path.basename(file_path)
            
        documents = []
        try:
            if ext == '.pdf':
                loader = PyMuPDFLoader(file_path)
                documents = loader.load()
            elif ext == '.docx':
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            elif ext == '.txt':
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
            elif ext == '.md':
                loader = UnstructuredMarkdownLoader(file_path)
                documents = loader.load()
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
                
            # Add custom metadata
            for doc in documents:
                doc.metadata['source'] = filename
                
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {filename}: {e}")
            raise e

    @staticmethod
    def load_bytes(file_bytes: bytes, filename: str) -> List[Document]:
        """
        Helper to load file from bytes (useful for Streamlit uploads).
        Writes to a temp file, loads it, then cleans up.
        """
        ext = os.path.splitext(filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
            
        try:
            documents = DocumentLoader.load_file(temp_path, filename)
            return documents
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
