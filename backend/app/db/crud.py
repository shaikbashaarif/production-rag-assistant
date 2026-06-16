# import json
# from datetime import datetime
# from sqlalchemy.orm import Session
# from app.db.models import ChatThread, ChatMessage, UploadedDocument


# def get_or_create_thread(db: Session, thread_id: str, title: str = "New Chat") -> ChatThread:
#     thread = db.get(ChatThread, thread_id)
#     if not thread:
#         thread = ChatThread(id=thread_id, title=title)
#         db.add(thread)
#         db.commit()
#         db.refresh(thread)
#     return thread


# def update_thread_title(db: Session, thread_id: str, title: str):
#     thread = get_or_create_thread(db, thread_id)
#     if thread.title == "New Chat" and title:
#         thread.title = title[:80]
#     thread.updated_at = datetime.utcnow()
#     db.commit()


# def add_message(db: Session, thread_id: str, role: str, content: str, sources=None):
#     get_or_create_thread(db, thread_id)
#     msg = ChatMessage(thread_id=thread_id, role=role, content=content, sources_json=json.dumps(sources or []))
#     db.add(msg)
#     thread = db.get(ChatThread, thread_id)
#     thread.updated_at = datetime.utcnow()
#     db.commit()
#     return msg


# def list_threads(db: Session):
#     return db.query(ChatThread).order_by(ChatThread.updated_at.desc()).all()


# def get_messages(db: Session, thread_id: str):
#     return db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at.asc()).all()


# def add_document(db: Session, filename: str, stored_path: str, chunks_added: int):
#     doc = UploadedDocument(filename=filename, stored_path=stored_path, chunks_added=chunks_added)
#     db.add(doc)
#     db.commit()
#     return doc



import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import ChatThread, ChatMessage, UploadedDocument, EvaluationLog


def get_or_create_thread(db: Session, thread_id: str):
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()

    if not thread:
        thread = ChatThread(id=thread_id, title="New Chat")
        db.add(thread)
        db.commit()
        db.refresh(thread)

    return thread


def update_thread_title(db: Session, thread_id: str, title: str):
    thread = get_or_create_thread(db, thread_id)
    thread.title = title
    thread.updated_at = datetime.utcnow()
    db.commit()
    return thread


def add_message(db: Session, thread_id: str, role: str, content: str, sources=None):
    get_or_create_thread(db, thread_id)

    message = ChatMessage(
        thread_id=thread_id,
        role=role,
        content=content,
        sources_json=json.dumps(sources or []),
    )

    db.add(message)

    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    thread.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    return message


def get_messages(db: Session, thread_id: str):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.thread_id == thread_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def list_threads(db: Session):
    return db.query(ChatThread).order_by(ChatThread.updated_at.desc()).all()


def add_document(
    db: Session,
    document_id: str,
    filename: str,
    stored_path: str,
    chunks_added: int,
    chunk_ids: list[str],
):
    doc = UploadedDocument(
        document_id=document_id,
        filename=filename,
        stored_path=stored_path,
        chunks_added=chunks_added,
        chunk_ids_json=json.dumps(chunk_ids),
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


def list_documents(db: Session):
    return db.query(UploadedDocument).order_by(UploadedDocument.created_at.desc()).all()


def get_document(db: Session, document_id: str):
    return (
        db.query(UploadedDocument)
        .filter(UploadedDocument.document_id == document_id)
        .first()
    )


def delete_document_record(db: Session, document_id: str):
    doc = get_document(db, document_id)

    if not doc:
        return None

    db.delete(doc)
    db.commit()

    return doc


def add_evaluation(
    db: Session,
    thread_id: str,
    question: str,
    answer: str,
    latency_ms: float,
    sources_count: int,
):
    no_answer = 1 if "I don't know based on the uploaded documents" in answer else 0

    row = EvaluationLog(
        thread_id=thread_id,
        question=question,
        answer=answer,
        latency_ms=latency_ms,
        sources_count=sources_count,
        no_answer=no_answer,
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return row


def list_evaluations(db: Session):
    return db.query(EvaluationLog).order_by(EvaluationLog.created_at.desc()).all()


def evaluation_summary(db: Session):
    rows = db.query(EvaluationLog).all()
    documents = db.query(UploadedDocument).all()

    total_queries = len(rows)
    total_documents = len(documents)
    total_chunks = sum(doc.chunks_added for doc in documents)
    no_answer_count = sum(row.no_answer for row in rows)

    avg_latency = (
        sum(row.latency_ms for row in rows) / total_queries
        if total_queries > 0
        else 0
    )

    return {
        "total_queries": total_queries,
        "total_documents": total_documents,
        "total_chunks": total_chunks,
        "average_latency_ms": round(avg_latency, 2),
        "no_answer_count": no_answer_count,
    }

from app.db.models import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_id: str, email: str, hashed_password: str):
    user = User(
        id=user_id,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user