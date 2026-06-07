"""The Unofficial Guide — coffee RAG application entry point.

Run the whole thing:
    python3 app.py

On startup it ingests the documents/ corpus into Chroma (skipped if already
populated), then launches a Gradio chat UI whose answers are grounded only in
the retrieved sources.
"""

import gradio as gr

from ingest import build_chunks, load_documents
from embedding import embed_and_store, get_collection
from generator import answer_markdown


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup
# ---------------------------------------------------------------------------
def run_ingestion():
    """Load + chunk the coffee documents and store them in ChromaDB.

    If the vector store is already populated, ingestion is skipped. To re-ingest
    (e.g. after changing your chunking strategy), delete the ./chroma_db folder
    and restart the app.
    """
    collection = get_collection()

    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). Skipping ingestion.")
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    print("Ingesting coffee documents...")
    chunks = build_chunks()

    if chunks:
        embed_and_store(chunks)
        print(f"Ingestion complete. {len(chunks)} chunks stored.")
    else:
        print(
            "\n⚠️  No chunks produced. Make sure documents/ contains .txt files.\n"
            "    The guide will start, but won't be able to answer questions yet.\n"
        )


def loaded_sources() -> list[str]:
    """Distinct 'Origin — Source' labels for the documents currently loaded."""
    seen: list[str] = []
    for doc in load_documents():
        label = f"{doc.metadata.get('origin')} — {doc.metadata.get('source')}"
        if label not in seen:
            seen.append(label)
    return seen


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------
def chat(message, history):
    if not message.strip():
        return ""
    return answer_markdown(message)


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
_sources_html = "\n".join(
    f'<li style="color:#000000 !important;">☕ {label}</li>' for label in loaded_sources()
)

with gr.Blocks(title="The Unofficial Guide — Coffee") as demo:

    gr.HTML("""
        <div style="text-align:center; padding:1.25rem 0 0.5rem;">
            <h1 style="font-size:2rem; font-weight:700; color:#5b3a1a; margin:0;">
                ☕ The Unofficial Guide
            </h1>
            <p style="color:#6b7280; font-size:1rem; margin:0.4rem 0 0;">
                Ask about regional coffee flavor profiles — answers straight from the sources.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat,
                chatbot=gr.Chatbot(
                    height=460,
                    placeholder=(
                        "<div style='text-align:center; color:#9ca3af; margin-top:3rem;'>"
                        "Ask a coffee question to get started 🌱"
                        "</div>"
                    ),
                ),
                textbox=gr.Textbox(
                    placeholder='e.g. "What flavor profile does Ugandan coffee have?"',
                    container=False,
                    scale=7,
                ),
                examples=[
                    "What flavor profile does Ugandan coffee have?",
                    "What are the key flavor differences between Arabica and Robusta coffee?",
                    "What does Colombian coffee taste like and what makes it unique?",
                    "What is Kona Coffee?",
                    "What makes Ethiopian Yirgacheffe coffee unique compared to other Ethiopian coffees?",
                ],
                cache_examples=False,
            )

        with gr.Column(scale=1, min_width=200):
            gr.HTML(f"""
                <div style="background:#faf5ef !important; border:1px solid #e7d8c4;
                            border-radius:10px; padding:1rem; margin-top:0.5rem; color:#000000 !important;">
                    <p style="font-size:0.8rem; font-weight:700; color:#000000 !important;
                               margin:0 0 0.5rem; letter-spacing:0.05em;">
                        📚 RETRIEVED FROM
                    </p>
                    <ul style="font-size:0.85rem; color:#000000 !important; list-style:none;
                                padding:0; margin:0; line-height:1.7;">
                        {_sources_html}
                    </ul>
                    <hr style="border:none; border-top:1px solid #e7d8c4; margin:0.75rem 0;">
                    <p style="font-size:0.75rem; color:#000000 !important; margin:0; line-height:1.5;">
                        Answers are grounded in the loaded sources only. If the corpus
                        doesn't cover it, the guide will say so.
                    </p>
                </div>
            """)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  The Unofficial Guide — starting up")
    print("=" * 50 + "\n")
    run_ingestion()
    demo.launch(theme=gr.themes.Soft(primary_hue="amber"))
