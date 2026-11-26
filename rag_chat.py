import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from google import genai

# --------------------------------------------------
# 1. Load API keys
# --------------------------------------------------

load_dotenv()

pinecone_key = os.getenv("PINECONE_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not pinecone_key:
    raise ValueError("Pinecone API key not found in .env!")

if not gemini_key:
    raise ValueError("Gemini API key not found in .env!")

# --------------------------------------------------
# 2. Connect to Pinecone
# --------------------------------------------------

pc = Pinecone(api_key=pinecone_key)
index = pc.Index("rag-research-papers")

# --------------------------------------------------
# 3. Load embedding model
# --------------------------------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------------------------------
# 4. Connect to Gemini
# --------------------------------------------------

gemini_client = genai.Client(api_key=gemini_key)

# --------------------------------------------------
# 5. RAG function
# --------------------------------------------------

def answer_question(question):

    # Convert question into an embedding
    query_embedding = embedding_model.encode(
        question
    ).tolist()

    # Retrieve the 5 most relevant chunks
    results = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True
    )

    if not results.matches:
        return "No relevant information was found.", []

    # Prepare retrieved context
    context_parts = []
    sources = []

    for i, match in enumerate(results.matches, start=1):

        metadata = match.metadata or {}

        text = metadata.get("text", "")
        source = metadata.get("source", "Unknown source")

        if not text:
            continue

        context_parts.append(
            f"[Source {i}: {source}]\n{text}"
        )

        if source not in sources:
            sources.append(source)

    if not context_parts:
        return "No readable information was retrieved.", []

    context = "\n\n".join(context_parts)

    # Prepare prompt for Gemini
    prompt = f"""
You are a research assistant.

Answer the user's question using ONLY the
information provided in the research paper excerpts below.

Instructions:
1. Give a clear and simple answer.
2. Do not invent facts or unsupported information.
3. If the provided information is insufficient,
   clearly say so.
4. Mention source labels such as [Source 1]
   when supporting your answer.

RESEARCH PAPER EXCERPTS:

{context}

USER QUESTION:
{question}

ANSWER:
"""

    # Generate answer using Gemini
    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text, sources


# --------------------------------------------------
# 6. Interactive question-answering
# --------------------------------------------------

print("\n==========================================")
print("   RAG RESEARCH PAPER ASSISTANT")
print("==========================================")

print("Ask questions about your 5 research papers.")
print("Type 'exit' to stop.")

while True:

    question = input("\nYour question: ").strip()

    if question.lower() == "exit":
        print("\nThank you for using the RAG assistant!")
        break

    if not question:
        print("Please enter a question.")
        continue

    try:
        answer, sources = answer_question(question)

        print("\nGENERATED ANSWER")
        print("=" * 60)
        print(answer)

        print("\nRETRIEVED SOURCES")
        print("=" * 60)

        for source in sources:
            print("-", source)

        print("=" * 60)

    except Exception as error:
        print("\nError:", error)
