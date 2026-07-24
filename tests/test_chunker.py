import pytest
from langchain_core.documents import Document
from src.document.chunker import DocumentChunker

def test_document_chunker_basic():
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    
    # Create a dummy doc
    text = "This is a very long string that needs to be chunked into multiple pieces so we can test the chunker properly."
    doc = Document(page_content=text, metadata={"source": "test.txt"})
    
    chunks = chunker.chunk_documents([doc])
    
    # Assert we got chunks back
    assert len(chunks) > 1
    # Assert metadata is preserved
    assert chunks[0].metadata["source"] == "test.txt"
    # Assert no chunk exceeds chunk size too severely (allowing for word boundaries)
    assert len(chunks[0].page_content) <= 50
