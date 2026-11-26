# RAG Research Paper Assistant

A Retrieval-Augmented Generation (RAG) research assistant that retrieves information from research papers and answers questions using the content of those documents, with source references.

This project was developed as part of the **VK Internship – AI-3: RAG System (200 points)** task.

## Project Overview

The system retrieves relevant passages from research papers and uses Google's Gemini model to generate answers grounded in retrieved content, rather than relying solely on the model's pretrained knowledge.

The workflow includes:

- Downloading open-access research papers
- Extracting text from documents
- Splitting text into manageable, overlapping chunks
- Generating embeddings for document chunks
- Storing embeddings in Pinecone
- Retrieving relevant chunks for a user's question
- Generating grounded answers using Gemini
- Providing source references for retrieved content

## Technologies Used

- **Python** – Core development
- **Gemini API** – Answer generation
- **Pinecone** – Cloud vector database
- **ChromaDB** – Alternative local vector storage
- **Embeddings** – Semantic representation of document chunks
- **RAG** – Retrieval-Augmented Generation
- **PyMuPDF** – PDF text extraction

## Requirements

- Python 3.10 or later
- Pinecone API key
- Google AI Studio API key for Gemini

## Setup

### 1. Clone the repository

```powershell
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_NAME
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create your local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Add your API keys to `.env`:

```dotenv
PINECONE_API_KEY=your-pinecone-api-key
GEMINI_API_KEY=your-gemini-api-key
```

The `.env` file is excluded from Git. Never commit or share API keys. Use `.env.example` as the safe configuration template.

## RAG Pipeline

The main Pinecone-based workflow consists of the following stages:

1. **Document Download** – Collect open-access research papers.
2. **Text Extraction** – Extract readable text from downloaded documents.
3. **Chunking** – Split the extracted text into overlapping chunks to preserve contextual information.
4. **Embedding Generation** – Convert chunks into vector embeddings.
5. **Vector Indexing** – Store embeddings and metadata in Pinecone.
6. **Retrieval** – Retrieve relevant document chunks for a user's question.
7. **Generation** – Pass retrieved context and the question to Gemini.
8. **Source References** – Return an answer with source information from the retrieved documents.

## Running the Pinecone Workflow

Run the following scripts from the project directory in the listed order:

```powershell
python download_papers.py
python extract_text.py
python chunk_documents.py
python create_pinecone_index.py
python upload_embeddings.py
python rag_chat.py
```

The downloaded documents and associated metadata are stored under `documents/`. Extracted text, chunks, and local vector database files are generated locally and excluded from Git.

## RAG vs. Without RAG

A key objective of this project is to demonstrate how retrieval improves answers to questions that depend on a specific document collection.

### Without RAG

The question is sent directly to the language model without retrieving information from the ingested research papers.

### With RAG

The system retrieves relevant chunks from the ingested documents, includes them as context in the prompt, and generates an answer grounded in the retrieved content.

### Comparison Example

*Add an actual experiment from your ingested document collection here.*

| Test | Without RAG | With RAG |
|---|---|---|
| Document-specific question | Answer generated from the model's existing knowledge; may lack the document's specific details | Answer generated using retrieved passages from the ingested documents |
| Source grounding | No retrieved document evidence | Retrieved passages provide supporting context |
| Source references | No retrieval-based references | Sources can be identified from retrieved document metadata |

> The comparison should be demonstrated using an actual question, retrieved passages, and outputs from both runs. This table describes the intended difference in workflow, not measured results.

## Alternative Local Embedding Storage

The project also includes `create_embeddings.py`, an alternative workflow for storing chunk embeddings locally using ChromaDB.

This provides a local vector storage option without requiring a managed Pinecone index. The main question-answering workflow described above uses Pinecone.

## Project Structure

```text
RAG-Research-Paper-Assistant/
│
├── documents/                 # Downloaded research papers and metadata
├── download_papers.py         # Paper downloader
├── extract_text.py            # PDF text extraction
├── chunk_documents.py         # Text chunking
├── create_pinecone_index.py  # Pinecone index creation
├── upload_embeddings.py       # Embedding upload
├── create_embeddings.py       # Alternative local ChromaDB workflow
├── rag_chat.py               # Retrieval-based question answering
├── requirements.txt
├── .env.example
└── README.md
```

*The structure above is illustrative; adjust it to match the actual files in the repository.*

## Security and Data Handling

- API keys are stored locally in `.env`.
- `.env` must never be committed to GitHub.
- `.env.example` contains placeholder values only.
- Downloaded research papers remain local and are excluded from Git.
- Check the licensing and redistribution terms of each paper before sharing its content.

## Internship Task

**Platform:** VK Internship – `valentiuskryptix`

**Task:** AI-3 – RAG System

**Points:** 200

**Objective:** Build a RAG application that answers questions using a custom document collection, with meaningful retrieval, vector storage, and grounded generation.

## Learning Outcomes

- Understanding the Retrieval-Augmented Generation workflow
- Working with document ingestion and preprocessing
- Implementing chunking and embeddings
- Using a vector database
- Building context-grounded LLM prompts
- Testing retrieval quality and answer grounding
- Comparing LLM responses with and without retrieval

## Future Improvements

- Evaluate retrieval quality using relevant and irrelevant questions
- Improve chunk size and overlap strategies
- Add source citation validation
- Compare different embedding models
- Add a user-friendly interface
- Evaluate hallucination and grounding performance systematically

---

*Developed as part of the VK Internship AI-3 RAG System task.*
