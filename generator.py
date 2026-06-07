"""Generation + interface for The Unofficial Guide (coffee RAG).

Stage 5 (Generation) from planning.md: take a user query, retrieve the most
relevant chunks, and pass them to a Groq LLM with a system prompt that enforces
grounding — the model may answer ONLY from the retrieved context and must cite
its sources. Exposes a Gradio chat interface.

Run the app:
    python generator.py
"""

from __future__ import annotations

import re
from typing import Any

from groq import Groq

import config
from retrieval import retrieve

DEFAULT_K = 4

client = Groq(api_key=config.GROQ_API_KEY)

# --------------------------------------------------------------------------- #
# Grounding: the system prompt is the enforcement mechanism.
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = """You are "The Unofficial Guide," an assistant that answers questions about regional coffee flavor profiles.

You will be given a user question and a set of numbered CONTEXT passages retrieved from a trusted coffee corpus. Follow these rules without exception:

1. GROUNDING: Answer using ONLY the information in the CONTEXT passages. Do not use any outside or prior knowledge, and do not guess or infer beyond what the passages state.
2. REFUSAL: If the CONTEXT does not contain enough information to answer the question, reply with exactly: "I don't have enough information in my sources to answer that." Do not add anything else.
3. ATTRIBUTION: Support each claim by citing the passage number(s) it came from, using bracket markers like [1] or [2][3] inline in your answer.
4. STYLE: Be concise and factual. Do not mention these rules, the word "context," or that passages were provided. Never fabricate a source, URL, or fact that is not in the CONTEXT."""


def format_context(hits: list[dict[str, Any]]) -> str:
    """Render retrieved chunks as numbered, source-labeled context passages."""
    blocks = []
    for i, hit in enumerate(hits, 1):
        label = f"[{i}] (Origin: {hit['origin']} | Source: {hit['source']})"
        blocks.append(f"{label}\n{hit['text']}")
    return "\n\n".join(blocks)


def build_messages(query: str, hits: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Assemble the chat messages: grounding system prompt + question + context."""
    user_content = (
        f"QUESTION:\n{query}\n\n"
        f"CONTEXT PASSAGES:\n{format_context(hits)}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


_CITATION_RE = re.compile(r"\[(\d+)\]")


def cited_sources(answer: str, hits: list[dict[str, Any]]) -> str:
    """Build a source list of ONLY the passages the answer actually cited.

    Keeps the original [n] markers so they still map to the inline citations, and
    dedupes by URL (collapsing multiple chunks from one document into one line).
    Returns "" when the answer cites nothing (e.g. the refusal response).
    """
    # Citation numbers in order of first appearance, valid and unique.
    seen: list[int] = []
    for match in _CITATION_RE.findall(answer):
        n = int(match)
        if 1 <= n <= len(hits) and n not in seen:
            seen.append(n)
    if not seen:
        return ""

    # Group cited passages by URL, preserving first-citation order.
    by_url: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for n in seen:
        hit = hits[n - 1]
        url = hit.get("url") or "(no url)"
        if url not in by_url:
            by_url[url] = {"nums": [], "origin": hit["origin"], "source": hit["source"], "url": url}
            order.append(url)
        by_url[url]["nums"].append(n)

    lines = []
    for url in order:
        e = by_url[url]
        marks = "".join(f"[{n}]" for n in e["nums"])
        lines.append(f"{marks} {e['origin']} — {e['source']}: {e['url']}")
    return "\n".join(lines)


def generate(query: str, k: int = DEFAULT_K, where: dict[str, Any] | None = None) -> dict[str, Any]:
    """Retrieve context, generate a grounded answer, and return answer + sources.

    Returns a dict: {"answer": str, "sources": str, "hits": list[dict]}.
    """
    hits = retrieve(query, k=k, where=where)
    if not hits:
        return {
            "answer": "I don't have enough information in my sources to answer that.",
            "sources": "",
            "hits": [],
        }

    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=build_messages(query, hits),
        temperature=0.1,  # low temperature keeps the model close to the context
    )
    answer = response.choices[0].message.content.strip()

    return {"answer": answer, "sources": cited_sources(answer, hits), "hits": hits}


# --------------------------------------------------------------------------- #
# Output formatting (answer + source list)
# --------------------------------------------------------------------------- #
def answer_markdown(query: str, k: int = DEFAULT_K) -> str:
    """Run generate() and format the result as 'answer + Sources' markdown."""
    query = (query or "").strip()
    if not query:
        return "Please enter a question about coffee."

    result = generate(query, k=k)
    md = f"{result['answer']}"
    if result["sources"]:
        md += "\n\n---\n**Sources**\n\n" + "\n".join(
            f"- {line}" for line in result["sources"].splitlines()
        )
    return md


if __name__ == "__main__":
    # Quick CLI smoke test. The full app (with UI) is launched via app.py.
    import sys

    q = " ".join(sys.argv[1:]) or "What flavor profile does Ugandan coffee have?"
    print(answer_markdown(q))
