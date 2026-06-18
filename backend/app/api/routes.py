# import os
# import uuid
# import json
# from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session

# from app.core.config import settings
# from app.db.database import get_db
# from app.db import crud
# from app.models.schemas import (
#     ChatRequest,
#     ChatResponse,
#     Source,
#     UploadResponse,
#     ThreadResponse,
#     MessageResponse,
# )
# from app.services.vector_store import ingest_file
# from app.services.rag_graph import ask_rag, stream_rag, generate_title

# router = APIRouter()


# @router.get("/health")
# def health():
#     return {"status": "ok", "app": settings.app_name}


# @router.post("/upload", response_model=UploadResponse)
# async def upload_document(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     print("UPLOAD HIT:", file.filename)
#     if not file.filename.lower().endswith((".pdf", ".txt")):
#         raise HTTPException(
#             status_code=400,
#             detail="Only PDF and TXT files are supported.",
#         )

#     os.makedirs(settings.upload_dir, exist_ok=True)

#     safe_name = f"{uuid.uuid4()}_{file.filename}"
#     path = os.path.join(settings.upload_dir, safe_name)

#     with open(path, "wb") as f:
#         f.write(await file.read())

#     chunks_added = ingest_file(path, file.filename)

#     crud.add_document(db, file.filename, path, chunks_added)

#     return UploadResponse(
#         filename=file.filename,
#         chunks_added=chunks_added,
#         message="Document uploaded, persisted, and indexed successfully.",
#     )


# @router.post("/chat", response_model=ChatResponse)
# def chat(
#     request: ChatRequest,
#     db: Session = Depends(get_db),
# ):
#     crud.get_or_create_thread(db, request.thread_id)

#     existing = crud.get_messages(db, request.thread_id)

#     if len(existing) == 0:
#         crud.update_thread_title(
#             db,
#             request.thread_id,
#             generate_title(request.question),
#         )

#     crud.add_message(
#         db,
#         request.thread_id,
#         "user",
#         request.question,
#     )

#     answer, sources = ask_rag(
#         request.question,
#         request.thread_id,
#         request.top_k,
#     )

#     crud.add_message(
#         db,
#         request.thread_id,
#         "assistant",
#         answer,
#         sources=sources,
#     )

#     return ChatResponse(
#         answer=answer,
#         sources=[Source(**s) for s in sources],
#         thread_id=request.thread_id,
#     )


# @router.post("/chat/stream")
# async def chat_stream(
#     request: ChatRequest,
#     db: Session = Depends(get_db),
# ):
#     crud.get_or_create_thread(db, request.thread_id)

#     existing = crud.get_messages(db, request.thread_id)

#     if len(existing) == 0:
#         crud.update_thread_title(
#             db,
#             request.thread_id,
#             generate_title(request.question),
#         )

#     crud.add_message(
#         db,
#         request.thread_id,
#         "user",
#         request.question,
#     )

#     async def event_generator():
#         full_answer = ""

#         async for token in stream_rag(
#             request.question,
#             request.thread_id,
#             request.top_k,
#         ):
#             full_answer += token

#             yield f"data: {json.dumps({'token': token})}\n\n"

#         crud.add_message(
#             db,
#             request.thread_id,
#             "assistant",
#             full_answer,
#             sources=[],
#         )

#         yield f"data: {json.dumps({'done': True})}\n\n"

#     return StreamingResponse(
#         event_generator(),
#         media_type="text/event-stream",
#     )


# @router.get("/threads", response_model=list[ThreadResponse])
# def threads(db: Session = Depends(get_db)):
#     return crud.list_threads(db)


# @router.get(
#     "/threads/{thread_id}/messages",
#     response_model=list[MessageResponse],
# )
# def thread_messages(
#     thread_id: str,
#     db: Session = Depends(get_db),
# ):
#     rows = crud.get_messages(db, thread_id)

#     return [
#         MessageResponse(
#             role=m.role,
#             content=m.content,
#             sources=json.loads(m.sources_json or "[]"),
#             created_at=m.created_at,
#         )
#         for m in rows
#     ]


