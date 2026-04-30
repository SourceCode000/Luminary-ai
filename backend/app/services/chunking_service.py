import os
from pypdf import PdfReader
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import get_settings

settings = get_settings()


class ChunkingService:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,         # each chunk is ~500 characters
            chunk_overlap=50,       # 50 character overlap between chunks
            separators=["\n\n", "\n", ".", " ", ""]
        )

    # ── Text Extraction ────────────────────────────────────────────

    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract raw text from PDF, DOCX, or TXT file."""

        if file_type == "pdf":
            return self._extract_from_pdf(file_path)
        elif file_type == "docx":
            return self._extract_from_docx(file_path)
        elif file_type == "txt":
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file page by page."""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file paragraph by paragraph."""
        doc = DocxDocument(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _extract_from_txt(self, file_path: str) -> str:
        """Read plain text file directly."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # ── Chunking ───────────────────────────────────────────────────

    def chunk_text(self, text: str) -> list[str]:
        """Split extracted text into overlapping chunks."""
        if not text.strip():
            return []
        return self.splitter.split_text(text)

    # ── Main Entry Point ───────────────────────────────────────────

    def process(self, file_path: str, file_type: str) -> list[str]:
        """
        Full pipeline — extract text then chunk it.
        Returns a list of text chunks ready for embedding.
        """
        text = self.extract_text(file_path, file_type)
        chunks = self.chunk_text(text)
        return chunks