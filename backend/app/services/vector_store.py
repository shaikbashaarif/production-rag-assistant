# # import os
# # from typing import List
# # from langchain_openai import OpenAIEmbeddings
# # from langchain_community.vectorstores import Chroma
# # from langchain_community.document_loaders import PyPDFLoader, TextLoader
# # from langchain_text_splitters import RecursiveCharacterTextSplitter
# # from langchain_core.documents import Document
# # from app.core.config import settings

# # #_embeddings = OpenAIEmbeddings(model=settings.embedding_model)
# # _embeddings = OpenAIEmbeddings(
# #     model=settings.embedding_model,
# #     api_key=settings.openai_api_key,
# # )


# # def get_vector_store() -> Chroma:
# #     os.makedirs(settings.chroma_dir, exist_ok=True)
# #     return Chroma(
# #         persist_directory=settings.chroma_dir,
# #         embedding_function=_embeddings,
# #         collection_name="rag_documents",
# #     )


# # def load_file(path: str) -> List[Document]:
# #     if path.lower().endswith(".pdf"):
# #         return PyPDFLoader(path).load()
# #     if path.lower().endswith(".txt"):
# #         return TextLoader(path, encoding="utf-8").load()
# #     raise ValueError("Only PDF and TXT files are supported.")


# # def ingest_file(path: str, original_filename: str) -> int:
# #     docs = load_file(path)
# #     for doc in docs:
# #         doc.metadata["filename"] = original_filename
# #         doc.metadata["source"] = path

# #     splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# #     chunks = splitter.split_documents(docs)
# #     vector_store = get_vector_store()
# #     vector_store.add_documents(chunks)
# #     return len(chunks)


# # def retrieve(question: str, top_k: int = 4) -> List[Document]:
# #     return get_vector_store().similarity_search(question, k=top_k)

# # def similarity_search(question: str, k: int = 4) -> List[Document]:
# #     return get_vector_store().similarity_search(question, k=k)


# import os
# from typing import List, Tuple

# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_community.document_loaders import PyPDFLoader, TextLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document

# from app.core.config import settings


# _embeddings = OpenAIEmbeddings(
#     model=settings.embedding_model,
#     api_key=settings.openai_api_key,
# )


# def get_vector_store() -> Chroma:
#     os.makedirs(settings.chroma_dir, exist_ok=True)

#     return Chroma(
#         persist_directory=settings.chroma_dir,
#         embedding_function=_embeddings,
#         collection_name="rag_documents",
#     )


# def load_file(path: str) -> List[Document]:
#     if path.lower().endswith(".pdf"):
#         return PyPDFLoader(path).load()

#     if path.lower().endswith(".txt"):
#         return TextLoader(path, encoding="utf-8").load()

#     raise ValueError("Only PDF and TXT files are supported.")


# def ingest_file(path: str, original_filename: str, document_id: str) -> Tuple[int, List[str]]:
#     docs = load_file(path)

#     for doc in docs:
#         doc.metadata["document_id"] = document_id
#         doc.metadata["filename"] = original_filename
#         doc.metadata["source"] = original_filename
#         doc.metadata["stored_path"] = path

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#     )

#     chunks = splitter.split_documents(docs)

#     chunk_ids = []

#     for index, chunk in enumerate(chunks):
#         chunk_id = f"{document_id}_chunk_{index}"
#         chunk.metadata["chunk_id"] = chunk_id
#         chunk_ids.append(chunk_id)

#     vector_store = get_vector_store()
#     vector_store.add_documents(chunks, ids=chunk_ids)

#     return len(chunks), chunk_ids


# def similarity_search(question: str, k: int = 4) -> List[Document]:
#     return get_vector_store().similarity_search(question, k=k)


# def delete_document_chunks(chunk_ids: List[str]):
#     if not chunk_ids:
#         return

#     vector_store = get_vector_store()
#     vector_store.delete(ids=chunk_ids)


import os
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import text

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import DocumentChunk


_embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    api_key=settings.openai_api_key,
)


def load_file(path: str) -> List[Document]:
    if path.lower().endswith(".pdf"):
        return PyPDFLoader(path).load()

    if path.lower().endswith(".txt"):
        return TextLoader(path, encoding="utf-8").load()

    raise ValueError("Only PDF and TXT files are supported.")


def ingest_file(path: str, original_filename: str, document_id: str) -> Tuple[int, List[str]]:
    docs = load_file(path)

    for doc in docs:
        doc.metadata["document_id"] = document_id
        doc.metadata["filename"] = original_filename
        doc.metadata["source"] = original_filename

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(docs)

    chunk_ids = []

    db = SessionLocal()

    try:
        for index, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{index}"
            chunk_ids.append(chunk_id)

            embedding = _embeddings.embed_query(chunk.page_content)

            row = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                filename=original_filename,
                page=chunk.metadata.get("page"),
                content=chunk.page_content,
                embedding=embedding,
            )

            db.add(row)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    return len(chunks), chunk_ids


def similarity_search(question: str, k: int = 4) -> List[Document]:
    query_embedding = _embeddings.embed_query(question)

    db = SessionLocal()

    try:
        rows = (
            db.query(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(k)
            .all()
        )

        docs = []

        for row in rows:
            docs.append(
                Document(
                    page_content=row.content,
                    metadata={
                        "document_id": row.document_id,
                        "filename": row.filename,
                        "source": row.filename,
                        "page": row.page,
                        "chunk_id": row.chunk_id,
                    },
                )
            )

        return docs

    finally:
        db.close()


def delete_document_chunks(chunk_ids: List[str]):
    if not chunk_ids:
        return

    db = SessionLocal()

    try:
        db.query(DocumentChunk).filter(DocumentChunk.chunk_id.in_(chunk_ids)).delete(
            synchronize_session=False
        )
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()