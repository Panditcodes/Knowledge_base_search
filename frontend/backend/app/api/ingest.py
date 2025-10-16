"""
Ingest API endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import logging
import uuid
from datetime import datetime
from app.workers.ingest_worker import IngestWorker
import os
import tempfile

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for ingestion status (TODO: use Redis or DB in production)
ingestion_status = {}

class IngestTextRequest(BaseModel):
    text: str
    source_name: str
    metadata: Optional[dict] = {}

@router.post("/", include_in_schema=True)
@router.post("", include_in_schema=False)
async def ingest_documents(
    background_tasks: BackgroundTasks,
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),  # Accept single file from frontend
    text: Optional[str] = None,
    source_name: str = "upload"
):
    """
    Ingest documents or text
    
    Accepts:
    - files: One or more PDF/TXT/MD files
    - text: Raw text string (if no files)
    - source_name: Name for the source
    
    Returns:
    - ingestion_id: ID to track ingestion status
    """
    ingestion_id = str(uuid.uuid4())
    
    ingestion_status[ingestion_id] = {
        "id": ingestion_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "files": [],
        "chunks_created": 0,
        "vectors_indexed": 0,
        "error": None
    }
    
    try:
        # Handle both single file and multiple files
        upload_files = []
        if file:  # Single file from frontend
            upload_files = [file]
        elif files:  # Multiple files
            upload_files = files
        
        if upload_files:
            # Save uploaded files temporarily (cross-platform)
            temp_dir = os.path.join(tempfile.gettempdir(), "rag_uploads")
            os.makedirs(temp_dir, exist_ok=True)
            
            file_paths = []
            for upload_file in upload_files:
                file_path = os.path.join(temp_dir, f"{ingestion_id}_{upload_file.filename}")
                with open(file_path, "wb") as f:
                    content = await upload_file.read()
                    f.write(content)
                file_paths.append(file_path)
                ingestion_status[ingestion_id]["files"].append(upload_file.filename)
            
            # Start background ingestion
            background_tasks.add_task(
                process_files_background,
                ingestion_id,
                file_paths,
                source_name
            )
            
        elif text:
            # Process text directly
            background_tasks.add_task(
                process_text_background,
                ingestion_id,
                text,
                source_name
            )
        else:
            raise HTTPException(status_code=400, detail="Either files or text must be provided")
        
        return {
            "task_id": ingestion_id,  # Frontend expects task_id
            "job_id": ingestion_id,
            "ingestion_id": ingestion_id,  # Keep for backward compatibility
            "status": "processing",
            "message": "Ingestion started"
        }
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        ingestion_status[ingestion_id]["status"] = "failed"
        ingestion_status[ingestion_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ingestion_id}/status")
async def get_ingestion_status(ingestion_id: str):
    """Get status of an ingestion job"""
    if ingestion_id not in ingestion_status:
        # Status not found in memory (server may have restarted)
        # Return a helpful message instead of 404
        logger.warning(f"Ingestion ID {ingestion_id} not found in memory. Server may have restarted during processing.")
        return {
            "task_id": ingestion_id,
            "status": "unknown",
            "message": "Status not available. The server may have restarted. Please check the Query page to verify if your document was indexed.",
            "error": None,
            "chunks_created": 0,
            "vectors_indexed": 0
        }
    
    status_data = ingestion_status[ingestion_id]
    
    # Return format expected by frontend
    return {
        "task_id": ingestion_id,
        "status": status_data["status"],
        "message": status_data.get("error") if status_data["status"] == "failed" else None,
        "error": status_data.get("error"),
        "chunks_created": status_data.get("chunks_created", 0),
        "vectors_indexed": status_data.get("vectors_indexed", 0)
    }

def process_files_background(ingestion_id: str, file_paths: List[str], source_name: str):
    """Background task to process uploaded files"""
    try:
        ingestion_status[ingestion_id]["status"] = "processing"
        
        worker = IngestWorker()
        result = worker.ingest_files(file_paths, source_name)
        
        ingestion_status[ingestion_id].update({
            "status": "completed",
            "chunks_created": result["chunks_created"],
            "vectors_indexed": result["vectors_indexed"],
            "completed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Background ingestion failed: {e}")
        ingestion_status[ingestion_id].update({
            "status": "failed",
            "error": str(e)
        })

def process_text_background(ingestion_id: str, text: str, source_name: str):
    """Background task to process text"""
    try:
        ingestion_status[ingestion_id]["status"] = "processing"
        
        worker = IngestWorker()
        result = worker.ingest_text(text, source_name)
        
        ingestion_status[ingestion_id].update({
            "status": "completed",
            "chunks_created": result["chunks_created"],
            "vectors_indexed": result["vectors_indexed"],
            "completed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Background text ingestion failed: {e}")
        ingestion_status[ingestion_id].update({
            "status": "failed",
            "error": str(e)
        })
