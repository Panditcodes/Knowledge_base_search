"""
Text chunker with overlap strategy
Supports token-accurate chunking
"""
import tiktoken
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(
        self,
        chunk_size: int = 400,
        overlap: int = 75,
        model_name: str = "gpt-3.5-turbo"
    ):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target chunk size in tokens
            overlap: Overlap size in tokens
            model_name: Tokenizer model to use
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Could not load encoding for {model_name}, using cl100k_base")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text with overlap
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dicts with 'text' and 'metadata'
        """
        if not text or not text.strip():
            return []
        
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        chunk_id = 0
        
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens).strip()
            
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_id"] = chunk_id
            chunk_metadata["start_token"] = start
            chunk_metadata["end_token"] = end
            chunk_metadata["token_count"] = len(chunk_tokens)
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
            
            if end == len(tokens):
                break
            
            start = max(0, end - self.overlap)
            chunk_id += 1
        
        logger.info(f"Created {len(chunks)} chunks from text ({len(tokens)} tokens)")
        return chunks
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of dicts with 'text' and 'metadata'
            
        Returns:
            List of all chunks
        """
        all_chunks = []
        
        for doc in documents:
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            chunks = self.chunk_text(text, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks
