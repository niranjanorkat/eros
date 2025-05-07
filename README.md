# Eros
Eros is a private, local AI memory to help you remember the little things about the people you care about.

It combines a Retrieval-Augmented Generation (RAG) system with an LLM, powered by Ollama, LangChain, and Chroma.

Shoutout to Greg Kamradt for the semantic chunking approach, adapted from his work:
https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb

## Backstory  
I can be a forgetful person — especially when it comes to the small but important details about people I'm dating. So I built Eros: a personal memory system to help me log what they say, what they like, and what I should probably remember.

The idea had been floating around for a while, but it all came together after I read [Geoffrey Litt’s post](https://www.geoffreylitt.com/2025/04/12/how-i-made-a-useful-ai-assistant-with-one-sqlite-table-and-a-handful-of-cron-jobs). That gave me the push to actually build it.

## How It Works
1. First, the logged text is converted into an embedding database using Chroma.  
2. Whenever a query is made, the system retrieves the top N chunks that are closest in meaning to the query.  
3. These N chunks are supplied to the LLM, along with the query, to generate a contextual answer.

At first, I tried normal chunking with a max token threshold, then single-sentence chunking. But neither gave accurate enough results, mostly because they didn’t take context into account.  

With fixed-length chunking, the problem is that each chunk might contain unrelated content. Since logs are often short, multiple different ideas can end up in the same chunk.  
Sentence chunking wasn’t great either — sometimes the relevant context spans two or three sentences, and splitting them apart weakened the retrieval.

While exploring alternatives, I came across Greg Kamradt’s notebook on chunking strategies. The semantic chunking section stood out:

1. Sentences are first split from the logged text.  
2. A buffer window (e.g., `BUFFER_SIZE` sentences before and after) is applied to each sentence to provide local context.  
3. Each buffered group is embedded into a vector using the embedding function.  
4. Cosine distances are computed between each pair of adjacent embeddings.  
5. A threshold (e.g., 95th percentile of distances) is used to detect significant shifts in meaning.  
6. Breakpoints are inserted where the distance exceeds this threshold.  
7. Final chunks are formed by splitting the original text at these breakpoints, resulting in semantically coherent segments.
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







