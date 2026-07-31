import os
from typing import Any

try:
    from langchain_chroma import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
except Exception as exc:
    Chroma = Any
    HuggingFaceEmbeddings = Any
    RecursiveCharacterTextSplitter = Any
    Document = Any
    _LANGCHAIN_IMPORT_ERROR = exc
else:
    _LANGCHAIN_IMPORT_ERROR = None

CHROMA_DIR = "vector_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _require_langchain():
    if _LANGCHAIN_IMPORT_ERROR is not None:
        raise RuntimeError("LangChain dependencies are not available. Please install requirements first.") from _LANGCHAIN_IMPORT_ERROR


def get_embeddings():
    _require_langchain()
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})


def build_vector_store(transcript: str) -> Any:
    _require_langchain()
    print("Building vector store")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(transcript)
    docs = [Document(page_content=chunk, metadata={"chunk_index": i}) for i, chunk in enumerate(chunks)]
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )
    return vector_store


def load_vector_store() -> Any:
    _require_langchain()
    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    return vector_store


def get_retriever(vector_store: Any, k: int = 4) -> Any:
    _require_langchain()
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
