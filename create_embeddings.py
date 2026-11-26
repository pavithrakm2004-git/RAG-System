
import csv
import chromadb
from sentence_transformers import SentenceTransformer

# Paths
CHUNKS_FILE = "chunks/all_chunks.csv"
DB_FOLDER = "chroma_db"

# Load embedding model
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded!")

# Read chunks from CSV
documents = []
ids = []
metadatas = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        documents.append(row["text"])
        ids.append(row["chunk_id"])

        metadatas.append({
            "source": row["source"],
            "chunk_number": int(row["chunk_number"]),
            "word_count": int(row["word_count"])
        })

print(f"Total chunks loaded: {len(documents)}")

# Create persistent ChromaDB database
client = chromadb.PersistentClient(path=DB_FOLDER)

# Create collection
collection = client.get_or_create_collection(
    name="research_papers"
)

# Generate embeddings and store chunks
print("\nGenerating embeddings and storing in ChromaDB...")

batch_size = 32

for start in range(0, len(documents), batch_size):
    end = start + batch_size

    batch_documents = documents[start:end]
    batch_ids = ids[start:end]
    batch_metadatas = metadatas[start:end]

    embeddings = model.encode(
        batch_documents,
        convert_to_numpy=True
    ).tolist()

    collection.upsert(
        ids=batch_ids,
        documents=batch_documents,
        embeddings=embeddings,
        metadatas=batch_metadatas
    )

    print(f"Processed {min(end, len(documents))}/{len(documents)} chunks")

print("\n" + "=" * 55)
print("EMBEDDING AND STORAGE COMPLETED")
print("=" * 55)

print("Total chunks stored:", collection.count())
print("Database location:", DB_FOLDER)
