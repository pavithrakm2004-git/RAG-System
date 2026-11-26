
from pathlib import Path
import fitz  # PyMuPDF

# Folder containing the downloaded research papers
PDF_FOLDER = Path("documents")

pdf_files = list(PDF_FOLDER.glob("*.pdf"))

print("=" * 55)
print("PDF VALIDATION REPORT")
print("=" * 55)

if not pdf_files:
    print("No PDF files found!")
else:
    total_pages = 0

    for pdf_file in pdf_files:
        try:
            document = fitz.open(pdf_file)
            page_count = len(document)

            # Check whether text can be extracted
            extracted_text = ""
            for page in document:
                extracted_text += page.get_text()

            total_pages += page_count

            print(f"\nFile: {pdf_file.name}")
            print(f"Pages: {page_count}")
            print(f"Readable text: {'Yes' if extracted_text.strip() else 'No'}")

            document.close()

        except Exception as error:
            print(f"\nFile: {pdf_file.name}")
            print(f"ERROR: {error}")

    print("\n" + "=" * 55)
    print(f"Total PDF files: {len(pdf_files)}")
    print(f"Total pages: {total_pages}")
    print("=" * 55)
