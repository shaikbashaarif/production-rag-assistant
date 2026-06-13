# import json
# import sqlite3
# from typing import TypedDict, Annotated, List, Dict, Any

# from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
# from langchain_openai import ChatOpenAI
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langgraph.checkpoint.sqlite import SqliteSaver

# from app.core.config import settings
# #from app.services.vector_store import similarity_search
# from app.services.vector_store import hybrid_search


# llm = ChatOpenAI(
#     model=settings.chat_model,
#     api_key=settings.openai_api_key,
#     streaming=True,
# )


# class RAGState(TypedDict):
#     messages: Annotated[List[BaseMessage], add_messages]


# def generate_title(user_message: str) -> str:
#     title_llm = ChatOpenAI(
#         model=settings.chat_model,
#         api_key=settings.openai_api_key,
#     )

#     prompt = f"""
# Generate a very short chat title. Maximum 4 words.

# User message:
# {user_message}
# """

#     return title_llm.invoke(prompt).content.strip()


# def build_rag_prompt(question: str, docs: List[Any]) -> str:
#     # context = "\n\n".join(
#     #     [
#     #         f"Source: {doc.metadata.get('source', 'unknown')}\nContent: {doc.page_content}"
#     #         for doc in docs
#     #     ]
#     # )

#     context = "\n\n".join(
#     [
#         f"""
#     Source: {doc.metadata.get('filename', 'unknown')}
#     Page: {doc.metadata.get('page', 'N/A')}
#     Content: {doc.page_content}
#     """
#             for doc in docs
#         ]
#     )

#     prompt = f"""
# You are a helpful AI assistant.

# Answer the user's question using only the provided context.
# If the answer is not available in the context, say:
# "I don't know based on the uploaded documents."

# Context:
# {context}

# Question:
# {question}
# """

#     return prompt


# def rag_node(state: RAGState):
#     user_question = state["messages"][-1].content

#     docs = hybrid_search(user_question, k=4)

#     prompt = build_rag_prompt(user_question, docs)

#     response = llm.invoke(
#         [
#             SystemMessage(content="You are a helpful RAG assistant."),
#             HumanMessage(content=prompt),
#         ]
#     )

#     return {"messages": [response]}


# conn = sqlite3.connect("rag_checkpoints.db", check_same_thread=False)
# checkpointer = SqliteSaver(conn)

# graph = StateGraph(RAGState)
# graph.add_node("rag_node", rag_node)
# graph.add_edge(START, "rag_node")
# graph.add_edge("rag_node", END)

# rag_app = graph.compile(checkpointer=checkpointer)


# def ask_rag(question: str, thread_id: str, top_k: int = 4):
#     docs = hybrid_search(question, k=top_k)

#     prompt = build_rag_prompt(question, docs)

#     response = llm.invoke(
#         [
#             SystemMessage(content="You are a helpful RAG assistant."),
#             HumanMessage(content=prompt),
#         ]
#     )

#     # sources = [
#     #     {
#     #         "filename": doc.metadata.get("source", "unknown"),
#     #         "content": doc.page_content[:500],
#     #     }
#     #     for doc in docs
#     # ]


# #     sources = [
# #     {
# #         "filename": doc.metadata.get("filename", "unknown"),
# #         "page": doc.metadata.get("page"),
# #         "preview": doc.page_content[:150],
# #         "document_id": doc.metadata.get("document_id"),
# #     }
# #     for doc in docs
# # ]

#     best_doc = docs[0] if docs else None

#     sources = []

#     if best_doc:
#         sources = [
#             {
#                 "filename": best_doc.metadata.get("filename", "unknown"),
#                 "page": best_doc.metadata.get("page"),
#                 "preview": best_doc.page_content[:180],
#                 "document_id": best_doc.metadata.get("document_id"),
#             }
#         ]

#     return response.content, sources


# async def stream_rag(question: str, thread_id: str, top_k: int = 4):
#     docs = hybrid_search(question, k=top_k)

