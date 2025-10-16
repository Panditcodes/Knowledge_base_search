import pytest
from unittest.mock import Mock, patch
from app.services.groq_adapter import GroqAdapter

@pytest.fixture
def groq_client():
    """Create a Groq client instance"""
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        return GroqAdapter()

def test_groq_generate(groq_client):
    """Test text generation"""
    with patch('requests.post') as mock_post:
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = groq_client.generate(
            "Test prompt",
            temperature=0.7,
            max_tokens=100
        )
        
        assert response == "This is a test response"
        assert mock_post.called

def test_groq_generate_with_context(groq_client):
    """Test context-aware generation"""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Answer based on context"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        contexts = [
            {"text": "Context 1", "score": 0.9},
            {"text": "Context 2", "score": 0.8}
        ]
        
        response = groq_client.generate_with_context(
            query="Test query",
            contexts=contexts
        )
        
        assert response == "Answer based on context"
        assert mock_post.called

def test_groq_missing_api_key():
    """Test that missing API key raises error"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            GroqAdapter()
