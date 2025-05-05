import os

DATA_DIR = "data"
LOG_DIR = os.path.join(DATA_DIR, "logs")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")
MEMORY_PATH = os.path.join(DATA_DIR, "memory")

LLM_MODEL = "gemma3:1b"
EMBEDDING_MODEL = "nomic-embed-text"
COLLECTION_NAME = "eros-logs"

CONTEXT_N = 5
