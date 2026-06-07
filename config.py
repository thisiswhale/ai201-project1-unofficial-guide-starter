import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM (Groq, per planning.md Generation stage) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

# --- Embeddings (sentence-transformers, per Retrieval Approach) ---
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

# --- Vector store ---
CHROMA_COLLECTION = "coffee_guide"
CHROMA_PATH = "./chroma_db"

# --- Retrieval (top-k, per Retrieval Approach) ---
N_RESULTS = 5

# --- Documents ---
DOCS_PATH = "./documents"

# --- Chunking (per Chunking Strategy) ---
CHUNK_SIZE = 400        # target tokens per chunk
CHUNK_OVERLAP = 30      # token overlap between consecutive chunks
MIN_CHUNK_TOKENS = 120  # docs at or below this are kept whole
LONG_DOC_TOKENS = 600   # docs above this are split by section header first