import os
import uuid
import json
import time

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user

from app.core.config import settings
from app.db.database import get_db
from app.db import crud
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Source,
    UploadResponse,
    ThreadResponse,
    MessageResponse,
    DocumentResponse,
    EvaluationResponse,
    EvaluationSummary,
)
from app.services.vector_store import ingest_file, delete_document_chunks
from app.services.rag_graph import ask_rag, stream_rag, generate_title

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    os.makedirs(settings.upload_dir, exist_ok=True)

    document_id = str(uuid.uuid4())
    safe_name = f"{document_id}_{file.filename}"
    path = os.path.join(settings.upload_dir, safe_name)

    with open(path, "wb") as f:
        f.write(await file.read())

    # chunks_added, chunk_ids = ingest_file(path, file.filename, document_id)
    chunks_added, chunk_ids = ingest_file(
    path,
    file.filename,
    document_id,
    current_user.id,
    )

    crud.add_document(
        db=db,
        user_id=current_user.id,
        document_id=document_id,
        filename=file.filename,
        stored_path=path,
        chunks_added=chunks_added,
        chunk_ids=chunk_ids,
    )

    return UploadResponse(
        document_id=document_id,
        filename=file.filename,
        chunks_added=chunks_added,
        message="Document uploaded, persisted, and indexed successfully.",
    )


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return crud.list_documents(db, current_user.id)


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    doc = crud.get_document(db, document_id, current_user.id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunk_ids = json.loads(doc.chunk_ids_json or "[]")

    delete_document_chunks(chunk_ids)

    if os.path.exists(doc.stored_path):
        os.remove(doc.stored_path)

    crud.delete_document_record(db, document_id, current_user.id)

    return {
        "message": "Document and vector chunks deleted successfully.",
        "document_id": document_id,
    }

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    start = time.time()

    crud.get_or_create_thread(db, request.thread_id, current_user.id)

    existing = crud.get_messages(db, request.thread_id, current_user.id)

    if len(existing) == 0:
        crud.update_thread_title(
            db,
            request.thread_id,
            current_user.id,
            generate_title(request.question),
        )

    crud.add_message(
        db,
        request.thread_id,
        current_user.id,
        "user",
        request.question,
    )

    answer, sources = ask_rag(
        question=request.question,
        thread_id=request.thread_id,
        user_id=current_user.id,
        top_k=request.top_k,
    )

    crud.add_message(
        db,
        request.thread_id,
        current_user.id,
        "assistant",
        answer,
        sources=sources,
    )

    latency_ms = (time.time() - start) * 1000

    crud.add_evaluation(
        db=db,
        user_id=current_user.id,
        thread_id=request.thread_id,
        question=request.question,
        answer=answer,
        latency_ms=latency_ms,
        sources_count=len(sources),
    )

    return ChatResponse(
        answer=answer,
        sources=[Source(**s) for s in sources],
        thread_id=request.thread_id,
    )


# @router.post("/chat/stream")
# async def chat_stream(
#     request: ChatRequest,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     start = time.time()

#     crud.get_or_create_thread(db, request.thread_id, current_user.id)

#     existing = crud.get_messages(db, request.thread_id, current_user.id)

#     if len(existing) == 0:
#         crud.update_thread_title(
#             db,
#             request.thread_id,
#             current_user.id,
#             generate_title(request.question),
#         )

#     crud.add_message(
#         db,
#         request.thread_id,
#         current_user.id,
#         "user",
#         request.question,
#     )

#     async def event_generator():
#         full_answer = ""

#         answer, sources = ask_rag(
#             question=request.question,
#             thread_id=request.thread_id,
#             user_id=current_user.id,
#             top_k=request.top_k,
#         )

#         for token in answer.split(" "):
#             full_answer += token + " "
#             yield f"data: {json.dumps({'token': token + ' '})}\n\n"

#         crud.add_message(
#             db,
#             request.thread_id,
#             current_user.id,
#             "assistant",
#             full_answer.strip(),
#             sources=sources,
#         )

#         latency_ms = (time.time() - start) * 1000

#         crud.add_evaluation(
#             db=db,
#             user_id=current_user.id,
#             thread_id=request.thread_id,
#             question=request.question,
#             answer=full_answer.strip(),
#             latency_ms=latency_ms,
#             sources_count=len(sources),
#         )

#         yield f"data: {json.dumps({'sources': sources})}\n\n"
#         yield f"data: {json.dumps({'done': True})}\n\n"

#     return StreamingResponse(
#         event_generator(),
#         media_type="text/event-stream",
#     )

# @router.post("/chat/stream")
# async def chat_stream(
#     request: ChatRequest,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     start = time.time()

#     crud.get_or_create_thread(db, request.thread_id, current_user.id)

#     existing = crud.get_messages(db, request.thread_id, current_user.id)

#     if len(existing) == 0:
#         crud.update_thread_title(
#             db,
#             request.thread_id,
#             current_user.id,
#             generate_title(request.question),
#         )

#     crud.add_message(
#         db,
#         request.thread_id,
#         current_user.id,
#         "user",
#         request.question,
#     )

#     async def event_generator():
#         full_answer = ""

#         answer, sources = ask_rag(
#             question=request.question,
#             thread_id=request.thread_id,
#             user_id=current_user.id,
#             top_k=request.top_k,
#         )

#         for token in answer.split(" "):
#             full_answer += token + " "
#             yield f"data: {json.dumps({'token': token + ' '})}\n\n"

#         crud.add_message(
#             db,
#             request.thread_id,
#             current_user.id,
#             "assistant",
#             full_answer.strip(),
#             sources=sources,
#         )

#         latency_ms = (time.time() - start) * 1000

#         crud.add_evaluation(
#             db=db,
#             user_id=current_user.id,
#             thread_id=request.thread_id,
#             question=request.question,
#             answer=full_answer.strip(),
#             latency_ms=latency_ms,
#             sources_count=len(sources),
#         )

#         yield f"data: {json.dumps({'sources': sources})}\n\n"
#         yield f"data: {json.dumps({'done': True})}\n\n"

#     return StreamingResponse(
#         event_generator(),
#         media_type="text/event-stream",
#     )

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    start = time.time()
    user_id = current_user.id

    crud.get_or_create_thread(db, request.thread_id, user_id)

    existing = crud.get_messages(db, request.thread_id, user_id)

    if len(existing) == 0:
        crud.update_thread_title(
            db,
            request.thread_id,
            user_id,
            generate_title(request.question),
        )

    crud.add_message(
        db,
        request.thread_id,
        user_id,
        "user",
        request.question,
    )

    answer, sources = ask_rag(
        question=request.question,
        thread_id=request.thread_id,
        user_id=user_id,
        top_k=request.top_k,
    )

    crud.add_message(
        db,
        request.thread_id,
        user_id,
        "assistant",
        answer,
        sources=sources,
    )

    latency_ms = (time.time() - start) * 1000

    crud.add_evaluation(
        db=db,
        user_id=user_id,
        thread_id=request.thread_id,
        question=request.question,
        answer=answer,
        latency_ms=latency_ms,
        sources_count=len(sources),
    )

    async def event_generator():
        for token in answer.split(" "):
            yield f"data: {json.dumps({'token': token + ' '})}\n\n"

        yield f"data: {json.dumps({'sources': sources})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.get("/threads", response_model=list[ThreadResponse])
def threads(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud.list_threads(db, current_user.id)


@router.get("/threads/{thread_id}/messages", response_model=list[MessageResponse])
def thread_messages(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = crud.get_messages(db, thread_id, current_user.id)

    return [
        MessageResponse(
            role=m.role,
            content=m.content,
            sources=json.loads(m.sources_json or "[]"),
            created_at=m.created_at,
        )
        for m in rows
    ]


@router.get("/evaluations", response_model=list[EvaluationResponse])
def evaluations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud.list_evaluations(db, current_user.id)


@router.get("/evaluations/summary", response_model=EvaluationSummary)
def evaluations_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud.evaluation_summary(db, current_user.id)