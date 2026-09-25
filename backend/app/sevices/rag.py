import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List,Dict
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

_embedder: SentenceTransformer = None
_chroma_client : chromadb.PersistentClient = None

def get_embedder() -> SentenceTransformer: 
    global _embeder 
    if _embedder is None:
        logger.info("Loading embedding model...")
        _embedder =  SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def det_chroma()-> chromadb.PersistentClient:
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chroma.PersistentClient(
            path =settings.chroma_persist_dir,
            settings = ChromaSettings(anonymized_telemetry=False),
        ) 
    return _chroma_client 

def get_collection(session_id: str):
    client = get_chroma()
    collection_name  = f" session_ {session_id.replace('-', '_')}"
    return client.get_or_create_collection(name = collection.name,
    metadata={"hnsw:space": "cosine"},
    )

def chink_text(text:str)-> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size= 1800,
            chunk_overlap=200,
            seperators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_text(text)
        return [c.strip() for c in chunks if c.strip()]

def index_document (session_id:str, file_id: str, file_name: str, text:str)-> int:
     chunks = chunk_text(text)
     if not chunks:
        logger.warning(f"No chunks for {file_name}")
        return 0

    embedder = get_embedder()
    collection  = get_collection(session_id)

    embeddings = embedder.encode(chunks, show_progress_bar = False).tolist()

    ids = [f"{file_id}_chunk_{i}" for i in range (len(chunks))]

    metadatas= [
        {
            "file_id":   file_id,
            "file_name": file_name,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids =ids,
        embeddings =embeddings,
        documents =chunks,
        metadatas = metadatas,
    )

    logger.info(f"Indexed {len(chunks)} chunks for'{file_name}")
    return len(chunks)

def retrive_context(
        session_id: str,
        query : str,
        top_k: int 5
)-> List[Dict]:
    embedder = get_embedder()
    collection = get_collection(session_id)

    if collection.count() == 0:
        return []

    query_embedding = embedder.encode(
        [query],
        show_progress_bar=False
    ).tolist()[0]


    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text":        doc,
            "file_name":   meta.get("file_name", "Unknown"),
            "chunk_index": meta.get("chunk_index", 0),
            "relevance":   round(1 - dist, 3),
        })

    return chunks


def delete_session_index(session_id: str):
    client = get_chroma()
    collection_name = f"session_{session_id.replace('-', '_')}"
    try:
        client.delete_collection(collection_name)
        logger.info(f"Deleted collection for session {session_id}")
    except Exception as e:
        logger.warning(f"Could not delete collection: {e}")