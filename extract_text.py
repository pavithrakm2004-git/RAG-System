
from pathlib import Path
from pypdf import PdfReader

PDF_FOLDER = Path("documents")
OUTPUT_FOLDER = Path("extracted_text")

OUTPUT_FOLDER.mkdir(exist_ok=True)

pdf_files = list(PDF_FOLDER.glob("*.pdf"))

print("=" * 55)
print("PDF TEXT EXTRACTION")
print("=" * 55)

for pdf_path in pdf_files:
    try:
        reader = PdfReader(str(pdf_path))

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                extracted_pages.append(
                    f"\n--- Page {page_number} ---\n{text}"
                )

        full_text = "\n".join(extracted_pages)

        output_file = OUTPUT_FOLDER / f"{pdf_path.stem}.txt"
        output_file.write_text(full_text, encoding="utf-8")

        print(f"\nPDF: {pdf_path.name}")
        print(f"Pages: {len(reader.pages)}")
        print(f"Extracted characters: {len(full_text)}")
        print(f"Saved: {output_file}")

    except Exception as error:
        print(f"\nError processing {pdf_path.name}: {error}")

print("\n" + "=" * 55)
print("TEXT EXTRACTION COMPLETED")
print("=" * 55)
