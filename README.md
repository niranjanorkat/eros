# Eros
Eros is a private, local AI memory to help you remember the little things about the people you care about.

It combines a Retrieval-Augmented Generation (RAG) system with an LLM, powered by Ollama, LangChain, and Chroma.

## Backstory  
I can be a forgetful person — especially when it comes to the small but important details about people I'm dating. So I built Eros: a personal memory system to help me log what they say, what they like, and what I should probably remember.

The idea had been floating around for a while, but it all came together after I read [Geoffrey Litt’s post](https://www.geoffreylitt.com/2025/04/12/how-i-made-a-useful-ai-assistant-with-one-sqlite-table-and-a-handful-of-cron-jobs). That gave me the push to actually build it.

## Installation  
1. Install [Ollama](https://github.com/ollama/ollama)  
2. `pip install -r requirements.txt`  
3. Run with `python eros.py <command>

## Usage  
- `python eros.py add "<text>"` — log something quickly  
- `python eros.py add --continuous` — multiline journaling (e.g. while you're in a call)  
- `python eros.py update` — embed new logs into the vector database  
- `python eros.py update --init` — reset and re-embed everything from scratch  
- `python eros.py query "<question>"` — ask something you've logged  
- `python eros.py query --continuous` — interactive chat mode  
- `python eros.py profile` — generate a one-paragraph summary  
- `python eros.py profile --export filename.pdf` — export the summary as a PDF  







