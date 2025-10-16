"""
Pinecone Vector Store Adapter
Handles indexing and retrieval from Pinecone
"""
import os
import logging
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
import time

logger = logging.getLogger(__name__)

class PineconeAdapter:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY", "")
        self.environment = os.getenv("PINECONE_ENV", "us-east-1")
        self.index_name = os.getenv("PINECONE_INDEX", "rag-index")
        self.dimension = int(os.getenv("PINECONE_DIMENSION", "768"))
        
        if not self.api_key:
            logger.warning("PINECONE_API_KEY not set")
            
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        self._ensure_index()
    
    def _ensure_index(self):
        """Create index if it doesn't exist"""
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment
                    )
                )
                # Wait for index to be ready
                time.sleep(5)
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {e}")
            raise
    
    def upsert(self, vectors: List[Dict[str, Any]]):
        """
        Upsert vectors to Pinecone
        
        Args:
            vectors: List of dicts with keys: id, values (embedding), metadata
        """
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")
            raise
    
    def query(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Dict = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar vectors
        
        Returns:
            List of matches with id, score, and metadata
        """
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter,
                include_metadata=include_metadata
            )
            
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": float(match.score),
                    "metadata": match.metadata if include_metadata else {}
                })
            
            return matches
            
        except Exception as e:
            logger.error(f"Pinecone query failed: {e}")
            raise
    
    def delete(self, ids: List[str]):
        """Delete vectors by IDs"""
        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors from Pinecone")
        except Exception as e:
            logger.error(f"Pinecone delete failed: {e}")
            raise
    
    def get_index_stats(self) -> Dict:
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            raise
    
    def delete_all(self):
        """Delete all vectors from index (use with caution)"""
        try:
            self.index.delete(delete_all=True)
            logger.warning("Deleted all vectors from Pinecone index")
        except Exception as e:
            logger.error(f"Failed to delete all vectors: {e}")
            raise
