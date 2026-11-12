"""Safe text extraction for supported study document formats."""
from pathlib import Path
import fitz
from docx import Document
from pptx import Presentation
from PIL import Image
import pytesseract

SUPPORTED_TYPES = {".pdf": "pdf", ".docx": "docx", ".pptx": "pptx",
                   ".jpg": "image", ".jpeg": "image", ".png": "image", ".txt": "txt"}

def detect_file_type(filename: str) -> str:
    kind = SUPPORTED_TYPES.get(Path(filename).suffix.lower())
    if not kind:
        raise ValueError("Unsupported file extension")
    return kind

def extract_text(file_path: str, file_type: str) -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError("Uploaded file was not found")
    parsers = {"pdf": _parse_pdf, "docx": _parse_docx, "pptx": _parse_pptx,
               "image": _parse_image, "txt": _parse_txt}
    parser = parsers.get(file_type)
    if parser is None:
        raise ValueError("Unsupported document type")
    return parser(path)

def _parse_pdf(path: Path) -> str:
    pages = []
    with fitz.open(path) as document:
        for number, page in enumerate(document, start=1):
            value = page.get_text("text").strip()
            if value:
                pages.append(f"[Page {number}]\n{value}")
    return "\n\n".join(pages)

def _parse_docx(path: Path) -> str:
    document = Document(path)
    parts = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n".join(parts)

def _parse_pptx(path: Path) -> str:
    presentation = Presentation(path)
    slides = []
    for number, slide in enumerate(presentation.slides, start=1):
        lines = [shape.text.strip() for shape in slide.shapes if shape.has_text_frame and shape.text.strip()]
        if lines:
            slides.append(f"[Slide {number}]\n" + "\n".join(lines))
    return "\n\n".join(slides)

def _parse_image(path: Path) -> str:
    with Image.open(path) as image_file:
        image_file.verify()
    with Image.open(path) as image_file:
        return pytesseract.image_to_string(image_file.convert("RGB"), lang="eng").strip()

def _parse_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()
