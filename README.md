# 🚀 RAG Knowledge Base Search Engine

A production-ready **Retrieval-Augmented Generation (RAG)** system for intelligent document search and question answering. Built with FastAPI, React, Pinecone, Jina AI, and Groq LLaMA.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.3-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.6-blue.svg)

## ✨ Features

- **� Document Processing**: Upload PDF, TXT, and MD files
- **🔍 Semantic Search**: Vector-based similarity search using Jina embeddings (768-dim)
- **🤖 AI-Powered Answers**: LLaMA 3.3 70B generates comprehensive, formatted responses
- **📊 Admin Dashboard**: Monitor system health, view statistics, rebuild index
- **🎨 Modern UI**: Beautiful Tailwind CSS + shadcn/ui components
- **📝 Markdown Rendering**: Formatted responses with headings, lists, code blocks
- **� Source Citations**: All answers cite specific document sections

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI    │────▶│  Pinecone   │
│  React + TS │     │   Backend    │     │  Vector DB  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ├──────────▶ Jina AI (Embeddings)
                           │
                           └──────────▶ Groq (LLaMA 3.3 70B)
```

### Tech Stack

**Backend:**
- FastAPI 0.115.6
- Pinecone 5.0.1 (Serverless)
- Jina AI Embeddings v2-base-en
- Groq LLaMA 3.3 70B Versatile
- Tiktoken 0.8.0

**Frontend:**
- React 18.3 + TypeScript
- Vite 5.4
- Tailwind CSS
- shadcn/ui + Radix UI
- react-markdown

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API Keys:
  - [Pinecone](https://www.pinecone.io/)
  - [Jina AI](https://jina.ai/)
  - [Groq](https://groq.com/)

### 1. Clone Repository

```bash
# Option A: Download or copy the source into a local folder
# Option B: If using Git, initialize your own repository (instructions later)
cd Knowledge_base_search
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys
```

**Required Environment Variables:**

```env
# backend/.env
PINECONE_API_KEY=your_pinecone_api_key
JINA_API_KEY=your_jina_api_key
GROQ_API_KEY=your_groq_api_key
ADMIN_API_KEY=your_admin_secret_key
```

### 3. Frontend Setup

```bash
# From project root
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application at **http://localhost:8080**

## 📖 Usage

### Upload Documents

1. Navigate to the **Upload** page
2. Drag & drop or select PDF/TXT/MD files
3. Click "Upload" and wait for processing
4. System will:
   - Extract text from documents
   - Split into 400-token chunks (75-token overlap)
   - Generate 768-dimensional embeddings
   - Store vectors in Pinecone

### Query Knowledge Base

1. Go to the **Query** page
2. Enter your question
3. Adjust settings (optional):
   - **Top-K**: Number of relevant chunks to retrieve (default: 5)
   - **Temperature**: Response creativity (default: 0.3)
   - **Max Tokens**: Response length (default: 2048)
4. Get comprehensive answers with source citations

### Admin Panel

- **Health Check**: Monitor Pinecone, Jina, and Groq connectivity
- **Statistics**: View total vectors, index size, namespaces
- **Rebuild Index**: Clear and recreate vector database

## 🎯 API Endpoints

### Ingestion

- `POST /ingest` - Upload document(s)
- `GET /ingest/{id}/status` - Check processing status

### Query

- `POST /query` - Ask questions
- `POST /vector/search` - Raw vector search (testing)

### Admin

- `GET /health` - System health check
- `GET /admin/stats` - Database statistics
- `POST /admin/rebuild-index` - Rebuild vector index

### Documentation

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🔧 Configuration

### Backend Settings

**Chunk Size** (`backend/app/services/chunker.py`):
```python
chunk_size = 400  # tokens per chunk
chunk_overlap = 75  # token overlap between chunks
```

**Embedding Model** (`backend/app/services/jina_embedding.py`):
```python
model = "jina-embeddings-v2-base-en"  # 768 dimensions
```

**LLM Model** (`backend/app/services/groq_adapter.py`):
```python
model = "llama-3.3-70b-versatile"
temperature = 0.3  # 0.0-1.0
max_tokens = 2048  # max response length
```

### Frontend Settings

**API Proxy** (`frontend/vite.config.ts`):
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

## 📊 System Prompt

The system uses advanced prompt engineering for high-quality responses:

- **Comprehensive explanations** with proper structure
- **Markdown formatting** (headings, lists, code blocks)
- **Source citations** for every claim
- **Professional tone** matching expert-level outputs
- **Special handling** for how-to, comparison, and troubleshooting questions

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Stop services
docker-compose down
```

Access:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Test specific module
pytest tests/test_chunker.py -v
```

## 📁 Project Structure

```
Knowledge_base_search/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── services/     # Core services (embeddings, LLM, DB)
│   │   └── workers/      # Background tasks
│   ├── tests/            # Unit tests
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment template
├── frontend/
│   ├── src/
│   │   ├── pages/        # Upload, Query, Admin pages
│   │   ├── services/     # API client
│   │   └── components/   # UI components
│   ├── package.json      # Node dependencies
│   └── vite.config.ts    # Vite configuration
├── docker-compose.yml    # Docker orchestration
├── .gitignore
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pinecone](https://www.pinecone.io/) - Vector database
- [Jina AI](https://jina.ai/) - Embedding models
- [Groq](https://groq.com/) - LLM inference
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework

## 📧 Contact

For questions or support, please open an issue or contact the maintainer.

---

**Built with ❤️ using RAG architecture**

```env
JINA_API_KEY=your_jina_api_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=rag-knowledge-base
GROQ_API_KEY=your_groq_key
ADMIN_API_KEY=your_secure_admin_key
```

### Tuning Parameters

**Chunking**: Edit `backend/app/services/chunker.py`
- `chunk_size`: 400 tokens (increase for more context)
- `overlap`: 75 tokens (increase to reduce fragmentation)

**Retrieval**: In query request
- `top_k`: 5 (number of chunks to retrieve)

**Generation**: In query request
- `temperature`: 0.7 (0.0-1.0, higher = more creative)
- `max_tokens`: 500 (max response length)

## 🧪 Testing

```powershell
cd backend
pytest                    # Run all tests
pytest -v                # Verbose output
pytest --cov=app         # With coverage
```

## 🎯 Fine-Tuning Workflow

1. **Upload** sample docs from `samples/` folder
2. **Query** using questions from `samples/qa_pairs.json`
3. **Adjust** chunking parameters if context is missing
4. **Tune** `top_k` if retrieval is too narrow/broad
5. **Modify** `temperature` if answers are too creative/rigid
6. **Edit** system prompt in `backend/app/services/groq_adapter.py`

## 🔧 Troubleshooting

**Health check fails:**
```powershell
curl http://localhost:8001/health
```
Check which service (Jina/Pinecone/Groq) is failing and verify API keys.

**Port conflicts:**
```powershell
# Kill process on port 8001
Get-NetTCPConnection -LocalPort 8001 | Select-Object OwningProcess | ForEach-Object {Stop-Process -Id $_.OwningProcess -Force}
```

**Import errors:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📝 License

MIT License

---

**Built with Jina AI, Pinecone, and Groq LLaMA 3.3 70B**
