"""Retrieval for The Unofficial Guide (coffee RAG).

Stage 4 (Retrieval) from planning.md: embed the user query and return the top-k
most relevant chunks from the Chroma collection, along with their source metadata
and cosine distance scores.

Run directly to test retrieval against the evaluation-plan queries:
    python retrieval.py
"""

from __future__ import annotations

from typing import Any

from embedding import get_collection, get_model

# bge models recommend this instruction prefix on the QUERY side only (passages
# were embedded without it in embedding.py).
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def embed_query(query: str) -> list[float]:
    """Embed a query with the bge instruction prefix, normalized for cosine."""
    vector = get_model().encode(QUERY_PREFIX + query, normalize_embeddings=True)
    return vector.tolist()


def retrieve(
    query: str,
    k: int = 4,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return the top-k most relevant chunks for `query`.

    Args:
        query: the user question.
        k: number of chunks to retrieve (start at 4; tune after seeing results).
        where: optional Chroma metadata filter, e.g. {"origin": "Kenya"}.

    Returns:
        A list of dicts (closest first), each with:
            text, distance, origin, source, source_type, url, filename, chunk_index
    """
    result = get_collection().query(
        query_embeddings=[embed_query(query)],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    hits: list[dict[str, Any]] = []
    for doc, meta, dist in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        hits.append(
            {
                "text": doc,
                "distance": dist,
                "origin": meta.get("origin"),
                "source": meta.get("source"),
                "source_type": meta.get("source_type"),
                "url": meta.get("url"),
                "filename": meta.get("filename"),
                "chunk_index": meta.get("chunk_index"),
            }
        )
    return hits


# Evaluation-plan queries (planning.md Evaluation Plan).
EVAL_QUERIES = [
    "What flavor profile does Ugandan coffee have?",
    "What are the key flavor differences between Arabica and Robusta coffee?",
    "What does Colombian coffee taste like and what makes it unique?",
    "What is Kona Coffee?",
    "What makes Ethiopian Yirgacheffe coffee unique compared to other Ethiopian coffees?",
]

# How many characters of each chunk to show in the test output.
PREVIEW_CHARS = 240


def _preview(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= PREVIEW_CHARS else text[:PREVIEW_CHARS] + " …"


if __name__ == "__main__":
    k = 4
    for query in EVAL_QUERIES:
        print("=" * 100)
        print(f"QUERY: {query}   (k={k})")
        print("=" * 100)
        for rank, hit in enumerate(retrieve(query, k=k), 1):
            print(
                f"\n[{rank}] distance={hit['distance']:.4f}  "
                f"origin={hit['origin']}  source={hit['source']}  "
                f"({hit['filename']} #{hit['chunk_index']})"
            )
            print(f"    {_preview(hit['text'])}")
        print()
