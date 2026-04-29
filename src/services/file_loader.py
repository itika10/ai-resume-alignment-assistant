from io import BytesIO
from typing import List, Optional

import pdfplumber
from docx import Document


def _is_useful_url(url: str) -> bool:
    """
    Filter out non-profile URIs that the parser does not need.
    Email/phone are extracted from the body separately.
    """
    if not url:
        return False
    lowered = url.strip().lower()
    if lowered.startswith("mailto:") or lowered.startswith("tel:"):
        return False
    if not (lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("www.")):
        return False
    return True


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
    return out


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF file using pdfplumber.

    Also extracts URI annotations (clickable hyperlinks) and appends them
    as a 'DETECTED URLS' block so the parser can match them to social
    profiles even when the visible text only shows a label like 'LinkedIn'.
    """
    text_parts: List[str] = []
    urls: List[str] = []

    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

            for annot in (page.annots or []):
                try:
                    uri = annot.get("uri") or ""
                    if _is_useful_url(uri):
                        urls.append(uri)

                    # Some PDFs nest the URI under the action data
                    data = annot.get("data") or {}
                    action_uri = ""
                    if isinstance(data, dict):
                        action = data.get("A") or data.get("/A") or {}
                        if isinstance(action, dict):
                            action_uri = action.get("URI") or action.get("/URI") or ""
                    if _is_useful_url(action_uri):
                        urls.append(action_uri)
                except Exception:
                    continue

    body = "\n".join(text_parts)
    return _append_url_block(body, urls)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file using python-docx.

    Also pulls hyperlink target URLs from the document's relationships table
    and appends them as a 'DETECTED URLS' block.
    """
    document = Document(BytesIO(file_bytes))
    text_parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    body = "\n".join(text_parts).strip()

    urls: List[str] = []
    try:
        for rel in document.part.rels.values():
            if "hyperlink" in (rel.reltype or ""):
                target = (rel.target_ref or "").strip()
                if _is_useful_url(target):
                    urls.append(target)
    except Exception:
        pass

    return _append_url_block(body, urls)


def _append_url_block(body: str, urls: List[str]) -> str:
    deduped = _dedupe_preserve_order(urls)
    if not deduped:
        return body

    block_lines = ["", "DETECTED URLS (from hyperlinks in source file):"]
    for url in deduped:
        block_lines.append(f"- {url}")

    return body + "\n" + "\n".join(block_lines)


def clean_text(text: str) -> str:
    """
    Clean the extracted text by removing extra whitespace and normalizing it.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines).strip()


def load_resume_text(uploaded_file) -> str:
    """
    Detect the file_type and extract text from uploaded resume.
    Supports PDF and DOCX.
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
