import os
import json
import re
import chromadb
from langchain_ollama import OllamaEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
from src.constants import (
    LOG_DIR,
    CHROMA_DIR,
    MEMORY_PATH,
    EMBEDDING_MODEL,
    COLLECTION_NAME,
)


# Chroma Helpers
class ChromaDBEmbeddingFunction:
    def __init__(self, langchain_embeddings):
        self.langchain_embeddings = langchain_embeddings

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        return self.langchain_embeddings.embed_documents(input)


def get_embedding_function():
    return ChromaDBEmbeddingFunction(
        OllamaEmbeddings(model=EMBEDDING_MODEL, base_url="http://localhost:11434")
    )


def get_vector_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


# Memory Config Helpers
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


def semantic_chunk_log_text(text, buffer_size=1, percentile_threshold=95):
    """
    Semantic chunking logic adapted from Greg Kamradt's work:
    https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/5_Levels_Of_Text_Splitting.ipynb
    """

    sentences = [
        s.strip() for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()
    ]
    if len(sentences) <= 2:
        return [text]

    # Combine with buffer in one pass
    combined_sentences = []
    for i in range(len(sentences)):
        start = max(0, i - buffer_size)
        end = min(len(sentences), i + buffer_size + 1)
        combined = " ".join(sentences[start:end])
        combined_sentences.append(combined)

    # Embed combined chunks
    embed_fn = get_embedding_function()
    embeddings = embed_fn(combined_sentences)

    # Compute distances
    distances = [
        1 - cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
        for i in range(len(embeddings) - 1)
    ]
    if not distances:
        return [text]

    # Threshold and breakpoints
    threshold = np.percentile(distances, percentile_threshold)
    breakpoints = [i for i, d in enumerate(distances) if d > threshold]

    # Form chunks
    chunks = []
    start_idx = 0
    for idx in breakpoints:
        end_idx = idx + 1
        chunk = " ".join(sentences[start_idx:end_idx])
        if chunk:
            chunks.append(chunk)
        start_idx = end_idx
    if start_idx < len(sentences):
        final_chunk = " ".join(sentences[start_idx:])
        if final_chunk:
            chunks.append(final_chunk)

    return chunks


def update_vector_db(reinitialized=False):
    memory = read_memory()
    last_n = 0 if reinitialized else int(memory.get("LAST_LOG", 0))
    files_to_update = get_unsynced_logs(last_n)

    if not files_to_update:
        print("No new logs to sync.")
        return

    chroma_client = get_vector_client()
    if reinitialized:
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
            print("Old collection deleted.")
        except:
            pass

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=get_embedding_function()
    )

    for file in files_to_update:
        path = os.path.join(LOG_DIR, file)
        with open(path, "r") as f:
            logs = json.load(f)

        combined_text = " ".join(log["text"] for log in logs)

        chunks = semantic_chunk_log_text(combined_text, buffer_size=3)

        for j, chunk in enumerate(chunks):
            doc_id = f"{file}-{j}"
            collection.add(
                documents=[chunk], ids=[doc_id], metadatas=[{"source": file}]
            )

        print(f"Added {file} to Vector Database.")

    latest_n = max(int(re.findall(r"log-(\d+)", f)[0]) for f in files_to_update)
    memory["LAST_LOG"] = str(latest_n)
    write_memory(memory)
    print(f"Updated memory: LAST_LOG={latest_n}")
