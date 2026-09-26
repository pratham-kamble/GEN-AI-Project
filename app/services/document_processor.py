import os
import pdfplumber
from docx import Document

from app.utils.exceptions import (
    DocumentProcessingError,
    UnsupportedFileFormatError,
    EmptyDocumentError,
    CorruptedDocumentError,
)

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def extract_text_from_pdf(file_path: str) -> str:
    try:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise CorruptedDocumentError(f"Failed to read PDF: {e}")


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        text_parts = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise CorruptedDocumentError(f"Failed to read DOCX: {e}")


def extract_text(file_path: str) -> str:
    """
    Extract raw text from a resume/JD file. Supports .pdf and .docx.
    Raises DocumentProcessingError subclasses on failure.
    """
    if not os.path.isfile(file_path):
        raise DocumentProcessingError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileFormatError(
            f"Unsupported file format: '{ext}'. Supported: {SUPPORTED_EXTENSIONS}"
        )

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_docx(file_path)

    if not text:
        raise EmptyDocumentError("Document contains no extractable text.")

    return text 