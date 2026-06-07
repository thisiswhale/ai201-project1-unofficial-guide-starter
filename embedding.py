"""Embedding + vector store for The Unofficial Guide (coffee RAG).

Stage 3 (Embedding + Vector Store) from planning.md: embed every chunk produced
by ingest.py with sentence-transformers (bge-large-en-v1.5) and persist them to a
local Chroma collection, preserving each chunk's metadata for filtered retrieval.

Run directly to (re)build the store:
    python embedding.py
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

import config
from ingest import Document, build_chunks

# Resolve the Chroma path (config.CHROMA_PATH) relative to this file so the store
# always lands in the project root regardless of the working directory.
CHROMA_DIR = (Path(__file__).parent / config.CHROMA_PATH).resolve()

# Cache the embedding model across calls (loading bge-large-en-v1.5 is expensive).
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load (once) and return the sentence-transformers embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of passages. Vectors are L2-normalized for cosine similarity.

    Note: bge models recommend a query-side instruction prefix only for *queries*
    at retrieval time, not for the corpus, so passages are embedded as-is here.
    """
    embeddings = get_model().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return embeddings.tolist()


def embed_and_store(
    chunks: list[Document] | None = None,
    *,
    collection_name: str = config.CHROMA_COLLECTION,
    reset: bool = True,
) -> chromadb.api.models.Collection.Collection:
    """Embed all chunks and persist them to a local Chroma collection.

    Args:
        chunks: pre-built chunk Documents; if None, built from ingest.build_chunks().
        collection_name: Chroma collection to write to.
        reset: drop any existing collection first so re-runs don't duplicate chunks.

    Returns:
        The populated Chroma collection.
    """
    if chunks is None:
        chunks = build_chunks()
    if not chunks:
        raise ValueError("No chunks to embed — check the documents/ folder.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    if reset:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass  # collection didn't exist yet

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c.text for c in chunks]
    metadatas = [c.metadata for c in chunks]
    # Unique, stable id per chunk: "<filename>::<chunk_index>".
    ids = [f"{c.metadata['filename']}::{c.metadata['chunk_index']}" for c in chunks]

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embed_texts(texts),
    )

    return collection


if __name__ == "__main__":
    chunks = build_chunks()
    print(f"Embedding {len(chunks)} chunks with {config.EMBEDDING_MODEL} ...")

    collection = embed_and_store(chunks)

    count = collection.count()
    print(f"\nStored {count} chunks in Chroma collection '{config.CHROMA_COLLECTION}'")
    print(f"Persisted to: {CHROMA_DIR}")

    # Verification (planning.md Stage 3): collection count == chunk count,
    # and metadata is retained on stored records.
    assert count == len(chunks), f"count {count} != chunk count {len(chunks)}"
    sample = collection.get(limit=1, include=["metadatas"])
    print(f"Sample stored metadata: {sample['metadatas'][0]}")
