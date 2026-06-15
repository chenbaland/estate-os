"""RAG utilities for document chunking, embedding, and retrieval."""
import math
from typing import Callable, Iterable, List


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """Split document text into overlapping chunks for embedding."""
    if not text:
        return []
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 5)
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end >= text_len:
            break
        start += chunk_size - overlap
    return chunks


def embed_chunks(
    chunks: Iterable[str],
    embed_fn: Callable[[str], List[float]],
    model_name: str = "text-embedding-3-small",
) -> List[dict]:
    """Generate embeddings for each chunk using the provided embed function."""
    return [
        {
            "chunk_index": index,
            "chunk_text": chunk,
            "embedding_vector": embed_fn(chunk),
            "model_name": model_name,
        }
        for index, chunk in enumerate(chunks)
    ]


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0.0
    dot = sum(x * y for x, y in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(x * x for x in vector_a))
    norm_b = math.sqrt(sum(x * x for x in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_relevant_chunks(
    query_embedding: List[float],
    embeddings: List[dict],
    top_k: int = 3,
) -> List[dict]:
    """Return top-k chunks most similar to the query embedding."""
    scored = [
        (cosine_similarity(query_embedding, item["embedding_vector"]), item)
        for item in embeddings
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:top_k]]
