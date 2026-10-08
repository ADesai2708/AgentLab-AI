from pathlib import Path

from pypdf import PdfReader

from researchops.models import DocumentChunk


class PDFDocumentLoader:

    def load(self, file_path: str) -> list[DocumentChunk]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

        reader = PdfReader(str(path))

        document_id = path.stem
        chunks = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):
            text = page.extract_text() or ""

            text = " ".join(
                text.split()
            )

            if not text:
                continue

            chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    chunk_id=f"{document_id}-page-{page_number}",
                    text=text,
                    page_number=page_number,
                    source=str(path)
                )
            )

        return chunks