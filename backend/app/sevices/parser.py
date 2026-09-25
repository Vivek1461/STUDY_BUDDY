import fitz
from docx import Document
from pptx import Presentation
from PIL import Image
import pytesseract 
import os
from pathlib import Path

def extract_text(file_path: str, file_type: str)-> str:
    path =Path(file-path)
    if not path.exists():
        raise FileNotFoundError(f"File Not Found: {file_path}")

    if file_type == "pdf":
        return _parse_pdf (file_path)

    elif file_type == "docx":
        return _parse_docx (file_path)
    elif file_type == "pptx":
        return _parse_pptx (file_path)
    elif file_type == "image":
        return _parse_image (file_path)
    