import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("PLC_RAG_DATA", ROOT / "data"))
DOCS_DIR = Path(os.getenv("PLC_DOCS_DIR", ROOT / "Docs_Export"))
CHUNKS_FILE = DATA_DIR / "chunks.jsonl"
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION = "plc_st_docs"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("PLC_CHAT_MODEL", "qwen2.5-coder:7b")
EMBED_MODEL = os.getenv("PLC_EMBED_MODEL", "nomic-embed-text")

# Total context window handed to Ollama; the prompt builder fits everything inside it.
NUM_CTX = int(os.getenv("PLC_NUM_CTX", "4096"))
MAX_NEW_TOKENS = int(os.getenv("PLC_MAX_NEW_TOKENS", "768"))
TOP_K = int(os.getenv("PLC_TOP_K", "4"))
