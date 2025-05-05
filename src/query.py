from langchain_ollama import OllamaLLM
from .vector import get_vector_client, get_embedding_function
from src.constants import LLM_MODEL, COLLECTION_NAME, CONTEXT_N


def query_rag(question, collection):
    results = collection.query(query_texts=[question], n_results=CONTEXT_N)
    retrieved = results["documents"][0] if results["documents"] else []
    context = "\n".join(retrieved) if retrieved else "No relevant context found."

    prompt = f"""Use only the context below to answer the question.

    - If the answer is explicitly present, state it directly.
    - If the answer requires combining multiple ideas, respond with a concise summary.
    - If the context lacks enough information to make a reasonable inference, respond with “I don’t know.”

    Context:
    {context}

    Question: {question}
    Answer:"""
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
