"""Document ingestion and chunking for The Unofficial Guide (coffee RAG).

Stage 1 (Document Ingestion): load every .txt in documents/ into a record with
metadata (origin, source, source_type, url) per the planning.md Documents table.

Stage 2 (Chunking): chunk_text() implements the routing strategy from planning.md:
  - short docs (< 120 tokens)        -> kept whole
  - medium docs                      -> recursive split at 400 tokens / 30 overlap
  - long editorial docs (> 600 tok)  -> split by section header first, then recursive

Note: the project's requirements.txt does not include LangChain, so the
RecursiveCharacterTextSplitter / MarkdownHeaderTextSplitter behavior described in
planning.md is reimplemented here in pure Python (no extra dependencies). Token
counts are an approximation (word + punctuation count); swap count_tokens() for a
model tokenizer if you need exact subword counts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DOCUMENTS_DIR = Path(__file__).parent / "documents"

# Chunking parameters from planning.md (Chunking Strategy section).
MIN_TOKENS = 120        # docs at or below this are kept whole
CHUNK_TOKENS = 400      # target chunk size
OVERLAP_TOKENS = 30     # overlap carried between consecutive chunks
LONG_DOC_TOKENS = 600   # docs above this are split by section header first

# Metadata for each source file, keyed by filename stem.
# Mirrors the Documents table in planning.md.
SOURCE_METADATA: dict[str, dict[str, str]] = {
    "costa-rica": {
        "origin": "Costa Rica",
        "source": "Espresso Coffee Guide",
        "source_type": "guide",
        "url": "https://espressocoffeeguide.com/gourmet-coffee/coffees-of-the-americas/costa-rica-coffee/",
    },
    "history-of-coffee": {
        "origin": "Global",
        "source": "Wikipedia",
        "source_type": "encyclopedia",
        "url": "https://en.wikipedia.org/wiki/History_of_coffee",
    },
    "brazil": {
        "origin": "Brazil",
        "source": "Sweet Maria's",
        "source_type": "roaster_overview",
        "url": "https://library.sweetmarias.com/coffee-producing-countries/south-america/brazil-coffee-overview/",
    },
    "yirgacheffe": {
        "origin": "Ethiopia (Yirgacheffe)",
        "source": "Suvie",
        "source_type": "blog",
        "url": "https://blog.suvie.com/a-beginners-guide-to-coffee-ethiopian-yirgacheffe",
    },
    "colombia": {
        "origin": "Colombia",
        "source": "Cooper Coffee Co.",
        "source_type": "blog",
        "url": "https://www.cooperscoffeeco.com/discover-the-rich-flavors-what-does-colombian-coffee-taste-like/",
    },
    "kona-hawaii": {
        "origin": "Hawaii (Kona)",
        "source": "Kona Farm Direct",
        "source_type": "blog",
        "url": "https://www.konafarmdirect.com/post/the-ultimate-guide-to-kona-coffee-what-makes-it-the-world-s-most-sought-after-bean",
    },
    "sumatra": {
        "origin": "Indonesia (Sumatra)",
        "source": "Sweet Maria's",
        "source_type": "roaster_overview",
        "url": "https://library.sweetmarias.com/coffee-producing-countries/indonesia-se-asia/sumatra-coffee-overview/",
    },
    "arabica-vs-robusta": {
        "origin": "General",
        "source": "Lavazza",
        "source_type": "comparison",
        "url": "https://www.lavazzausa.com/en/recipes-and-coffee-hacks/difference-type-arabica-robusta-coffee",
    },
    "yunnan": {
        "origin": "China (Yunnan)",
        "source": "Nature Brew Escape",
        "source_type": "blog",
        "url": "https://naturebrewescape.com/the-extraordinary-rise-how-yunnan-coffee-became-asias-new-coffee-champion/",
    },
    "uganda": {
        "origin": "Uganda",
        "source": "Homeland Coffee",
        "source_type": "blog",
        "url": "https://homelandcoffee.co/blogs/our-blog/the-flavor-profile-of-ugandan-coffee",
    },
    "ecuador": {
        "origin": "Ecuador",
        "source": "Sweet Maria's",
        "source_type": "roaster_overview",
        "url": "https://library.sweetmarias.com/coffee-producing-countries/south-america/ecuador-coffee-overview/",
    },
    "kenya": {
        "origin": "Kenya",
        "source": "Sweet Maria's",
        "source_type": "roaster_overview",
        "url": "https://library.sweetmarias.com/coffee-producing-countries/africa/kenya-coffee-overview/",
    },
}


@dataclass
class Document:
    """A loaded source document and its retrieval metadata."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Stage 1: Document ingestion
