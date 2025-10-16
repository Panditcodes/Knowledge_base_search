"""
Jina Embedding Service
Generates embeddings for text chunks using Jina API
"""
import os
import requests
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

class JinaEmbedding:
    def __init__(self):
        self.api_key = os.getenv("JINA_API_KEY", "")
        # Try different model versions
        self.model = os.getenv("JINA_EMBEDDING_MODEL", "jina-embeddings-v2-base-en")
        self.base_url = "https://api.jina.ai/v1/embeddings"
        self.batch_size = int(os.getenv("JINA_BATCH_SIZE", "32"))
        
        if not self.api_key:
            logger.warning("JINA_API_KEY not set - embedding will fail")
    
    def test_connection(self):
        """Test Jina API connectivity"""
        try:
            result = self.embed_texts(["test"], show_progress=False)
            return len(result) > 0
        except Exception as e:
            raise Exception(f"Jina connection failed: {e}")
    
    def embed_texts(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for a list of texts using Jina API
        
        Args:
            texts: List of text strings to embed
            show_progress: Whether to log progress
            
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        all_embeddings = []
        
        # Batch processing
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            if show_progress:
                logger.info(f"Embedding batch {i // self.batch_size + 1}/{(len(texts) - 1) // self.batch_size + 1}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "input": batch
                # Removed "encoding_format" - not supported by Jina API anymore
            }
            
            try:
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                # Log detailed error information
                if response.status_code != 200:
                    logger.error(f"Jina API Error {response.status_code}: {response.text}")
                    logger.error(f"Request payload: {payload}")
                    logger.error(f"API Key present: {bool(self.api_key)}")
                
                response.raise_for_status()
                
                data = response.json()
                embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(embeddings)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Jina API request failed: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Response content: {e.response.text}")
                raise Exception(f"Jina embedding failed: {e}")
        
        return np.array(all_embeddings, dtype=np.float32)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string"""
        result = self.embed_texts([query], show_progress=False)
        return result[0] if len(result) > 0 else np.array([])
    
    def get_embedding_dim(self) -> int:
        """Get the dimensionality of embeddings for this model"""
        # jina-embeddings-v2-base-en produces 768-dim vectors
        # TODO: make configurable or query from API
        model_dims = {
            "jina-embeddings-v2-base-en": 768,
            "jina-embeddings-v2-small-en": 512,
        }
        return model_dims.get(self.model, 768)
