import os
import csv
import time

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

# --------------------------------------------------
# 1. Load API key
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise ValueError("Pinecone API key not found in .env file")

# --------------------------------------------------
# 2. Connect to Pinecone
# --------------------------------------------------

INDEX_NAME = "rag-research-papers"

pc = Pinecone(api_key=api_key)
index = pc.Index(INDEX_NAME)

print("Connected to Pinecone!")

# --------------------------------------------------
# 3. Load embedding model
# --------------------------------------------------

print("\nLoading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded!")

# --------------------------------------------------
# 4. Read document chunks
# --------------------------------------------------

CHUNKS_FILE = "chunks/all_chunks.csv"

records = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    records = list(reader)

print(f"\nTotal chunks loaded: {len(records)}")

# --------------------------------------------------
# 5. Generate embeddings and upload
# --------------------------------------------------

BATCH_SIZE = 10

print("\nGenerating embeddings and uploading to Pinecone...")

for start in range(0, len(records), BATCH_SIZE):

    batch = records[start:start + BATCH_SIZE]

    texts = [row["text"] for row in batch]

    # Generate 384-dimensional embeddings
    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    vectors = []

    for row, embedding in zip(batch, embeddings):

        vectors.append({
            "id": row["chunk_id"],
            "values": embedding.tolist(),
            "metadata": {
                "text": row["text"],
                "source": row["source"],
                "chunk_number": int(row["chunk_number"]),
                "word_count": int(row["word_count"])
            }
        })

    # Upload batch
    index.upsert(vectors=vectors)

    uploaded = min(start + len(batch), len(records))

    print(f"Uploaded {uploaded}/{len(records)} chunks")

# --------------------------------------------------
# 6. Verify upload
# --------------------------------------------------

print("\nWaiting for Pinecone to update...")

time.sleep(5)

stats = index.describe_index_stats()

print("\n" + "=" * 55)
print("PINECONE UPLOAD COMPLETED")
print("=" * 55)

print("Index name:", INDEX_NAME)
print("Total vectors stored:", stats.total_vector_count)
print("Index dimensions:", stats.dimension)