#     prompt = build_rag_prompt(question, docs)

#     async for chunk in llm.astream(
#         [
#             SystemMessage(content="You are a helpful RAG assistant."),
#             HumanMessage(content=prompt),
#         ]
#     ):
#         if chunk.content:
#             yield chunk.content

import sqlite3
from typing import TypedDict, Annotated, List, Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

from app.core.config import settings
from app.services.vector_store import hybrid_search


llm = ChatOpenAI(
    model=settings.chat_model,
    api_key=settings.openai_api_key,
    streaming=True,
)


class RAGState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


def generate_title(user_message: str) -> str:
    try:
        title_llm = ChatOpenAI(
            model=settings.chat_model,
            api_key=settings.openai_api_key,
        )

        prompt = f"""
Generate a very short chat title. Maximum 4 words.

User message:
{user_message}
"""
        return title_llm.invoke(prompt).content.strip()

    except Exception:
        return user_message[:30] or "New Chat"


def build_rag_prompt(question: str, docs: List[Any]) -> str:
    context = "\n\n".join(
        [
            f"""
Source: {doc.metadata.get('filename', 'unknown')}
Page: {doc.metadata.get('page', 'N/A')}
Content: {doc.page_content}
"""
            for doc in docs
        ]
    )

    return f"""
You are a helpful AI assistant.

Answer the user's question using only the provided context.
If the answer is not available in the context, say:
"I don't know based on the uploaded documents."

Context:
{context}

Question:
{question}
"""


def get_best_preview(question: str, content: str, max_chars: int = 220) -> str:
    question_terms = [
        word.lower().strip(".,:;!?()[]{}")
        for word in question.split()
        if len(word.strip(".,:;!?()[]{}")) >= 4
    ]

    clean_content = content.replace("\n", " ")
    sentences = clean_content.split(".")

    for sentence in sentences:
        sentence_lower = sentence.lower()

        if any(term in sentence_lower for term in question_terms):
            preview = sentence.strip()

            if len(preview) > max_chars:
                preview = preview[:max_chars] + "..."

            return preview + "."

    preview = clean_content[:max_chars]

    if len(clean_content) > max_chars:
        preview += "..."

    return preview


def rag_node(state: RAGState):
    user_question = state["messages"][-1].content
    docs = hybrid_search(user_question, k=4)
    prompt = build_rag_prompt(user_question, docs)

    response = llm.invoke(
        [
            SystemMessage(content="You are a helpful RAG assistant."),
            HumanMessage(content=prompt),
        ]
    )

    return {"messages": [response]}


conn = sqlite3.connect("rag_checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = StateGraph(RAGState)
graph.add_node("rag_node", rag_node)
graph.add_edge(START, "rag_node")
graph.add_edge("rag_node", END)

rag_app = graph.compile(checkpointer=checkpointer)


def ask_rag(question: str, thread_id: str, top_k: int = 4):
    docs = hybrid_search(question, k=top_k)

    prompt = build_rag_prompt(question, docs)

    response = llm.invoke(
        [
            SystemMessage(content="You are a helpful RAG assistant."),
            HumanMessage(content=prompt),
        ]
    )

    best_doc = docs[0] if docs else None

    sources = []

    if best_doc:
        sources = [
            {
                "filename": best_doc.metadata.get("filename", "unknown"),
                "page": best_doc.metadata.get("page"),
                "preview": get_best_preview(question, best_doc.page_content),
                "document_id": best_doc.metadata.get("document_id"),
            }
        ]

    return response.content, sources


async def stream_rag(question: str, thread_id: str, top_k: int = 4):
    docs = hybrid_search(question, k=top_k)

    prompt = build_rag_prompt(question, docs)

    async for chunk in llm.astream(
        [
            SystemMessage(content="You are a helpful RAG assistant."),
            HumanMessage(content=prompt),
        ]
    ):
        if chunk.content:
            yield chunk.content