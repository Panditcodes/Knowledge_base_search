from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api import ingest, query, admin
from app.services.pinecone_adapter import PineconeAdapter
from app.services.groq_adapter import GroqAdapter
from app.services.jina_embedding import JinaEmbedding
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG System API",
    description="Production RAG with Jina + Pinecone + Groq LLaMA 3.3 70B",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(query.router, prefix="", tags=["query"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.on_event("startup")
async def startup():
    logger.info("Starting RAG API server")
    # Initialize connections (lazy init in adapters)

@app.get("/health")
async def health_check():
    """Health check for all external dependencies"""
    health_status = {
        "pinecone": False,
        "groq": False,
        "jina": False
    }
    
    try:
        # Check Pinecone
        pinecone = PineconeAdapter()
        pinecone.get_index_stats()
        health_status["pinecone"] = True
    except Exception as e:
        logger.error(f"Pinecone health check failed: {e}")
    
    try:
        # Check Groq
        groq = GroqAdapter()
        groq.test_connection()
        health_status["groq"] = True
    except Exception as e:
        logger.error(f"Groq health check failed: {e}")
    
    try:
        # Check Jina
        jina = JinaEmbedding()
        jina.test_connection()
        health_status["jina"] = True
    except Exception as e:
        logger.error(f"Jina health check failed: {e}")
    
    all_ok = all(health_status.values())
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "services": health_status
    }

@app.get("/")
async def root():
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs"
    }
