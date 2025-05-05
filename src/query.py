import readline  # for better input UX
from .vector import get_vector_client, get_embedding_function
from langchain_ollama import OllamaLLM

LLM_MODEL = "llama3.2"
COLLECTION_NAME = "eros-logs"


def query_rag(question, collection):
    results = collection.query(query_texts=[question], n_results=3)
    retrieved = results["documents"][0] if results["documents"] else []
    context = "\n".join(retrieved) if retrieved else "No relevant context found."

    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    llm = OllamaLLM(model=LLM_MODEL)
    return llm.invoke(prompt)


def query_cli(question):
    chroma_client = get_vector_client()
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=get_embedding_function()
    )
    response = query_rag(question, collection)
    print(f"\n→ {response}\n")


def query_continuous():
    print("Enter a question (Ctrl+D to exit):")
    chroma_client = get_vector_client()
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=get_embedding_function()
    )
    try:
        while True:
            question = input("\n> ")
            response = query_rag(question, collection)
            print(f"\n→ {response}")
    except EOFError:
        print("\nSession ended.")
