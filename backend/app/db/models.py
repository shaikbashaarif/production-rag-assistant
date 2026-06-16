# # from datetime import datetime
# # from typing import Optional, List

# # from sqlalchemy import String, DateTime, Integer, Text, ForeignKey
# # from sqlalchemy.orm import Mapped, mapped_column, relationship

# # from app.db.database import Base


# # class ChatThread(Base):
# #     __tablename__ = "chat_threads"

# #     id: Mapped[str] = mapped_column(String, primary_key=True)
# #     title: Mapped[str] = mapped_column(String, default="New Chat")
# #     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
# #     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# #     messages: Mapped[List["ChatMessage"]] = relationship(
# #         back_populates="thread",
# #         cascade="all, delete-orphan",
# #     )


# # class ChatMessage(Base):
# #     __tablename__ = "chat_messages"

# #     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
# #     thread_id: Mapped[str] = mapped_column(ForeignKey("chat_threads.id"))
# #     role: Mapped[str] = mapped_column(String)
# #     content: Mapped[str] = mapped_column(Text)
# #     sources_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
# #     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# #     thread: Mapped["ChatThread"] = relationship(back_populates="messages")


# # class UploadedDocument(Base):
# #     __tablename__ = "uploaded_documents"

# #     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
# #     filename: Mapped[str] = mapped_column(String)
# #     stored_path: Mapped[str] = mapped_column(String)
# #     chunks_added: Mapped[int] = mapped_column(Integer)
# #     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)




# from datetime import datetime
# from typing import Optional, List

# from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Float
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.db.database import Base


# class ChatThread(Base):
#     __tablename__ = "chat_threads"

#     id: Mapped[str] = mapped_column(String, primary_key=True)
#     title: Mapped[str] = mapped_column(String, default="New Chat")
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

#     messages: Mapped[List["ChatMessage"]] = relationship(
#         back_populates="thread",
#         cascade="all, delete-orphan",
#     )


# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     thread_id: Mapped[str] = mapped_column(ForeignKey("chat_threads.id"))
#     role: Mapped[str] = mapped_column(String)
#     content: Mapped[str] = mapped_column(Text)
#     sources_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

#     thread: Mapped["ChatThread"] = relationship(back_populates="messages")


# class UploadedDocument(Base):
#     __tablename__ = "uploaded_documents"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     document_id: Mapped[str] = mapped_column(String, unique=True, index=True)
#     filename: Mapped[str] = mapped_column(String)
#     stored_path: Mapped[str] = mapped_column(String)
#     chunks_added: Mapped[int] = mapped_column(Integer)
#     chunk_ids_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# class EvaluationLog(Base):
#     __tablename__ = "evaluation_logs"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     thread_id: Mapped[str] = mapped_column(String)
#     question: Mapped[str] = mapped_column(Text)
#     answer: Mapped[str] = mapped_column(Text)
#     latency_ms: Mapped[float] = mapped_column(Float)
#     sources_count: Mapped[int] = mapped_column(Integer)
#     no_answer: Mapped[int] = mapped_column(Integer, default=0)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from sqlalchemy import Boolean


EMBEDDING_DIM = 1536

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)

    email = Column(String, unique=True, nullable=False)

    hashed_password = Column(
        String,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    documents = relationship(
    "UploadedDocument",
    back_populates="user",
    )

    threads = relationship(
        "ChatThread",
        back_populates="user",
    )

    evaluations = relationship(
        "EvaluationLog",
        back_populates="user",
    )

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, default="New Chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )
    user = relationship(
    "User",
    back_populates="threads",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey("chat_threads.id"))
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    sources_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    thread: Mapped["ChatThread"] = relationship(back_populates="messages")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
    )
    document_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    filename: Mapped[str] = mapped_column(String)
    stored_path: Mapped[str] = mapped_column(String)
    chunks_added: Mapped[int] = mapped_column(Integer)
    chunk_ids_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship(
    "User",
    back_populates="documents",
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chunk_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    document_id: Mapped[str] = mapped_column(String, index=True)
    filename: Mapped[str] = mapped_column(String)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(EMBEDDING_DIM))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
    )
    thread_id: Mapped[str] = mapped_column(String)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[float] = mapped_column(Float)
    sources_count: Mapped[int] = mapped_column(Integer)
    no_answer: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship(
    "User",
    back_populates="evaluations",
    )