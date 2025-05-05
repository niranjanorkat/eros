import os
from fpdf import FPDF
from langchain_ollama import OllamaLLM
from .vector import get_vector_client, get_embedding_function

LLM_MODEL = "llama3.2"
COLLECTION_NAME = "eros-logs"


def generate_profile_summary():
    chroma = get_vector_client()
    collection = chroma.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=get_embedding_function()
    )

    results = collection.query(query_texts=["profile summary"], n_results=10)
    context = "\n".join(results["documents"][0]) if results["documents"] else ""

    prompt = (
        f"Context:\n{context}\n\n"
        "Based on these logs, generate a one-paragraph, heartfelt profile summary about her. "
        "Include favorite things, emotional traits, and meaningful cues."
    )

    llm = OllamaLLM(model=LLM_MODEL)
    return llm.invoke(prompt)


def export_profile_to_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)
    print(f"✅ Exported to {filename}")
