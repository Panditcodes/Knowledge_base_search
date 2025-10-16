"""
Ingest Worker
Handles document extraction, chunking, embedding, and indexing
"""
import logging
import os
from typing import List, Dict
from PyPDF2 import PdfReader
from app.services.chunker import TextChunker
from app.services.jina_embedding import JinaEmbedding
from app.services.pinecone_adapter import PineconeAdapter
import uuid

logger = logging.getLogger(__name__)

class IngestWorker:
    def __init__(self):
        self.chunker = TextChunker(chunk_size=400, overlap=75)
        self.jina = JinaEmbedding()
        self.pinecone = PineconeAdapter()
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF or TXT file"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
            
        elif ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def ingest_files(self, file_paths: List[str], source_name: str) -> Dict:
        """Ingest multiple files"""
        all_chunks = []
        
        for file_path in file_paths:
            logger.info(f"Processing file: {file_path}")
            text = self.extract_text_from_file(file_path)
            
            metadata = {
                "source": source_name,
                "filename": os.path.basename(file_path),
                "filepath": file_path
            }
            
            chunks = self.chunker.chunk_text(text, metadata)
            all_chunks.extend(chunks)
        
        return self._index_chunks(all_chunks)
    
    def ingest_text(self, text: str, source_name: str) -> Dict:
        """Ingest raw text"""
        metadata = {"source": source_name}
        chunks = self.chunker.chunk_text(text, metadata)
        return self._index_chunks(chunks)
    
    def _index_chunks(self, chunks: List[Dict]) -> Dict:
        """Embed and index chunks into Pinecone"""
        if not chunks:
            return {"chunks_created": 0, "vectors_indexed": 0}
        
        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.jina.embed_texts(texts)
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = str(uuid.uuid4())
            
            metadata = chunk["metadata"].copy()
            metadata["text"] = chunk["text"][:1000]  # Store snippet
            
            vectors.append({
                "id": vector_id,
                "values": embedding.tolist(),
                "metadata": metadata
            })
        
        # Upsert to Pinecone
        logger.info(f"Upserting {len(vectors)} vectors to Pinecone")
        self.pinecone.upsert(vectors)
        
        return {
            "chunks_created": len(chunks),
            "vectors_indexed": len(vectors)
        }
