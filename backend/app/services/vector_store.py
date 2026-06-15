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


# import os
# from typing import List, Tuple

# from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.document_loaders import PyPDFLoader, TextLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from sqlalchemy import text

# from app.core.config import settings
# from app.db.database import SessionLocal
# from app.db.models import DocumentChunk


# _embeddings = OpenAIEmbeddings(
#     model=settings.embedding_model,
#     api_key=settings.openai_api_key,
# )


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

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200,
#     )

#     chunks = splitter.split_documents(docs)

#     chunk_ids = []

#     db = SessionLocal()

#     try:
#         for index, chunk in enumerate(chunks):
#             chunk_id = f"{document_id}_chunk_{index}"
#             chunk_ids.append(chunk_id)

#             embedding = _embeddings.embed_query(chunk.page_content)

#             row = DocumentChunk(
#                 chunk_id=chunk_id,
#                 document_id=document_id,
#                 filename=original_filename,
#                 page=chunk.metadata.get("page"),
#                 content=chunk.page_content,
#                 embedding=embedding,
#             )

#             db.add(row)

#         db.commit()

#     except Exception:
#         db.rollback()
#         raise

#     finally:
#         db.close()

#     return len(chunks), chunk_ids


# def similarity_search(question: str, k: int = 4) -> List[Document]:
#     query_embedding = _embeddings.embed_query(question)

#     db = SessionLocal()

#     try:
#         rows = (
#             db.query(DocumentChunk)
#             .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
#             .limit(k)
#             .all()
#         )

#         docs = []

#         for row in rows:
#             docs.append(
#                 Document(
#                     page_content=row.content,
#                     metadata={
#                         "document_id": row.document_id,
#                         "filename": row.filename,
#                         "source": row.filename,
#                         "page": row.page,
#                         "chunk_id": row.chunk_id,
#                     },
#                 )
#             )

#         return docs

#     finally:
#         db.close()

# def keyword_search(question: str, k: int = 4) -> List[Document]:
#     db = SessionLocal()

#     try:
#         rows = (
#             db.query(DocumentChunk)
#             .filter(DocumentChunk.content.ilike(f"%{question}%"))
#             .limit(k)
#             .all()
#         )

#         docs = []

#         for row in rows:
#             docs.append(
#                 Document(
#                     page_content=row.content,
#                     metadata={
#                         "document_id": row.document_id,
#                         "filename": row.filename,
#                         "source": row.filename,
#                         "page": row.page,
#                         "chunk_id": row.chunk_id,
#                         "search_type": "keyword",
#                     },
#                 )
#             )

#         return docs

#     finally:
#         db.close()


# def hybrid_search(question: str, k: int = 4) -> List[Document]:
#     vector_docs = similarity_search(question, k=k)
#     keyword_docs = keyword_search(question, k=k)

#     combined = []
#     seen_chunk_ids = set()

#     for doc in vector_docs + keyword_docs:
#         chunk_id = doc.metadata.get("chunk_id")

#         if chunk_id and chunk_id not in seen_chunk_ids:
#             seen_chunk_ids.add(chunk_id)
#             combined.append(doc)

#     return combined[:k]


# def delete_document_chunks(chunk_ids: List[str]):
#     if not chunk_ids:
#         return

#     db = SessionLocal()

#     try:
#         db.query(DocumentChunk).filter(DocumentChunk.chunk_id.in_(chunk_ids)).delete(
#             synchronize_session=False
#         )
#         db.commit()

#     except Exception:
#         db.rollback()
#         raise

#     finally:
#         db.close()

import re
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from sqlalchemy import or_
from sqlalchemy import or_, text

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


def get_splitter(file_name: str) -> RecursiveCharacterTextSplitter:
    if file_name.lower().endswith(".pdf"):
        return RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    return RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_keywords(question: str) -> List[str]:
    words = re.findall(r"[A-Za-z0-9_\-]+", question)

    stopwords = {
        "what", "when", "where", "which", "who", "whom", "whose",
        "is", "are", "was", "were", "the", "a", "an", "of",
        "to", "in", "on", "for", "about", "tell", "me", "does",
        "do", "did", "and", "or", "with", "from",
    }

    keywords = []

    for word in words:
        cleaned = word.strip().lower()

        if len(cleaned) >= 4 and cleaned not in stopwords:
            keywords.append(cleaned)

    return list(dict.fromkeys(keywords))


