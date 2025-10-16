import pytest
from app.services.chunker import TextChunker

def test_chunker_creates_chunks():
    """Test that chunker creates appropriate chunks"""
    chunker = TextChunker(chunk_size=100, overlap=20)
    
    text = "This is a test. " * 50  # Create long text
    metadata = {"source": "test"}
    
    chunks = chunker.chunk_text(text, metadata)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)

def test_chunker_respects_metadata():
    """Test that metadata is attached to chunks"""
    chunker = TextChunker(chunk_size=100, overlap=20)
    
    text = "Test text"
    metadata = {"source": "test-source", "filename": "test.txt"}
    
    chunks = chunker.chunk_text(text, metadata)
    
    assert all(chunk["metadata"]["source"] == "test-source" for chunk in chunks)
    assert all(chunk["metadata"]["filename"] == "test.txt" for chunk in chunks)

def test_chunker_with_short_text():
    """Test chunker with text shorter than chunk size"""
    chunker = TextChunker(chunk_size=1000, overlap=100)
    
    text = "Short text."
    metadata = {"source": "test"}
    
    chunks = chunker.chunk_text(text, metadata)
    
    assert len(chunks) == 1
    assert chunks[0]["text"] == text
