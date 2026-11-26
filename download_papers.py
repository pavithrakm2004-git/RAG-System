
import csv
import hashlib
import re
import time
import requests

from pathlib import Path
from urllib.parse import unquote


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"

METADATA_FILE = DOCUMENTS_DIR / "paper_metadata.csv"
REPORT_FILE = DOCUMENTS_DIR / "download_report.txt"

OPENALEX_API = "https://api.openalex.org/works"

# Keep existing five papers and aim for 12 papers in total.
TARGET_TOTAL_PAPERS = 12

# Search up to 50 results for each topic.
MAX_RESULTS_PER_QUERY = 50

MIN_PUBLICATION_YEAR = 2020

HEADERS = {
    "User-Agent": "RAG-Research-Assistant/1.0"
}


# ============================================================
# RESEARCH TOPICS
# ============================================================

SEARCH_TOPICS = [
    "retrieval augmented generation large language models",

    "RAG systems architecture retrieval generation",

    "text embeddings sentence transformers semantic search",

    "dense passage retrieval neural information retrieval",

    "vector databases similarity search document retrieval",

    "hallucination reduction factuality large language models",

    "evaluation metrics retrieval augmented generation",

    "document chunking text splitting retrieval",

    "prompt engineering large language models"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_title(title):

    title = (title or "").lower()

    title = re.sub(r"[^a-z0-9]", "", title)

    return title


def normalize_doi(doi):

    doi = (doi or "").strip().lower()

    doi = doi.replace("https://doi.org/", "")
    doi = doi.replace("http://doi.org/", "")
    doi = doi.replace("https://dx.doi.org/", "")

    return doi.strip()


def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def clean_filename(title):

    title = re.sub(r'[<>:"/\\|?*]', "", title)

    title = re.sub(r"\s+", "_", title.strip())

    return title[:100]


def get_authors(work):

    authors = []

    for authorship in work.get("authorships", []):

        author = authorship.get("author", {})

        name = author.get("display_name")

        if name:
            authors.append(name)

    return "; ".join(authors)


def get_openalex_id(work):

    return work.get("id", "")


# ============================================================
# LOAD EXISTING METADATA
# ============================================================

def load_existing_metadata():

    if not METADATA_FILE.exists():

        existing_pdfs = list(DOCUMENTS_DIR.glob("*.pdf"))

        if existing_pdfs:

            raise RuntimeError(
                "PDF files already exist, but paper_metadata.csv "
                "is missing. Stopping to protect existing files."
            )

        return []

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


# ============================================================
# BUILD DUPLICATE DATABASE
# ============================================================

def build_existing_records(metadata):

    existing_ids = set()
    existing_dois = set()
    existing_titles = set()
    existing_hashes = set()

    for record in metadata:

        openalex_id = record.get("openalex_id", "").strip()

        doi = normalize_doi(record.get("doi", ""))

        title = normalize_title(record.get("title", ""))

        if openalex_id:
            existing_ids.add(openalex_id)

        if doi:
            existing_dois.add(doi)

        if title:
            existing_titles.add(title)

    # Also inspect all existing PDFs.
    for pdf_file in DOCUMENTS_DIR.glob("*.pdf"):

        try:

            file_hash = calculate_sha256(pdf_file)

            existing_hashes.add(file_hash)

        except Exception as error:

            print(f"Could not hash {pdf_file.name}: {error}")

    return (
        existing_ids,
        existing_dois,
        existing_titles,
        existing_hashes
    )


# ============================================================
# BACKFILL OLD OPENALEX IDS
# ============================================================

def recover_old_openalex_ids(metadata):

    print("\nChecking OpenAlex IDs for existing records...")

    for record in metadata:

        if record.get("openalex_id", "").strip():
            continue

        title = record.get("title", "").strip()

        doi = normalize_doi(record.get("doi", ""))

        if not title:
            continue

        try:

            response = requests.get(
                OPENALEX_API,
                params={
                    "search": title,
                    "per-page": 5
                },
                headers=HEADERS,
                timeout=30
            )

            response.raise_for_status()

            results = response.json().get("results", [])

            for work in results:

                api_title = (
                    work.get("title")
                    or work.get("display_name")
                    or ""
                )

                api_doi = normalize_doi(work.get("doi", ""))

                exact_title_match = (
                    normalize_title(api_title)
                    == normalize_title(title)
                )

                doi_match = (
                    doi and api_doi and doi == api_doi
                )

                if exact_title_match or doi_match:

                    record["openalex_id"] = get_openalex_id(work)

                    break

            time.sleep(0.2)

        except Exception as error:

            print(
                f"Could not recover OpenAlex ID for "
                f"{title[:60]}: {error}"
            )

    print("Existing record ID check completed.")


# ============================================================
# GET PDF URLS
# ============================================================

def get_pdf_urls(work):

    urls = []

    best_location = work.get("best_oa_location") or {}

    best_pdf = best_location.get("pdf_url")

    if best_pdf:
        urls.append(best_pdf)

    for location in work.get("locations", []):

        if not location:
            continue

        if location.get("is_oa") is False:
            continue

        pdf_url = location.get("pdf_url")

        if pdf_url and pdf_url not in urls:
            urls.append(pdf_url)

    return urls


# ============================================================
# SEARCH OPENALEX
# ============================================================

def search_openalex(topic):

    print(f"\nSearching: {topic}")

    params = {
        "search": topic,
        "filter": (
            f"type:article,is_oa:true,"
            f"from_publication_date:{MIN_PUBLICATION_YEAR}-01-01"
        ),
        "per-page": MAX_RESULTS_PER_QUERY
    }

    try:

        response = requests.get(
            OPENALEX_API,
            params=params,
            headers=HEADERS,
            timeout=40
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        print(f"Found {len(results)} research records.")

        return results

    except requests.RequestException as error:

        print(f"OpenAlex search failed: {error}")

        return []


# ============================================================
# DOWNLOAD PDF SAFELY
# ============================================================

def download_pdf(url, destination):

    temporary_file = destination.with_suffix(".download")

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=(20, 90),
            stream=True
        )

        response.raise_for_status()

        file_hash = hashlib.sha256()

        first_bytes = b""

        with open(temporary_file, "wb") as file:

            for chunk in response.iter_content(chunk_size=1024 * 64):

                if not chunk:
                    continue

                if len(first_bytes) < 1024:
                    first_bytes += chunk[:1024 - len(first_bytes)]

                file.write(chunk)

                file_hash.update(chunk)

        # Check whether the downloaded file is actually a PDF.
        if b"%PDF-" not in first_bytes:

            temporary_file.unlink(missing_ok=True)

            print("Skipped: URL did not return a valid PDF.")

            return None, None

        file_hash_value = file_hash.hexdigest()

        file_size = temporary_file.stat().st_size

        # Never overwrite an existing file.
        if destination.exists():

            temporary_file.unlink(missing_ok=True)

            print("Skipped: destination already exists.")

            return None, None

        # Move the verified download into its final location.
        temporary_file.replace(destination)

        return file_hash_value, file_size

    except Exception as error:

        temporary_file.unlink(missing_ok=True)

        print(f"PDF download failed: {error}")

        return None, None


# ============================================================
# SAVE METADATA SAFELY
# ============================================================

def save_metadata(metadata):

    new_columns = [
        "openalex_id",
        "cited_by_count",
        "license"
    ]

    fieldnames = list(metadata[0].keys()) if metadata else []

    for column in new_columns:

        if column not in fieldnames:
            fieldnames.append(column)

    temporary_file = METADATA_FILE.with_suffix(".tmp")

    with open(
        temporary_file,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()

        writer.writerows(metadata)

    # Replace metadata only after the temporary CSV is complete.
    temporary_file.replace(METADATA_FILE)


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("RAG RESEARCH PAPER COLLECTION")
    print("=" * 65)

    # Load existing records.
    metadata = load_existing_metadata()

    print(f"\nExisting metadata records: {len(metadata)}")

    # Recover OpenAlex IDs for older records where possible.
    recover_old_openalex_ids(metadata)

    (
        existing_ids,
        existing_dois,
        existing_titles,
        existing_hashes
    ) = build_existing_records(metadata)

    # Include recovered IDs in the duplicate database.
    for record in metadata:

        openalex_id = record.get("openalex_id", "").strip()

        if openalex_id:
            existing_ids.add(openalex_id)

    downloaded_count = 0
    skipped_count = 0

    # Existing metadata records plus new downloads.
    current_total = len(metadata)

    print(f"Target total papers: {TARGET_TOTAL_PAPERS}")

    if current_total >= TARGET_TOTAL_PAPERS:

        print("\nTarget already reached. No new downloads required.")

    else:

        # Search each research topic.
        for topic in SEARCH_TOPICS:

            if current_total >= TARGET_TOTAL_PAPERS:
                break

            results = search_openalex(topic)

            for work in results:

                if current_total >= TARGET_TOTAL_PAPERS:
                    break

                title = (
                    work.get("title")
                    or work.get("display_name")
                    or ""
                )

                if not title:
                    skipped_count += 1
                    continue

                openalex_id = get_openalex_id(work)

                doi = normalize_doi(work.get("doi", ""))

                normalized_title = normalize_title(title)

                # Check duplicate OpenAlex ID.
                if openalex_id in existing_ids:

                    skipped_count += 1
                    continue

                # Check duplicate DOI.
                if doi and doi in existing_dois:

                    skipped_count += 1
                    continue

                # Check duplicate title.
                if normalized_title in existing_titles:

                    skipped_count += 1
                    continue

                # Only consider papers with an accessible PDF URL.
                pdf_urls = get_pdf_urls(work)

                if not pdf_urls:

                    skipped_count += 1
                    continue

                authors = get_authors(work)

                year = work.get("publication_year", "")

                cited_by_count = work.get("cited_by_count", 0)

                # Find the available license information.
                best_location = work.get("best_oa_location") or {}

                license_name = best_location.get("license") or "Unknown"

                # Try available PDF locations.
                downloaded = False

                for pdf_url in pdf_urls:

                    paper_number = current_total + 1

                    filename = (
                        f"Paper_{paper_number}_"
                        f"{clean_filename(title)}.pdf"
                    )

                    destination = DOCUMENTS_DIR / filename

                    # Never overwrite an existing filename.
                    suffix = 2

                    while destination.exists():

                        filename = (
                            f"Paper_{paper_number}_"
                            f"{clean_filename(title)}_{suffix}.pdf"
                        )

                        destination = DOCUMENTS_DIR / filename

                        suffix += 1

                    print(f"\nTrying PDF: {title}")

                    file_hash, file_size = download_pdf(
                        pdf_url,
                        destination
                    )

                    if not file_hash:
                        continue

                    # Check identical file contents.
                    if file_hash in existing_hashes:

                        destination.unlink(missing_ok=True)

                        print("Skipped: identical PDF already exists.")

                        continue

                    # Record successful download.
                    record = {
                        "title": title,
                        "authors": authors,
                        "year": year,
                        "doi": doi,
                        "topic": topic,
                        "pdf_url": pdf_url,
                        "filename": filename,
                        "file_size_kb": round(file_size / 1024, 2),
                        "openalex_id": openalex_id,
                        "cited_by_count": cited_by_count,
                        "license": license_name
                    }

                    metadata.append(record)

                    existing_ids.add(openalex_id)

                    if doi:
                        existing_dois.add(doi)

                    existing_titles.add(normalized_title)

                    existing_hashes.add(file_hash)

                    current_total += 1

                    downloaded_count += 1

                    downloaded = True

                    print(f"SUCCESS: {filename}")

                    break

                if not downloaded:
                    skipped_count += 1

            time.sleep(0.2)

    # Preserve old records and save new metadata.
    save_metadata(metadata)

    # Generate report.
    report = [
        "=" * 65,
        "RAG RESEARCH PAPER DOWNLOAD REPORT",
        "=" * 65,
        f"Existing and new metadata records: {len(metadata)}",
        f"New papers downloaded: {downloaded_count}",
        f"Skipped candidates: {skipped_count}",
        f"Target total papers: {TARGET_TOTAL_PAPERS}",
        f"PDF folder: {DOCUMENTS_DIR}",
        "",
        "Existing PDF files were not overwritten or deleted.",
        "Metadata records were preserved.",
        "=" * 65
    ]

    report_text = "\n".join(report)

    REPORT_FILE.write_text(report_text, encoding="utf-8")

    print("\n" + report_text)


if __name__ == "__main__":
    main()
