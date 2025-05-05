import os
import json
import re
import chromadb
from langchain_ollama import OllamaEmbeddings

# === Constants ===
DATA_DIR = "data"
LOG_DIR = os.path.join(DATA_DIR, "logs")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")
MEMORY_PATH = os.path.join(DATA_DIR, "memory")
LLM_MODEL = "llama3.2"
COLLECTION_NAME = "eros-logs"


# === Embedding Wrapper ===
class ChromaDBEmbeddingFunction:
    def __init__(self, langchain_embeddings):
        self.langchain_embeddings = langchain_embeddings

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        return self.langchain_embeddings.embed_documents(input)


# === Helpers ===
def get_embedding_function():
    return ChromaDBEmbeddingFunction(
        OllamaEmbeddings(model=LLM_MODEL, base_url="http://localhost:11434")
    )


def get_vector_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def read_memory():
    mem = {}
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    mem[key] = val
    return mem


def write_memory(mem):
    with open(MEMORY_PATH, "w") as f:
        for key, val in mem.items():
            f.write(f"{key}={val}\n")


def get_unsynced_logs(last_n):
    files = sorted(
        [f for f in os.listdir(LOG_DIR) if re.match(r"log-(\d+)\.json", f)],
        key=lambda x: int(re.findall(r"log-(\d+)", x)[0]),
    )
    return [f for f in files if int(re.findall(r"log-(\d+)", f)[0]) > last_n]


# === Main Sync Function ===
def update_vector_db():
    memory = read_memory()
    last_n = int(memory["LAST_LOG"]) if "LAST_LOG" in memory else 1
    files_to_update = get_unsynced_logs(last_n)

    if not files_to_update:
        print("No new logs to sync.")
        return

    chroma_client = get_vector_client()
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=get_embedding_function()
    )

    for file in files_to_update:
        path = os.path.join(LOG_DIR, file)
        with open(path, "r") as f:
            logs = json.load(f)

        for i, log in enumerate(logs):
            doc_id = f"{file}-{i}"
            text = log["text"]
            collection.add(documents=[text], ids=[doc_id], metadatas=[{"source": file}])

        print(f"Pushed {file} to Chroma.")

    latest_n = max(int(re.findall(r"log-(\d+)", f)[0]) for f in files_to_update)
    memory["LAST_LOG"] = str(latest_n)
    write_memory(memory)
    print(f"Updated memory: LAST_LOG={latest_n}")
