# Production-oriented RAG Assistant — Full Stack AI Document Chatbot

A GitHub-ready, freelance-portfolio RAG application converted from an IPYNB notebook into a real backend + frontend product.

## Included Features

- PDF/TXT upload and indexing
- Persistent vector database using ChromaDB
- FastAPI backend
- React + Vite frontend
- LangGraph RAG workflow
- SQLite database for chat threads, messages, uploaded document records, and LangGraph checkpoints
- Threaded conversations using `thread_id`
- Streaming response endpoint using Server-Sent Events
- Source preview support
- GitHub-friendly structure

## Architecture

```text
frontend React UI
   ↓
FastAPI backend
   ↓
Upload API → document loader → splitter → OpenAI embeddings → persistent ChromaDB
   ↓
Chat API / Streaming API → LangGraph RAG → OpenAI model
   ↓
SQLite stores threads, messages, uploads, and LangGraph checkpoints
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

Built a production-ready RAG document assistant using FastAPI, React, LangGraph, OpenAI embeddings, persistent ChromaDB, SQLite chat history, threaded conversations, and streaming responses.
