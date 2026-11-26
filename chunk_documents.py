
from pathlib import Path
import csv

INPUT_FOLDER = Path("extracted_text")
OUTPUT_FOLDER = Path("chunks")

OUTPUT_FOLDER.mkdir(exist_ok=True)

CHUNK_SIZE = 400
CHUNK_OVERLAP = 80

all_chunks = []

def create_chunks(text, chunk_size, overlap):
    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        if chunk_text.strip():
            chunks.append(chunk_text)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


print("=" * 55)
print("DOCUMENT CHUNKING")
print("=" * 55)

text_files = list(INPUT_FOLDER.glob("*.txt"))

for file_path in text_files:

    text = file_path.read_text(encoding="utf-8")

    chunks = create_chunks(
        text,
        CHUNK_SIZE,
        CHUNK_OVERLAP
    )

    print(f"\nPaper: {file_path.name}")
    print(f"Total words: {len(text.split())}")
    print(f"Chunks created: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        all_chunks.append({
            "chunk_id": f"{file_path.stem}_chunk_{index}",
            "source": file_path.name,
            "chunk_number": index,
            "word_count": len(chunk.split()),
            "text": chunk
        })


# Save all chunks into one CSV file
output_file = OUTPUT_FOLDER / "all_chunks.csv"

with open(output_file, "w", encoding="utf-8", newline="") as file:
    fieldnames = [
        "chunk_id",
        "source",
        "chunk_number",
        "word_count",
        "text"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_chunks)


print("\n" + "=" * 55)
print("CHUNKING COMPLETED")
print("=" * 55)

print(f"Total papers processed: {len(text_files)}")
print(f"Total chunks created: {len(all_chunks)}")
print(f"Saved to: {output_file}")
