"""
Query API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from app.services.jina_embedding import JinaEmbedding
from app.services.pinecone_adapter import PineconeAdapter
from app.services.groq_adapter import GroqAdapter

logger = logging.getLogger(__name__)
router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    temperature: float = 0.3  # Slightly higher for more natural responses
    max_tokens: int = 2048  # Increased for comprehensive answers
    system_prompt: Optional[str] = None

class VectorSearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/query")
async def query_rag(request: QueryRequest):
    """
    Main RAG query endpoint
    
    1. Embed query with Jina
    2. Retrieve top_k from Pinecone
    3. Build prompt with contexts
    4. Generate answer with Groq LLaMA 3.3 70B
    5. Return answer + sources
    """
    try:
        # Embed query
        jina = JinaEmbedding()
        query_vector = jina.embed_query(request.query)
        
        # Retrieve from Pinecone
        pinecone = PineconeAdapter()
        matches = pinecone.query(
            query_vector=query_vector.tolist(),
            top_k=request.top_k
        )
        
        if not matches:
            return {
                "answer": "No relevant documents found in the knowledge base.",
                "sources": [],
                "raw_llm_output": None
            }
        
        # Prepare contexts for LLM
        contexts = []
        sources = []
        
        for match in matches:
            contexts.append({
                "text": match["metadata"].get("text", ""),
                "score": match["score"]
            })
            sources.append({
                "id": match["id"],
                "score": match["score"],
                "text_snippet": match["metadata"].get("text", "")[:200] + "...",
                "source": match["metadata"].get("source", "unknown"),
                "chunk_id": match["metadata"].get("chunk_id", -1)
            })
        
        # Generate answer with Groq
        groq = GroqAdapter()
        result = groq.generate_with_context(
            query=request.query,
            contexts=contexts,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_instruction=request.system_prompt
        )
        
        # Format sources for frontend
        formatted_sources = []
        for src in sources:
            formatted_sources.append({
                "text": src["text_snippet"],
                "score": src["score"],
                "metadata": {
                    "source": src["source"],
                    "chunk_id": src["chunk_id"]
                }
            })
        
        return {
            "answer": result["answer"],
            "sources": formatted_sources,
            "tokens_used": result.get("tokens_used", 0),
            "model": result.get("model", "groq-llama")
        }
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vector/search")
async def vector_search(request: VectorSearchRequest):
    """
    Raw vector search endpoint (for testing)
    Returns matching vectors without LLM generation
    """
    try:
        jina = JinaEmbedding()
        query_vector = jina.embed_query(request.query)
        
        pinecone = PineconeAdapter()
        matches = pinecone.query(
            query_vector=query_vector.tolist(),
            top_k=request.top_k
        )
        
        return {"matches": matches}
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
