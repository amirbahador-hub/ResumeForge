from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

SUPPORTED_TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".text"}


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(path)
    if suffix in SUPPORTED_TEXT_SUFFIXES:
        return path.read_text(encoding="utf-8")
    raise ValueError(
        f"Unsupported document type {path.suffix!r}. "
        "Supported types: .pdf, .md, .markdown, .txt, .text"
    )


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"--- Page {index} ---\n{text.strip()}")
    extracted = "\n\n".join(pages).strip()
    if not extracted:
        raise ValueError(f"No extractable text found in PDF: {path}")
    return extracted
