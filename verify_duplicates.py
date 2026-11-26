
import csv
import re
import hashlib
from pathlib import Path
from collections import defaultdict

# Your existing document folder
FOLDER = Path(
    r"C:\Users\User\OneDrive\Desktop\VK\RAG_Document_Chatbot\documents"
)

CSV_FILE = FOLDER / "paper_metadata.csv"


def normalize_title(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def check_duplicates():

    if not CSV_FILE.exists():
        print("ERROR: paper_metadata.csv not found.")
        return

    with open(CSV_FILE, "r", encoding="utf-8-sig") as file:
        papers = list(csv.DictReader(file))

    print("=" * 60)
    print("RESEARCH PAPER DUPLICATE VERIFICATION")
    print("=" * 60)

    print(f"\nTotal metadata records: {len(papers)}")

    checks = {
        "DOI": defaultdict(list),
        "Title": defaultdict(list),
        "PDF file hash": defaultdict(list)
    }

    for paper in papers:

        title = paper.get("title", "").strip()
        doi = paper.get("doi", "").strip().lower()
        filename = paper.get("filename", "").strip()

        if title:
            checks["Title"][normalize_title(title)].append(title)

        if doi:
            checks["DOI"][doi].append(title)

        pdf_path = FOLDER / filename

        if pdf_path.exists():
            file_hash = calculate_hash(pdf_path)
            checks["PDF file hash"][file_hash].append(filename)
        else:
            print(f"\nWARNING: Missing PDF: {filename}")

    duplicates_found = False

    for check_name, records in checks.items():

        print(f"\n--- {check_name} check ---")

        found = False

        for key, values in records.items():

            if len(values) > 1:

                found = True
                duplicates_found = True

                print("\nDUPLICATE FOUND:")

                for value in values:
                    print(" -", value)

        if not found:
            print("No duplicates found.")

    print("\n" + "=" * 60)

    if duplicates_found:
        print("RESULT: Potential duplicates detected.")
        print("Review the records before removing anything.")
    else:
        print("RESULT: No duplicates detected.")

    print("=" * 60)


if __name__ == "__main__":
    check_duplicates()
