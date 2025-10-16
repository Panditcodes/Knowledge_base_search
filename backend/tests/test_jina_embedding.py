import pytest
from unittest.mock import Mock, patch
from app.services.jina_embedding import JinaEmbedding
import numpy as np

@pytest.fixture
def jina_client():
    """Create a Jina client instance"""
    with patch.dict('os.environ', {'JINA_API_KEY': 'test-key'}):
        return JinaEmbedding()

def test_jina_embed_query(jina_client):
    """Test single query embedding"""
    with patch('requests.post') as mock_post:
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1] * 768}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        embedding = jina_client.embed_query("test query")
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (768,)
        assert mock_post.called

def test_jina_embed_texts(jina_client):
    """Test batch text embedding"""
    with patch('requests.post') as mock_post:
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1] * 768},
                {"embedding": [0.2] * 768}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        embeddings = jina_client.embed_texts(["text1", "text2"])
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 2
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)
        assert all(emb.shape == (768,) for emb in embeddings)

def test_jina_missing_api_key():
    """Test that missing API key raises error"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="JINA_API_KEY"):
            JinaEmbedding()
