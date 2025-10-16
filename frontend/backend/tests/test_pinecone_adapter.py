import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.pinecone_adapter import PineconeAdapter

@pytest.fixture
def pinecone_client():
    """Create a mocked Pinecone client"""
    with patch.dict('os.environ', {
        'PINECONE_API_KEY': 'test-key',
        'PINECONE_INDEX': 'test-index',
        'PINECONE_ENV': 'us-east-1'
    }):
        with patch('app.services.pinecone_adapter.Pinecone') as mock_pinecone:
            mock_instance = Mock()
            mock_index = Mock()
            mock_instance.Index.return_value = mock_index
            mock_pinecone.return_value = mock_instance
            
            client = PineconeAdapter()
            client.index = mock_index
            return client

def test_upsert_vectors(pinecone_client):
    """Test upserting vectors"""
    vectors = [
        {"id": "1", "values": [0.1] * 768, "metadata": {"text": "test"}},
        {"id": "2", "values": [0.2] * 768, "metadata": {"text": "test2"}}
    ]
    
    pinecone_client.upsert(vectors)
    
    assert pinecone_client.index.upsert.called
    call_args = pinecone_client.index.upsert.call_args
    assert len(call_args[1]['vectors']) == 2

def test_query_vectors(pinecone_client):
    """Test querying vectors"""
    query_vector = [0.1] * 768
    
    # Mock query response
    mock_matches = [
        Mock(id="1", score=0.9, metadata={"text": "result1"}),
        Mock(id="2", score=0.8, metadata={"text": "result2"})
    ]
    pinecone_client.index.query.return_value = Mock(matches=mock_matches)
    
    results = pinecone_client.query(query_vector, top_k=2)
    
    assert len(results) == 2
    assert results[0]["score"] == 0.9
    assert results[0]["metadata"]["text"] == "result1"

def test_delete_all(pinecone_client):
    """Test deleting all vectors"""
    pinecone_client.delete_all()
    
    assert pinecone_client.index.delete.called
