from io import BytesIO
from typing import Optional

import pdfplumber
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file using PDFplumber
    """
    text_parts = []

    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file using python-docx
    """
    document = Document(BytesIO(file_bytes))
    text_parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(text_parts).strip()

def clean_text(text: str) -> str:
    """
    Clean the extracted text by removing extra whitespace and normalizing it.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines).strip()

def load_resume_text(uploaded_file) -> str:
    """
    Detect the file_type and extract text from uploaded resume.
    Supports PDF and DOC
    """
    if uploaded_file is None:
        raise ValueError("No file uploaded")
    
    file_name = uploaded_file.name
    file_bytes = uploaded_file.read()

    if file_name.lower().endswith('.pdf'):
        raw_text = extract_text_from_pdf(file_bytes)
    elif file_name.lower().endswith('.docx'):
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")
    
    cleaned_text = clean_text(raw_text)

    if not cleaned_text:
        raise ValueError("No text could be extracted from the uploaded file. Please ensure the file is not empty and is properly formatted.")
    
    return cleaned_text