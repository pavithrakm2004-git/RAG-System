# RAG Research Paper Assistant

A command-line research assistant that downloads open-access papers, extracts and chunks their text, stores embeddings in Pinecone, and uses Gemini to answer questions with source references.

## Requirements

- Python 3.10 or later
- A [Pinecone](https://www.pinecone.io/) API key
- A [Google AI Studio](https://aistudio.google.com/) API key for Gemini

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Add your own keys to `.env`:

```dotenv
PINECONE_API_KEY=your-pinecone-api-key
GEMINI_API_KEY=your-gemini-api-key
```

`.env` is ignored by Git. Never commit or share it; use `.env.example` as the safe template.

## Run the Pinecone workflow

Run these scripts from the project directory, in order:

```powershell
python download_papers.py
python extract_text.py
python chunk_documents.py
python create_pinecone_index.py
python upload_embeddings.py
python rag_chat.py
```

The paper downloader stores its files and metadata under `documents/`. Extracted text, chunks, and local ChromaDB data are generated locally and are excluded from Git. Check the source and license terms for each paper before redistributing it.

`create_embeddings.py` is an alternative script that stores chunk embeddings in a local ChromaDB database. The question-answering script in this project uses Pinecone.
