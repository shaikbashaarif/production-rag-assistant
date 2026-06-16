from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    question: str
    thread_id: str = "default"
    top_k: int = 4

class Source(BaseModel):
    filename: Optional[str] = None
    page: Optional[int] = None
    preview: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    thread_id: str

class UploadResponse(BaseModel):
    filename: str
    chunks_added: int
    message: str

class ThreadResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    role: str
    content: str
    sources: list = []
    created_at: datetime

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    stored_path: str
    chunks_added: int
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    id: int
    thread_id: str
    question: str
    answer: str
    latency_ms: float
    sources_count: int
    no_answer: int
    created_at: datetime

class Config:
    from_attributes = True


class EvaluationSummary(BaseModel):
    total_queries: int
    total_documents: int
    total_chunks: int
    average_latency_ms: float
    no_answer_count: int

class UserRegister(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool

class Config:
     from_attributes = True