# --------------------------------------------------------------------------- #
def load_documents(folder: str | Path = DOCUMENTS_DIR) -> list[Document]:
    """Load every .txt file in `folder` into a Document with metadata.

    Metadata is looked up from SOURCE_METADATA by filename stem. Files without a
    mapping still load, tagged with their stem as the origin so nothing is dropped.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Documents folder not found: {folder}")

    documents: list[Document] = []
    for path in sorted(folder.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue  # skip empty files

        meta = dict(SOURCE_METADATA.get(path.stem, {"origin": path.stem}))
        meta.setdefault("source", "unknown")
        meta.setdefault("source_type", "unknown")
        meta.setdefault("url", "")
        meta["filename"] = path.name

        documents.append(Document(text=text, metadata=meta))

    return documents


# --------------------------------------------------------------------------- #
# Stage 2: Chunking
# --------------------------------------------------------------------------- #
_TOKEN_RE = re.compile(r"\w+|[^\w\s]")
# A "header" line: short, standalone, and not ending in sentence punctuation.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def count_tokens(text: str) -> int:
    """Approximate token count (words + punctuation marks).

    This is a dependency-free proxy. For exact subword counts, replace with the
    tokenizer of your embedding model, e.g.:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("BAAI/bge-large-en-v1.5")
        return len(tok.encode(text, add_special_tokens=False))
    """
    return len(_TOKEN_RE.findall(text))


def _is_header(line: str) -> bool:
    """Heuristic: a standalone section header line (no trailing sentence punctuation)."""
    s = line.strip()
    if not s or len(s) > 60:
        return False
    return s[-1] not in ".!?,;:"


def _split_into_sections(text: str) -> list[str]:
    """Split a long doc into sections at heuristic header lines.

    Mirrors the intent of MarkdownHeaderTextSplitter for documents that use plain
    header lines instead of Markdown '#' syntax. The header line stays attached to
    the top of its section so each chunk keeps its topical context.
    """
    lines = text.splitlines()
    sections: list[list[str]] = []
    current: list[str] = []

    for i, line in enumerate(lines):
        prev_blank = i == 0 or not lines[i - 1].strip()
        next_content = i + 1 < len(lines) and bool(lines[i + 1].strip())
        if _is_header(line) and prev_blank and next_content and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)

    return ["\n".join(s).strip() for s in sections if "\n".join(s).strip()]


def _units(text: str) -> list[str]:
    """Break text into atomic units (sentences / lines) for greedy packing."""
    units: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for sentence in _SENTENCE_END.split(paragraph):
            sentence = sentence.strip()
            if sentence:
                units.append(sentence)
    return units


def _pack(units: list[str], chunk_tokens: int, overlap_tokens: int) -> list[str]:
    """Greedily pack units into chunks of ~chunk_tokens with token overlap."""
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for unit in units:
        unit_tokens = count_tokens(unit)
        if current and current_tokens + unit_tokens > chunk_tokens:
            chunks.append(" ".join(current))
            # Build overlap from the tail of the chunk we just emitted.
            overlap: list[str] = []
            ot = 0
            for u in reversed(current):
                ot += count_tokens(u)
                overlap.insert(0, u)
                if ot >= overlap_tokens:
                    break
            current = overlap
            current_tokens = sum(count_tokens(u) for u in current)
        current.append(unit)
        current_tokens += unit_tokens

    if current:
        chunks.append(" ".join(current))
    return chunks


def chunk_text(
    text: str,
    *,
    min_tokens: int = MIN_TOKENS,
    chunk_tokens: int = CHUNK_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
    long_doc_tokens: int = LONG_DOC_TOKENS,
) -> list[str]:
    """Split `text` into chunks following the planning.md routing strategy.

    - <= min_tokens         -> returned whole (one chunk)
    - > long_doc_tokens     -> split by section header, then recursively packed
    - otherwise (medium)    -> recursively packed at chunk_tokens with overlap
    """
    text = text.strip()
    if not text:
        return []

    if count_tokens(text) <= min_tokens:
        return [text]

    sections = _split_into_sections(text) if count_tokens(text) > long_doc_tokens else [text]

    chunks: list[str] = []
    for section in sections:
        chunks.extend(_pack(_units(section), chunk_tokens, overlap_tokens))
    return chunks


def build_chunks(folder: str | Path = DOCUMENTS_DIR) -> list[Document]:
    """Load all documents and chunk them, propagating metadata to each chunk."""
    chunked: list[Document] = []
    for doc in load_documents(folder):
        pieces = chunk_text(doc.text)
        for i, piece in enumerate(pieces):
            meta = dict(doc.metadata)
            meta["chunk_index"] = i
            meta["chunk_count"] = len(pieces)
            chunked.append(Document(text=piece, metadata=meta))
    return chunked


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {DOCUMENTS_DIR}\n")

    total = 0
    for doc in docs:
        pieces = chunk_text(doc.text)
        total += len(pieces)
        print(
            f"  {doc.metadata['filename']:<24} "
            f"{count_tokens(doc.text):>5} tokens -> {len(pieces):>2} chunk(s)  "
            f"[{doc.metadata['source']}]"
        )

    print(f"\nTotal chunks across corpus: {total}")
