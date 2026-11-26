
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load API key from .env
load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise ValueError("Pinecone API key not found in .env")

# Connect to Pinecone
pc = Pinecone(api_key=api_key)

INDEX_NAME = "rag-research-papers"

# Check whether the index already exists
existing_indexes = [index.name for index in pc.indexes.list()]

if INDEX_NAME in existing_indexes:
    print("Index already exists:", INDEX_NAME)

else:
    print("Creating Pinecone index...")

    pc.indexes.create(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        vector_type="dense",
        deployment={
            "deployment_type": "managed",
            "cloud": "aws",
            "region": "us-east-1"
        }
    )

    print("Index created successfully!")

# Verify index details
index_info = pc.indexes.describe(INDEX_NAME)

print("\nINDEX DETAILS")
print("Name:", index_info.name)
print("Status:", index_info.status.state)
print("Dimensions:", index_info.dimension)
