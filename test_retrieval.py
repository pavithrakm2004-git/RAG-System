import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

load_dotenv()

# Connect to Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("rag-research-papers")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Ask a question
query = "What is Retrieval-Augmented Generation and how does it work?"

# Convert question into embedding
query_embedding = model.encode(query).tolist()

# Search Pinecone
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)

# Display retrieved chunks
print("\nQUESTION:", query)
print("\nRETRIEVED DOCUMENT CHUNKS")
print("=" * 60)

for i, match in enumerate(results.matches, start=1):
    print(f"\nResult {i}")
    print("Source:", match.metadata.get("source"))
    print("Similarity score:", match.score)
    print("Text:", match.metadata.get("text")[:500])
    print("-" * 60)
