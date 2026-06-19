# Production RAG Assistant — Multi-User AI Document Chatbot

A GitHub-ready, freelance-portfolio RAG application converted from an IPYNB notebook into a real backend + frontend product.

## Included Features

- JWT Authentication (Register/Login)
- Multi-user document ownership
- User-isolated retrieval
- User-isolated chat threads
- User-isolated evaluations
- PDF/TXT upload and indexing
- Hybrid Retrieval (Vector + Keyword Search)
- PostgreSQL + pgvector
- FastAPI backend
- React + Vite frontend
- LangGraph RAG workflow
- Streaming responses (SSE)
- Source citations
- Evaluation dashboard
- GitHub-friendly structure

## Architecture

```text
React Frontend
      ↓
JWT Authentication
      ↓
FastAPI Backend
      ↓
LangGraph RAG Pipeline
      ↓
Hybrid Retrieval
(Vector Search + Full Text Search)
      ↓
PostgreSQL + pgvector
      ↓
OpenAI LLM
```

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/Scripts/activate
#venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env
```

Add your OpenAI key in `.env`:

```env
OPENAI_API_KEY=your_key_here
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```


## Screenshots

### Login

![Login](screenshots/login.png)

### Upload

![Upload](screenshots/upload.png)

### Chat

![Chat](screenshots/chat.png)

### Sources

![Sources](screenshots/sources.png)

### Dashboard

![Dashboard](screenshots/dashboard.png)



## Security Features

- JWT Authentication
- Protected APIs
- User-owned Documents
- User-owned Threads
- User-owned Messages
- User-owned Evaluations
- User-Isolated Retrieval



## Important Persistence Details

- Uploaded files are stored in `backend/app/storage/uploads`
- Chroma vector DB persists in `backend/app/storage/chroma`
- SQLite DB persists in `backend/app/storage/app.db`
- Chat threads are available through `/api/threads`
- Messages are available through `/api/threads/{thread_id}/messages`
- Streaming endpoint is `/api/chat/stream`

## GitHub Upload Notes

Do not commit:

- `.env`
- `venv/`
- uploaded files
- local SQLite database
- local Chroma vector database

These are already included in `.gitignore`.

## Suggested GitHub Repository Name

`production-rag-assistant-fastapi-react-langgraph`

## Resume Line

Built a production-ready multi-user RAG platform using FastAPI, React, PostgreSQL, pgvector, LangGraph, OpenAI embeddings, JWT authentication, hybrid retrieval, streaming responses, and complete user data isolation.
