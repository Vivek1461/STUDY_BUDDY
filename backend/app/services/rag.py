"""Lazy-loaded ChromaDB retrieval service."""
import logging
from pathlib import Path
from typing import Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import get_settings

logger = logging.getLogger(__name__)
_embedder: SentenceTransformer | None = None
_client: Any = None

def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(get_settings().embedding_model)
    return _embedder

def get_chroma() -> Any:
    global _client
    if _client is None:
        directory = get_settings().chroma_persist_dir
        Path(directory).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(directory), settings=ChromaSettings(anonymized_telemetry=False))
    return _client

def get_collection(session_id: str):
    safe_id = session_id.replace("-", "_")
    return get_chroma().get_or_create_collection(name=f"session_{safe_id}", metadata={"hnsw:space": "cosine"})

def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150,
                                               separators=["\n\n", "\n", ". ", " ", ""])
    return [part.strip() for part in splitter.split_text(text) if part.strip()]

def index_document(session_id: str, file_id: str, file_name: str, text: str) -> int:
    chunks = chunk_text(text)
    if not chunks:
        return 0
    vectors = get_embedder().encode(chunks, show_progress_bar=False).tolist()
    collection = get_collection(session_id)
    ids = [f"{file_id}_{index}" for index in range(len(chunks))]
    metadata = [{"file_id": file_id, "file_name": file_name, "chunk_index": index}
                for index in range(len(chunks))]
    collection.upsert(ids=ids, embeddings=vectors, documents=chunks, metadatas=metadata)
    return len(chunks)

def retrieve_context(session_id: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    collection = get_collection(session_id)
    count = collection.count()
    if count == 0:
        return []
    vector = get_embedder().encode([query], show_progress_bar=False).tolist()[0]
    result = collection.query(query_embeddings=[vector], n_results=min(max(1, top_k), count),
                              include=["documents", "metadatas", "distances"])
    docs = result.get("documents", [[]])[0] or []
    metas = result.get("metadatas", [[]])[0] or []
    distances = result.get("distances", [[]])[0] or []
    return [{"text": doc, "file_name": meta.get("file_name", "Unknown"),
             "chunk_index": meta.get("chunk_index", 0), "relevance": round(1 - distance, 3)}
            for doc, meta, distance in zip(docs, metas, distances)]

def delete_file_index(session_id: str, file_id: str) -> None:
    get_collection(session_id).delete(where={"file_id": file_id})

def delete_session_index(session_id: str) -> None:
    name = f"session_{session_id.replace('-', '_')}"
    try:
        get_chroma().delete_collection(name)
    except Exception:
        logger.exception("Unable to remove vector collection for session %s", session_id)
