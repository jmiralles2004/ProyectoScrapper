"""Utilities for extracting text from PDF files."""

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
import pypdfium2 as pdfium
import pytesseract


class PdfExtractionError(Exception):
    """Raised when PDF text extraction fails."""


@dataclass(slots=True)
class PdfTextExtractionResult:
    """Result of extracting text from a PDF file."""

    text: str
    method: str


def _extract_embedded_text(file_bytes: bytes) -> str:
    """Extract embedded text from a PDF without OCR."""

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as exc:
        raise PdfExtractionError("No se pudo leer el PDF") from exc

    chunks: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        page_text = page_text.strip()
        if page_text:
            chunks.append(page_text)

    return "\n".join(chunks).strip()


def _extract_text_with_ocr(file_bytes: bytes, languages: str, dpi: int) -> str:
    """Render PDF pages as images and run OCR with Tesseract."""

    try:
        document = pdfium.PdfDocument(file_bytes)
    except Exception as exc:
        raise PdfExtractionError("No se pudo abrir el PDF para OCR") from exc

    chunks: list[str] = []
    scale = max(dpi, 72) / 72.0

    try:
        for page in document:
            pil_image = page.render(scale=scale).to_pil()
            page_text = pytesseract.image_to_string(pil_image, lang=languages).strip()
            if page_text:
                chunks.append(page_text)
    except pytesseract.TesseractNotFoundError as exc:
        raise PdfExtractionError("OCR no disponible: falta instalar tesseract") from exc
    except Exception as exc:
        raise PdfExtractionError("Fallo al ejecutar OCR sobre el PDF") from exc

    return "\n".join(chunks).strip()


def extract_text_from_pdf(
    file_bytes: bytes,
    ocr_enabled: bool = True,
    ocr_languages: str = "spa+eng",
    ocr_dpi: int = 300,
) -> PdfTextExtractionResult:
    """Extract text from a PDF, falling back to OCR when needed."""

    embedded_text = _extract_embedded_text(file_bytes)
    if embedded_text:
        return PdfTextExtractionResult(text=embedded_text, method="embedded")

    if not ocr_enabled:
        return PdfTextExtractionResult(text="", method="none")

    ocr_text = _extract_text_with_ocr(file_bytes, ocr_languages, ocr_dpi)
    if not ocr_text:
        return PdfTextExtractionResult(text="", method="ocr")

    return PdfTextExtractionResult(text=ocr_text, method="ocr")
