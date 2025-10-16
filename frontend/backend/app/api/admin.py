"""
Admin API endpoints
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
import os
from app.services.pinecone_adapter import PineconeAdapter
from app.workers.ingest_worker import IngestWorker

logger = logging.getLogger(__name__)
router = APIRouter()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-me-in-production")

def verify_admin(x_api_key: str = Header(None)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("/rebuild-index", dependencies=[])
async def rebuild_index(x_api_key: str = Header(None)):
    """
    Rebuild the entire Pinecone index
    WARNING: Deletes all existing vectors
    """
    verify_admin(x_api_key)
    
    try:
        pinecone = PineconeAdapter()
        # Get count before deleting
        stats = pinecone.get_index_stats()
        deleted_count = stats.get("total_vector_count", 0)
        
        pinecone.delete_all()
        
        logger.info("Index rebuilt successfully")
        return {
            "message": "Index cleared successfully. Re-ingest documents to populate.",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Index rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", dependencies=[])
async def get_stats(x_api_key: str = Header(None)):
    """Get system statistics"""
    verify_admin(x_api_key)
    
    try:
        pinecone = PineconeAdapter()
        stats = pinecone.get_index_stats()
        
        # Format response for frontend
        return {
            "total_vectors": stats.get("total_vector_count", 0),
            "index_size": f"{stats.get('dimension', 0)} dimensions",
            "namespaces": list(stats.get("namespaces", {}).keys()) if stats.get("namespaces") else []
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
