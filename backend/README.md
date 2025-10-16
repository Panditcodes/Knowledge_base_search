# Production RAG System Backend

A production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI, Jina AI, Pinecone, and Groq LLaMA 3.3 70B.

## Tech Stack

- **Embeddings**: Jina AI (jina-embeddings-v2-base-en, 768-dimensional)
- **Vector Database**: Pinecone (serverless, cosine similarity)
- **LLM**: Groq LLaMA 3.3 70B (llama-3.3-70b-versatile)
- **Framework**: FastAPI with async support
- **Chunking**: tiktoken-based token-accurate chunking (400 tokens, 75 overlap)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required API keys:
- **Jina AI**: Get from https://jina.ai/
- **Pinecone**: Get from https://www.pinecone.io/
- **Groq**: Get from https://groq.com/

```env
JINA_API_KEY=your_jina_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-east-1
PINECONE_INDEX=rag-knowledge-base
GROQ_API_KEY=your_groq_api_key_here
ADMIN_API_KEY=your_secure_admin_key_here
```

### 3. Run Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The server will start at `http://localhost:8001`

## API Endpoints

### Health Check
```bash
curl http://localhost:8001/health
```

### Ingest Documents

**Upload Files:**
```bash
curl -X POST http://localhost:8001/ingest \
  -F "files=@document.pdf" \
  -F "source=my-docs"
```

**Ingest Text:**
```bash
curl -X POST http://localhost:8001/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text content here",
    "source": "manual-input"
  }'
```

**Check Ingestion Status:**
```bash
curl http://localhost:8001/ingest/status/{job_id}
```

### Query RAG System

```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5,
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

Response format:
```json
{
  "answer": "Machine learning is...",
  "sources": [
    {
      "text": "Chunk text...",
      "score": 0.85,
      "metadata": {
        "source": "ml-guide",
        "filename": "intro.pdf"
      }
    }
  ]
}
```

### Vector Search (Testing)

```bash
curl -X POST http://localhost:8001/vector/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "top_k": 5
  }'
```

### Admin Endpoints

**Rebuild Index (delete all vectors):**
```bash
curl -X POST http://localhost:8001/admin/rebuild-index \
  -H "x-api-key: your_admin_api_key"
```

**Get Index Statistics:**
```bash
curl http://localhost:8001/admin/stats \
  -H "x-api-key: your_admin_api_key"
```

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API routes
│   │   ├── ingest.py        # Document ingestion endpoints
│   │   ├── query.py         # RAG query endpoints
│   │   └── admin.py         # Admin operations
│   ├── services/            # External service adapters
│   │   ├── jina_embedding.py
│   │   ├── pinecone_adapter.py
│   │   ├── groq_adapter.py
│   │   └── chunker.py
│   └── workers/             # Background workers
│       └── ingest_worker.py
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration & Tuning

### Chunking Parameters
Edit `app/services/chunker.py`:
```python
TextChunker(chunk_size=400, overlap=75)
```
- `chunk_size`: Number of tokens per chunk (default: 400)
- `overlap`: Overlapping tokens between chunks (default: 75)

### Embedding Settings
Edit `app/services/jina_embedding.py`:
```python
JinaEmbedding(batch_size=32)
```
- `batch_size`: Number of texts to embed in one API call (default: 32)

### Retrieval Settings
In query request:
```json
{
  "top_k": 5  // Number of chunks to retrieve (default: 5)
}
```

### Generation Settings
In query request:
```json
{
  "temperature": 0.7,  // Randomness (0.0-1.0, default: 0.7)
  "max_tokens": 500    // Max response length (default: 500)
}
```

## Iterative Fine-Tuning Workflow

### 1. Baseline Evaluation
- Ingest sample documents
- Run test queries with default settings
- Record answer quality and relevance

### 2. Chunking Optimization
- **Too fragmented**: Increase `chunk_size` (500-600)
- **Context missing**: Increase `overlap` (100-150)
- **Too large**: Decrease `chunk_size` (300-350)

### 3. Retrieval Tuning
- **Low recall**: Increase `top_k` (7-10)
- **Noisy results**: Decrease `top_k` (3-4)
- **Check vector search scores**: Use `/vector/search` endpoint

### 4. Generation Tuning
- **Too creative/hallucinating**: Lower `temperature` (0.3-0.5)
- **Too rigid/repetitive**: Raise `temperature` (0.8-0.9)
- **Truncated answers**: Increase `max_tokens` (700-1000)

### 5. Prompt Engineering
Edit `app/services/groq_adapter.py` → `generate_with_context()`:
```python
system_prompt = """You are a helpful AI assistant..."""
```

### 6. Testing & Validation
- Create `qa_pairs.json` with expected Q&A
- Run evaluation script (see evaluation/ folder)
- Measure accuracy, relevance, citation quality

## Deployment

### Docker
```bash
docker build -t rag-backend .
docker run -p 8001:8001 --env-file .env rag-backend
```

### Production Checklist
- [ ] Set strong `ADMIN_API_KEY`
- [ ] Use environment-specific Pinecone indexes
- [ ] Enable rate limiting (add middleware)
- [ ] Set up monitoring (Sentry, Datadog)
- [ ] Configure CORS for frontend domain
- [ ] Use Redis for ingestion job status (replace in-memory dict)
- [ ] Add authentication for query endpoints
- [ ] Set up backup for Pinecone index

## Troubleshooting

### Health Check Fails
```bash
curl http://localhost:8001/health
```
Check which service is failing:
- Jina: Verify `JINA_API_KEY`
- Pinecone: Verify `PINECONE_API_KEY` and `PINECONE_INDEX` exists
- Groq: Verify `GROQ_API_KEY`

### Ingestion Fails
- Check file formats (only PDF, TXT, MD supported)
- Verify file size limits
- Check logs for extraction errors

### Poor Query Results
- Run `/vector/search` to check retrieval quality
- Verify document ingestion completed
- Check `/admin/stats` for vector count

### Rate Limits
- Jina: 1000 requests/minute
- Groq: Check your plan limits
- Pinecone: Serverless auto-scales

## API Keys & Pricing

| Service | Free Tier | Pricing |
|---------|-----------|---------|
| Jina AI | 1M tokens/month | $0.02/1M tokens |
| Pinecone | 1 index, 100K vectors | Serverless: pay per read/write |
| Groq | Limited free | Check groq.com/pricing |

## License

MIT