def ingest_file(path: str, original_filename: str, document_id: str) -> Tuple[int, List[str]]:
    docs = load_file(path)

    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
        doc.metadata["document_id"] = document_id
        doc.metadata["filename"] = original_filename
        doc.metadata["source"] = original_filename

    splitter = get_splitter(original_filename)
    chunks = splitter.split_documents(docs)

    chunk_ids = []
    db = SessionLocal()

    try:
        for index, chunk in enumerate(chunks):
            content = clean_text(chunk.page_content)

            if not content:
                continue

            chunk_id = f"{document_id}_chunk_{index}"
            chunk_ids.append(chunk_id)

            embedding = _embeddings.embed_query(content)

            row = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                filename=original_filename,
                page=chunk.metadata.get("page"),
                content=content,
                embedding=embedding,
            )

            db.add(row)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    return len(chunk_ids), chunk_ids


def _row_to_doc(row: DocumentChunk, search_type: str, score: float = 0.0) -> Document:
    return Document(
        page_content=row.content,
        metadata={
            "document_id": row.document_id,
            "filename": row.filename,
            "source": row.filename,
            "page": row.page,
            "chunk_id": row.chunk_id,
            "search_type": search_type,
            "score": score,
        },
    )


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

        return [_row_to_doc(row, "vector") for row in rows]

    finally:
        db.close()


# def keyword_search(question: str, k: int = 4) -> List[Document]:
#     keywords = extract_keywords(question)

#     if not keywords:
#         return []

#     db = SessionLocal()

#     try:
#         conditions = [
#             DocumentChunk.content.ilike(f"%{keyword}%")
#             for keyword in keywords
#         ]

#         rows = (
#             db.query(DocumentChunk)
#             .filter(or_(*conditions))
#             .limit(k)
#             .all()
#         )

#         results = []

#         for row in rows:
#             content_lower = row.content.lower()

#             keyword_score = sum(
#                 1 for keyword in keywords if keyword in content_lower
#             )

#             results.append(_row_to_doc(row, "keyword", score=keyword_score))

#         results.sort(key=lambda doc: doc.metadata.get("score", 0), reverse=True)

#         return results[:k]

#     finally:
#         db.close()

def keyword_search(question: str, k: int = 4) -> List[Document]:
    db = SessionLocal()

    try:
        sql = """
        SELECT
            id,
            chunk_id,
            document_id,
            filename,
            page,
            content,
            ts_rank(
                to_tsvector('english', content),
                plainto_tsquery('english', :query)
            ) AS rank
        FROM document_chunks
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
        ORDER BY rank DESC
        LIMIT :limit
        """

        rows = db.execute(
            text(sql),
            {
                "query": question,
                "limit": k,
            },
        ).fetchall()

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
                        "search_type": "postgres_full_text",
                        "score": float(row.rank or 0),
                    },
                )
            )

        return docs

    finally:
        db.close()



def hybrid_search(question: str, k: int = 4) -> List[Document]:
    vector_docs = similarity_search(question, k=k * 2)
    keyword_docs = keyword_search(question, k=k * 2)

    scores = {}

    for rank, doc in enumerate(vector_docs):
        chunk_id = doc.metadata.get("chunk_id")
        if not chunk_id:
            continue

        scores[chunk_id] = {
            "doc": doc,
            "score": 1.0 / (rank + 1),
        }

    for rank, doc in enumerate(keyword_docs):
        chunk_id = doc.metadata.get("chunk_id")
        if not chunk_id:
            continue

        keyword_boost = 2.0 / (rank + 1)

        if chunk_id in scores:
            scores[chunk_id]["score"] += keyword_boost
            scores[chunk_id]["doc"].metadata["search_type"] = "hybrid"
        else:
            scores[chunk_id] = {
                "doc": doc,
                "score": keyword_boost,
            }

    ranked = sorted(
        scores.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    final_docs = []

    for item in ranked[:k]:
        doc = item["doc"]
        doc.metadata["hybrid_score"] = item["score"]
        final_docs.append(doc)

    return final_docs


def delete_document_chunks(chunk_ids: List[str]):
    if not chunk_ids:
        return

    db = SessionLocal()

    try:
        db.query(DocumentChunk).filter(
            DocumentChunk.chunk_id.in_(chunk_ids)
        ).delete(synchronize_session=False)

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


    