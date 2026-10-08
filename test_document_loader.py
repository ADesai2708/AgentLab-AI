from researchops.tools.document_loader import PDFDocumentLoader


loader = PDFDocumentLoader()

chunks = loader.load(
    "data/documents/sample.pdf"
)

print(f"Total chunks: {len(chunks)}")

for chunk in chunks[:3]:
    print("\n--- CHUNK ---")
    print("Document:", chunk.document_id)
    print("Chunk ID:", chunk.chunk_id)
    print("Page:", chunk.page_number)
    print("Source:", chunk.source)
    print("Text:", chunk.text[:300])